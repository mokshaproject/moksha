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

import tw2.core as twc
import tw2.jquery

orbited_host = twc.Required
orbited_port = twc.Required
orbited_scheme = twc.Required


class OrbitedWidget(twc.Widget):
    onopen = twc.Param("A javascript callback for when the connection opens",
                       default=twc.JSSymbol(src="function(){}"))
    onread = twc.Param("A javascript callback for when new data is read",
                       default=twc.JSSymbol(src="function(){}"))
    onclose = twc.Param("A javascript callback for when the connection closes",
                        default=twc.JSSymbol(src="function(){}"))
    orbited_port = twc.Param("Orbited port", default=orbited_port)
    orbited_host = twc.Param("Orbited host", default=orbited_host)
    orbited_scheme = twc.Param("Orbited scheme", default=orbited_scheme)
    template = "mako:moksha.wsgi.widgets.api.orbited.templates.orbited"

    def prepare(self):
        orbited_url = '%s://%s:%s' % (
            self.orbited_scheme,
            self.orbited_host,
            self.orbited_port,
        )
        orbited_js = twc.JSLink(link=orbited_url + '/static/Orbited.js',
                                resources=[tw2.jquery.jquery_js])
        self.resources.append(orbited_js)
