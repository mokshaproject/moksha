# This file is part of Moksha.
#
# Moksha is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Moksha is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Moksha.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2008, Red Hat, Inc.
# Authors: Luke Macken <lmacken@redhat.com>

from tg import config
from tw.api import Widget, JSLink, js_callback
from moksha.orbited import orbited_js, orbited_url

stomp_js = JSLink(link=orbited_url + '/static/protocols/stomp/stomp.js')

def stomp_subscribe(topic):
    """ Return a javascript callback that subscribes to a given topic,
        or a list of topics.
    """
    sub = 'stomp.subscribe("%s");'
    if isinstance(topic, list):
        sub = ''.join([sub % t for t in topic])
    else:
        sub = sub % topic
    return js_callback('function(){ %s }' % sub)


class StompWidget(Widget):
    params = ['onopen', 'onerror', 'onerrorframe', 'onclose', 
              'onconnectedframe', 'onmessageframe']
    onopen = onconnectedframe = js_callback('function(){}')
    onerror = js_callback('function(error){ console.log("Error: " + error) }')
    onclose = js_callback('function(c){ console.log("Lost Connection: " + c) }')
    onerrorframe = js_callback('function(f){ console.log("Error: " + f.body) }')
    onmessageframe = js_callback('function(frame){ console.log(frame) }')
    javascript = [orbited_js, stomp_js]
    template = """
      <script>
        Orbited.settings.port = %s;
        Orbited.settings.hostname = '%s';
        document.domain = document.domain;
        TCPSocket = Orbited.TCPSocket;
        stomp = new STOMPClient();
        stomp.onopen = ${onopen};
        stomp.onclose = ${onclose};
        stomp.onerror = ${onerror};
        stomp.onerrorframe = ${onerrorframe};
        stomp.onconnectedframe = ${onconnectedframe};
        // To handle multiple destinations we 
        // would have to check frame.headers.destination.
        stomp.onmessageframe = ${onmessageframe};
        stomp.connect('%s', %s);
      </script>
    """ % (config['orbited_port'], config['orbited_host'],
           config['stomp_host'], config['stomp_port'])
    engine_name = 'mako'


stomp_widget = StompWidget('stomp')
