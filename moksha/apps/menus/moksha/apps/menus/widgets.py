## -*- coding: utf-8 -*-
# This file is part of Moksha.
# Copyright (C) 2008-2009  Red Hat, Inc.
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

from tw.api import JSLink, Widget, CSSLink, js_symbol
from tw.jquery import jquery_js, jQuery

from moksha.lib.helpers import when_ready

modname = __name__

jquery_mbmenu_js = JSLink(modname=modname,
                          filename='static/mbMenu.js',
                          javascript=[jquery_js])

jquery_mbmenu_min_js = JSLink(modname=modname,
                              filename='static/mbMenu.min.js',
                              javascript=[jquery_js])


class MokshaMenuBase(Widget):
    template = "mako:moksha.apps.menus.templates.mbmenu"
    javascript = [jquery_mbmenu_min_js]
    css = [CSSLink(modname=modname, filename='static/css/menu1.css',
                   media='screen')]
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


class MokshaMenu(MokshaMenuBase):

    def update_params(self, d):
        super(MokshaMenu, self).update_params(d)

        if not d.id:
            raise Exception("MokshaMenu must have an id!")
        if not d.callback:
            raise Exception("Must provide a callback URL!")

        menus = []
        for menu in d.menus:
            menus.append((menu.lower().replace(' ', ''), menu))
        d.menus = menus

        self.add_call(when_ready(jQuery('.%s' % d.id).buildMenu({
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


class MokshaContextualMenu(MokshaMenuBase):

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

        self.add_call(jQuery(js_symbol('document')).buildContextualMenu({
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
