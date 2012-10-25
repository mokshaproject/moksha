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
#
# Authors: Luke Macken <lmacken@redhat.com>

import uuid
import tw2.core as twc
import tw2.jquery

from moksha.wsgi.widgets.api.live import LiveWidget, LiveWidgetMeta
from moksha.wsgi.widgets.api.live import subscribe_topics, unsubscribe_topics


container_js = twc.JSLink(
    filename='static/js/mbContainer.min.js',
    resources=[
        tw2.jquery.jquery_js,
        tw2.jqplugins.ui.jquery_ui_js,
    ],
    modname=__name__)
container_css = twc.CSSLink(
    filename='static/css/mbContainer.css',
    resources=[
        twc.DirLink(filename='static/css/elements', modname=__name__)
    ],
    modname=__name__)


class MokshaContainer(twc.Widget):
    template = 'mako:moksha.wsgi.widgets.container.templates.container'
    resources = [container_js, container_css]
    options = ['draggable', 'resizable']
    button_options = ['iconize', 'minimize', 'close']
    params = ['buttons', 'skin', 'height', 'width', 'left', 'top', 'id',
              'title', 'icon', 'content', 'widget_name', 'view_source', 'dock',
              'onResize', 'onClose', 'onCollapse', 'onIconize', 'onDrag',
              'onRestore'] + options[:]
    draggable = droppable = True
    resizable = False
    iconize = minimize = close = True
    hidden = True  # hide from the moksha menu
    content = ''  # either text, or a Widget instance
    widget_name = ''
    title = 'Moksha Container'
    skin = 'default'  # default, black, white, stiky, alert
    view_source = True
    dock = 'moksha_dock'
    icon = 'gears.png'

    # Pixel tweaking
    width = 450
    height = 500
    left = 170
    top = 125

    # Javascript callbacks
    onResize = "function(o){}"
    onClose = "function(o){}"
    onCollapse = "function(o){}"
    onIconize = "function(o){}"
    onDrag = "function(o){}"
    onRestore = "function(o){}"

    def prepare(self):
        super(MokshaContainer, self).prepare()
        if self.content and not isinstance(self.content,
                                           tw2.core.widgets.WidgetMeta):
            # This does not have to be cause for ultra-alarm.  We could take
            # care to render tw1 widgets inside tw2 widgets, but I'm throwing
            # hard errors here so I don't mess up jquery dependencies.
            raise ValueError("non-tw2 widget found inside tw2 container")

        # If we weren't passed a widget_name explicitly, then take a guess.
        if not getattr(self, 'widget_name') and hasattr(self.content, 'id'):
            self.widget_name = self.content.id

        content_args = getattr(self, 'content_args', {})
        if isinstance(self.content, (LiveWidget, LiveWidgetMeta)):
            topics = self.content.get_topics()
            # FIXME: also unregister the moksha callback functions.  Handle
            # cases where multiple widgets are listening to the same topics

            obj = self.content.req()

            if not isinstance(unsubscribe_topics(obj, topics), basestring):
                raise ValueError('wtf')

            self.onClose = "function(o){%s $(o).remove();}" % \
                unsubscribe_topics(obj, topics)
            self.onIconize = self.onCollapse = "function(o){%s}" % \
                unsubscribe_topics(obj, topics)
            self.onRestore = "function(o){%s}" % \
                subscribe_topics(obj, topics)

        if self.content:
            self.content = self.content.display(**content_args)

        for option in self.options:
            setattr(self, option, getattr(self, option, True) and option or '')

        self.buttons = ''
        for button in self.button_options:
            if getattr(self, button, True):
                self.buttons += '%s,' % button[:1]
        self.buttons = self.buttons[:-1]

        self.id = str(uuid.uuid4())

        self.elementsPath = '/tw2/resources/moksha.wsgi.widgets.container.container/static/css/elements/'
#        self.add_call(tw2.jquery.jQuery('#%s' % self.id).buildContainers({
#            'elementsPath':
#            'onClose': self.onClose,
#            'onResize': self.onResize,
#            'onCollapse': self.onCollapse,
#            'onIconize': self.onIconize,
#            'onDrag': self.onDrag,
#            'onRestore': self.onRestore,
#            }))


container = MokshaContainer(id='moksha_container')
