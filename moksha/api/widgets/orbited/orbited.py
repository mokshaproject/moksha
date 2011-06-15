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

orbited_host = config.get('orbited_host', 'localhost')
orbited_port = config.get('orbited_port', 9000)
orbited_url = '%s://%s:%s' % (config.get('orbited_scheme', 'http'), orbited_host, orbited_port)

import tw.api
tw1_orbited_js = tw.api.JSLink(link=orbited_url + '/static/Orbited.js')

class TW1OrbitedWidget(tw.api.Widget):
    params = {
        'onopen': 'A javascript callback for when the connection opens',
        'onread': 'A javascript callback for when new data is read',
        'onclose': 'A javascript callback for when the connection closes',
    }
    onopen = onread = onclose = tw.api.js_callback('function(){}')
    javascript = [tw1_orbited_js]
    template = """
        <script type="text/javascript">
            Orbited.settings.port = %(port)s
            Orbited.settings.hostname = '%(host)s'
            document.domain = document.domain
            TCPSocket = Orbited.TCPSocket
            connect = function() {
                conn = new TCPSocket()
                conn.onread = ${onread}
                conn.onopen = ${onopen}
                conn.onclose = ${onclose}
                conn.open('%(host)s', %(port)s)
            }
            $(document).ready(function() {
                connect()
            })
        </script>
    """ % {'port': orbited_port, 'host': orbited_host}

if asbool(config.get('moksha.use_tw2', False)):
    raise NotImplementedError(__name__ + " is not ready for tw2")
else:
    OrbitedWidget = TW1OrbitedWidget
    orbited_js = tw1_orbited_js
