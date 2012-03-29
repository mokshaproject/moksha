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

import logging
import pkg_resources

from tg import config, url
from paste.deploy.converters import asbool
from pylons import request
from inspect import isclass

import tw2.core as twc
import tw2.core.widgets

from moksha.widgets.moksha_js import (
    moksha_js, moksha_extension_points_js,
    moksha_js, moksha_extension_points_js,
)
from moksha.api.widgets.live import moksha_socket

log = logging.getLogger(__name__)


class GlobalResourceInjectionWidget(twc.Widget):
    """
    This widget will pull in all JSLink, CSSLink, and Widget resources that
    are listed on the `[moksha.global]` entry-point.

    :Note: Global Widget injection will only work when the global_resource
           widget is actually rendered in the template.  Otherwise, only JS
           and CSS resources will get injected.  Moksha's index.mak template
           handles this for us, otherwise you can import the `global_resources`
           widget from this module and do it yourself.
    """
    resources = [moksha_js]
    children = []
    css = []
    template = "mako:moksha.api.widgets.global_resources.templates.global"

    params = [
        'base_url', 'csrf_token', 'user_id', 'debug', 'profile',
        'csrf_trusted_domains',
    ]
    base_url = '/'
    csrf_token = ''
    user_id = ''
    debug = 'false'
    profile = 'false'

    @property
    def c(self):
        """ Synonym for the 'c' property for backwards compat with tw1 """
        return self.children

    def __init__(self):
        super(GlobalResourceInjectionWidget, self).__init__()
        if asbool(config.get('debug')):
            self.debug = 'true'
        if asbool(config['global_conf'].get('profile')):
            self.profile = 'true'

        for widget_entry in pkg_resources.iter_entry_points('moksha.global'):
            log.info('Loading global resource: %s' % widget_entry.name)
            loaded = widget_entry.load()
            #if isclass(loaded):
            #    loaded = loaded(id=widget_entry.name)
            if isinstance(loaded, twc.JSLink):
                self.resources.append(loaded)
            elif isinstance(loaded, twc.CSSLink):
                self.resources.append(loaded)
            elif isinstance(loaded, tw2.core.widgets.WidgetMeta):
                if loaded in self.children:
                    log.debug("Skipping duplicate global widget: %s" %
                              widget_entry.name)
                else:
                    if loaded is moksha_socket:
                        if not asbool(config.get('moksha.livesocket', True)):
                            log.debug('Moksha Live Socket disabled in the config')
                            continue
                    self.children.append(loaded)
            else:
                raise Exception("Unknown global resource: %s.  Should be "
                                "either a JSLink or CSSLink." %
                                widget_entry.name)

        self.csrf_token_id = config.get('moksha.csrf.token_id', '_csrf_token')
        if asbool(config.get('moksha.extensionpoints', False)):
            self.resources.append(moksha_extension_points_js)

        trusted_domain_list = config.get('moksha.csrf.trusted_domains', '').split(',')
        # turn into quick lookup hash
        item_list = []
        for domain in trusted_domain_list:
            item_list.append('"%s": true' % domain)
        trusted_domain_hash = '{%s}' % ','.join(item_list)
        self.csrf_trusted_domains_hash = trusted_domain_hash
        self.csrf_trusted_domains = self.csrf_trusted_domains_hash

    def prepare(self):
        super(GlobalResourceInjectionWidget, self).prepare()

        self.base_url = url('/')

        identity = request.environ.get('repoze.who.identity')
        if identity:
            self.csrf_token = identity.get(self.csrf_token_id, '')
            self.user_id = identity.get('user_id', '')


global_resources = GlobalResourceInjectionWidget
