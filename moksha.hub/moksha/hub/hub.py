# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors: Luke Macken <lmacken@redhat.com>
#          Ralph Bean  <rbean@redhat.com>


import os
import sys
import json as JSON


from moksha.common.lib.helpers import appconfig

# Look in the current directory for egg-info
if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

import pkg_resources
import logging

try:
    from twisted.internet.error import ReactorNotRunning
except ImportError:  # Twisted 8.2.0 on RHEL5
    class ReactorNotRunning(object):
        pass

from twisted.internet import protocol
from txws import WebSocketFactory
from moksha.common.lib.helpers import trace, defaultdict, get_moksha_config_path
from moksha.common.lib.converters import asbool

AMQPHubExtension, StompHubExtension, ZMQHubExtension = None, None, None
try:
    from moksha.hub.amqp import AMQPHubExtension
except ImportError:
    pass

try:
    from moksha.hub.stomp import StompHubExtension
except ImportError:
    pass

try:
    from moksha.hub.zeromq import ZMQHubExtension
except ImportError as e:
    print e
    pass

log = logging.getLogger('moksha.hub')

_hub = None

from moksha.hub import NO_CONFIG_MESSAGE


def find_hub_extensions(config):
    """ Return a tuple of hub extensions found in the config file. """

    possible_bases = {
        'amqp_broker': AMQPHubExtension,
        'stomp_broker': StompHubExtension,
        'zmq_enabled': ZMQHubExtension,
    }

    broker_vals = [config.get(k, None) for k in possible_bases.keys()]

    # If we're running outside of middleware and hub, load config
    if not any(broker_vals):
        config_path = get_moksha_config_path()
        if not config_path:
            raise ValueError(NO_CONFIG_MESSAGE)

        cfg = appconfig('config:' + config_path)
        config.update(cfg)
        broker_vals = [config.get(k, None) for k in possible_bases.keys()]

    # If there are no brokers defined.. that's a problem.
    if not any(broker_vals):
        raise ValueError("No messaging methods defined.")

    if len(filter(None, broker_vals)) > 1:
        log.warning("Running with multiple brokers.  "
                    "This mode is experimental and may or may not work")

    extensions = tuple([
        b for k, b in possible_bases.items() if config.get(k, None)
    ])
    import pprint
    pprint.pprint(extensions)
    return extensions


class MokshaHub(object):
    topics = None  # {topic_name: [callback,]}

    def __init__(self, config, topics=None):
        self.config = config

        if not self.topics:
            self.topics = defaultdict(list)

        if topics == None:
            topics = {}

        for topic, callbacks in topics.iteritems():
            if not isinstance(callbacks, list):
                callbacks = [callbacks]

            for callback in callbacks:
                self.topics[topic].append(callback)

        self.extensions = [
            ext(self, config) for ext in find_hub_extensions(config)
        ]

    def send_message(self, topic, message, jsonify=True):
        """ Send a message to a specific topic.

        :topic: A topic or list of topics to send the message to.
        :message: The message body.  Can be a string, list, or dict.
        :jsonify: To automatically encode non-strings to JSON

        """

        if jsonify:
            message = JSON.dumps(message)

        if not isinstance(topic, list):
            topics = [topic]
        else:
            topics = topic

        for topic in topics:
            if isinstance(topic, unicode):
                # txzmq isn't smart enough to handle unicode yet.
                # Try removing this and sending a unicode topic in the future to
                # see if it works.
                topic = topic.encode('utf-8')

            for ext in self.extensions:
                ext.send_message(topic, message)

    def close(self):
        try:
            for ext in self.extensions:
                if hasattr(ext, 'close'):
                    ext.close()
        except Exception, e:
            log.warning('Exception when closing MokshaHub: %s' % str(e))

    def subscribe(self, topic, callback):
        """
        This method will cause the specified `callback` to be executed with
        each message that goes through a given topic.
        """

        for ext in self.extensions:
            ext.subscribe(topic, callback)

    def consume_amqp_message(self, message):
        self.message_accept(message)
        try:
            topic = message.get('delivery_properties').routing_key
        except AttributeError:
            # If we receive an AMQP message without a toipc, don't proxy it to STOMP
            return

        # TODO -- this isn't extensible.  how should forwarding work if there
        # are three broker types enabled?
        for ext in self.extensions:
            if StompHubExtension and isinstance(ext, StompHubExtension):
                ext.send_message(self, topic.encode('utf8'),
                                 message.body.encode('utf8'))

    def consume_stomp_message(self, message):
        from moksha.hub.reactor import reactor

        topic = message['headers'].get('destination')
        if not topic:
            log.debug("Got message without a topic: %r" % message)
            return

        # FIXME: only do this if the consumer wants it `jsonified`
        try:
            body = JSON.decode(message['body'])
        except Exception, e:
            log.warning('Cannot decode message from JSON: %s' % e)
            #body = {}
            body = message['body']

        # feed all of our consumers
        for callback in self.topics.get(topic, []):
            reactor.callInThread(callback, {'body': body, 'topic': topic})


class CentralMokshaHub(MokshaHub):
    """
    The Moksha Hub is responsible for initializing all of the Hooks,
    AMQP queues, exchanges, etc.
    """
    producers = None # [<Producer>,]

    def __init__(self, config, consumers=None, producers=None):
        log.info('Loading the Moksha Hub')
        self.topics = defaultdict(list)

        # These are used to override the entry-points behavior
        self._consumers = consumers
        self._producers = producers

        self.__init_consumers()

        super(CentralMokshaHub, self).__init__(config)

        # FIXME -- this needs to be reworked.
        # TODO -- consider moving this to the AMQP specific modules
        for ext in self.extensions:
            if AMQPHubExtension and isinstance(ext, AMQPHubExtension):
                self.__init_amqp()

        self.__run_consumers()
        self.__init_producers()
        self.__init_websocket_server()

    def __init_websocket_server(self):
        from moksha.hub.reactor import reactor

        if self.config.get('moksha.livesocket.backend', 'amqp') != 'websocket':
            return
        log.info("Enabling websocket server")

        port = int(self.config.get('moksha.livesocket.websocket.port', 0))
        if not port:
            raise ValueError("websocket is backend, but no port set")

        class RelayProtocol(protocol.Protocol):
            moksha_hub = self

            def dataReceived(self, data):
                """ Messages sent from the browser arrive here.

                This hook:
                  1) Acts on any special control messages
                  2) Forwards messages onto the zeromq hub
                """

                try:
                    json = JSON.loads(data)

                    if json['topic'] == '__topic_subscribe__':
                        # If this is a custom control message, then subscribe.
                        def send_to_websocket(zmq_message):
                            """ Callback.  Sends a message to the browser """
                            msg = JSON.dumps({
                                'topic': zmq_message.topic,
                                'body': JSON.loads(zmq_message.body),
                            })
                            self.transport.write(msg)

                        _topic = json['body']
                        log.info("Websocket subscribing to %r." % _topic)
                        self.moksha_hub.subscribe(_topic, send_to_websocket)
                    else:
                        # FIXME - The following is disabled temporarily until we can
                        # devise a secure method of "firewalling" where messages
                        # can and can't go.  See the following for more info:
                        #   https://fedorahosted.org/moksha/ticket/245
                        #   https://github.com/gregjurman/zmqfirewall

                        key = 'moksha.livesocket.websocket.client2server'
                        if asbool(self.config.get(key, False)):
                            # Simply forward on the message through the hub.
                            self.moksha_hub.send_message(
                                json['topic'],
                                json['body'],
                            )


                except Exception as e:
                    import traceback
                    log.error(traceback.format_exc())


        class RelayFactory(protocol.Factory):
            def buildProtocol(self, addr):
                return RelayProtocol()

        reactor.listenTCP(port, WebSocketFactory(RelayFactory()))
        log.info("Websocket server set to run on port %r" % port)

    # TODO -- consider moving this to the AMQP specific modules
    def __init_amqp(self):
        # Ok this looks odd at first.  I think this is only used when we are briding stomp/amqp,
        # Since each producer and consumer opens up their own AMQP connections anyway
        if not (StompHubExtension and isinstance(self, StompHubExtension)):
            return

        log.debug("Initializing local AMQP queue...")
        self.server_queue_name = 'moksha_hub_' + self.session.name
        self.queue_declare(queue=self.server_queue_name,
                           exclusive=True, auto_delete=True)
        self.exchange_bind(self.server_queue_name, binding_key='#')
        self.local_queue_name = 'moksha_hub'
        self.local_queue = self.session.incoming(self.local_queue_name)
        self.message_subscribe(queue=self.server_queue_name,
                               destination=self.local_queue_name)
        self.local_queue.start()
        self.local_queue.listen(self.consume_amqp_message)

    def __init_consumers(self):
        """ Initialize all Moksha Consumer objects """
        log.info('Loading Consumers')
        if self._consumers == None:
            log.debug("Loading from entry-points.")
            self._consumers = []
            for consumer in pkg_resources.iter_entry_points('moksha.consumer'):
                try:
                    c = consumer.load()
                    self._consumers.append(c)
                except Exception as e:
                    log.warn("Failed to load %r consumer." % consumer.name)
                    log.warn(str(e))
        else:
            log.debug("Loading explicitly passed entry-points.")

        for c_class in self._consumers:
            log.info("%s consumer is watching the %r topic" % (
                     c_class.__name__, c_class.topic))
            self.topics[c_class.topic].append(c_class)

    def __run_consumers(self):
        """ Instantiate the consumers """
        self.consumers = []
        for topic in self.topics:
            for i, consumer in enumerate(self.topics[topic]):
                try:
                    c = consumer(self)
                    if not getattr(c, "_initialized", None):
                        log.warn((
                            "%r didn't initialize correctly.  " +
                            "Did you call super(..).__init__?") % consumer)

                    self.consumers.append(c)
                    self.topics[topic][i] = c.consume
                except Exception as e:
                    log.warn("Failed to init %r consumer." % consumer)
                    log.warn(str(e))

    def __init_producers(self):
        """ Initialize all producers (aka data streams) """
        log.info('Loading Producers')
        if self._producers == None:
            log.debug("Loading from entry-points.")
            self._producers = []
            for producer in sum([
                list(pkg_resources.iter_entry_points(epoint))
                for epoint in ('moksha.producer', 'moksha.stream')
            ], []):
                try:
                    p = producer.load()
                    self._producers.append(p)
                except Exception as e:
                    log.warn("Failed to load %r producer." % producer.name)
                    log.warn(str(e))
        else:
            log.debug("Loading explicitly passed entry-points.")

        self.producers = []
        for producer_class in self._producers:
            log.info('Initializing %s producer' % producer_class.__name__)
            try:
                producer_obj = producer_class(self)
                self.producers.append(producer_obj)
            except Exception as e:
                log.warn("Failed to init %r producer." % producer_class)
                log.warn(str(e))

    @trace
    def create_topic(self, topic):
        if AMQPHubExtension and self.amqp_broker:
            AMQPHubExtension.create_queue(topic)

        # @@ remove this when we keep track of this in a DB
        if topic not in self.topics:
            self.topics[topic] = []

    def stop(self):
        log.debug("Stopping the CentralMokshaHub")
        MokshaHub.close(self)
        if self.producers:
            for producer in self.producers:
                log.debug("Stopping producer %s" % producer)
                producer.stop()
        if self.consumers:
            for consumer in self.consumers:
                log.debug("Stopping consumer %s" % consumer)
                consumer.stop()


if __name__ == '__main__':
    from moksha.hub import main
    main()
