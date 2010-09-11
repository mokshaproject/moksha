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
