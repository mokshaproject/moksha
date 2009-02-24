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

"""
:mod:`moksha.api.menus.default` - The default Moksha Menu
=========================================================
The default Moksha menu is an example Menu that lists
the installed Applications, Widgets, etc.

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

import moksha
from moksha.api.menus import MokshaMenu, MokshaContextualMenu

class MokshaContextMenu(MokshaContextualMenu):

    def default(self, *args, **kw):
        return """
            <a rel="text">
                <img src="/images/moksha-icon.png" style="position:absolute;margin-top:-20px; margin-left:-25px;margin-bottom:10px"/><br/>
            </a>
            <a href="/widget">Documentation</a>
            <a href="https://fedorahosted.org/moksha/report/3">Tickets</a>
            <a href="https://fedorahosted.org/moksha/">Wiki</a>
        """

class MokshaDefaultMenu(MokshaMenu):
    menus = ['Moksha', 'Widgets', 'Fedora']
    #menus = ['Moksha', 'Applications', 'Widgets', 'Fedora']

    def applications(self, *args, **kw):
        menu = """
        <a rel="text">
            <img src="/images/gears.png" style="position:absolute;margin-top:-20px; margin-left:-25px;margin-bottom:10px"/><br>
        </a>
        """
        for app in moksha.apps:
            menu += '<a href="#" disabled=true>%s</a>' % moksha.apps[app]['name']
        return menu

    def widgets(self, *args, **kw):
        menu = """
        <a rel="text">
            <img src="/images/block.png" style="position:absolute;margin-top:-20px; margin-left:-25px;margin-bottom:10px"/>
            <br/>
        </a>
        """
        for id, widget in moksha._widgets.iteritems():
            if not getattr(widget['widget'], 'hidden', False):
                menu += """
                    <a href="#" onclick="$('<div/>').appendTo('#footer').load('/widgets/%s?chrome=True'); return false;">%s</a>
                """ % (id, widget['name'])
        return menu

    def moksha(self, *args, **kw):
        return """
        <a rel="text">
            <img src="/images/moksha-icon.png" style="position:absolute;margin-top:-20px; margin-left:-25px;margin-bottom:10px"/><br>
            <br>Moksha is a platform for creating live collaborative web applications.<br><br>
        </a>
        <a rel="separator"></a>
        <a href="/docs/">Documentation</a>
        <a href="https://fedorahosted.org/moksha/report/3">Tickets</a>
        <a href="https://fedorahosted.org/moksha/">Wiki</a>
        """

    def fedora(self, *args, **kw):
        links = {
                'Wiki': 'http://fedoraproject.org/wiki',
                'Hosted': 'http://fedorahosted.org',
                'Bugzilla': 'http://bugzilla.redhat.com',
                'Elections': 'https://admin.fedoraproject.org/voting',
                'Translations': 'http://translate.fedoraproject.org',
                'Build System': 'http://koji.fedoraproject.org',
                'Update System': 'http://bodhi.fedoraproject.org',
                'Package Database': 'http://admin.fedoraproject.org/pkgdb',
                'Account System': 'http://admin.fedoraproject.org/accounts',
                'Hardware Database': 'http://smolts.org',
        }
        menu = """
            <a rel="text">
                <img src="/images/fedora-icon.png" style="position:absolute;margin-top:-20px; margin-left:-25px;margin-bottom:10px"/><br>
            </a>
            <a rel="separator"></a>
        """
        for title, url in links.items():
            menu += '<a href="%s" target="_blank">%s</a>' % (url, title)
        return menu
