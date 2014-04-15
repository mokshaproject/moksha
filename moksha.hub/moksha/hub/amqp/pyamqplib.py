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
from moksha.common.lib.converters import asbool


from moksha.hub.amqp.base import BaseAMQPHubExtension

log = logging.getLogger(__name__)

NONPERSISTENT_DELIVERY = PERSISTENT_DELIVERY = range(1, 3)


class AMQPLibHubExtension(BaseAMQPHubExtension):
    """ An AMQPHub implemention using the amqplib module """

    def __init__(self, hub, config):
        import amqplib.client_0_8 as amqp

        self.config = config

        broker = self.config.get('amqp_broker')
        ssl = asbool(self.config.get('amqp_broker_ssl', False))
        use_threading = asbool(self.config.get('amqp_broker_threaded', False))
        username = self.config.get('amqp_broker_username', 'guest')
        password = self.config.get('amqp_broker_password', 'guest')

        self.conn = amqp.Connection(
            host=broker,
            ssl=ssl,
            use_threading=use_threading,
            userid=username,
            password=password
        )
        self.channel = self.conn.channel()
        self.channel.access_request(
            '/data', active=True, write=True, read=True)
        super(AMQPLibHubExtension, self).__init__()

    def create_queue(self, queue, exchange='amq.fanout', durable=True,
                     exclusive=False, auto_delete=False):
        """ Declare a `queue` and bind it to an `exchange` """
        if not queue in self.queues:
            log.info("Creating %s queue" % queue)
            self.channel.queue_declare(queue,
                                       durable=durable,
                                       exclusive=exclusive,
                                       auto_delete=auto_delete)

    def exchange_declare(self, exchange, type='fanout', durable=True,
                         auto_delete=False):
        self.channel.exchange_declare(exchange=exchange, type=type,
                                      durable=durable, auto_delete=auto_delete)

    def queue_bind(self, queue, exchange, routing_key=''):
        self.channel.queue_bind(queue, exchange, routing_key=routing_key)

    def send_message(self, topic, message, **headers):
        """
        Send an AMQP message to a given exchange with the specified routing key
        """
        import amqplib.client_0_8 as amqp

        msg = amqp.Message(message, **headers)
        msg.properties["delivery_mode"] = headers.get(
            "delivery_mode", PERSISTENT_DELIVERY)
        self.channel.basic_publish(
            msg,
            headers.get('exchange', 'amq.topic'),
            routing_key=topic
        )
        super(AMQPLibHubExtension, self).send_message(
            topic, message, **headers)

    def subscribe(self, topic, callback):
        queue_name = str(uuid.uuid4())
        self.queue_declare(queue=queue_name, exclusive=True,
                           auto_delete=True)
        self.exchange_bind(queue_name, binding_key=topic)
        self.queue_subscribe(queue_name, callback)
        super(AMQPLibHubExtension, self).subscribe(topic, callback)

    def get_message(self, queue):
        """ Immediately grab a message from the queue.

        This call will not block, and will return None if there are no new
        messages in the queue.
        """
        msg = self.channel.basic_get(queue, no_ack=True)
        return msg

    def queue_subscribe(self, queue, callback, no_ack=True):
        """
        Consume messages from a given `queue`, passing each to `callback`
        """
        self.channel.basic_consume(queue, callback=callback, no_ack=no_ack)

    def wait(self):
        self.channel.wait()

    def close(self):
        try:
            if hasattr(self, 'channel') and self.channel:
                self.channel.close()
        except Exception as e:
            log.exception(e)
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
        except Exception as e:
            log.exception(e)
