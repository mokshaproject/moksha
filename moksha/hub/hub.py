# This file is part of Moksha.
#
# Moksha is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Moksha is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Moksha.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2008, Red Hat, Inc.
# Authors: Luke Macken <lmacken@redhat.com>

import os
import sys
import signal
import pkg_resources
import logging

from orbited import json
from threading import Thread
from collections import defaultdict
from twisted.internet import reactor
from twisted.internet.threads import deferToThread

from moksha.api.hub import Consumer
from moksha.lib.utils import trace
from moksha.hub.amqp import AMQPHub
from moksha.hub.stomp import StompHub

log = logging.getLogger(__name__)
deferred = deferToThread.__get__

AMQP = False
STOMP = True

class MokshaConsumer(Consumer):
    topic = 'feed_demo'
    def consume(self, message):
        print "MokshaConsumer.consume(%s)" % message


class OtherConsumer(Consumer):
    topic = 'graph_demo'
    def consume(self, message):
        print "OtherConsumer.consume(%s)" % message


class MokshaHub(StompHub, AMQPHub):

    def __init__(self, broker='127.0.0.1', port='5672', username='guest',
                 password='guest', ssl=False, topics=None):
        # @@ read configuration...

        # if there is an amqp host, load the amqp hub
        if AMQP:
            AMQPHub.__init__(self, broker + ':' + port, username=username,
                             password=password, ssl=ssl)
        # if there's a stomp_host, load the stomp hub
        if STOMP:
            self.topics = topics or {}
            StompHub.__init__(self, broker, username=username,
                              password=password, topics=self.topics.keys())

    def send_message(self, topic, message, jsonify=True):
        """ Send a message to a specific topic.

        :topic: The stop to send the message to
        :message: The message body.  Can be a string, list, or dict.
        :jsonify: To automatically encode non-strings to JSON

        """
        if jsonify and not isinstance(message, basestring):
            message = json.encode(message)
        if AMQP:
            AMQPHub.send_message(self, message, exchange=topic)
        elif STOMP:
            StompHub.send_message(self, topic, message)

    @trace
    def watch_topic(self, topic, callback):
        """
        This method will cause the specified `callback` to be executed with
        each message that goes through a given topic.
        """
        if len(self.topics[topic]) == 0:
            if AMQP:
                self.subscribe(topic,
                               callback=self.consume_amqp_message,
                               no_ack=True)
            if STOMP:
                self.subscribe(topic)
        self.topics[topic].append(callback)

    @trace
    def consume_amqp_message(self, message):
        topic = message.delivery_info['routing_key']
        try:
            body = json.decode(message.body)
        except Exception, e:
            log.warning('Cannot decode message from JSON: %s' % e)
            body = message.body
        for callback in self.topics.get(topic, []):
            Thread(target=callback, args=[body]).start()

    def consume_stomp_message(self, message):
        topic = message['headers'].get('destination')
        if not topic:
            return
        try:
            body = json.decode(message['body'])
        except Exception, e:
            log.warning('Cannot decode message from JSON: %s' % e)
            body = message['body']
        for callback in self.topics.get(topic, []):
            Thread(target=callback, args=[body]).start()

    def start(self):
        log.debug('MokshaHub.start()')
        while True:
            try:
                AMQPHub.wait(self)
            except Exception, e:
                log.warning('Exception thrown while waiting on AMQP '
                            'channel: %s' % str(e))
                break
        log.warning('MokshaHub.start exiting...')

    def stop(self):
        if AMQP:
            try:
                AMQPHub.close(self)
            except Exception, e:
                log.warning('Exception when closing AMQPHub: %s' % str(e))


class CentralMokshaHub(MokshaHub):
    """
    The Moksha Hub is responsible for initializing all of the Hooks,
    AMQP queues, exchanges, etc.
    """
    topics = None # {topic_name: [<Consumer>,]}
    data_streams = None # [<DataStream>,]

    def __init__(self, broker='127.0.0.1', port='5672', username='guest',
                 password='guest', ssl=False):
        self.topics = defaultdict(list)
        self.__init_consumers()

        MokshaHub.__init__(self, broker=broker, port=port, username=username,
                           password=password, ssl=ssl,
                           topics=self.topics)

        self.__run_consumers()
        self.__init_data_streams()

    def __init_consumers(self):
        """ Initialize all Moksha Consumer objects """
        for consumer in pkg_resources.iter_entry_points('moksha.consumer'):
            c_class = consumer.load()
            log.debug("%s consumer is watching the %r topic" % (
                      c_class.__name__, c_class.topic))
            self.topics[c_class.topic].append(c_class)

    def __run_consumers(self):
        """ Instantiate the consumers """
        for topic in self.topics:
            for i, consumer in enumerate(self.topics[topic]):
                c = consumer()
                self.topics[topic][i] = c.consume
                if AMQP:
                    AMQPHub.watch_topic(c.topic,
                                        callback=lambda msg: c.consume(msg))

                # The StompHub will automatically subscribe to the topics
                # when the stomp connection is successful.

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
        if AMQP:
            AMQPHub.create_queue(topic)

        # We don't need to do anything special for Stomp

        # @@ remove this when we keep track of this in a DB
        if topic not in self.topics:
            self.topics[topic] = []

    @deferred
    def start(self):
        """ The MokshaHub's main loop """
        MokshaHub.start(self)

    def stop(self):
        log.debug("Stopping the CentralMokshaHub")
        MokshaHub.stop(self)
        if self.data_streams:
            for stream in self.data_streams:
                log.debug("Stopping data stream %s" % stream)
                stream.stop()
        if AMQP:
            try:
                AMQPHub.close(self)
            except Exception, e:
                log.warning('Exception when closing AMQPHub: %s' % str(e))



def main():
    hub = CentralMokshaHub()
    #hub.create_topic("testing")
    #hub.queue_bind("testing", "amq.topic")
    #hub.send_message('foo', exchange='amq.topic', routing_key='testing')

    #def callback(msg):
    #    for key, val in msg.properties.items():
    #        print '%s: %s' % (key, str(val))
    #    for key, val in msg.delivery_info.items():
    #        print '> %s: %s' % (key, str(val))
    #    print ''
    #    print msg.body
    #    print '-------'

    #hub.watch_topic('testing', callback=callback)
    #hub.send_message('bar', exchange='amq.topic', routing_key='testing')

    ## only with amqp ?
    #hub.start(hub)

    def handle_signal(signum, stackframe):
        from twisted.internet import reactor
        if signum in [signal.SIGHUP, signal.SIGINT]:
            reactor.stop()
            hub.stop()
            sys.exit(0)

    print "Running the reactor!"
    signal.signal(signal.SIGHUP, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    reactor.run(installSignalHandlers=False)
    print "Reactor stopped!"

def setup_logger(verbose):
    global log
    sh = logging.StreamHandler()
    level = verbose and logging.DEBUG or logging.INFO
    log.setLevel(level)
    sh.setLevel(level)
    format = logging.Formatter("%(message)s")
    sh.setFormatter(format)
    log.addHandler(sh)

if __name__ == '__main__':
    import sys
    setup_logger('-v' in sys.argv or '--verbose' in sys.argv)
    main()
