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
"""
:mod:`moksha.wsgi.widgets.api.websocket` - An "WebSocket" Live Moksha socket
==================================================================

.. moduleauthor:: Ralph Bean <rbean@redhat.com>
"""

from kitchen.text.converters import to_unicode as unicode
import warnings

import tw2.core as twc

from moksha.common.lib.helpers import listify
from moksha.wsgi.widgets.api.socket import AbstractMokshaSocket

def websocket_subscribe(topic):
    """ Return a javascript callback that subscribes to a given topic,
        or a list of topics.
    """
    sub = "moksha.topic_subscribe('%(topic)s');"
    return ''.join([sub % {'topic': t} for t in listify(topic)])


def websocket_unsubscribe(topic):
    """ Return a javascript callback that unsubscribes to a given topic,
        or a list of topics.
    """
    return ""
    # TODO:
    #sub = "stomp.unsubscribe('%s');"
    #if isinstance(topic, list):
    #    sub = ''.join([sub % t for t in topic])
    #else:
    #    sub = sub % topic
    #return sub


class WebSocketWidget(AbstractMokshaSocket):
    __shorthand__ = 'WebSocket'

    ws_host = twc.Param(default=twc.Required)
    ws_port = twc.Param(default=twc.Required)

    template = "mako:moksha.wsgi.widgets.api.websocket.templates.websocket"
