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

import tw2.jqplugins.flot
import tw2.excanvas

from moksha.wsgi.widgets.api import LiveWidget


class LiveFlotWidget(LiveWidget):
    """ A live graphing widget """
    topic = None
    params = ['id', 'data', 'options', 'height', 'width', 'onmessage']
    onmessage = '$.plot($("#${id}"),json[0]["data"],json[0]["options"])'
    template = "mako:moksha.wsgi.widgets.api.flot.templates.flot"
    resources = [
        tw2.jqplugins.flot.flot_js,
        tw2.excanvas.excanvas_js
    ]
    height = '250px'
    width = '390px'
    options = {}
    data = [{}]
