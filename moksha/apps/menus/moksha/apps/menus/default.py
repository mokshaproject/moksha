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
:mod:`moksha.apps.menus.default` - The default Moksha Menu
=========================================================
The default Moksha menu is an example Menu that lists
the installed Applications, Widgets, etc.

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

import moksha
import moksha.utils

from moksha.apps.menus import (
    MokshaMenu, MokshaContextualMenu,
)

class MokshaContextMenu(MokshaContextualMenu):

    @classmethod
    def default(cls, *args, **kw):
        return """
            <a rel="text">
                <img src="/images/moksha-icon.png" style="position:absolute;margin-top:-20px; margin-left:-25px;margin-bottom:10px"/><br/>
            </a>
            <a href="/widget">Documentation</a>
            <a href="https://fedorahosted.org/moksha/report/3">Tickets</a>
            <a href="https://fedorahosted.org/moksha/">Wiki</a>
            <a menu="moksha">Moksha</a>
        """

class MokshaDefaultMenu(MokshaMenu):
    menus = ['Moksha', 'Widgets', 'Fedora']

    @classmethod
    def widgets(cls, *args, **kw):
        menu = """
        <a rel="text">
            <img src="/images/block.png" style="position:absolute;margin-top:-20px; margin-left:-25px;margin-bottom:10px"/>
            <br/>
        </a>
        """
        for id, widget in moksha.utils._widgets.iteritems():
            if not getattr(widget['widget'], 'hidden', False):
                menu += """
                      <a href="#" onclick="
                            $('<div/>').attr('id', '%(id)s_loader').appendTo('body')
                            $.ajax({
                                url: moksha.url('/widgets/%(id)s?chrome=True&live=%(live)s'),
                                success: function(r, s) {
                                    $('#%(id)s_loader')
                                      .append(moksha.filter_resources(r));
                                }
                            });
                            return false;">%(name)s</a>

                """ % {'name': widget['name'], 'id': id, 'live': widget['live']}
        return menu

    @classmethod
    def moksha(cls, *args, **kw):
        return """
        <a rel="text">
            <img src="/images/moksha-icon.png" style="position:absolute;margin-top:-20px; margin-left:-25px;margin-bottom:10px"/><br>
            <br>Moksha is a platform for creating live collaborative web applications.<br><br>
        </a>
        <a rel="separator"></a>
        <a href="http://mokshaproject.net/">Homepage</a>
        <a href="http://mokshaproject.net/apps/docs/">Documentation</a>
        <a href="https://fedorahosted.org/moksha/report/3">Tickets</a>
        <a href="https://fedorahosted.org/moksha/">Wiki</a>
        """

    @classmethod
    def fedora(cls, *args, **kw):
        links = {
                'Wiki': 'http://fedoraproject.org/wiki',
                'Hosted': 'http://fedorahosted.org',
                'Bugzilla': 'http://bugzilla.redhat.com',
                'Community': 'https://admin.fedoraproject.org/community',
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
