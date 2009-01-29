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

""" A powerful dynamic Menu """

from tw.api import JSLink, Widget, CSSLink
from tw.jquery import jquery_js, jQuery

modname = __name__

jquery_mbmenu_js = JSLink(modname=modname,
                          filename='static/mbMenu.js',
                          javascript=[jquery_js])

jquery_mbmenu_min_js = JSLink(modname=modname,
                              filename='static/mbMenu.min.js',
                              javascript=[jquery_js])


class MokshaMenu(Widget):
    template = "mako:moksha.api.menus.templates.mbmenu"
    javascript = [jquery_mbmenu_min_js]
    css = [CSSLink(modname=modname, filename='static/css/menu.css',
                   media='screen'),
           CSSLink(modname=modname, filename='static/css/menu1.css',
                   media='screen')]
    params = ['callback', 'rootMenuSelector', 'menuSelector', 'id', 'menus',
              'additionalData', 'iconPath', 'menuWidth', 'openOnRight',
              'hasImages', 'fadeTime', 'adjustLeft', 'adjustTop', 'opacity',
              'shadow', 'fadeInTime', 'fadeOutTime']


    rootMenuSelector = 'rootVoices'
    menuSelector = 'menuContainer'
    callback = '/appz/menu'
    iconPath = '/toscawidgets/resources/moksha.api.menus.widgets/static/images/'
    additionalData = ""
    menus = []
    menuWidth = 200
    openOnRight =  False
    hasImages = False
    fadeTime = 200
    fadeInTime = 100
    fadeOutTime = 100
    adjustLeft = 2
    adjustTop = 10
    opacity = 0.95
    shadow = True

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

        self.add_call(jQuery('.%s' % d.id).buildMenu({
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
            }))
