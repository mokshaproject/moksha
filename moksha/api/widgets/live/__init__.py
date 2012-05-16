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

from live import (
    LiveWidget, LiveWidgetMeta,
    subscribe_topics, unsubscribe_topics
)
from moksha.api.widgets.stomp import StompWidget
from moksha.api.widgets.amqp import AMQPSocket
from moksha.api.widgets.websocket import WebSocketWidget


def get_moksha_socket(config):
    livesocket_backend = \
            config.get('moksha.livesocket.backend', 'stomp').lower()
    if livesocket_backend == 'stomp':
        keys = [
            'orbited_host',
            'orbited_port',
            'orbited_scheme',
            'stomp_broker',
            'stomp_port',
            'stomp_user',
            'stomp_pass',
        ]
        kwargs = dict([(key, config.get(key, None)) for key in keys])
        moksha_socket = StompWidget(**kwargs)
    elif livesocket_backend == 'amqp':
        keys = [
            'orbited_host',
            'orbited_port',
            'orbited_scheme',
            'amqp_broker_host',
            'amqp_broker_port',
            'amqp_broker_user',
            'amqp_broker_pass',
        ]
        kwargs = dict([(key, config.get(key, None)) for key in keys])
        moksha_socket = AMQPSocket(**kwargs)
    elif livesocket_backend == 'websocket':
        ws_host = config.get('moksha.livesocket.websocket.host', 'localhost')
        ws_port = config.get('moksha.livesocket.websocket.port', '9998')
        moksha_socket = WebSocketWidget(ws_host=ws_host, ws_port=ws_port)
    else:
        raise Exception(
            "Unknown `moksha.livesocket.backend` %r.  Available backends: "
            "stomp, amqp, websocket" % livesocket_backend)

    return moksha_socket
