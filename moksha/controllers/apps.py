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
#
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
        if app not in moksha._apps:
            raise ApplicationNotFound(app)
        return moksha.get_app(app), remainder

    @expose('mako:moksha.templates.widget')
    def container(self, application, height=675, width=910, left=55,
                  top=50, **kw):
        """ Return an application rendered in a Moksha Widget Container """
        app = moksha.get_app(application)
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
