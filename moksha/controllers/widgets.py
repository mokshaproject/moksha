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

from tg import expose, tmpl_context

from moksha.exc import WidgetNotFound
from moksha.lib.base import Controller
from moksha.widgets.container import container

class WidgetController(Controller):

    @expose('mako:moksha.templates.widget')
    def default(self, widget, chrome=None, **kw):
        options = {}
        options.update(kw)
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
        return dict(options=options)
