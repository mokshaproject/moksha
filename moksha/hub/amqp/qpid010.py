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

"""
Below is an attempt at building the Moksha hub with the python-qpid bindings.

There are two attempts, one using the AMQP 0.8 spec, and another using the 0.10.
Both of these implementations are incomplete, most-likely buggy, and not fully
integrated or tested with the MokshaHub.  They are here for reference, and to
potentially utilize further down the road when we move from amqplib to python-qpid.
"""

import qpid
import logging

from qpid.util import connect, URL, ssl
from qpid.queue import Empty
from qpid.datatypes import Message, RangedSet, uuid4
from qpid.connection import Connection

from moksha.lib.utils import trace
from moksha.hub.amqp.base import BaseAMQPHub

log = logging.getLogger(__name__)

class QpidAMQPHub(BaseAMQPHub):
    """
     Initialize the Moksha Hub.

    `broker`
        [amqps://][<user>[/<password>]@]<host>[:<port>]

    """

    @trace
    def __init__(self, broker):
        self.set_broker(broker)
        self.socket = connect(self.url, self.port)
        if self.url.scheme == URL.AMQPS:
            self.socket = ssl(self.socket)
        self.connection = Connection(sock=self.socket,
                                     username=self.user,
                                     password=self.password)
        self.connection.start()
        self.session = connection.session(str(uuid4()))

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

    @trace
    def send_message(self, topic, message, exchange='amq.topic', **headers):
        props = self.session.delivery_properties(**headers)
        msg = Message(props, message)
        self.session.message_transfer(destination=exchange, message=msg)

    @trace
    def subscribe_queue(server_queue_name, local_queue_name):
        queue = self.session.incoming(local_queue_name)
        self.session.message_subscribe(queue=server_queue_name,
                                       destination=local_queue_name)
        queue.start()
        return queue

# don't we want to call this from the Moksha Hub with the
# binding_key='*' ?

    @trace
    def queue_declare(self, queue, exchange, durable=True, exclusive=False,
                      auto_delete=False, **kw):
        self.sesison.queue_declare(queue=queue, excluse=exclusive, 
                                   auto_delete=auto_delete, **kw)

    @trace
    def exchange_bind(self, queue, exchange='amq.topic', binding_key=None):
        self.session.exchange_bind(exchange=exchange, queue=queue,
                                   binding_key=binding_key)

# this binding key should be the widgets topic?
# ie: fedora.#, fedora.packages.#.bugs

    @trace
    def message_subscribe(queue, destination):
        return self.session.message_subscribe(queue=queue,
                                              destination=destination)

    @trace
    def close(self):
        self.session.close(timeout=2)
        self.connection.close(timeout=2)
        self.socket.close()

    #@trace
    #def subscribe(self, queue, callback, no_ack=True):
    #    raise NotImplementedError


    #def wait(self):
    #    """ Block for new messages """
    #    raise NotImplementedError

    #@trace
    #def get(self, destination):
    #    return self.session.incoming(destination).get(timeout=self.timeout)

    #@trace
    #def delete_queue(self, queue):
    #    self.session.queue_delete(queue=queue)

    #@trace
    #def query(self, queue):
    #    return self.session.queue_query(queue=queue)



