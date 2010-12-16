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
#
# Authors: Luke Macken <lmacken@redhat.com>

import moksha
import logging

from urllib import urlencode
from tg import expose, tmpl_context, flash, redirect, validate
from formencode import validators

from moksha.exc import WidgetNotFound
from moksha.lib.base import Controller
from moksha.widgets.source import code_widget
from moksha.widgets.container import container
from moksha.widgets.iframe import iframe_widget

log = logging.getLogger(__name__)

class WidgetController(Controller):

    @expose('mako:moksha.templates.widget')
    @validate({
        'live': validators.StringBool(),
        'chrome': validators.StringBool(),
        'source': validators.UnicodeString(),
        'module': validators.StringBool(),
        'iframe': validators.StringBool(),
    })
    def _default(self, widget, chrome=False, live=False, source=False,
                module=False, iframe=False, **kw):
        """ Display a single widget.

        :chrome: Display in a Moksha Container
        :live: Inject a socket for live widgets
        :source: Display the source code for this widget
        """
        options = {}
        options.update(kw)
        w = moksha._widgets.get(widget)
        if not w:
            raise WidgetNotFound(widget)
        if (chrome and getattr(w['widget'], 'visible', True)) or source:
            tmpl_context.widget = container
            options['content'] = w['widget']
            options['content_args'] = kw
            options['title'] =  w['name']
            options['id'] = widget + '_container'

            # Allow widgets to specify container options
            container_options = getattr(w['widget'], 'container_options', None)
            if container_options:
                options.update(container_options)
        else:
            tmpl_context.widget = w['widget']
        if live:
            tmpl_context.moksha_socket = moksha.get_widget('moksha_socket')
        if source:
            options['content'] = iframe_widget(url='/widgets/code/' + source +
                                               '?module=%s' % module,
                                               height='425px')
            options['id'] += source + '_source'
            options['view_source'] = False
        if iframe:
            options['content'] = iframe_widget(url='/widgets/' + widget +
                                               '?' + urlencode(kw),
                                               height='425px')
            options['view_source'] = False
        return dict(options=options)

    @expose('mako:moksha.templates.widget')
    @validate({
        'module': validators.StringBool(),
    })
    def code(self, widget, module=False):
        tmpl_context.widget = code_widget
        return dict(options={'widget': widget, 'module': module})
