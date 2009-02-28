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

from moksha.api.widgets.orbited import orbited_host, orbited_port, orbited_url

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
    params = callbacks[:] + ['topics']
    onopen = js_callback('function(){}')
    onerror = js_callback('function(error){}')
    onclose = js_callback('function(c){}')
    onerrorframe = js_callback('function(f){}')
    onmessageframe = ''
    onconnectedframe = ''
    engine_name = 'mako'
    template = """
      <script>

        /* Create a new TCPSocket & Stomp client */
        if (typeof stomp == 'undefined') {
            var moksha_callbacks = new Object();

            Orbited.settings.port = %s;
            Orbited.settings.hostname = '%s';
            Orbited.settings.streaming = true;
            document.domain = document.domain;
            TCPSocket = Orbited.TCPSocket;
            stomp = new STOMPClient();
            stomp.onopen = ${onopen};
            stomp.onclose = ${onclose};
            stomp.onerror = ${onerror};
            stomp.onerrorframe = ${onerrorframe};
            stomp.onconnectedframe = function(){ ${onconnectedframe} };
            stomp.onmessageframe = function(f){
                var json = JSON.parse(f.body);
                var dest = f.headers.destination;
                if (moksha_callbacks[dest]) {
                    for (var i = 0; i < moksha_callbacks[dest].length; i++) {
                        moksha_callbacks[dest][i](json, f);
                    }
                }
            };

            stomp.connect('%s', %s, '%s', '%s');

        /* Utilize the existing stomp connection */
        } else {
            ${onconnectedframe}
        }

        %% for topic in topics:
            var topic = "${topic}";
            if (!moksha_callbacks[topic]) {
                moksha_callbacks[topic] = [];
            }
            moksha_callbacks[topic].push(function(json, frame){ ${onmessageframe}; });
        %% endfor

      </script>
    """ % (orbited_port, orbited_host,
           config.get('stomp_host', 'localhost'),
           config.get('stomp_port', 61613),
           config.get('stomp_user', 'guest'),
           config.get('stomp_pass', 'guest'))

    def update_params(self, d):
        super(StompWidget, self).update_params(d)
        d.topics = []
        for callback in self.callbacks:
            if len(moksha.stomp[callback]):
                cbs = ''
                if callback == 'onmessageframe':
                    for topic in moksha.stomp[callback]:
                        d.topics.append(topic)
                        for cb in moksha.stomp[callback][topic]:
                            cbs += "%s;" % str(cb)
                else:
                    for cb in moksha.stomp[callback]:
                        if isinstance(cb, js_callback):
                            cbs += '$(%s);' % str(cb)
                        else:
                            cbs += str(cb)
                if cbs:
                    d[callback] = cbs


stomp_widget = StompWidget('stomp')
