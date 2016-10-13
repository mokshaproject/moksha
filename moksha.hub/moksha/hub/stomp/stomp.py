# This file is part of Moksha.
# Copyright (C) 2008-2014  Red Hat, Inc.
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
#          Ralph Bean <rbean@redhat.com>

try:
    # Try first to use modern stomp-1.1
    import stomper.stomp_11 as stomper
except ImportError:
    # Failing that, use whatever is available.
    try:
        import stomper
    except ImportError:
        pass

import logging

from twisted.internet.protocol import ClientFactory

from moksha.hub.stomp.protocol import StompProtocol
from moksha.hub.messaging import MessagingHubExtension
from moksha.hub.reactor import reactor

log = logging.getLogger('moksha.hub')


class StompHubExtension(MessagingHubExtension, ClientFactory):
    username = None
    password = None
    proto = None
    frames = None

    def __init__(self, hub, config):
        self.config = config
        self.hub = hub
        self._topics = hub.topics.keys()
        self._frames = []

        uri = self.config.get('stomp_uri', None)
        if not uri:
            port = int(self.config.get('stomp_port', 61613))
            host = self.config.get('stomp_broker')
            uri = "%s:%i" % (host, port)

        # Sometimes, a stomp consumer may wish to be subscribed to a queue
        # which is composed of messages from many different topics.  In this
        # case, the hub hands dispatching messages to the right consumers.
        # This extension is only concerned with the queue, and negotiating that
        # with the broker.
        stomp_queue = self.config.get('stomp_queue', None)
        if stomp_queue:
            # Overwrite the declarations of all of our consumers.
            self._topics = [stomp_queue]

        # A list of addresses over which we emulate failover()
        self.addresses = [pair.split(":") for pair in uri.split(',')]
        self.address_index = 0

        # An exponential delay used to back off if we keep failing.
        self._delay = float(self.config.get('stomp_delay', '0.1'))

        self.username = self.config.get('stomp_user', 'guest')
        self.password = self.config.get('stomp_pass', 'guest')

        self.key = self.config.get('stomp_ssl_key', None)
        self.crt = self.config.get('stomp_ssl_crt', None)

        self.client_heartbeat = int(self.config.get('stomp_heartbeat', 0))

        self.connect(self.addresses[self.address_index], self.key, self.crt)
        super(StompHubExtension, self).__init__()

    def connect(self, address, key=None, crt=None):
        host, port = address
        if key and crt:
            log.info("connecting encrypted to %r %r %r" % (
                host, int(port), self))

            from twisted.internet import ssl

            with open(key) as key_file:
                with open(crt) as cert_file:
                    client_cert = ssl.PrivateCertificate.loadPEM(
                        key_file.read() + cert_file.read())

            ssl_context = client_cert.options()
            reactor.connectSSL(host, int(port), self, ssl_context)
        else:
            log.info("connecting unencrypted to %r %r %r" % (
                host, int(port), self))
            reactor.connectTCP(host, int(port), self)

    def buildProtocol(self, addr):
        self._delay = float(self.config.get('stomp_delay', '0.1'))
        log.debug("build protocol was called with %r" % addr)
        self.proto = StompProtocol(self, self.username, self.password)
        return self.proto

    def connected(self, server_heartbeat):
        if server_heartbeat and self.client_heartbeat:
            interval = max(self.client_heartbeat, server_heartbeat)
            log.debug("Heartbeat of %ims negotiated from (%i,%i); starting." % (
                interval, self.client_heartbeat, server_heartbeat))
            self.start_heartbeat(interval)
        else:
            log.debug("Skipping heartbeat initialization")

        for topic in self._topics:
            log.info('Subscribing to %s topic' % topic)
            self.subscribe(topic, callback=lambda msg: None)

        for frame in self._frames:
            log.debug('Flushing queued frame')
            self.proto.transport.write(frame.pack())
        self._frames = []

    def clientConnectionLost(self, connector, reason):
        log.info('Lost connection.  Reason: %s' % reason)
        self.stop_heartbeat()
        self.failover()

    def clientConnectionFailed(self, connector, reason):
        log.error('Connection failed. Reason: %s' % reason)
        self.stop_heartbeat()
        self.failover()

    def failover(self):
        self.address_index = (self.address_index + 1) % len(self.addresses)
        args = (self.addresses[self.address_index], self.key, self.crt,)
        self._delay = self._delay * (1 + (2.0 / len(self.addresses)))
        log.info('(failover) reconnecting in %f seconds.' % self._delay)
        reactor.callLater(self._delay, self.connect, *args)

    def start_heartbeat(self, interval):
        self._heartbeat_enabled = True
        reactor.callLater(interval / 1000.0, self.heartbeat, interval)

    def heartbeat(self, interval):
        if self._heartbeat_enabled:
            self.proto.transport.write(chr(0x0A))  # Lub-dub
            reactor.callLater(interval / 1000.0, self.heartbeat, interval)
        else:
            log.debug("(heartbeat stopped)")

    def stop_heartbeat(self):
        log.debug("stopping heartbeat")
        self._heartbeat_enabled = False

    def send_message(self, topic, message, **headers):
        f = stomper.Frame()
        f.unpack(stomper.send(topic, message))
        if not self.proto:
            log.info("Queueing stomp frame for later delivery")
            self._frames.append(f)
        else:
            self.proto.transport.write(f.pack())

        super(StompHubExtension, self).send_message(topic, message, **headers)

    def subscribe(self, topic, callback):
        # FIXME -- note, the callback is just thrown away here.
        if not self.proto:
            log.info("queuing topic for later subscription %r." % topic)
            if topic not in self._topics:
                self._topics.append(topic)
        else:
            log.debug("sending subscription to the protocol")
            self.proto.subscribe(topic)

        super(StompHubExtension, self).subscribe(topic, callback)
