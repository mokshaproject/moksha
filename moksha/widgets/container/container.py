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
from tw.jquery import jquery_js, jQuery

container_js = JSLink(filename='static/js/mbContainer.min.js', modname=__name__)
container_css = CSSLink(filename='static/css/mbContainer.css', modname=__name__)

class MokshaContainer(Widget):
    template = 'mako:moksha.widgets.container.templates.container'
    javascript = [container_js]
    css = [container_css]
    options = ['draggable', 'resizable']
    button_options = ['iconize', 'minimize', 'close']
    params = ['buttons', 'skin', 'height', 'width', 'left', 'top', 'id',
              'title', 'icon'] + \
             options[:]
    draggable = droppable = resizable = True
    iconize = minimize = close = True
    stikynote = False
    hidden = True # hide from the moksha menu
    content = '' # either text, or a Widget
    title = 'Moksha Container'
    skin = 'default' # default, black, white, stiky, alert
    #icon = 'chart.png'

    # Pixel tweaking
    width = 430
    #height = 500
    #left = 170
    #top = 270

    def update_params(self, d):
        super(MokshaContainer, self).update_params(d)

        if isinstance(d.content, Widget):
            d.content = d.content.display()

        for option in self.options:
            d[option] = d.get(option, True) and option or ''

        d.buttons = ''
        for button in self.button_options:
            if d.get(button, True):
                d.buttons += '%s,' % button[:1]
        d.buttons = d.buttons[:-1]

        self.add_call(jQuery('#%s' % d.id).buildContainers(
            {'elementsPath': '/toscawidgets/resources/moksha.widgets.container.container/static/css/elements/'}
            ))


container = MokshaContainer('moksha_container')
