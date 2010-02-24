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
:mod:`moksha.apps.docs.docs` - Moksha Documentation & Widget Demo App
=====================================================================

This Moksha app integrates your Sphinx documentation with the ToscaWidgets
WidgetBrowser.  This gives you the ability to write your documentation
in reStructuredText, and easily expose it in your application via the 
`/apps/docs` URL.  Since it integrates the ToscaWidgets WidgetBrowser,
this also gives you the ability to create Widget demos and embed them
in your documentation.

.. seealso::

    See the ToscaWidgets WidgetBrowser documentation for more information
    http://toscawidgets.org/documentation/WidgetBrowser/widget_demo_howto.html

.. moduleauthor:: Luke Macken <lmacken@redhat.com>

"""

import os

from tg import config
from tg.controllers import WSGIAppController
from pkg_resources import resource_filename
from moksha.widgetbrowser import WidgetBrowser

os.environ['TW_BROWSER_PREFIX'] = '/apps/docs'

docs = WSGIAppController(
            WidgetBrowser(
                template_dirs=[
                    resource_filename('moksha.widgetbrowser','templates')],
                docs_dir=config.get('docs_dir', 'docs'),
                full_stack=False,
                interactive=False))
