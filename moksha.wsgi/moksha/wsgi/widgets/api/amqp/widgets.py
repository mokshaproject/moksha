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
:mod:`moksha.wsgi.widgets.api.amqp` - An AMQP driven live Moksha socket
==================================================================

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

import tw2.core as twc

from moksha.wsgi.widgets.api.socket import AbstractMokshaSocket
from moksha.common.lib.helpers import defaultdict, listify

orbited_host = twc.Required
orbited_port = twc.Required
orbited_scheme = twc.Required

jsio_js = twc.JSLink(
    filename='static/jsio/jsio.js',
    modname=__name__)

amqp_resources = twc.DirLink(
    filename='static/',
    modname=__name__)


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


class AMQPSocket(AbstractMokshaSocket):
    __shorthand__ = "AMQP Socket"

    resources = AbstractMokshaSocket.resources + \
            [amqp_resources, jsio_js]

    orbited_host = twc.Param(default=orbited_host)
    orbited_port = twc.Param(default=orbited_port)
    orbited_scheme = twc.Param(default=orbited_scheme)

    moksha_domain = twc.Param(twc.Required)

    amqp_broker_host = twc.Param(default=twc.Required)
    amqp_broker_port = twc.Param(default=twc.Required)
    amqp_broker_user = twc.Param(default=twc.Required)
    amqp_broker_pass = twc.Param(default=twc.Required)

    template = "mako:moksha.wsgi.widgets.api.amqp.templates.amqp"

    def prepare(self):
        super(AMQPSocket, self).prepare()
        self.orbited_url = '%s://%s:%s' % (
            self.orbited_scheme,
            self.orbited_host,
            self.orbited_port,
        )
