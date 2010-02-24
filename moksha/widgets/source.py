# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
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
:mod:`moksha.widgets.source` -- Source Code Widget
==================================================

The SourceCodeWidget takes a Widget instance, and
returns the source code, in HTML.

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

import moksha
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
                d.widget = moksha.get_widget(d.widget)
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
