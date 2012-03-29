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
from kitchen.text.converters import to_unicode as unicode

import tw2.core as twc

from moksha.api.widgets.socket import AbstractMokshaSocket
from moksha.api.widgets.orbited import orbited_host, orbited_port, orbited_url
from moksha.api.widgets.orbited import orbited_js
from moksha.lib.helpers import defaultdict

from tw2.jqplugins.gritter import gritter_resources, gritter_callback

tstomp_js = twc.JSLink(
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


class StompWidget(AbstractMokshaSocket):
    __shorthand__ = 'STOMP Socket'

    orbited_host = twc.Param(
        default=config.get('orbited_host', 'localhost'))
    orbited_port = twc.Param(
        default=unicode(config.get('orbited_port', 9000)))
    orbited_scheme = twc.Param(
        default=config.get('orbited_scheme', 'http'))
    orbited_js = twc.Param(default=orbited_js)

    stomp_host = twc.Param(
        default=config.get('stomp_host', 'localhost'))
    stomp_port = twc.Param(
        default=unicode(config.get('stomp_port', 61613)))
    stomp_user = twc.Param(
        default=config.get('stomp_user', 'guest'))
    stomp_pass = twc.Param(
        default=config.get('stomp_pass', 'guest'))

    template = "mako:moksha.api.widgets.stomp.templates.stomp"

    def prepare(self):
        super(StompWidget, self).prepare()
        self.orbited_url = '%s://%s:%s' % (self.orbited_scheme,
                self.orbited_host, self.orbited_port)
