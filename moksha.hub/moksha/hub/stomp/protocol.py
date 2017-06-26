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

    def subscribe(self, dest, **headers):
        f = stomper.Frame()
        # https://stomp.github.io/stomp-specification-1.2.html#SUBSCRIBE_ack_Header
        ack = self.client.hub.config.get('stomp_ack_mode', 'auto')
        if stomper.STOMP_VERSION != '1.0':
            f.unpack(stomper.subscribe(dest, dest, ack=ack))
        else:
            f.unpack(stomper.subscribe(dest, ack=ack))
        f.headers.update(headers)
        cmd = f.pack()
        log.debug(cmd)
        self.transport.write(cmd)

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
        log.debug(cmd)
        self.transport.write(cmd)


    def ack(self, msg):
        """ Override stomper's own ack to be smarter, based on mode. """
        # stomper does the incorrect thing when the ack mode is auto.  It acks
        # every message, regardless of the mode.  However, if the mode is
        # 'auto', then we should *not* send acks.  Here, make sure we don't
        # send an ack in that mode.
        if self.client.hub.config.get('stomp_ack_mode', 'auto') == 'auto':
            return stomper.NO_REPONSE_NEEDED

        # Otherwise, do what stomper do if the mode is *not* auto.
        return super(StompProtocol, self).ack(msg)

    def dataReceived(self, data):
        """Data received, react to it and respond if needed """
        self.buffer.appendData(data)
        while True:
           msg = self.buffer.getOneMessage()
           if msg is None:
               break

           handled = self.client.hub.consume_stomp_message(msg)

           # See if stomper thinks we need to send anything back.
           response = self.react(msg)

           # If this kind of message doesn't need any response, then quit.
           if not response:
               log.debug("StompProtocol sending no response to broker.")
               return

           # Otherwise, see if we need to turn a naive 'ack' from stomper into
           # a 'nack' if our consumers failed to do their jobs.
           if handled is False and response.startswith("ACK\n"):
               if stomper.STOMP_VERSION != '1.1':
                   log.error("Unable to NACK stomp %r" % stomper.STOMP_VERSION)
                   # Also, not sending an erroneous ack.
                   return

               message_id = msg['headers']['message-id']
               subscription = msg['headers']['subscription']
               transaction_id = msg['headers'].get('transaction-id')
               response = stomper.stomp_11.nack(message_id, subscription, transaction_id)

           # Finally, send our response (ACK or NACK) back to the broker.
           log.debug(response)
           self.transport.write(response)
