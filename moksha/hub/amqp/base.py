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

from moksha.hub.messaging import MessagingHub

class BaseAMQPHub(MessagingHub):
    """
    A skeleton class for what we expect from an AMQP implementation.
    This allows us to bounce between different AMQP modules without too much
    pain and suffering.
    """
    conn = None

    def __init__(self, host, port, username, password):
        """ Initialize a connection to a specified broker.

        This method must set self.channel to an active channel.
        """
        raise NotImplementedError

    def send_message(self, topic, message, exchange=None,
                     routing_key=None, **headers):
        raise NotImplementedError

    def subscribe(self, queue, callback, no_ack=True):
        raise NotImplementedError

    def create_queue(self, queue, exchange, durable, exclusive, auto_delete):
        raise NotImplementedError

    def bind_queue(self, queue, exchange):
        raise NotImplementedError

    def wait(self):
        """ Block for new messages """
        raise NotImplementedError

    def close(self):
        raise NotImplementedError
