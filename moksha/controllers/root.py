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
        return {'title': 'Moksha'}

    @expose('mako:moksha.templates.widget')
    def widgets(self, widget, **kw):
        tmpl_context.widget = moksha.get_widget(widget)
        tmpl_context.container = container
        kw['id'] = widget + '_container'
        return {'title': moksha._widgets[widget]['name'],
                'container_options': kw}

    @expose('moksha.templates.login')
    def login(self, **kw):
        came_from = kw.get('came_from', '/')
        return dict(page='login', header=lambda *arg: None,
                    footer=lambda *arg: None, came_from=came_from)
