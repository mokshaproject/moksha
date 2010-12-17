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

import moksha

from tw.api import Widget, JSLink, CSSLink
from tw.jquery import jquery_js

layout_js = JSLink(filename='static/layout.js', modname=__name__)
layout_css = CSSLink(filename='static/layout.css', modname=__name__)
ui_core_js = JSLink(filename='static/ui/ui.core.js', modname=__name__)
ui_draggable_js = JSLink(filename='static/ui/ui.draggable.js', modname=__name__)
ui_droppable_js = JSLink(filename='static/ui/ui.droppable.js', modname=__name__)
ui_sortable_js = JSLink(filename='static/ui/ui.sortable.js', modname=__name__)

class LayoutWidget(Widget):
    template = 'mako:moksha.api.widgets.layout.templates.layout'
    params = ['header', 'content', 'sidebar', 'footer', 'invisible']
    css = [layout_css]
    javascript = [jquery_js, layout_js, ui_core_js, ui_draggable_js,
                  ui_droppable_js, ui_sortable_js]

    header = content = sidebar = footer = invisible = []

    def update_params(self, d):
        super(LayoutWidget, self).update_params(d)
        for widget in moksha._widgets.itervalues():
            if hasattr(widget['widget'], 'visible') and \
               not getattr(widget['widget'], 'visible'):
                d['invisible'].append(widget)
            elif hasattr(widget['widget'], 'view'):
                d[getattr(widget['widget'], 'view')].append(widget)
            else:
                d['content'].append(widget)
