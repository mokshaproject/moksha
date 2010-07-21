# This file is part of Moksha.
#
# Copyright (C) 2008-2010  Red Hat, Inc.
# Copyright (C) 2008-2010  Luke Macken <lmacken@redhat.com>
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
Moksha AreaChart Widget
=======================

A widget for the Javascript InfoVis Toolkit.

.. moduleauthor:: Ralph Bean <ralph.bean@gmail.com> 
.. upstream:: http://thejit.org
.. upstream-license:: BSD
"""

from tw.api import Widget, JSLink, CSSLink
from tw.jquery import jquery_js
from tw.jquery.flot import excanvas_js

jit_yc_js = JSLink(filename='static/jit-yc.js', javascript=[excanvas_js], modname=__name__)
jit_base_css = CSSLink(filename='static/css/base.css', modname=__name__)
jit_areachart_css = CSSLink(filename='static/css/Areachart.css', modname=__name__)

class AreaChart(Widget):
    params = {
            'query': 'URL to query for JSON data',
            'title': 'The title of this graph',
            'description': 'A description of this graph',
    }
    javascript = [jit_yc_js]
    css = [jquery_js, jit_base_css, jit_areachart_css]
    template = 'mako:moksha.widgets.mokshajit.templates.areachart'
    query = '/apps/mokshajit/query'
