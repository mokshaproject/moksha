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

from tw.api import Widget
from tw.jquery import jquery_js
from moksha.lib.helpers import eval_app_config, ConfigWrapper

from paste.deploy.converters import asbool
from tg import config


class TW1AppListWidget(Widget):
    template = 'mako:moksha.api.widgets.containers.templates.layout_applist'
    params = ['category']

    def update_params(self, d):
        super(TW1AppListWidget, self).update_params(d)

        # ignore categories that don't exist
        c = d['category']
        if isinstance(c, basestring):
            found = False
            for cat in d['layout']:
                if cat['label'] == c:
                    d['category'] = cat
                    found = True
                    break

            # ignore categories that don't exist
            if not found:
                d['category'] = None

if asbool(config.get('moksha.use_tw2', False)):
    raise NotImplementedError(__name__ + " is not ready for tw2")
else:
    AppListWidget = TW1AppListWidget

applist_widget = AppListWidget('applist');


class TW1DashboardContainer(Widget):
    template = 'mako:moksha.api.widgets.containers.templates.dashboardcontainer'
    params = ['layout', 'applist_widget']
    css = []
    javascript = []
    config_key = None
    layout = []
    applist_widget = applist_widget
    engine_name = 'mako'

    def update_params(self, d):
        super(TW1DashboardContainer, self).update_params(d)
        layout = eval_app_config(config.get(self.config_key, "None"))

        if not layout:
            if isinstance(d.layout, basestring):
                layout = eval_app_config(d.layout)
            else:
                layout = d.layout

        # Filter out any None's in the layout which signify apps which are
        # not allowed to run with the current session's authorization level
        d.layout = ConfigWrapper.process_wrappers(layout, d)

        return d

if asbool(config.get('moksha.use_tw2', False)):
    raise NotImplementedError(__name__ + " is not ready for tw2")
else:
    DashboardContainer = TW1DashboardContainer
