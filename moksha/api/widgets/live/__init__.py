# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
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

import pylons

from live import LiveWidget, subscribe_topics, unsubscribe_topics
from moksha.api.widgets.stomp import StompWidget
from moksha.api.widgets.amqp import AMQPSocket

livesocket_backend = pylons.config.get('moksha.livesocket.backend', 'stomp').lower()
if livesocket_backend == 'stomp':
    moksha_socket = StompWidget
elif livesocket_backend == 'amqp':
    moksha_socket = AMQPSocket
else:
    raise Exception("Unknown `moksha.livesocket.backend` %r.  Available backends: "
                    "stomp, amqp" % livesocket_backend)
del(livesocket_backend)
