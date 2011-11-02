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
:mod:`moksha.api.widgets.amqp` - An AMQP driven live Moksha socket
==================================================================

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

import moksha
import moksha.utils

from tg import config
from paste.deploy.converters import asbool

import tw.api
import tw2.core as twc

from moksha.api.widgets.orbited import orbited_host, orbited_port, orbited_url
from moksha.api.widgets.orbited import orbited_js
from moksha.lib.helpers import defaultdict, listify
from moksha.widgets.notify import moksha_notify
from moksha.widgets.moksha_js import tw1_moksha_js, tw2_moksha_js
from moksha.widgets.json import tw1_jquery_json_js, tw2_jquery_json_js

from widgets import tw1_amqp_resources, tw2_amqp_resources

def amqp_subscribe(topic):
    """ Return a javascript callback that subscribes to a given topic,
        or a list of topics.
    """
    sub = """
        moksha.debug("Subscribing to the '%(topic)s' topic");
        moksha_amqp_queue.subscribe({
            exchange: 'amq.topic',
            remote_queue: moksha_amqp_remote_queue,
            binding_key: '%(topic)s',
            callback: moksha_amqp_on_message,
        });
    """
    return ''.join([sub % {'topic': t} for t in listify(topic)])


def amqp_unsubscribe(topic):
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


class TW1AMQPSocket(tw.api.Widget):
    callbacks = ['onconnectedframe', 'onmessageframe']
    javascript = [tw1_jquery_json_js, tw1_moksha_js, tw1_amqp_resources]
    params = callbacks[:] + ['topics', 'notify', 'orbited_host',
            'orbited_port', 'orbited_url', 'orbited_js', 'amqp_broker_host',
            'amqp_broker_port', 'amqp_broker_user', 'amqp_broker_pass',
            'send_hook', 'recieve_hook']
    onconnectedframe = ''
    onmessageframe = ''
    send_hook = ''
    recieve_hook = ''

    template = "mako:moksha.api.widgets.amqp.templates.amqp"

    hidden = True

    def __init__(self, *args, **kw):
        self.notify = asbool(config.get('moksha.socket.notify', False))
        self.orbited_host = config.get('orbited_host', 'localhost')
        self.orbited_port = config.get('orbited_port', 9000)
        self.orbited_scheme = config.get('orbited_scheme', 'http')
        self.orbited_url = '%s://%s:%s' % (
            self.orbited_scheme, self.orbited_host, self.orbited_port)
        self.orbited_js = tw.api.JSLink(
            link=self.orbited_url + '/static/Orbited.js')
        self.amqp_broker_host = config.get('amqp_broker_host', 'localhost')
        self.amqp_broker_port = config.get('amqp_broker_port', 5672)
        self.amqp_broker_user = config.get('amqp_broker_user', 'guest')
        self.amqp_broker_pass = config.get('amqp_broker_pass', 'guest')
        super(TW1AMQPSocket, self).__init__(*args, **kw)

    def update_params(self, d):
        super(TW1AMQPSocket, self).update_params(d)
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


# TODO -- AMQPSocket and StompSocket have a *lot* in common.
#         They should both inherit from an abstract CometSocket! -- threebean
class TW2AMQPSocket(twc.Widget):
    callbacks = ['onconnectedframe', 'onmessageframe']
    resources = [tw2_jquery_json_js, tw2_moksha_js, tw2_amqp_resources]
    topics = twc.Variable()
    notify = twc.Param(
        default=asbool(config.get('moksha.socket.notify', False)))
    hidden = twc.Param(default=True)

    orbited_host = twc.Param(
        default=config.get('orbited_host', 'localhost'))
    orbited_port = twc.Param(
        default=config.get('orbited_port', 9000))
    orbited_scheme = twc.Param(
        default=config.get('orbited_scheme', 'http'))
    orbited_js = twc.Param(default=orbited_js)

    amqp_broker_host = twc.Param(
        default=config.get('amqp_broker_host', 'localhost'))
    amqp_broker_port = twc.Param(
        default=config.get('amqp_broker_port', 5672))
    amqp_broker_user = twc.Param(
        default=config.get('amqp_broker_user', 'guest'))
    amqp_broker_pass = twc.Param(
        default=config.get('amqp_broker_pass', 'guest'))

    onconnectedframe = twc.Param(default='')
    onmessageframe = twc.Param(default='')
    send_hook = twc.Param(default='')
    receive_hook = twc.Param(default='')

    template = "mako:moksha.api.widgets.amqp.templates.amqp"

    def prepare(self):
        super(TW2AMQPSocket, self).prepare()
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


if asbool(config.get('moksha.use_tw2', False)):
    AMQPSocket = TW2AMQPSocket
else:
    AMQPSocket = TW1AMQPSocket
