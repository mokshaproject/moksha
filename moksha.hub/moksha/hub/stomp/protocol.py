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
#
# Based on code from stomper's examples
# (c) Oisin Mulvihill, 2007-07-26.
# License: http://www.apache.org/licenses/LICENSE-2.0

import logging


try:
    # stomper is not ready for py3
    try:
        # Try first to use modern stomp-1.1
        import stomper.stomp_11 as stomper
    except ImportError:
        # Failing that, use whatever is available.
        try:
            import stomper
        except ImportError:
            pass
    from stomper.stompbuffer import StompBuffer
    from twisted.internet.protocol import Protocol
    class Base(Protocol, stomper.Engine):
        pass
except ImportError:
    Base = object

log = logging.getLogger(__name__)

class StompProtocol(Base):

    def __init__(self, client, username='', password=''):
        stomper.Engine.__init__(self)
        self.username = username
        self.password = password
        self.counter = 1
        self.client = client
        self.buffer = StompBuffer()

    def connected(self, msg):
        """Once connected, subscribe to message queues """
        stomper.Engine.connected(self, msg)
        log.info("StompProtocol Connected: session %s." %
                 msg['headers']['session'])

        # https://stomp.github.io/stomp-specification-1.1.html#Heart-beating
        server_heartbeat = msg['headers'].get('heart-beat', 0)
        if server_heartbeat:
            log.debug("(server wants heart-beat (%s))" % server_heartbeat)
            sx, sy = server_heartbeat.split(',')
            server_heartbeat = int(sy)

        self.client.connected(server_heartbeat)

        #f = stomper.Frame()
        #f.unpack(stomper.subscribe(topic))
        #print f
        #return f.pack()

    def ack(self, msg):
        """Processes the received message. I don't need to
        generate an ack message.
        """
        #stomper.Engine.ack(self, msg)
        #log.debug("SENDER - received: %s " % msg['body'])
        return stomper.NO_REPONSE_NEEDED

    def subscribe(self, dest, **headers):
        f = stomper.Frame()
        if stomper.STOMP_VERSION != '1.0':
            f.unpack(stomper.subscribe(dest, dest))
        else:
            f.unpack(stomper.subscribe(dest))
        f.headers.update(headers)
        self.transport.write(f.pack())

    def connectionMade(self):
        """ Register with stomp server """
        log.debug("Connecting with stomp-%s" % stomper.STOMP_VERSION)
        if stomper.STOMP_VERSION != '1.0':
            host, port = self.client.addresses[self.client.address_index]
            interval = (self.client.client_heartbeat, 0)
            log.debug("(proposing heartbeat of (%i,%i))" % interval)
            cmd = stomper.connect(self.username, self.password, host, interval)
        else:
            cmd = stomper.connect(self.username, self.password)
        self.transport.write(cmd)

    def dataReceived(self, data):
        """Data received, react to it and respond if needed """
        self.buffer.appendData(data)
        while True:
           msg = self.buffer.getOneMessage()
           if msg is None:
               break

           returned = self.react(msg)
           if returned:
               self.transport.write(returned)

           self.client.hub.consume_stomp_message(msg)
