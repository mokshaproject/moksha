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

import moksha

class BaseAMQPHub(moksha.hub.MessagingHub):
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
