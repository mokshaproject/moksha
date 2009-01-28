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

from tg import expose, flash, require, tmpl_context, redirect, validate
from tg.controllers import WSGIAppController
from repoze.what import predicates
#from widgetbrowser.wsgiapp import WidgetBrowser

from moksha import _
from moksha.model import DBSession
from moksha.lib.base import BaseController
from moksha.controllers.secc import AdminController
from moksha.controllers.error import ErrorController
from moksha.api.widgets.layout import LayoutWidget

layout_widget = LayoutWidget('layout')

class RootController(BaseController):

    admin = AdminController()
    error = ErrorController()

    # Not packaged or in PyPi yet...
    #widgets = WSGIAppController(WidgetBrowser(interactive=False))

    @expose('moksha.templates.widget')
    def index(self):
        tmpl_context.widget = layout_widget
        return dict()

    @expose('moksha.templates.widget')
    def widget(self, name):
        """ Display a widget by name """
        tmpl_context.widget = moksha.get_widget(name)
        return dict()

    @expose('moksha.templates.about')
    def about(self):
        return dict(page='about')

    @expose('moksha.templates.index')
    @require(predicates.has_permission('manage', msg=_('Only for managers')))
    def manage_permission_only(self, **kw):
        return dict(page='managers stuff')

    @expose('moksha.templates.index')
    @require(predicates.is_user('editor'))
    def editor_user_only(self, **kw):
        return dict(page='editor stuff')

    @expose('moksha.templates.login')
    def login(self, **kw):
        came_from = kw.get('came_from', '/')
        return dict(page='login', header=lambda *arg: None,
                    footer=lambda *arg: None, came_from=came_from)
