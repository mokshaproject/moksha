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

import moksha
import moksha.utils

from tg import config
from paste.deploy.converters import asbool

import tw.api
import tw2.core as twc

from moksha.api.widgets.orbited import orbited_host, orbited_port, orbited_url
from moksha.api.widgets.orbited import orbited_js
from moksha.lib.helpers import defaultdict
from moksha.widgets.notify import moksha_notify
from moksha.widgets.json import tw1_jquery_json_js, tw2_jquery_json_js

tw1_stomp_js = tw.api.JSLink(
    link=orbited_url + '/static/protocols/stomp/stomp.js')
tw2_stomp_js = twc.JSLink(
    link=orbited_url + '/static/protocols/stomp/stomp.js')


def stomp_subscribe(topic):
    """ Return a javascript callback that subscribes to a given topic,
        or a list of topics.
    """
    sub = "stomp.subscribe('%s');"
    if isinstance(topic, list):
        sub = ''.join([sub % t for t in topic])
    else:
        sub = sub % topic
    return sub


def stomp_unsubscribe(topic):
    """ Return a javascript callback that unsubscribes to a given topic,
        or a list of topics.
    """
    sub = "stomp.unsubscribe('%s');"
    if isinstance(topic, list):
        sub = ''.join([sub % t for t in topic])
    else:
        sub = sub % topic
    return sub


class TW1StompWidget(tw.api.Widget):
    callbacks = ['onopen', 'onerror', 'onerrorframe', 'onclose',
                 'onconnectedframe', 'onmessageframe']
    javascript = [tw1_jquery_json_js]
    params = callbacks[:] + ['topics', 'notify', 'orbited_host',
            'orbited_port', 'orbited_url', 'orbited_js', 'stomp_host',
            'stomp_port', 'stomp_user', 'stomp_pass']
    onopen = tw.api.js_callback('function(){}')
    onerror = tw.api.js_callback('function(error){}')
    onclose = tw.api.js_callback('function(c){}')
    onerrorframe = tw.api.js_callback('function(f){}')
    onmessageframe = ''
    onconnectedframe = ''

    # Popup notification bubbles on socket state changes
    notify = False

    template = "mako:moksha.api.widgets.stomp.templates.stomp"

    hidden = True

    def __init__(self, *args, **kw):
        self.notify = asbool(config.get('moksha.socket.notify', False))
        self.orbited_host = config.get('orbited_host', 'localhost')
        self.orbited_port = str(config.get('orbited_port', 9000))
        self.orbited_scheme = config.get('orbited_scheme', 'http')
        self.orbited_url = '%s://%s:%s' % (
            self.orbited_scheme, self.orbited_host, self.orbited_port)
        self.orbited_js = tw.api.JSLink(
            link=self.orbited_url + '/static/Orbited.js')
        self.stomp_host = config.get('stomp_host', 'localhost')
        self.stomp_port = str(config.get('stomp_port', 61613))
        self.stomp_user = config.get('stomp_user', 'guest')
        self.stomp_pass = config.get('stomp_pass', 'guest')
        super(TW1StompWidget, self).__init__(*args, **kw)

    def update_params(self, d):
        super(TW1StompWidget, self).update_params(d)
        d.topics = []
        d.onmessageframe = defaultdict(str)  # {topic: 'js callbacks'}
        for callback in self.callbacks:
            if len(moksha.utils.livewidgets[callback]):
                cbs = ''
                if callback == 'onmessageframe':
                    for topic in moksha.utils.livewidgets[callback]:
                        d.topics.append(topic)
                        for cb in moksha.utils.livewidgets[callback][topic]:
                            d.onmessageframe[topic] += '%s;' % str(cb)
                else:
                    for cb in moksha.utils.livewidgets[callback]:
                        if isinstance(cb, (tw.api.js_callback,
                                           tw.api.js_function)):
                            cbs += '$(%s);' % str(cb)
                        else:
                            cbs += str(cb)
                if cbs:
                    d[callback] = cbs

        if d.notify:
            moksha_notify.register_resources()
            d.onopen = tw.api.js_callback('function() { $.jGrowl("Moksha live socket connected") }')
            d.onerror = tw.api.js_callback('function(error) { $.jGrowl("Moksha Live Socket Error: " + error) }')
            d.onerrorframe = tw.api.js_callback('function(f) { $.jGrowl("Error frame received from Moksha Socket: " + f) }')
            d.onclose = tw.api.js_callback('function(c) { $.jGrowl("Moksha Socket Closed") }')


class TW2StompWidget(twc.Widget):
    callbacks = ['onopen', 'onerror', 'onerrorframe', 'onclose',
                 'onconnectedframe', 'onmessageframe']
    resources = [tw2_jquery_json_js]
    topics = twc.Variable()
    notify = twc.Param(
        default=asbool(config.get('moksha.socket.notify', False)))
    hidden = twc.Param(default=True)

    orbited_host = twc.Param(
        default=config.get('orbited_host', 'localhost'))
    orbited_port = twc.Param(
        default=str(config.get('orbited_port', 9000)))
    orbited_scheme = twc.Param(
        default=config.get('orbited_scheme', 'http'))
    orbited_js = twc.Param(default=orbited_js)

    stomp_host = twc.Param(
        default=config.get('stomp_host', 'localhost'))
    stomp_port = twc.Param(
        default=str(config.get('stomp_port', 61613)))
    stomp_user = twc.Param(
        default=config.get('stomp_user', 'guest'))
    stomp_pass = twc.Param(
        default=config.get('stomp_pass', 'guest'))

    onopen = twc.Param(default=twc.js_callback("function(){}"))
    onerror = twc.Param(default=twc.js_callback("function(){}"))
    onclose = twc.Param(default=twc.js_callback("function(){}"))
    onerrorframe = twc.Param(default=twc.js_callback("function(){}"))
    onmessageframe = twc.Param(default='')
    onconnectedframe = twc.Param(default='')

    template = "mako:moksha.api.widgets.stomp.templates.stomp"

    def prepare(self):
        super(TW2StompWidget, self).prepare()
        self.orbited_url = '%s://%s:%s' % (self.orbited_scheme,
                self.orbited_host, self.orbited_port)

        self.topics = []
        self.onmessageframe = defaultdict(str)  # {topic: 'js callbacks'}
        for callback in self.callbacks:
            if len(moksha.utils.livewidgets[callback]):
                cbs = ''
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
                    setattr(self, callback, cbs)

        if self.notify:
            moksha_notify.req().prepare()  # Inject moksha_notify resources.
            self.onopen = twc.js_callback('function() { $.jGrowl("Moksha live socket connected") }')
            self.onerror = twc.js_callback('function(error) { $.jGrowl("Moksha Live Socket Error: " + error) }')
            self.onerrorframe = twc.js_callback('function(f) { $.jGrowl("Error frame received from Moksha Socket: " + f) }')
            self.onclose = twc.js_callback('function(c) { $.jGrowl("Moksha Socket Closed") }')

if asbool(config.get('moksha.use_tw2', False)):
    StompWidget = TW2StompWidget
    stomp_js = tw2_stomp_js
else:
    StompWidget = TW1StompWidget
    stomp_js = tw1_stomp_js
