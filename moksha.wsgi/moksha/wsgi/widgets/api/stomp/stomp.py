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

import moksha.common.utils

import tw2.core as twc
import tw2.jquery

from moksha.wsgi.widgets.api.socket import AbstractMokshaSocket
from moksha.common.lib.helpers import defaultdict

orbited_host = twc.Required
orbited_port = twc.Required
orbited_scheme = twc.Required

stomp_broker = twc.Required
stomp_port = twc.Required
stomp_user = twc.Required
stomp_pass = twc.Required



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

    orbited_host = twc.Param(default=orbited_host)
    orbited_port = twc.Param(default=orbited_port)
    orbited_scheme = twc.Param(default=orbited_scheme)

    stomp_broker = twc.Param(default=stomp_broker)
    stomp_port = twc.Param(default=stomp_port)
    stomp_user = twc.Param(default=stomp_user)
    stomp_pass = twc.Param(default=stomp_pass)

    template = "mako:moksha.wsgi.widgets.api.stomp.templates.stomp"

    def prepare(self):
        super(StompWidget, self).prepare()
        self.orbited_url = '%s://%s:%s' % (
            self.orbited_scheme,
            self.orbited_host,
            self.orbited_port,
        )

        orbited_js = twc.JSLink(
            link=self.orbited_url + '/static/Orbited.js',
            resources=[tw2.jquery.jquery_js])

        tstomp_js = twc.JSLink(
            link=self.orbited_url + '/static/protocols/stomp/stomp.js')

        self.resources.extend([orbited_js, tstomp_js])

