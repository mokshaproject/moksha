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

from paste.deploy.converters import asbool

from live import (
    LiveWidget, LiveWidgetMeta,
    subscribe_topics, unsubscribe_topics
)

from moksha.wsgi.widgets.api.stomp import StompWidget
from moksha.wsgi.widgets.api.amqp import AMQPSocket
from moksha.wsgi.widgets.api.websocket import WebSocketWidget

def _make_kwargs(mappings, config):
    return dict([
        (
            d['left_key'],
            d.get('formatter', lambda o: o)(
                config.get(d['right_key'], d['default'])
            )
        ) for d in mappings
    ])

def get_moksha_socket(config):
    livesocket_backend = \
            config.get('moksha.livesocket.backend', 'stomp').lower()

    # This is a mapping of config mappings to widget attributes for the three types
    # of socket widgets: stomp, amqp, and websocket.
    global_mappings = [
        dict(
            left_key='notify',
            right_key='moksha.socket.notify',
            default=True,
            formatter=asbool,
        ),
        dict(
            left_key='reconnect_interval',
            right_key='moksha.socket.reconnect_interval',
            default=None,
        ),
    ]
    orbited_mappings = [
        dict(
            left_key='orbited_host',
            right_key='orbited_host',
            default='localhost',
        ),
        dict(
            left_key='orbited_port',
            right_key='orbited_port',
            default='9000',
        ),
        dict(
            left_key='orbited_scheme',
            right_key='orbited_scheme',
            default='http',
        ),
    ]
    if livesocket_backend == 'stomp':
        mappings = global_mappings + orbited_mappings + [
            dict(
                left_key='stomp_broker',
                right_key='stomp_broker',
                default='localhost',
            ),
            dict(
                left_key='stomp_port',
                right_key='stomp_port',
                default='61613',
            ),
            dict(
                left_key='stomp_user',
                right_key='stomp_user',
                default='guest',
            ),
            dict(
                left_key='stomp_pass',
                right_key='stomp_pass',
                default='guest',
            ),
        ]
        socket_class = StompWidget
    elif livesocket_backend == 'amqp':
        mappings = global_mappings + orbited_mappings + [
            dict(
                left_key='moksha_domain',
                right_key='moksha.domain',
                default='localhost',
            ),
            dict(
                left_key='amqp_broker_host',
                right_key='amqp_broker_host',
                default='localhost',
            ),
            dict(
                left_key='amqp_broker_port',
                right_key='amqp_broker_port',
                default='5672',
            ),
            dict(
                left_key='amqp_broker_user',
                right_key='amqp_broker_user',
                default='guest',
            ),
            dict(
                left_key='amqp_broker_pass',
                right_key='amqp_broker_pass',
                default='guest',
            ),
        ]
        socket_class = AMQPSocket
    elif livesocket_backend == 'websocket':
        mappings = global_mappings + [
            dict(
                left_key='ws_host',
                right_key='moksha.livesocket.websocket.host',
                default='localhost',
            ),
            dict(
                left_key='ws_port',
                right_key='moksha.livesocket.websocket.port',
                default='9998',
            ),
        ]
        socket_class = WebSocketWidget
    else:
        raise Exception(
            "Unknown `moksha.livesocket.backend` %r.  Available backends: "
            "stomp, amqp, websocket" % livesocket_backend)

    moksha_socket = socket_class(**_make_kwargs(mappings, config))

    return moksha_socket
