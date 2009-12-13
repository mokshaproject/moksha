# This file is part of Moksha.
#
# Copyright (C) 2008-2009  Red Hat, Inc.
# Copyright (C) 2008-2009  Luke Macken <lmacken@redhat.com>
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
Moksha HyperTree Widget
=======================

A widget for the Javascript InfoVis Toolkit.

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
.. upstream:: http://thejit.org
.. upstream-license:: BSD
"""

from tw.api import Widget, JSLink, CSSLink
from tw.jquery import jquery_js
from tw.jquery.flot import excanvas_js

jit_js = JSLink(filename='static/jit.js', javascript=[excanvas_js], modname=__name__)
jit_base_css = CSSLink(filename='static/css/base.css', modname=__name__)
jit_hypertree_css = CSSLink(filename='static/css/Hypertree.css', modname=__name__)

class HyperTree(Widget):
    params = {
            'query': 'URL to query for JSON data',
            'root': 'The id of the selected root node',
            'title': 'The title of this graph',
            'description': 'A description of this graph',
            'child_fields': 'JS callback to display child data',
    }
    javascript = [jit_js]
    css = [jquery_js, jit_base_css, jit_hypertree_css]
    template = 'mako:moksha.widgets.mokshajit.templates.hypertree'
    query = '/apps/mokshajit/query'
    root = 0
    child_fields = ['summary', 'year', 'committee', 'assemblySameAs']
