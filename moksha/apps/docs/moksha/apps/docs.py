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
