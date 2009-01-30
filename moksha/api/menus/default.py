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
from moksha.api.menus import MokshaMenu

# @@ set widget 'Names' somewhere...  __name__ ?
# done, now do it with menus and apps..

"""
The default Moksha Menu.

Moksha Menu API
---------------

Howto..
    - define a MokshaMenu class with a `menu`, which is a list of top-level
      menu entries.
    - for dynamic menus, when selected, the corresponding method will be
      called on your menu object.  For example, if your menu is named
      'My Menu', then the 'mymenu' method will be executed when the menu
      is selcted.

Ideas
- Do we want each menu to point to a controller for handling the dynamic
  menu requests?

    benefits... we keep logic in these methods, and html elsewhere
                -we can use Mako...
                -@expose API ?
    drawbacks..
        - each menu/submenu needs to be stored in it's own template file
        - running mako == overhead

TODO:
    - test submenu's
    - test non-dynamic menus
    - make themable
"""

class MokshaDefaultMenu(MokshaMenu):
    menus = ['Moksha', 'Applications', 'Widgets']

    def applications(self, *args, **kw):
        menu = ""
        for app in moksha.apps:
            menu += '<a href="#">%s</a>' % moksha.apps[app]['name']
        return menu

    def widgets(self, *args, **kw):
        menu = ""
        for id, widget in moksha._widgets.iteritems():
            menu += """
                <a href="#" onclick="$('<div/>').appendTo('#content').load('/widgets/%s'); return false;">%s</a>
            """ % (id, widget['name'])
        return menu

    def moksha(self, *args, **kw):
        return """
        <a rel="text">
            <img src="/images/moksha-icon.png" style="position:absolute;margin-top:-20px; margin-left:-25px;margin-bottom:10px"/><br>
            <br>Moksha is a platform for creating live collaborative web applications.<br><br>
        </a>
        <a rel="separator"></a>
        <a href="http://moksha.fedorahosted.org" target="_blank">Moksha Homepage</a>
        <a href="http://lmacken.fedorapeople.org/moksha/">Documentation</a>
        <a href="https://fedorahosted.org/moksha/report/3">Tickets</a>
        <a href="https://fedorahosted.org/moksha/">Wiki</a>
        """
