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

import stomper
import logging

from twisted.internet.protocol import Protocol

log = logging.getLogger(__name__)

class StompProtocol(Protocol, stomper.Engine):

    def __init__(self, client, username='', password=''):
        stomper.Engine.__init__(self)
        self.username = username
        self.password = password
        self.counter = 1
        self.client = client
        self.topics = client._topics or []

    def connected(self, msg):
        """Once connected, subscribe to message queues """
        stomper.Engine.connected(self, msg)
        log.info("StompProtocol Connected: session %s." % 
                 msg['headers']['session'])
        for topic in self.topics:
            log.debug('Subscribing to %s topic' % topic)
            self.subscribe(topic)

        #f = stomper.Frame()
        #f.unpack(stomper.subscribe(topic))
        #print f
        #return f.pack()

    def ack(self, msg):
        """Processes the received message. I don't need to 
        generate an ack message.
        """
        #stomper.Engine.ack(self, msg)
        #log.info("SENDER - received: %s " % msg['body'])
        return stomper.NO_REPONSE_NEEDED

    def subscribe(self, dest, **headers):
        f = stomper.Frame()
        f.unpack(stomper.subscribe(dest))
        f.headers.update(headers)
        self.transport.write(f.pack())

    def connectionMade(self):
        """ Register with stomp server """
        cmd = stomper.connect(self.username, self.password)
        self.transport.write(cmd)

    def dataReceived(self, data):
        """Data received, react to it and respond if needed """
        msg = stomper.unpack_frame(data)
        returned = self.react(msg)
        if returned:
            self.transport.write(returned)
        self.client.consume_stomp_message(msg)
