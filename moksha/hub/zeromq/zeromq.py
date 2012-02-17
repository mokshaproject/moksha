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

from paste.deploy.converters import asbool

import logging
import time
import txZMQ
import zmq

from moksha.hub.zeromq.base import BaseZMQHub

log = logging.getLogger('moksha.hub')


class ZMQMessage(object):
    def __init__(self, topic, body):
        self.topic = topic
        self.body = body


class ZMQHub(BaseZMQHub):

    def __init__(self):
        self.validate_config(self.config)

        self.context = zmq.Context(1)

        # Set up the publishing socket
        self.pub_socket = self.context.socket(zmq.PUB)
        _endpoints = self.config['zmq_publish_endpoints'].split(',')
        for endpoint in _endpoints:
            log.info("Binding publish socket to '%s'" % endpoint)
            self.pub_socket.bind(endpoint)

        # Factory used to lazily produce subsequent subscribers
        self.twisted_zmq_factory = txZMQ.ZmqFactory()

        # Establish a list of subscription endpoints for later use
        _endpoints = self.config['zmq_subscribe_endpoints'].split(',')
        self.sub_endpoints = [
            txZMQ.ZmqEndpoint("connect", ep) for ep in _endpoints
        ]

        # This is required so that the publishing socket can fully set itself up
        # before we start trying to send messages on it.  This is a documented
        # zmq issue that they do not plan to fix.
        time.sleep(1)

        super(ZMQHub, self).__init__()

    def validate_config(self, config):
        if not asbool(config.get('zmq_enabled', False)):
            raise ValueError("zmq_enabled not set to True")

        required_attrs = ['zmq_publish_endpoints', 'zmq_subscribe_endpoints']
        for attr in required_attrs:
            if not config.get(attr, None):
                raise ValueError("no '%s' set.  %s is required." % (attr,)*2)
            endpoints = config[attr].split(',')
            for endpoint in endpoints:
                if 'localhost' in endpoint:
                    # See the following for why.
                    # http://stackoverflow.com/questions/6024003/why-doesnt-zeromq-work-on-localhost
                    raise ValueError("'localhost' in %s is disallowed" % attr)

    def send_message(self, topic, message, **headers):
        self.pub_socket.send_multipart([topic, message])
        super(ZMQHub, self).send_message(topic, message, **headers)

    def subscribe(self, topic, callback):
        for endpoint in self.sub_endpoints:
            log.info("Subscribing to %s on '%r'" % (topic, endpoint))
            s = txZMQ.ZmqSubConnection(self.twisted_zmq_factory, endpoint)

            def intercept(body, topic):
                return callback(ZMQMessage(topic, body))

            s.gotMessage = intercept
            s.subscribe(topic)
        super(ZMQHub, self).subscribe(topic, callback)

    def close(self):
        self.pub_socket.close()
        self.context.term()
