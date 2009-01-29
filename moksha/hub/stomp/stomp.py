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

import stomper
import logging

from twisted.internet.protocol import ReconnectingClientFactory

from moksha.hub.reactor import reactor
from moksha.hub.stomp.protocol import StompProtocol
from moksha.hub.messaging import MessagingHub

log = logging.getLogger('moksha.hub')

class StompHub(MessagingHub, ReconnectingClientFactory):
    username = None
    password = None
    proto = None
    frames = None

    def __init__(self, host, port, username, password, topics=None):
        self.username = username
        self.password = password
        self._topics = topics or []
        self._frames = []

        reactor.connectTCP(host, int(port), self)

    def buildProtocol(self, addr):
        self.proto = StompProtocol(self, self.username, self.password)
        return self.proto

    def connected(self):
        for topic in self._topics:
            log.debug('Subscribing to %s topic' % topic)
            self.subscribe(topic)
        self._topics = []
        for frame in self._frames:
            log.debug('Flushing queued frame')
            self.proto.transport.write(frame.pack())

    def clientConnectionLost(self, connector, reason):
        log.info('Lost connection.  Reason: %s' % reason)

    def clientConnectionFailed(self, connector, reason):
        log.error('Connection failed. Reason: %s' % reason)
        ReconnectingClientFactory.clientConnectionFailed(self,
                                                         connector,
                                                         reason)

    def send_message(self, topic, message):
        f = stomper.Frame()
        f.unpack(stomper.send(topic, message))
        if not self.proto:
            log.debug("Queueing stomp frame for later delivery")
            self._frames.append(f)
        else:
            self.proto.transport.write(f.pack())

    def subscribe(self, topic):
        if not self.proto:
            if topic not in self._topics:
                self._topics.append(topic)
        else:
            self.proto.subscribe(topic)
