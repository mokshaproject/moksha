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

import pylons

from live import (
    TW2LiveWidget, TW2LiveWidgetMeta,
    TW1LiveWidget,
    LiveWidget,
    subscribe_topics, unsubscribe_topics
)
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
