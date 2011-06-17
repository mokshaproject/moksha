## -*- coding: utf-8 -*-
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
"""
:mod:`moksha.apps.menus.widgets` - Moksha Menu Widgets
======================================================

This is a powerful component to build easily a multilevel tree menu or a
contextual menu (right click) in an intuitive way.

This module contains ToscaWidgets for the `mbMenu jQuery Plugin
<http://plugins.jquery.com/project/mbMenu>`_, which was developed by Matteo
Bicocchi. © 2002-2008 Open Lab srl, Matteo Bicocchi. GPL licensed.

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

from tg import config
from paste.deploy.converters import asbool

import tw.api
import tw.jquery
import tw2.core as twc
import tw2.jquery

from moksha.lib.helpers import when_ready

modname = __name__


tw1_jquery_mbmenu_js = tw.api.JSLink(
    modname=modname,
    filename='static/mbMenu.js',
    javascript=[tw.jquery.jquery_js])
tw1_jquery_mbmenu_min_js = tw.api.JSLink(
    modname=modname,
    filename='static/mbMenu.min.js',
    javascript=[tw.jquery.jquery_js])
tw1_mbmenu_css_1 = tw.api.CSSLink(
    modname=modname,
    filename='static/css/menu1.css',
    media='screen')
tw1_mbmenu_css = tw.api.CSSLink(
    modname=modname,
    filename='static/css/menu.css',
    media='screen')


tw2_jquery_mbmenu_js = twc.JSLink(
    modname=modname,
    filename='static/mbMenu.js',
    resources=[tw2.jquery.jquery_js])
tw2_jquery_mbmenu_min_js = twc.JSLink(
    modname=modname,
    filename='static/mbMenu.min.js',
    resources=[tw2.jquery.jquery_js])
tw2_mbmenu_css_1 = twc.CSSLink(
    modname=modname,
    filename='static/css/menu1.css',
    media='screen')
tw2_mbmenu_css = twc.CSSLink(
    modname=modname,
    filename='static/css/menu.css',
    media='screen')


class TW1MokshaMenuBase(tw.api.Widget):
    template = "mako:moksha.apps.menus.templates.mbmenu"
    javascript = [tw1_jquery_mbmenu_min_js]
    css = [tw1_mbmenu_css_1]
    params = ['callback', 'rootMenuSelector', 'menuSelector', 'id', 'menus',
              'additionalData', 'iconPath', 'menuWidth', 'openOnRight',
              'hasImages', 'fadeTime', 'adjustLeft', 'adjustTop', 'opacity',
              'shadow', 'fadeInTime', 'fadeOutTime', 'overflow', 'effect',
              'minZindex']

    rootMenuSelector = 'rootVoices'
    menuSelector = 'menuContainer'
    callback = '/apps/menu'
    iconPath = '/toscawidgets/resources/moksha.apps.menus.widgets/static/images/'
    additionalData = ""
    menus = []
    menuWidth = 200
    openOnRight =  False
    hasImages = True
    fadeTime = 200
    fadeInTime = 100
    fadeOutTime = 100
    adjustLeft = 2
    adjustTop = 10
    opacity = 0.95
    shadow = True
    overflow = 2
    effect = 'fade'
    minZindex = 'auto'


class TW2MokshaMenuBase(twc.Widget):
    template = "mako:moksha.apps.menus.templates.mbmenu"
    resources = [tw2_jquery_mbmenu_min_js, tw2_mbmenu_css_1]
    params = ['callback', 'rootMenuSelector', 'menuSelector', 'id', 'menus',
              'additionalData', 'iconPath', 'menuWidth', 'openOnRight',
              'hasImages', 'fadeTime', 'adjustLeft', 'adjustTop', 'opacity',
              'shadow', 'fadeInTime', 'fadeOutTime', 'overflow', 'effect',
              'minZindex']

    rootMenuSelector = 'rootVoices'
    menuSelector = 'menuContainer'
    callback = '/apps/menu'
    iconPath = '/resources/moksha.apps.menus.widgets/static/images/'
    additionalData = ""
    menus = []
    menuWidth = 200
    openOnRight =  False
    hasImages = True
    fadeTime = 200
    fadeInTime = 100
    fadeOutTime = 100
    adjustLeft = 2
    adjustTop = 10
    opacity = 0.95
    shadow = True
    overflow = 2
    effect = 'fade'
    minZindex = 'auto'


class TW1MokshaMenu(TW1MokshaMenuBase):

    def update_params(self, d):
        super(TW1MokshaMenu, self).update_params(d)

        if not d.id:
            raise Exception("MokshaMenu must have an id!")
        if not d.callback:
            raise Exception("Must provide a callback URL!")

        menus = []
        for menu in d.menus:
            menus.append((menu.lower().replace(' ', ''), menu))
        d.menus = menus

        self.add_call(when_ready(tw.jquery.jQuery('.%s' % d.id).buildMenu({
                'template': d.callback,
                'additionalData': d.additionalData,
                'menuWidth': d.menuWidth,
                'openOnRight': d.openOnRight,
                'rootMenuSelector': ".%s" % d.rootMenuSelector,
                'menuSelector': ".%s" % d.menuSelector,
                'iconPath': d.iconPath,
                'hasImages': d.hasImages,
                'fadeTime': d.fadeTime,
                'fadeInTime': d.fadeInTime,
                'fadeOutTime': d.fadeOutTime,
                'adjustLeft': d.adjustLeft,
                'adjustTop': d.adjustTop,
                'opacity': d.opacity,
                'shadow': d.shadow,
                'minZindex': d.minZindex,
                })))


class TW2MokshaMenu(TW2MokshaMenuBase):

    def prepare(self):
        super(TW2MokshaMenu, self).prepare()

        if not self.id:
            raise Exception("MokshaMenu must have an id!")
        if not self.callback:
            raise Exception("Must provide a callback URL!")

        menus = []
        for menu in self.menus:
            menus.append((menu.lower().replace(' ', ''), menu))
        self.menus = menus

        self.add_call(when_ready(tw2.jquery.jQuery('.%s' % self.id).buildMenu({
                'template': self.callback,
                'additionalData': self.additionalData,
                'menuWidth': self.menuWidth,
                'openOnRight': self.openOnRight,
                'rootMenuSelector': ".%s" % self.rootMenuSelector,
                'menuSelector': ".%s" % self.menuSelector,
                'iconPath': self.iconPath,
                'hasImages': self.hasImages,
                'fadeTime': self.fadeTime,
                'fadeInTime': self.fadeInTime,
                'fadeOutTime': self.fadeOutTime,
                'adjustLeft': self.adjustLeft,
                'adjustTop': self.adjustTop,
                'opacity': self.opacity,
                'shadow': self.shadow,
                'minZindex': self.minZindex,
                })))

class TW1MokshaContextualMenu(TW1MokshaMenuBase):

    def update_params(self, d):
        super(MokshaContextualMenu, self).update_params(d)

        if not d.id:
            raise Exception("MokshaMenu must have an id!")
        if not d.callback:
            raise Exception("Must provide a callback URL!")

        menus = []
        for menu in d.menus:
            menus.append((menu.lower().replace(' ', ''), menu))
        d.menus = menus

        self.add_call(tw.jquery.jQuery(tw.api.js_symbol('document')).buildContextualMenu({
                'template': d.callback,
                'menuWidth': d.menuWidth,
                'rootMenuSelector': ".%s" % d.rootMenuSelector,
                'menuSelector': ".%s" % d.menuSelector,
                'iconPath': d.iconPath,
                'hasImages': d.hasImages,
                'fadeTime': d.fadeTime,
                'fadeInTime': d.fadeInTime,
                'fadeOutTime': d.fadeOutTime,
                'adjustLeft': d.adjustLeft,
                'adjustTop': d.adjustTop,
                'opacity': d.opacity,
                'shadow': d.shadow,
                'effect': d.effect,
                'minZindex': d.minZindex
                }))


class TW2MokshaContextualMenu(TW1MokshaMenuBase):

    def prepare(self):
        super(MokshaContextualMenu, self).prepare()

        if not self.id:
            raise Exception("MokshaMenu must have an id!")
        if not self.callback:
            raise Exception("Must provide a callback URL!")

        menus = []
        for menu in self.menus:
            menus.append((menu.lower().replace(' ', ''), menu))
        self.menus = menus

        self.add_call(tw2.jquery.jQuery(twc.js_symbol('document')).buildContextualMenu({
                'template': self.callback,
                'menuWidth': self.menuWidth,
                'rootMenuSelector': ".%s" % self.rootMenuSelector,
                'menuSelector': ".%s" % self.menuSelector,
                'iconPath': self.iconPath,
                'hasImages': self.hasImages,
                'fadeTime': self.fadeTime,
                'fadeInTime': self.fadeInTime,
                'fadeOutTime': self.fadeOutTime,
                'adjustLeft': self.adjustLeft,
                'adjustTop': self.adjustTop,
                'opacity': self.opacity,
                'shadow': self.shadow,
                'effect': self.effect,
                'minZindex': self.minZindex
                }))


if asbool(config.get('moksha.use_tw2', False)):
    MokshaMenuBase = TW2MokshaMenuBase
    MokshaMenu = TW2MokshaMenu
    MokshaContextualMenu = TW2MokshaContextualMenu
else:
    MokshaMenuBase = TW1MokshaMenuBase
    MokshaMenu = TW1MokshaMenu
    MokshaContextualMenu = TW1MokshaContextualMenu
