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
# Copyright 2009, Moksha, Inc.

"""
:mod:`moksha.widgets.mindmap` -- A mind map widget
==================================================

.. widgetbrowser:: moksha.widgets.mindmap.MindMapDemo
   :tabs: demo, source
   :size: x-large

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

from tw.api import Widget, JSLink, CSSLink
from tw.jquery.flot import excanvas_js
from tw.mootools.base import moo_core_js_compressed, moo_more_js_compressed
from webhelpers.html import HTML

class MindMap(Widget):
    javascript = [JSLink(filename='static/js/js-mindmap.js', modname=__name__,
                         javascript=[moo_core_js_compressed,
                                     moo_more_js_compressed,
                                     excanvas_js],
                         location='bodybottom')]
    css = [CSSLink(filename='static/css/js-mindmap.css', modname=__name__)]
    template = """
        <script>jQuery.noConflict();</script>
        <div id="debug1"></div>
        <canvas id="cv" width="900" height="600" style="position:absolute;left:0;top:0;"></canvas>
        <div id="js-mindmap">${root} ${tree}</div>
    """
    engine_name = 'mako'
    params = ['data', 'root', 'tree']

    def update_params(self, d):
        super(MindMap, self).update_params(d)
        d.tree = self.traverse_branch(d.data)

    def traverse_branch(self, branch):
        mindmap = "<ul>"
        for value in branch:
            if isinstance(value, (list, tuple)):
                if len(value) != 2:
                    mindmap += self.traverse_branch(value)
                    continue
            mindmap += '<li><a href="%s">%s</a></li>' % (value[1], value[0])
        mindmap += "</ul>"
        return mindmap


class MindMapDemo(MindMap):
    id = 'MindMapDemo'
    root = HTML.tag('a', href='http://moksha.fedorahosted.org', c='Moksha')
    data = [('Wiki', 'http://fedorahosted.org/moksha'),
            ('Tickets', 'http://fedorahosted.org/moksha/tickets'),
            ('Demo', 'http://bit.ly/RICf'),
            ('Timeline', 'https://fedorahosted.org/moksha/timeline'),
            ('Roadmap', 'https://fedorahosted.org/moksha/roadmap'),
            ('Mailing List', 'https://fedorahosted.org/mailman/listinfo/moksha'),
            ]
