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

import logging

from qpid.util import connect, URL, ssl
from qpid.datatypes import Message, uuid4, RangedSet
from qpid.connection import Connection
from qpid.session import SessionClosed

from moksha.hub.amqp.base import BaseAMQPHubExtension

log = logging.getLogger('moksha.hub')


class QpidAMQPHubExtension(BaseAMQPHubExtension):
    """
     Initialize the Moksha Hub.

    `broker`
        [amqps://][<user>[/<password>]@]<host>[:<port>]

    """

    def __init__(self, hub, config):
        self.config = config
        self.set_broker(self.config.get('amqp_broker'))
        self.socket = connect(self.host, self.port)
        if self.url.scheme == URL.AMQPS:
            self.socket = ssl(self.socket)
        self.connection = Connection(sock=self.socket,
                                     username=self.user,
                                     password=self.password)
        self.connection.start()
        log.info("Connected to AMQP Broker %s" % self.host)
        self.session = self.connection.session(str(uuid4()))
        self.local_queues = []
        super(QpidAMQPHubExtension, self).__init__()

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

    def send_message(self, topic, message, **headers):
        headers['routing_key'] = headers.get('routing_key', topic)
        props = self.session.delivery_properties(**headers)
        msg = Message(props, message)
        self.session.message_transfer(
            destination=headers.get('exchange', 'amq.topic'),
            message=msg)
        super(QpidAMQPHubExtension, self).send_message(
            topic, message, **headers)

    def subscribe_queue(self, server_queue_name, local_queue_name):
        queue = self.session.incoming(local_queue_name)
        self.session.message_subscribe(queue=server_queue_name,
                                       destination=local_queue_name)
        queue.start()
        return queue

    def queue_declare(self, queue, durable=True, exclusive=False,
                      auto_delete=False, **kw):
        self.session.queue_declare(queue=queue, exclusive=exclusive,
                                   auto_delete=auto_delete,
                                   arguments={'qpid.max_count': 0,
                                              'qpid.max_size': 0}, **kw)

    def exchange_bind(self, queue, exchange='amq.topic', binding_key=None):
        self.session.exchange_bind(exchange=exchange, queue=queue,
                                   binding_key=binding_key)

    def message_subscribe(self, queue, destination):
        return self.session.message_subscribe(queue=queue,
                                              destination=destination)

    def message_accept(self, message):
        try:
            self.session.message_accept(RangedSet(message.id))
        except SessionClosed:
            log.debug("Accepted message on closed session: %s" % message.id)
            pass

    def subscribe(self, topic, callback):
        queue_name = '_'.join([
            "moksha_consumer", self.session.name, str(uuid4()),
        ])
        server_queue_name = local_queue_name = queue_name

        self.queue_declare(queue=server_queue_name, exclusive=True,
                           auto_delete=True)
        self.exchange_bind(server_queue_name, binding_key=topic)

        self.local_queues.append(self.session.incoming(local_queue_name))

        self.message_subscribe(queue=server_queue_name,
                               destination=local_queue_name)

        self.local_queues[-1].start()
        self.local_queues[-1].listen(callback)

        super(QpidAMQPHubExtension, self).subscribe(topic, callback)

    def close(self):
        self.session.close(timeout=2)
        self.connection.close(timeout=2)
        self.socket.close()
