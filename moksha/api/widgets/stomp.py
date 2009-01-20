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

import moksha

from tg import config
from tw.api import Widget, JSLink, js_callback

from moksha.api.widgets.orbited import orbited_host, orbited_port
from moksha.api.widgets.orbited import orbited_js, orbited_url

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
    return sub


class StompWidget(Widget):
    callbacks = ['onopen', 'onerror', 'onerrorframe', 'onclose',
                 'onconnectedframe', 'onmessageframe']
    params = callbacks[:]
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
        stomp.onconnectedframe = function(){ ${onconnectedframe} };
        stomp.onmessageframe = function(frame){
            var json = JSON.parse(frame.body);
            ${onmessageframe}
        };
        stomp.connect('%s', %s, '%s', '%s');
      </script>
    """ % (orbited_port, orbited_host,
           config.get('stomp_host', 'localhost'),
           config.get('stomp_port', 61613),
           config.get('stomp_user', 'guest'),
           config.get('stomp_pass', 'guest'))
    engine_name = 'mako'

    def update_params(self, d):
        super(StompWidget, self).update_params(d)
        for callback in self.callbacks:
            if len(moksha.stomp[callback]):
                cbs = ''
                if callback == 'onmessageframe':
                    for topic in moksha.stomp[callback]:
                        for cb in moksha.stomp[callback][topic]:
                            cbs += """
                              if (frame.headers.destination == "%s") {
                                  %s;
                              }
                            """ % (topic, str(cb))
                else:
                    for cb in moksha.stomp[callback]:
                        cbs += str(cb)
                d[callback] = cbs


stomp_widget = StompWidget('stomp')
