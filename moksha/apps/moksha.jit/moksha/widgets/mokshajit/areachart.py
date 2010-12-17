# This file is part of Moksha.
#
# Copyright (C) 2008-2010  Red Hat, Inc.
# Copyright (C) 2008-2010  Luke Macken <lmacken@redhat.com>
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
