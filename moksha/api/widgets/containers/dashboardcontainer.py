# This file is part of Moksha.
# Copyright (C) 2008-2009  Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from tw.api import Widget
from tw.jquery import jquery_js
from moksha.lib.helpers import eval_app_config, ConfigWrapper
from tg import config
from tw.api import Widget

from moksha.lib.helpers import eval_app_config, ConfigWrapper

class AppListWidget(Widget):
    template = 'mako:moksha.api.widgets.containers.templates.layout_applist'
    params = ['category']

    def update_params(self, d):
        super(AppListWidget, self).update_params(d)

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

applist_widget = AppListWidget('applist');

class DashboardContainer(Widget):
    template = 'mako:moksha.api.widgets.containers.templates.dashboardcontainer'
    params = ['layout', 'applist_widget']
    css = []
    javascript = []
    config_key = None
    layout = []
    applist_widget = applist_widget
    engine_name = 'mako'

    def update_params(self, d):
        super(DashboardContainer, self).update_params(d)
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
