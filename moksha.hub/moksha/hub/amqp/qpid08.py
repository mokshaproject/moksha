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

##
# Obsolete Qpid AMQP 0.8 implementation.
##

# AMQP 0.8 legacy modules
import qpid
from qpid.client import Client
from qpid.content import Content

class QpidAMQP08Hub(BaseAMQPHub):

    client = None

    def __init__(self, broker, username=None, password=None, ssl=False):
        """
        Initialize the Moksha Hub.

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
