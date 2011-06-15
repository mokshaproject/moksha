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

from tw.jquery.flot import flot_js, excanvas_js, flot_css
from moksha.api.widgets import LiveWidget

class TW1LiveFlotWidget(LiveWidget):
    """ A live graphing widget """
    topic = None
    params = ['id', 'data', 'options', 'height', 'width', 'onmessage']
    onmessage = '$.plot($("#${id}"),json[0]["data"],json[0]["options"])'
    template = '<div id="${id}" style="width:${width};height:${height};" />'
    javascript = [flot_js, excanvas_js]
    css = [flot_css]
    height = '250px'
    width = '390px'
    options = {}
    data = [{}]

if asbool(config.get('moksha.use_tw2', False)):
    raise NotImplementedError(__name__ + " is not ready for tw2")
else:
    LiveFlotWidget = TW1LiveFlotWidget
