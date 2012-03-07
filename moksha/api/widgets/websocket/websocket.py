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
:mod:`moksha.api.widgets.websocket` - An "WebSocket" Live Moksha socket
==================================================================

.. moduleauthor:: Ralph Bean <rbean@redhat.com>
"""

import moksha
import moksha.utils

from tg import config
from paste.deploy.converters import asbool
import warnings

import tw.api
import tw2.core as twc
from tw2.jqplugins.gritter import gritter_resources, gritter_callback

from moksha.lib.helpers import defaultdict, listify
from moksha.widgets.moksha_js import tw2_moksha_js

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


# TODO -- WebSocketWidget and StompSocket have a *lot* in common.
#         They should both inherit from an abstract CometSocket! -- threebean
class TW2WebSocketWidget(twc.Widget):
    resources = [tw2_moksha_js]
    topics = twc.Variable()
    notify = twc.Param(
        default=asbool(config.get('moksha.socket.notify', False)))
    hidden = twc.Param(default=True)

    ws_host = twc.Param(
        default=config.get('moksha.livesocket.websocket.host', 'localhost'))
    ws_port = twc.Param(
        default=config.get('moksha.livesocket.websocket.port', '9998'))
    ws_reconnect_interval = twc.Param(
        default=config.get('moksha.livesocket.websocket.reconnect_interval'))

    callbacks = [
        "onopen",
        "onclose",
        "onerror",
        "onconnectedframe",
        "onmessageframe",
    ]
    onopen = twc.Param(default='function (e) {moksha.debug(e)}')
    onclose = twc.Param(default='function (e) {moksha.debug(e)}')
    onerror = twc.Param(default='function (e) {moksha.debug(e)}')
    onconnectedframe = twc.Variable(default=None)

    # Used internally
    before_open = twc.Variable(default='function () {}')

    template = "mako:moksha.api.widgets.websocket.templates.websocket"

    def prepare(self):
        super(TW2WebSocketWidget, self).prepare()
        self.topics = []
        self.onmessageframe = defaultdict(str)

        notifications = {
            'before_open': 'Attempting to connect Moksha Live Socket',
            'onopen': 'Moksha Live socket connected',
            'onclose': 'Moksha Live socket closed',
            'onerror': 'Error with Moksha Live socket',
        }

        if self.notify:
            self.resources += gritter_resources
            self.before_open = "$(%s);" % str(gritter_callback(
                title="WebSocket", text=notifications['before_open'],
            ))

        for callback in self.callbacks:
            cbs = ''

            if self.notify and callback in notifications:
                cbs += "$(%s);" % str(gritter_callback(
                    title="WebSocket", text=notifications[callback]
                ))

            if self.ws_reconnect_interval and callback is 'onclose':
                cbs += "setTimeout(setup_moksha_websocket, %i)" % \
                        int(self.ws_reconnect_interval)

            if len(moksha.utils.livewidgets[callback]):
                if callback == 'onmessageframe':
                    for topic in moksha.utils.livewidgets[callback]:
                        self.topics.append(topic)
                        for cb in moksha.utils.livewidgets[callback][topic]:
                            self.onmessageframe[topic] += '%s;' % str(cb)
                else:
                    for cb in moksha.utils.livewidgets[callback]:
                        if isinstance(cb, (twc.js_callback, twc.js_function)):
                            cbs += '$(%s);' % str(cb)
                        else:
                            cbs += str(cb)
            if cbs:
                cbs = "function() { %s }" % cbs
                setattr(self, callback, cbs)


if asbool(config.get('moksha.use_tw2', False)):
    WebSocketWidget = TW2WebSocketWidget
else:
    warnings.warn("no tw1 support for websockets")
    WebSocketWidget = None
