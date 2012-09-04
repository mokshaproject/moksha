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

import stomper
import logging

from twisted.internet.protocol import ReconnectingClientFactory

from moksha.hub.stomp.protocol import StompProtocol
from moksha.hub.messaging import MessagingHubExtension

log = logging.getLogger('moksha.hub')


class StompHubExtension(MessagingHubExtension, ReconnectingClientFactory):
    username = None
    password = None
    proto = None
    frames = None

    def __init__(self, hub, config):
        from moksha.hub.reactor import reactor

        self.config = config
        self.hub = hub
        self._topics = hub.topics.keys()
        self._frames = []

        port = self.config.get('stomp_port', 61613)
        host = self.config.get('stomp_broker')

        self.username = self.config.get('stomp_user', 'guest')
        self.password = self.config.get('stomp_pass', 'guest')

        reactor.connectTCP(host, int(port), self)

        super(StompHubExtension, self).__init__()

    def buildProtocol(self, addr):
        self.proto = StompProtocol(self, self.username, self.password)
        return self.proto

    def connected(self):
        for topic in self._topics:
            log.debug('Subscribing to %s topic' % topic)
            self.subscribe(topic, callback=lambda msg: None)
        self._topics = []
        for frame in self._frames:
            log.debug('Flushing queued frame')
            self.proto.transport.write(frame.pack())
        self._frames = []

    def clientConnectionLost(self, connector, reason):
        log.info('Lost connection.  Reason: %s' % reason)

    def clientConnectionFailed(self, connector, reason):
        log.error('Connection failed. Reason: %s' % reason)
        ReconnectingClientFactory.clientConnectionFailed(self,
                                                         connector,
                                                         reason)

    def send_message(self, topic, message, **headers):
        f = stomper.Frame()
        f.unpack(stomper.send(topic, message))
        if not self.proto:
            log.debug("Queueing stomp frame for later delivery")
            self._frames.append(f)
        else:
            self.proto.transport.write(f.pack())

        super(StompHubExtension, self).send_message(topic, message, **headers)

    def subscribe(self, topic, callback):
        # FIXME -- note, the callback is just thrown away here.
        log.warn("STOMP callback thrown away.")
        if not self.proto:
            if topic not in self._topics:
                self._topics.append(topic)
        else:
            self.proto.subscribe(topic)

        super(StompHubExtension, self).subscribe(topic, callback)
