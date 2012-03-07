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

from tg import config
from paste.deploy.converters import asbool
from kitchen.text.converters import to_unicode as unicode

import moksha
import moksha.utils

import tw.api
import tw2.core as twc
from tw2.jqplugins.gritter import gritter_resources, gritter_callback

from moksha.api.widgets.orbited import orbited_host, orbited_port, orbited_url
from moksha.api.widgets.orbited import orbited_js
from moksha.lib.helpers import defaultdict, listify
from moksha.widgets.moksha_js import tw1_moksha_js, tw2_moksha_js

tw1_jsio_js = tw.api.JSLink(
    filename='static/jsio/jsio.js',
    modname=__name__)

tw1_amqp_resources = tw.api.Link(
    filename='static/',
    modname=__name__)

tw2_jsio_js = twc.JSLink(
    filename='static/jsio/jsio.js',
    modname=__name__)

tw2_amqp_resources = twc.DirLink(
    filename='static/',
    modname=__name__)


if asbool(config.get('moksha.use_tw2', False)):
    amqp_resources = tw2_amqp_resources
    jsio_js = tw2_jsio_js
else:
    amqp_resources = tw1_amqp_resources
    jsio_js = tw1_jsio_js


def amqp_subscribe(topic):
    """ Return a javascript callback that subscribes to a given topic,
        or a list of topics.
    """
    sub = """
        moksha.debug("Subscribing to the '%(topic)s' topic");
        var receiver = moksha_amqp_session.receiver('amq.topic/%(topic)s')
        receiver.onReady = raw_msg_callback;
        receiver.capacity(0xFFFFFFFF);
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
    javascript = [tw1_moksha_js,
                  tw1_amqp_resources, tw1_jsio_js]
    params = callbacks[:] + [
        'topics', 'notify', 'orbited_host', 'orbited_scheme',
        'orbited_port', 'orbited_url', 'orbited_js', 'amqp_broker_host',
        'amqp_broker_port', 'amqp_broker_user', 'amqp_broker_pass',
        'send_hook', 'recieve_hook', 'moksha_domain']
    onconnectedframe = ''
    onmessageframe = ''
    send_hook = ''
    recieve_hook = ''

    template = "mako:moksha.api.widgets.amqp.templates.amqp"

    hidden = True

    def __init__(self, *args, **kw):
        self.notify = asbool(config.get('moksha.socket.notify', False))
        self.orbited_host = config.get('orbited_host', 'localhost')
        self.orbited_port = unicode(config.get('orbited_port', 9000))
        self.orbited_scheme = config.get('orbited_scheme', 'http')
        self.orbited_url = '%s://%s:%s' % (
            self.orbited_scheme, self.orbited_host, self.orbited_port)
        self.orbited_js = tw.api.JSLink(
            link=self.orbited_url + '/static/Orbited.js')
        self.moksha_domain = config.get('moksha.domain', 'localhost')
        self.amqp_broker_host = config.get('amqp_broker_host', 'localhost')
        self.amqp_broker_port = unicode(config.get('amqp_broker_port', 5672))
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
                            d.onmessageframe[topic] += '%s;' % unicode(cb)
                else:
                    for cb in moksha.utils.livewidgets[callback]:
                        if isinstance(cb, (tw.api.js_callback,
                                           tw.api.js_function)):
                            cbs += '$(%s);' % unicode(cb)
                        else:
                            cbs += unicode(cb)
                if cbs:
                    d[callback] = cbs


# TODO -- AMQPSocket and StompSocket have a *lot* in common.
#         They should both inherit from an abstract CometSocket! -- threebean
class TW2AMQPSocket(twc.Widget):
    callbacks = ['onconnectedframe', 'onmessageframe']
    resources = [tw2_moksha_js,
                 tw2_amqp_resources, tw2_jsio_js]
    topics = twc.Variable()
    notify = twc.Param(
        default=asbool(config.get('moksha.socket.notify', False)))
    hidden = twc.Param(default=True)

    orbited_host = twc.Param(
        default=config.get('orbited_host', 'localhost'))
    orbited_port = twc.Param(
        default=unicode(config.get('orbited_port', 9000)))
    orbited_scheme = twc.Param(
        default=config.get('orbited_scheme', 'http'))
    orbited_js = twc.Param(default=orbited_js)

    moksha_domain = twc.Param(
        default=config.get('moksha.domain', 'localhost'))

    amqp_broker_host = twc.Param(
        default=config.get('amqp_broker_host', 'localhost'))
    amqp_broker_port = twc.Param(
        default=unicode(config.get('amqp_broker_port', 5672)))
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

        notifications = {
            'onconnectedframe': "Moksha Live socket connected",
        }

        if self.notify:
            self.resources += gritter_resources

        for callback in self.callbacks:
            cbs = ''

            if self.notify and callback in notifications:
                cbs += "$(%s);" % unicode(gritter_callback(
                    title="AMQP Socket", text=notifications[callback]
                ))

            if len(moksha.utils.livewidgets[callback]):
                if callback == 'onmessageframe':
                    for topic in moksha.utils.livewidgets[callback]:
                        self.topics.append(topic)
                        for cb in moksha.utils.livewidgets[callback][topic]:
                            self.onmessageframe[topic] += '%s;' % unicode(cb)
                else:
                    for cb in moksha.utils.livewidgets[callback]:
                        if isinstance(cb, (twc.js_callback, twc.js_function)):
                            cbs += '$(%s);' % unicode(cb)
                        else:
                            cbs += unicode(cb)
            if cbs:
                setattr(self, callback, cbs)


if asbool(config.get('moksha.use_tw2', False)):
    AMQPSocket = TW2AMQPSocket
else:
    AMQPSocket = TW1AMQPSocket
