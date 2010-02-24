# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
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

import uuid
from tw.api import Widget, JSLink, CSSLink, js_callback
from tw.jquery import jquery_js, jQuery

from moksha.api.widgets.live import LiveWidget
from moksha.api.widgets.live import subscribe_topics, unsubscribe_topics

container_js = JSLink(filename='static/js/mbContainer.min.js', modname=__name__)
container_css = CSSLink(filename='static/css/mbContainer.css', modname=__name__)

class MokshaContainer(Widget):
    template = 'mako:moksha.widgets.container.templates.container'
    javascript = [container_js]
    css = [container_css]
    options = ['draggable', 'resizable']
    button_options = ['iconize', 'minimize', 'close']
    params = ['buttons', 'skin', 'height', 'width', 'left', 'top', 'id',
              'title', 'icon', 'content', 'widget_name', 'view_source', 'dock',
              'onResize', 'onClose', 'onCollapse', 'onIconize', 'onDrag',
              'onRestore'] + options[:]
    draggable = droppable = True
    resizable = False
    iconize = minimize = close = True
    hidden = True # hide from the moksha menu
    content = '' # either text, or a Widget instance
    widget_name = None
    title = 'Moksha Container'
    skin = 'default' # default, black, white, stiky, alert
    view_source = True
    dock = 'moksha_dock'
    icon = 'gears.png'

    # Pixel tweaking
    width = 450
    height = 500
    left = 170
    top = 125

    # Javascript callbacks
    onResize = js_callback("function(o){}")
    onClose = js_callback("function(o){}")
    onCollapse = js_callback("function(o){}")
    onIconize = js_callback("function(o){}")
    onDrag = js_callback("function(o){}")
    onRestore = js_callback("function(o){}")

    def update_params(self, d):
        super(MokshaContainer, self).update_params(d)

        if isinstance(d.content, Widget):
            d.widget_name = d.content.__class__.__name__

            if isinstance(d.content, LiveWidget):
                topics = d.content.get_topics()
                # FIXME: also unregister the moksha callback functions.  Handle
                # cases where multiple widgets are listening to the same topics
                d.onClose = js_callback("function(o){%s $(o).remove();}" %
                        unsubscribe_topics(topics))
                d.onIconize = d.onCollapse = js_callback("function(o){%s}" %
                        unsubscribe_topics(topics))
                d.onRestore = js_callback("function(o){%s}" %
                        subscribe_topics(topics))

            d.content = d.content.display()

        for option in self.options:
            d[option] = d.get(option, True) and option or ''

        d.buttons = ''
        for button in self.button_options:
            if d.get(button, True):
                d.buttons += '%s,' % button[:1]
        d.buttons = d.buttons[:-1]

        d.id = str(uuid.uuid4())

        self.add_call(jQuery('#%s' % d.id).buildContainers({
            'elementsPath': '/toscawidgets/resources/moksha.widgets.container.container/static/css/elements/',
            'onClose': d.onClose,
            'onResize': d.onResize,
            'onCollapse': d.onCollapse,
            'onIconize': d.onIconize,
            'onDrag': d.onDrag,
            'onRestore': d.onRestore,
            }))


container = MokshaContainer('moksha_container')
