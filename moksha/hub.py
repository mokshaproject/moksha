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

import qpid
from qpid.util import connect, URL, ssl
from qpid.client import Client
from qpid.datatypes import Message
from qpid.connection import Connection

import logging
log = logging.getLogger(__name__)

class MokshaHub(object):

    queues = []
    exchanges = []
    client = None
    channel = None
    amqp_spec = qpid.spec.default()

    def __init__(self, broker='localhost', timeout=10):
        """ Initialize the Moksha Hub.

        `broker`
            [amqps://][<user>[/<password>]@]<host>[:<port>]

        """
        self.set_broker(broker)
        self.timeout = timeout
        self.amqp_spec = qpid.spec.load(self.amqp_spec)
        self.init_qpid_connection()
        self.init_qpid_session()
        self.init_qmf()

    def set_broker(self, broker):
        self.url = URL(broker)
        self.user = self.url.password or 'guest'
        self.password = self.url.password or 'guest'
        self.host = self.url.host
        if self.url.scheme == URL.AMQPS:
            self.ssl = True
            default_port = 5671
        else:
            self.ssl = False
            default_port = 5672
        self.port = self.url.port or default_port

    def init_qpid_connection(self):
        sock = connect(self.host, self.port)
        if self.url.scheme == URL.AMQPS:
            sock = ssl(sock)
        self.conn = Connection(sock, self.amqp_spec, username=self.user,
                               password=self.password)
        self.conn.start(timeout=self.timeout)

    def init_qpid_session(self, session_name='moksha'):
        self.session = self.conn.session(session_name, timeout=self.timeout)

    def init_qmf(self):
        try:
            import qmf.console
            self.qmf = qmf.console.Session()
            self.qmf_broker = self.qmf.addBroker(str(self.url))
        except ImportError:
            log.warning('qmf.console not available')
            self.qmf = None

    def close(self):
        if not self.session.error():
            self.session.close(timeout=self.timeout)
        self.conn.close(timeout=self.timeout)
        if self.qmf:
            self.qmf.delBroker(self.qmf_broker)

    def create_queue(self, queue, routing_key, exchange='amq.direct',
                     auto_delete=False, durable=False, **kw):
        self.session.queue_declare(queue=queue, auto_delete=auto_delete,
                                   durable=durable, **kw)

    def delete_queue(self, queue):
        self.session.queue_delete(queue=queue)

    def send_message(self, destination, message, routing_key='key',
                     delivery_mode=2):
        dp = self.session.delivery_properties(routing_key=routing_key,
                                              delivery_mode=delivery_mode)
        self.session.message_transfer(message=Message(dp, message))

    def subscribe(self, queue, destination, accept_mode=1, acquire_mode=0):
        """ Subscribe to a specific queue destination """
        self.session.message_subscribe(queue=queue, destination=destination,
                                       accept_mode=accept_mode,
                                       acquire_mode=acquire_mode)
        self.session.message_flow(destination=destination,
                                  unit=self.session.credit_unit.message,
                                  value=0xFFFFFFFF)
        self.session.message_flow(destination=destination,
                                  unit=self.session.credit_unit.byte,
                                  value=0xFFFFFFFF)

    def get(self, destination):
        return self.session.incoming(destination).get(timeout=self.timeout)

    def query(self, queue):
        return self.session.queue_query(queue=queue)

    # ability to get the latest messages from a given queue?

if __name__ == '__main__':
    sh = logging.StreamHandler()
    log.setLevel(logging.DEBUG)
    sh.setLevel(logging.DEBUG)
    log.addHandler(sh)

    print "Creating MokshaHub..."
    hub = MokshaHub()
    print "Creating queue..."
    hub.create_queue('wtf', 'key', 'amq.topic', durable=True)
    print "Sending message"
    hub.send_message('wtf', 'wtf', 'wtf')
    print "Subscribing to queue"
    hub.subscribe('wtf', 'wtf')
    print "Recieving message"
    msg = hub.get('wtf')
    print "msg = ", msg
    hub.close()
    print "Closed!"
