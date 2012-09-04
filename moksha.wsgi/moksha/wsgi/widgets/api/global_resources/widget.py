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
import types

from paste.deploy.converters import asbool

import tw2.core as twc
import tw2.core.widgets

from moksha.wsgi.widgets.moksha_js import (
    moksha_js, moksha_extension_points_js,
)
from moksha.wsgi.widgets.api.socket import AbstractMokshaSocket

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
    template = "mako:moksha.wsgi.widgets.api.global_resources.templates.global"

    base_url = '/'
    user_id = ''
    debug = twc.Param(default=False)
    profile = twc.Param(default=False)
    extensionpoints = twc.Param(default=False)

    base_url = twc.Param(default='/')

    config = twc.Param("Configuration dict.", default=twc.Required)
    request = twc.Param("The request.", default=twc.Required)


    @property
    def c(self):
        """ Synonym for the 'c' property for backwards compat with tw1 """
        return self.children

    def prepare(self):
        super(GlobalResourceInjectionWidget, self).prepare()

        for required in ['config', 'request']:
            if not getattr(self, required, None):
                raise ValueError("GlobalResources must be given a %r." %
                                 required)

        live = asbool(self.config.get('moksha.livesocket', True))

        for widget_entry in pkg_resources.iter_entry_points('moksha.global'):
            log.info('Loading global resource: %s' % widget_entry.name)
            loaded = widget_entry.load()
            if isinstance(loaded, types.FunctionType):
                loaded = loaded(self.config)
            if isinstance(loaded, twc.JSLink):
                self.resources.append(loaded)
            elif isinstance(loaded, twc.CSSLink):
                self.resources.append(loaded)
            elif isinstance(loaded, tw2.core.widgets.WidgetMeta):
                if loaded in self.children:
                    log.debug("Skipping duplicate global widget: %s" %
                              widget_entry.name)
                else:
                    if issubclass(loaded, AbstractMokshaSocket) and not live:
                        log.debug('Moksha Live Socket disabled in config')
                        continue

                    self.children.append(loaded)
            else:
                raise Exception("Unknown global resource: %s.  Should be "
                                "either a JSLink or CSSLink." %
                                widget_entry.name)

        if self.extensionpoints:
            self.resources.append(moksha_extension_points_js)

        identity = self.request.environ.get('repoze.who.identity')
        if identity:
            self.user_id = identity.get('user_id', '')


global_resources = GlobalResourceInjectionWidget
