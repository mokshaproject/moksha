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

from moksha import _
from moksha.model import DBSession
from moksha.lib.base import BaseController
from moksha.controllers.secc import AdminController
from moksha.controllers.error import ErrorController

from moksha.widgets.container import MokshaContainer
container = MokshaContainer('moksha_container')

class RootController(BaseController):

    admin = AdminController()
    error = ErrorController()

    @expose('mako:moksha.templates.index')
    def index(self):
        tmpl_context.menu_widget = moksha.menus['default_menu']
        tmpl_context.contextual_menu_widget = moksha.menus['contextual_menu']
        return dict(title='Moksha')

    @expose('mako:moksha.templates.widget')
    def widgets(self, widget, chrome=None, **kw):
        options = {}
        w = moksha._widgets.get(widget)
        if not w:
            raise WidgetNotFound(widget)
        if chrome and getattr(w['widget'], 'visible', True):
            tmpl_context.widget = container
            options['content'] = w['widget']
            options['title'] =  w['name']
            options['id'] = widget + '_container'
        else:
            tmpl_context.widget = w['widget']
        options.update(kw)
        return dict(options=options)

    @expose('moksha.templates.login')
    def login(self, **kw):
        came_from = kw.get('came_from', '/')
        return dict(page='login', header=lambda *arg: None,
                    footer=lambda *arg: None, came_from=came_from)
