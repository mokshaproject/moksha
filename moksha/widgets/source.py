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
:mod:`moksha.widgets.source` -- Source Code Widget
==================================================

The SourceCodeWidget takes a Widget instance, and
returns the source code, in HTML.

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

import moksha.utils
import inspect

from tw.api import Widget
from twisted.python.reflect import namedAny
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

class SourceCodeWidget(Widget):
    params = {
        'widget': 'The name of the widget',
        'module': 'Whether to display the entire module',
        'source': 'Optional source code',
        'code': 'The actual rendered source code',
        'title': ' An optional title for the document',
    }
    template = "${code}"
    engine_name = 'mako'
    container_options = {'width': 625, 'height': 675, 'title': 'View Source',
                         'icon': 'comment.png', 'top': 50, 'left': 300}
    hidden = True
    module = False
    title = None

    def update_params(self, d):
        super(SourceCodeWidget, self).update_params(d)
        title = d.widget.__class__.__name__
        if not d.source:
            try:
                d.widget = moksha.utils.get_widget(d.widget)
            except Exception, e:
                d.widget = namedAny(d.widget)
            if d.module:
                obj = namedAny(d.widget.__module__)
            else:
                obj = d.widget.__class__
            d.source = inspect.getsource(obj)
        html_args = {'full': True}
        if d.title:
            html_args['title'] = d.title
        d.code = highlight(d.source, PythonLexer(), HtmlFormatter(**html_args))

code_widget = SourceCodeWidget('code_widget')
