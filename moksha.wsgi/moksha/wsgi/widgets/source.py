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
:mod:`moksha.wsgi.widgets.source` -- Source Code Widget
==================================================

The SourceCodeWidget takes a Widget instance, and
returns the source code, in HTML.

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

import moksha.common.utils
import inspect

import tw2.core as twc

from moksha.common.lib.reflect import namedAny
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

class SourceCodeWidget(twc.Widget):
    widget = twc.Param("The name of the widget")
    module = twc.Param("Whether to display the entire module")
    source = twc.Param("Optional source code", default=None)
    code = twc.Param("The actual rendered source code")
    title = twc.Param("An optional title for the document", default='')

    template = "mako:moksha.wsgi.widgets.templates.source"

    container_options = {'width': 625, 'height': 675, 'title': 'View Source',
                         'icon': 'comment.png', 'top': 50, 'left': 300}
    hidden = True

    def prepare(self):
        super(SourceCodeWidget, self).prepare()
        title = self.widget.__class__.__name__
        if not self.source:
            try:
                self.widget = moksha.utils.get_widget(self.widget)
            except Exception, e:
                self.widget = namedAny(self.widget)
            if self.module:
                obj = namedAny(self.widget.__module__)
            else:
                obj = self.widget.__class__
            self.source = inspect.getsource(obj)
        html_args = {'full': True}
        if self.title:
            html_args['title'] = self.title
        self.code = highlight(self.source, PythonLexer(),
                              HtmlFormatter(**html_args))

code_widget = SourceCodeWidget(id='code_widget')
