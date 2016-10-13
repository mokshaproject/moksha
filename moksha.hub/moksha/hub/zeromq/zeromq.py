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
# Authors: Ralph Bean <rbean@redhat.com>


import logging
import six
import socket
import time
import txzmq
import zmq

from kitchen.text.converters import to_bytes

from moksha.common.lib.converters import asbool
from moksha.hub.zeromq.base import BaseZMQHubExtension

log = logging.getLogger('moksha.hub')


# TODO -- is there a better thing to use in this thing's place?  A dict-like
# object that also supports __getattr__ access would be ideal.
class ZMQMessage(object):
    def __init__(self, topic, body):
        self.topic = topic
        self.body = body

    def __json__(self):
        return {'topic': self.topic, 'body': self.body}

    def __repr__(self):
        return "<ZMQMessage; topic: %r, body: %r>" % (self.topic, self.body)


def hostname2ipaddr(endpoint):
    """ Utility function to convert "tcp://hostname:port" to "tcp://ip:port"

    Why?  -- http://bit.ly/Jwdf6v
    """

    hostname = endpoint[endpoint.rfind('/') + 1:endpoint.rfind(':')]
    ip_addrs = socket.gethostbyname_ex(hostname)[2]
    log.info("Resolving %s to %r" % (hostname, ip_addrs))
    for addr in ip_addrs:
        yield endpoint.replace(hostname, addr)


def splat2ipaddr(endpoint):
    return [endpoint.replace("*", "127.0.0.1")]


class ZMQHubExtension(BaseZMQHubExtension):

    def __init__(self, hub, config):
        self.config = config
        self.validate_config(self.config)
        self.strict = asbool(self.config.get('zmq_strict', False))
        self.subscriber_factories = {}

        self.context = zmq.Context(1)

        # Configure txZMQ to use our highwatermark and keepalive if we have 'em
        self.connection_cls = txzmq.ZmqSubConnection
        self.connection_cls.highWaterMark = \
            config.get('high_water_mark', 0)
        self.connection_cls.tcpKeepalive = \
            config.get('zmq_tcp_keepalive', 0)
        self.connection_cls.tcpKeepaliveCount = \
            config.get('zmq_tcp_keepalive_cnt', 0)
        self.connection_cls.tcpKeepaliveIdle = \
            config.get('zmq_tcp_keepalive_idle', 0)
        self.connection_cls.tcpKeepaliveInterval = \
            config.get('zmq_tcp_keepalive_intvl', 0)
        self.connection_cls.reconnectInterval = \
            config.get('zmq_reconnect_ivl', 100)
        self.connection_cls.reconnectIntervalMax = \
            config.get('zmq_reconnect_ivl_max', 100)

        # Set up the publishing socket
        self.pub_socket = self.context.socket(zmq.PUB)
        _endpoints = self.config.get('zmq_publish_endpoints', '').split(',')
        for endpoint in (e for e in _endpoints if e):
            log.info("Binding publish socket to '%s'" % endpoint)
            try:
                self.pub_socket.bind(endpoint)
            except zmq.ZMQError:
                map(self.pub_socket.bind, hostname2ipaddr(endpoint))

        # Factory used to lazily produce subsequent subscribers
        self.twisted_zmq_factory = txzmq.ZmqFactory()

        # Establish a list of subscription endpoints for later use
        _endpoints = self.config['zmq_subscribe_endpoints'].split(',')
        method = self.config.get('zmq_subscribe_method', 'connect')

        if method == 'bind':
            _endpoints = sum(map(list, map(hostname2ipaddr, _endpoints)), [])
        else:
            # Required for zeromq-3.x.
            _endpoints = sum(map(list, map(splat2ipaddr, _endpoints)), [])

        self.sub_endpoints = [
            txzmq.ZmqEndpoint(method, ep) for ep in _endpoints
        ]

        # This is required so that the publishing socket can fully set itself
        # up before we start trying to send messages on it.  This is a
        # documented zmq issue that they do not plan to fix.
        time.sleep(1)

        super(ZMQHubExtension, self).__init__()

    def validate_config(self, config):
        if not asbool(config.get('zmq_enabled', False)):
            raise ValueError("zmq_enabled not set to True")

        required_attrs = ['zmq_publish_endpoints', 'zmq_subscribe_endpoints']
        for attr in required_attrs:
            if not config.get(attr, None):
                log.warn("No '%s' set.  Are you sure?" % attr)
                continue

            endpoints = config[attr].split(',')
            for endpoint in endpoints:
                if 'localhost' in endpoint:
                    # This is why http://bit.ly/Jwdf6v
                    raise ValueError("'localhost' in %s is disallowed" % attr)

    def send_message(self, topic, message, **headers):
        if isinstance(topic, six.text_type):
            topic = topic.encode('utf-8')
        if isinstance(message, six.text_type):
            message = message.encode('utf-8')
        try:
            self.pub_socket.send_multipart([topic, message])
        except zmq.ZMQError as e:
            log.warn("Couldn't send message: %r" % e)

        super(ZMQHubExtension, self).send_message(topic, message, **headers)

    def unsubscribe(self, callback):
        for endpoint, factory in self.subscriber_factories.items():
            kill_list = []
            for intercept_func in factory._moksha_callbacks:
                if intercept_func.handled_callback == callback:
                    kill_list.append(intercept_func)
            for intercept_func in kill_list:
                factory._moksha_callbacks.remove(intercept_func)

    def subscribe(self, topic, callback):
        original_topic = topic

        # Mangle topic for zmq equivalence with AMQP
        topic = topic.replace('*', '')

        for endpoint in self.sub_endpoints:
            log.debug("Subscribing to %s on '%r'" % (topic, endpoint))
            if endpoint in self.subscriber_factories:
                log.debug("Using cached txzmq factory.")
                s = self.subscriber_factories[endpoint]
            else:
                log.debug("Creating new txzmq factory.")
                try:
                    s = self.subscriber_factories[endpoint] = \
                        self.connection_cls(
                            self.twisted_zmq_factory, endpoint)
                except zmq.ZMQError as e:
                    log.warn("Failed txzmq create on %r %r" % (endpoint, e))
                    continue

                def chain_over_moksha_callbacks(*parts):
                    if len(parts) != 2:
                        raise ValueError(
                            "Moksha can only handle multipart messages with a "
                            "topic followed by a body.  Got %r" % parts)

                    _body, _topic = parts

                    if isinstance(_topic, six.binary_type):
                        _topic = _topic.decode('utf-8')
                    if isinstance(_body, six.binary_type):
                        _body = _body.decode('utf-8')
                    for f in s._moksha_callbacks:
                        f(_body, _topic)

                s._moksha_callbacks = []
                s.gotMessage = chain_over_moksha_callbacks

            def intercept(_body, _topic):
                """ The purpose of this intercept callback is twofold:

                 - Callbacks from txzmq are called with two arguments, body and
                   topic but moksha is expecting an object which has a 'body'
                   attribute.  We create that object and pass it on here.
                 - 0mq topic-matching works differently than AMQP and STOMP.
                   By default, subscribing to 'abc' will get you messages
                   tagged 'abc' but also messages sent on the topic 'abcfoo'
                   and 'abcbar'.  Moksha introduces a custom parameter
                   'strict' (zmq_strict in the config file) that disallows
                   this behavior.
                """

                if self.strict and _topic != topic:
                    return None
                elif not self.strict and not _topic.startswith(topic):
                    # This second clause is a symptom that I'm doing something
                    # wrong.  The filtering should all be handled inside txZMQ
                    # by setsockopt.
                    return None

                return callback(ZMQMessage(_topic, _body))

            intercept.handled_callback = callback  # bookkeeping
            s._moksha_callbacks.append(intercept)
            s.subscribe(to_bytes(topic, encoding='utf8'))

        super(ZMQHubExtension, self).subscribe(original_topic, callback)

    def close(self):
        self.pub_socket.close()
        self.context.term()
