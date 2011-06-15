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
:mod:`moksha.widgets.iframe` - An IFrame Widget
===============================================

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

from tg import config
from paste.deploy.converters import asbool

from tw.api import Widget

class TW1IFrameWidget(Widget):
    params = ['id', 'url', 'title', 'height', 'width']
    template = """
      <h1>${title}</h1>
      <iframe id="${id}" src="${url}" width="${width}" height="${height}">
        <p>Your browser does not support iframes.</p>
      </iframe>
    """
    title = ''
    height = width = '100%'
    engine_name = 'mako'

if asbool(config.get('moksha.use_tw2', False)):
    raise NotImplementedError(__name__ + " is not ready for tw2")
else:
    IFrameWidget = TW1IFrameWidget

iframe_widget = IFrameWidget('iframe_widget')
