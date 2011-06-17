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
import tw.api
import tw.jquery
import tw2.core as twc
import tw2.jquery

from tg import config
from paste.deploy.converters import asbool

from moksha.api.widgets.live import LiveWidget, LiveWidgetMeta, TW2LiveWidget
from moksha.api.widgets.live import subscribe_topics, unsubscribe_topics


tw1_container_js = tw.api.JSLink(
    filename='static/js/mbContainer.min.js',
    javascript=[
        tw.jquery.jquery_js
    ],
    modname=__name__)
tw1_container_css = tw.api.CSSLink(
    filename='static/css/mbContainer.css',
    modname=__name__)

tw2_container_js = twc.JSLink(
    filename='static/js/mbContainer.min.js',
    resources=[
        tw2.jquery.jquery_js,
        tw2.jqplugins.ui.jquery_ui_js,
    ],
    modname=__name__)
tw2_container_css = twc.CSSLink(
    filename='static/css/mbContainer.css',
    resources=[
        twc.DirLink(filename='static/css/elements', modname=__name__)
    ],
    modname=__name__)


class TW1MokshaContainer(tw.api.Widget):
    template = 'mako:moksha.widgets.container.templates.container'
    javascript = [tw1_container_js]
    css = [tw1_container_css]
    options = ['draggable', 'resizable']
    button_options = ['iconize', 'minimize', 'close']
    params = ['buttons', 'skin', 'height', 'width', 'left', 'top', 'id',
              'title', 'icon', 'content', 'widget_name', 'view_source', 'dock',
              'onResize', 'onClose', 'onCollapse', 'onIconize', 'onDrag',
              'onRestore'] + options[:] + ['elementsPath']
    draggable = droppable = True
    resizable = False
    iconize = minimize = close = True
    hidden = True  # hide from the moksha menu
    content = ''  # either text, or a Widget instance
    widget_name = None
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

    def update_params(self, d):
        super(TW1MokshaContainer, self).update_params(d)
        if isinstance(d.content, tw2.core.widgets.WidgetMeta):
            d.content = d.content.req()

        if (isinstance(d.content, tw.api.Widget) or
            isinstance(d.content, tw2.core.Widget)):

            d.widget_name = d.content.__class__.__name__
            content_args = getattr(d, 'content_args', {})

            if isinstance(d.content, LiveWidget):
                topics = d.content.get_topics()
                # FIXME: also unregister the moksha callback functions.  Handle
                # cases where multiple widgets are listening to the same topics
                d.onClose = "function(o){%s $(o).remove();}" % \
                        unsubscribe_topics(topics)
                d.onIconize = d.onCollapse = "function(o){%s}" % \
                        unsubscribe_topics(topics)
                d.onRestore =  "function(o){%s}" % \
                        subscribe_topics(topics)
            elif isinstance(d.content, TW2LiveWidget):
                # TODO -- do we even need to worry about this since its a tw1
                # container?
                topics = d.content.get_topics()
                # FIXME: also unregister the moksha callback functions.  Handle
                # cases where multiple widgets are listening to the same topics
                d.onClose = "function(o){%s $(o).remove();}" % \
                        unsubscribe_topics(topics)
                d.onIconize = d.onCollapse = "function(o){%s}" % \
                        unsubscribe_topics(topics)
                d.onRestore = "function(o){%s}" % \
                        subscribe_topics(topics)

            d.content = d.content.display(**content_args)

        for option in self.options:
            d[option] = d.get(option, True) and option or ''

        d.buttons = ''
        for button in self.button_options:
            if d.get(button, True):
                d.buttons += '%s,' % button[:1]
        d.buttons = d.buttons[:-1]

        d.id = str(uuid.uuid4())

        d.elementsPath = '/toscawidgets/resources/moksha.widgets.container.container/static/css/elements/'
#        self.add_call(tw.api.jQuery('#%s' % d.id).buildContainers({
#            'elementsPath': '/toscawidgets/resources/moksha.widgets.container.container/static/css/elements/',
#            'onClose': d.onClose,
#            'onResize': d.onResize,
#            'onCollapse': d.onCollapse,
#            'onIconize': d.onIconize,
#            'onDrag': d.onDrag,
#            'onRestore': d.onRestore,
#            }))


class TW2MokshaContainer(twc.Widget):
    template = 'mako:moksha.widgets.container.templates.container'
    resources = [tw2_container_js, tw2_container_css]
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
    widget_name = None
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
        super(TW2MokshaContainer, self).prepare()
        if self.content and not isinstance(self.content,
                                           tw2.core.widgets.WidgetMeta):
            # This does not have to be cause for ultra-alarm.  We could take
            # care to render tw1 widgets inside tw2 widgets, but I'm throwing
            # hard errors here so I don't mess up jquery dependencies.
            raise ValueError("non-tw2 widget found inside tw2 container")

        self.widget_name = self.content.__class__.__name__
        content_args = getattr(self, 'content_args', {})
        if isinstance(self.content, (LiveWidget, LiveWidgetMeta)):
            topics = self.content.get_topics()
            # FIXME: also unregister the moksha callback functions.  Handle
            # cases where multiple widgets are listening to the same topics

            if not isinstance(unsubscribe_topics(topics), basestring):
                raise ValueError('wtf')

            self.onClose = "function(o){%s $(o).remove();}" % \
                unsubscribe_topics(topics)
            self.onIconize = self.onCollapse = "function(o){%s}" % \
                unsubscribe_topics(topics)
            self.onRestore = "function(o){%s}" % \
                subscribe_topics(topics)

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

        self.elementsPath = '/resources/moksha.widgets.container.container/static/css/elements/'
#        self.add_call(tw2.jquery.jQuery('#%s' % self.id).buildContainers({
#            'elementsPath':
#            'onClose': self.onClose,
#            'onResize': self.onResize,
#            'onCollapse': self.onCollapse,
#            'onIconize': self.onIconize,
#            'onDrag': self.onDrag,
#            'onRestore': self.onRestore,
#            }))


if asbool(config.get('moksha.use_tw2', False)):
    MokshaContainer = TW2MokshaContainer
    container_js = tw2_container_js
    container_css = tw2_container_css
    container = MokshaContainer(id='moksha_container')
else:
    MokshaContainer = TW1MokshaContainer
    container_js = tw1_container_js
    container_css = tw1_container_css
    container = MokshaContainer('moksha_container')
