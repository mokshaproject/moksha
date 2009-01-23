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
#
# Based on code from stomper's examples
# (c) Oisin Mulvihill, 2007-07-26.
# License: http://www.apache.org/licenses/LICENSE-2.0

import moksha
import stomper
import logging

from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory

from moksha.lib.utils import trace
from moksha.hub.stomp.protocol import StompProtocol

log = logging.getLogger(__name__)

class StompHub(moksha.hub.MessagingHub, ReconnectingClientFactory):
    username = None
    password = None
    proto = None

    def __init__(self, host='localhost', port=61613, username='guest', 
                 password='guest', ssl=False, topics=None):
        self.username = username
        self.password = password
        self.ssl = ssl
        self._topics = topics or []
        reactor.connectTCP(host, port, self)

    def buildProtocol(self, addr):
        self.proto = StompProtocol(self, self.username, self.password)
        return self.proto

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
        ReconnectingClientFactory.clientConnectionFailed(self,
                                                         connector,
                                                         reason)

    def send_message(self, topic, message):
        f = stomper.Frame()
        f.unpack(stomper.send(topic, message))
        self.proto.transport.write(f.pack())

    @trace
    def subscribe(self, topic):
        if not self.proto:
            self._topics.append(topic)
        else:
            self.proto.subscribe(topic)
