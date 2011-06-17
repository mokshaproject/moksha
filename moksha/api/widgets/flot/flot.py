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

from tg import config
from paste.deploy.converters import asbool

import tw.jquery.flot
import tw2.jqplugins.flot
import tw2.excanvas

from moksha.api.widgets import TW1LiveWidget, TW2LiveWidget


class TW1LiveFlotWidget(TW1LiveWidget):
    """ A live graphing widget """
    topic = None
    params = ['id', 'data', 'options', 'height', 'width', 'onmessage']
    onmessage = '$.plot($("#${id}"),json[0]["data"],json[0]["options"])'
    template = "mako:moksha.api.widgets.flot.templates.flot"
    javascript = [tw.jquery.flot.flot_js, tw.jquery.flot.excanvas_js]
    css = [tw.jquery.flot.flot_css]
    height = '250px'
    width = '390px'
    options = {}
    data = [{}]


class TW2LiveFlotWidget(TW2LiveWidget):
    """ A live graphing widget """
    topic = None
    params = ['id', 'data', 'options', 'height', 'width', 'onmessage']
    onmessage = '$.plot($("#${id}"),json[0]["data"],json[0]["options"])'
    template = "mako:moksha.api.widgets.flot.templates.flot"
    resources = [
        tw2.jqplugins.flot.flot_js,
        tw2.excanvas.excanvas_js
    ]
    height = '250px'
    width = '390px'
    options = {}
    data = [{}]


if asbool(config.get('moksha.use_tw2', False)):
    LiveFlotWidget = TW2LiveFlotWidget
else:
    LiveFlotWidget = TW1LiveFlotWidget
