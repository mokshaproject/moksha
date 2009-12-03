# This file is part of Moksha.
# Copyright (C) 2008-2009  Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors: Luke Macken <lmacken@redhat.com>

from moksha.hub.reactor import reactor

import sys
import signal
import pkg_resources
import logging

from tg import config
from orbited import json
from paste.deploy import appconfig

from moksha.lib.helpers import trace, defaultdict, get_moksha_config_path, get_moksha_appconfig
from moksha.hub.amqp import AMQPHub
from moksha.hub.stomp import StompHub

log = logging.getLogger('moksha.hub')

class MokshaHub(StompHub, AMQPHub):

    topics = None # {topic_name: [callback,]}

    def __init__(self, topics=None):
        global config
        self.amqp_broker = config.get('amqp_broker', None)
        self.stomp_broker = config.get('stomp_broker', None)

        # If we're running outside of middleware and hub, load config
        if not self.amqp_broker and not self.stomp_broker:
            config = get_moksha_appconfig()
            self.amqp_broker = config.get('amqp_broker', None)
            self.stomp_broker = config.get('stomp_broker', None)

        if self.amqp_broker and self.stomp_broker:
            log.warning("Running with both a STOMP and AMQP broker. "
                        "This mode is experimental and may or may not work")

        if not self.topics:
            self.topics = defaultdict(list)

        if topics:
            for topic, callbacks in topics.iteritems():
                if not isinstance(callbacks, list):
                    callbacks = [callbacks]
                for callback in callbacks:
                    self.topics[topic].append(callback)

        if self.amqp_broker:
            AMQPHub.__init__(self, self.amqp_broker)

        if self.stomp_broker:
            log.info('Initializing STOMP support')
            StompHub.__init__(self, self.stomp_broker,
                              port=config.get('stomp_port', 61613),
                              username=config.get('stomp_user', 'guest'),
                              password=config.get('stomp_pass', 'guest'),
                              topics=self.topics.keys())

    def send_message(self, topic, message, jsonify=True):
        """ Send a message to a specific topic.

        :topic: A topic or list of topics to send the message to.
        :message: The message body.  Can be a string, list, or dict.
        :jsonify: To automatically encode non-strings to JSON

        """
        if not isinstance(topic, list):
            topics = [topic]
        else:
            topics = topic
        for topic in topics:
            if jsonify and not isinstance(message, basestring):
                message = json.encode(message)
            if self.amqp_broker:
                AMQPHub.send_message(self, topic, message, routing_key=topic)
            elif self.stomp_broker:
                StompHub.send_message(self, topic, message)

    def close(self):
        if self.amqp_broker:
            try:
                AMQPHub.close(self)
            except Exception, e:
                log.warning('Exception when closing AMQPHub: %s' % str(e))

    def watch_topic(self, topic, callback):
        """
        This method will cause the specified `callback` to be executed with
        each message that goes through a given topic.
        """
        log.debug('watch_topic(%s)' % locals())
        if len(self.topics[topic]) == 0:
            if self.stomp_broker:
                self.subscribe(topic)
        self.topics[topic].append(callback)

    def consume_amqp_message(self, message):
        self.message_accept(message)
        topic = message.headers[0]['routing_key']
        try:
            body = json.decode(message.body)
        except Exception, e:
            log.warning('Cannot decode message from JSON: %s' % e)
            log.debug('Message: %r' % message.body)
            body = message.body
        if self.stomp_broker:
            StompHub.send_message(self, topic.encode('utf8'),
                                  message.body.encode('utf8'))

    def consume_stomp_message(self, message):
        topic = message['headers'].get('destination')
        if not topic:
            log.debug("Got message without a topic: %r" % message)
            return

        # FIXME: only do this if the consumer wants it `jsonified`
        try:
            body = json.decode(message['body'])
        except Exception, e:
            log.warning('Cannot decode message from JSON: %s' % e)
            body = {}

        # feed all of our consumers
        for callback in self.topics.get(topic, []):
            reactor.callInThread(callback, {'body': body, 'topic': topic})


class CentralMokshaHub(MokshaHub):
    """
    The Moksha Hub is responsible for initializing all of the Hooks,
    AMQP queues, exchanges, etc.
    """
    data_streams = None # [<DataStream>,]

    def __init__(self):
        self.topics = defaultdict(list)
        self.__init_consumers()

        MokshaHub.__init__(self)

        if self.amqp_broker:
            self.__init_amqp()

        self.__run_consumers()
        self.__init_data_streams()

    def __init_amqp(self):
        if self.stomp_broker:
            log.debug("Initializing local AMQP queue...")
            self.server_queue_name = 'moksha_hub_' + self.session.name
            self.queue_declare(queue=self.server_queue_name, exclusive=True)
            self.exchange_bind(self.server_queue_name, binding_key='#')
            self.local_queue_name = 'moksha_hub'
            self.local_queue = self.session.incoming(self.local_queue_name)
            self.message_subscribe(queue=self.server_queue_name,
                                   destination=self.local_queue_name)
            self.local_queue.start()
            self.local_queue.listen(self.consume_amqp_message)

    def __init_consumers(self):
        """ Initialize all Moksha Consumer objects """
        log.info('Loading Moksha Consumers')
        for consumer in pkg_resources.iter_entry_points('moksha.consumer'):
            c_class = consumer.load()
            log.info("%s consumer is watching the %r topic" % (
                     c_class.__name__, c_class.topic))
            self.topics[c_class.topic].append(c_class)

    def __run_consumers(self):
        """ Instantiate the consumers """
        self.consumers = []
        for topic in self.topics:
            for i, consumer in enumerate(self.topics[topic]):
                c = consumer()
                self.consumers.append(c)
                self.topics[topic][i] = c.consume

    def __init_data_streams(self):
        """ Initialize all data streams """
        self.data_streams = []
        for stream in pkg_resources.iter_entry_points('moksha.stream'):
            stream_class = stream.load()
            log.info('Loading %s data stream' % stream_class.__name__)
            stream_obj = stream_class()
            self.data_streams.append(stream_obj)

    @trace
    def create_topic(self, topic):
        if self.amqp_broker:
            AMQPHub.create_queue(topic)

        # @@ remove this when we keep track of this in a DB
        if topic not in self.topics:
            self.topics[topic] = []

    def stop(self):
        log.debug("Stopping the CentralMokshaHub")
        MokshaHub.close(self)
        if self.data_streams:
            for stream in self.data_streams:
                log.debug("Stopping data stream %s" % stream)
                stream.stop()
        if self.consumers:
            for consumer in self.consumers:
                log.debug("Stopping consumer %s" % consumer)
                consumer.stop()


def setup_logger(verbose):
    global log
    sh = logging.StreamHandler()
    level = verbose and logging.DEBUG or logging.INFO
    log.setLevel(level)
    sh.setLevel(level)
    format = logging.Formatter('[moksha.hub] %(levelname)s %(asctime)s %(message)s')
    sh.setFormatter(format)
    log.addHandler(sh)


def main():
    """ The main MokshaHub method """
    setup_logger('-v' in sys.argv or '--verbose' in sys.argv)
    cfg = appconfig('config:' + get_moksha_config_path())
    config.update(cfg)

    hub = CentralMokshaHub()

    def handle_signal(signum, stackframe):
        from moksha.hub.reactor import reactor
        if signum in [signal.SIGHUP, signal.SIGINT]:
            hub.stop()
            reactor.stop()

    signal.signal(signal.SIGHUP, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    log.info("Running the MokshaHub reactor")
    reactor.run(installSignalHandlers=False)
    log.info("MokshaHub reactor stopped")


if __name__ == '__main__':
    main()
