# This file is part of Moksha.
#
# Moksha is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Moksha is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Moksha.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2008, Red Hat, Inc.
# Authors: Luke Macken <lmacken@redhat.com>

import moksha

from tw.api import Widget
from tw.jquery import jQuery
from tg import expose, tmpl_context

from moksha.lib.base import Controller
from moksha.exc import ApplicationNotFound

from moksha.api.widgets.containers import DashboardContainer
from moksha.api.widgets import ContextAwareWidget
from moksha.lib.helpers import Category, MokshaApp, MokshaWidget

class AppWidgetContainer(DashboardContainer, ContextAwareWidget):
    template = "${applist_widget(category='main', layout=layout)}"

appwidget_container = AppWidgetContainer('appwidget')

class AppController(Controller):

    @expose()
    def lookup(self, app, *remainder):
        if app not in moksha.apps:
            raise ApplicationNotFound(app)
        return moksha.apps[app]['controller'], remainder

    @expose('mako:moksha.templates.widget')
    def container(self, application, height=675, width=910, left=55,
                  top=50, **kw):
        """ Return an application rendered in a Moksha Widget Container """
        app = moksha.apps.get(application)
        if not app:
            raise ApplicationNotFound(application)

        tmpl_context.widget = appwidget_container

        options = {}
        options['layout'] = [
            Category('main', [
                MokshaWidget(None, 'moksha_container', params={
                    'id': application + '_container',
                    'title': app['name'],
                    'content': appwidget_container(layout=[
                        Category('main', [MokshaApp(None, application,
                                                    params=kw)])]),
                    'height': 675,
                    'width': 910,
                    'left': 55,
                    'top': 50,
                    })
                ]),
        ]

        return dict(options=options)
