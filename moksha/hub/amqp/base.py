# This file is part of Moksha.
# Copyright (C) 2008-2009  Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
