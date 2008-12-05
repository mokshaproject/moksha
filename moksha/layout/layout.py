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

from tw.api import Widget, JSLink, CSSLink
from tw.jquery import jquery_js

layout_js = JSLink(filename='static/layout.js', modname=__name__)
layout_css = CSSLink(filename='static/layout.css', modname=__name__)
ui_core_js = JSLink(filename='static/ui/ui.core.js', modname=__name__)
ui_draggable_js = JSLink(filename='static/ui/ui.draggable.js', modname=__name__)
ui_droppable_js = JSLink(filename='static/ui/ui.droppable.js', modname=__name__)
ui_sortable_js = JSLink(filename='static/ui/ui.sortable.js', modname=__name__)

class LayoutWidget(Widget):
    template = 'mako:moksha.widgets.layout.templates.layout'
    params = {}
    css = [layout_css]
    javascript = [jquery_js, layout_js, ui_core_js, ui_draggable_js,
                  ui_droppable_js, ui_sortable_js]

    def update_params(self, d):
        super(LayoutWidget, self).update_params(d)
        # stuff apps into a slick layout
