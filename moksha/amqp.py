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

import logging
log = logging.getLogger(__name__)

from moksha.lib.utils import trace

class AMQPHub(object):
    """
    A skeleton class for what we expect from an AMQP implementation.
    This allows us to bounce between different AMQP modules without too much
    pain and suffering.
    """
    conn = None

    def __init__(self, broker):
        """ Initialize a connection to a specified broker.

        This method must set self.channel to an active channel.
        """
        raise NotImplementedError

    def create_queue(self, queue, exchange, durable, exclusive, auto_delete):
        raise NotImplementedError

    def send_message(self, message, exchange, routing_key, **kw):
        raise NotImplementedError

    def consume(self, queue, callback, no_ack):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError


import amqplib.client_0_8 as amqp

NONPERSISTENT_DELIVERY = 1
PERSISTENT_DELIVERY = 2

class AMQPLibHub(AMQPHub):
    """ An AMQPHub implemention using the amqplib module """

    def __init__(self, broker, username=None, password=None, ssl=False):
        self.conn = amqp.Connection(host=broker, ssl=ssl,
                                    userid=username, password=password)
        self.channel = self.conn.channel()
        self.channel.access_request('/data', active=True, write=True, read=True)

    @trace
    def create_queue(self, queue, exchange='amq.fanout', durable=True,
                     exclusive=False, auto_delete=False):
        """ Declare a `queue` and bind it to an `exchange` """
        if not queue in self.queues:
            log.info("Creating %s queue" % queue)
            self.channel.queue_declare(queue,
                                       durable=durable,
                                       exclusive=exclusive,
                                       auto_delete=auto_delete)

    @trace
    def exchange_declare(exchange, type='fanout', durable=True,
                         auto_delete=False):
        self.channel.exchange_declare(exchange=exchange, type=type,
                                      durable=durable, auto_delete=auto_delete)

    @trace
    def queue_bind(self, queue, exchange, routing_key=''):
        self.channel.queue_bind(queue, exchange, routing_key=routing_key)

    # Since queue_name == routing_key, should we just make this method
    # def send_message(self, queue, message) ?
    def send_message(self, message, exchange='amq.fanout', routing_key='', 
                     delivery_mode=PERSISTENT_DELIVERY, **kw):
        """
        Send an AMQP message to a given exchange with the specified routing key 
        """
        msg = amqp.Message(message, **kw)
        msg.properties["delivery_mode"] = delivery_mode
        self.channel.basic_publish(msg, exchange, routing_key=routing_key)

    @trace
    def get_message(self, queue):
        """ Immediately grab a message from the queue.

        This call will not block, and will return None if there are no new
        messages in the queue.
        """
        msg = self.channel.basic_get(queue, no_ack=True)
        return msg

    @trace
    def consume(self, queue, callback, no_ack=True):
        """
        Consume messages from a given `queue`, passing each to `callback` 
        """
        self.channel.basic_consume(queue, callback=callback, no_ack=no_ack)

    @trace
    def close(self):
        try:
            if self.channel:
                self.channel.close()
        except Exception, e:
            log.exception(e)
        try:
            if self.conn:
                self.conn.close()
        except Exception, e:
            log.exception(e)


"""
Below is an attempt at building the Moksha hub with the python-qpid bindings.

There are two attempts, one using the AMQP 0.8 spec, and another using the 0.10.
Both of these implementations are incomplete, most-likely buggy, and not fully
integrated or tested with the MokshaHub.  They are here for reference, and to
potentially utilize further down the road when we move from amqplib to python-qpid.
"""

try:
    import qpid
    from qpid.util import connect, URL, ssl
    from qpid.client import Client
    from qpid.datatypes import Message
    from qpid.connection import Connection
    from qpid.connection08 import Connection
    from qpid.content import Content
except ImportError:
    pass

class QpidAMQP08Hub(AMQPHub):

    client = None

    def __init__(self, broker, username=None, password=None, ssl=False):
        """ Initialize the Moksha Hub.

        `broker`
            [amqps://][<user>[/<password>]@]<host>[:<port>]

        """
        self.set_broker(broker)
        self.init_qpid_connection()

        # We need 0.8 for RabbitMQ
        self.amqp_spec=qpid.spec08.load('/usr/share/amqp/amqp.0-8.xml')

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
        self.client = Client(self.host, self.port, spec=self.amqp_spec)
        self.client.start({'LOGIN': self.user, 'PASSWORD': self.password})
        self.conn = self.client.channel(1)
        self.conn.channel_open()
        print "opened channel!"

    def create_queue(self, queue, routing_key, exchange='amq.topic',
                     auto_delete=False, durable=True, **kw):
        self.conn.queue_declare(queue=queue, auto_delete=auto_delete,
                                durable=durable, **kw)
        self.conn.queue_bind(queue=queue, exchange=exchange,
                             routing_key=routing_key)
        print "Created %s queue" % queue


    def send_message(self, message, exchange='amq.topic', routing_key=''):
        self.conn.basic_publish(routing_key=routing_key,
                                content=Content(message),
                                exchange=exchange)

    def get(self, queue):
        t = self.conn.basic_consume(queue=queue, no_ack=True)
        print "t.consumer_tag =", t.consumer_tag
        q = self.client.queue(t.consumer_tag)
        msg = q.get()
        print "got message: ", msg
        return msg.content.body
        q.close()

    def close(self):
        if self.conn:
            print "Closing connection"
            self.conn.close()

class QpidAMQP010Hub(AMQPHub):

    def __init__(self, broker, username=None, password=None, ssl=False):
        """ Initialize the Moksha Hub.

        `broker`
            [amqps://][<user>[/<password>]@]<host>[:<port>]

        """
        self.set_broker(broker)
        self.amqp_spec = qpid.spec.load(qpid.spec.default())
        self.init_qpid_connection()
        self.init_qpid_session()
        self.init_qmf()

    def init_qpid_connection(self):
        sock = connect(self.host, self.port)
        if self.url.scheme == URL.AMQPS:
            sock = ssl(sock)
        self.conn = Connection(sock, self.amqp_spec, username=self.user,
                               password=self.password)
        self.conn.start(timeout=self.timeout)

    def init_qpid_session(self, session_name):
        self.session = self.conn.session(session_name, timeout=self.timeout)

    def init_qmf(self):
        try:
            import qmf.console
            self.qmf = qmf.console.Session()
            self.qmf_broker = self.qmf.addBroker(str(self.url))
        except ImportError:
            log.warning('qmf.console not available')
            self.qmf = None

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

    def delete_queue(self, queue):
        self.session.queue_delete(queue=queue)

    def send_message(self, destination, message, routing_key='key',
                     delivery_mode=2):
        dp = self.session.delivery_properties(routing_key=routing_key,
                                              delivery_mode=delivery_mode)
        self.session.message_transfer(message=Message(dp, message))

    def query(self, queue):
        return self.session.queue_query(queue=queue)

    def close(self):
        if not self.session.error():
            self.session.close(timeout=self.timeout)
        self.conn.close()
        if self.qmf:
            self.qmf.delBroker(self.qmf_broker)
