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

import amqplib.client_0_8 as amqp

from moksha.lib.utils import trace
from moksha.hub.amqp.base import BaseAMQPHub

log = logging.getLogger(__name__)

NONPERSISTENT_DELIVERY = PERSISTENT_DELIVERY = range(1, 3)

class AMQPLibHub(BaseAMQPHub):
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
    def exchange_declare(self, exchange, type='fanout', durable=True,
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
    def subscribe(self, queue, callback, no_ack=True):
        """
        Consume messages from a given `queue`, passing each to `callback` 
        """
        self.channel.basic_consume(queue, callback=callback, no_ack=no_ack)


    def wait(self):
        self.channel.wait()

    @trace
    def close(self):
        try:
            if hasattr(self, 'channel') and self.channel:
                self.channel.close()
        except Exception, e:
            log.exception(e)
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
        except Exception, e:
            log.exception(e)
