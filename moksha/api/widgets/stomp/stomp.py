# This file is part of Moksha.
# Copyright (C) 2008-2009  Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors: Luke Macken <lmacken@redhat.com>

import moksha

from tg import config
from tw.api import Widget, JSLink, js_callback, js_function

from moksha.api.widgets.orbited import orbited_host, orbited_port, orbited_url
from moksha.api.widgets.orbited import orbited_js
from moksha.lib.helpers import defaultdict

stomp_js = JSLink(link=orbited_url + '/static/protocols/stomp/stomp.js')

def stomp_subscribe(topic):
    """ Return a javascript callback that subscribes to a given topic,
        or a list of topics.
    """
    sub = "stomp.subscribe('%s');"
    if isinstance(topic, list):
        sub = ''.join([sub % t for t in topic])
    else:
        sub = sub % topic
    return sub


def stomp_unsubscribe(topic):
    """ Return a javascript callback that unsubscribes to a given topic,
        or a list of topics.
    """
    sub = "stomp.unsubscribe('%s');"
    if isinstance(topic, list):
        sub = ''.join([sub % t for t in topic])
    else:
        sub = sub % topic
    return sub


class StompWidget(Widget):
    callbacks = ['onopen', 'onerror', 'onerrorframe', 'onclose',
                 'onconnectedframe', 'onmessageframe']
    #javascript = [stomp_js, orbited_js]
    #children = [stomp_js, orbited_js]
    params = callbacks[:] + ['topics']
    onopen = js_callback('function(){}')
    onerror = js_callback('function(error){}')
    onclose = js_callback('function(c){}')
    onerrorframe = js_callback('function(f){}')
    onmessageframe = ''
    onconnectedframe = ''
    engine_name = 'mako'
    template = u"""
      <script type="text/javascript">
        if (typeof TCPSocket == 'undefined') {
            moksha_callbacks = new Object();
        }

        ## Register our topic callbacks
        %% for topic in topics:
            var topic = "${topic}";
            if (!moksha_callbacks[topic]) {
                moksha_callbacks[topic] = [];
            }
            moksha_callbacks[topic].push(function(json, frame) {
                ${onmessageframe[topic]};
            });
        %% endfor

        if (typeof TCPSocket == 'undefined') {
            document.domain = document.domain;
            $.getScript("%(orbited_url)s/static/Orbited.js", function(){
                Orbited.settings.port = %(orbited_port)s;
                Orbited.settings.hostname = '%(orbited_host)s';
                Orbited.settings.streaming = true;
                TCPSocket = Orbited.TCPSocket;
                $.getScript("%(orbited_url)s/static/protocols/stomp/stomp.js", function(){
                    ## Create a new TCPSocket & Stomp client
                    stomp = new STOMPClient();
                    stomp.onopen = ${onopen};
                    stomp.onclose = ${onclose};
                    stomp.onerror = ${onerror};
                    stomp.onerrorframe = ${onerrorframe};
                    stomp.onconnectedframe = function(){ ${onconnectedframe} };
                    stomp.onmessageframe = function(f){
                        var dest = f.headers.destination;
                        var json = JSON.parse(f.body);
                        if (moksha_callbacks[dest]) {
                            for (var i=0; i < moksha_callbacks[dest].length; i++) {
                                moksha_callbacks[dest][i](json, f);
                            }
                        }
                    };

                    stomp.connect('%(stomp_host)s', %(stomp_port)s,
                                  '%(stomp_user)s', '%(stomp_pass)s');

                });
            });

        } else {
            ## Utilize the existing stomp connection
            ${onconnectedframe}
        }

        window.onbeforeunload = function() {
            if (typeof stomp != 'undefined') {
                stomp.reset();
            }
        }

      </script>
    """ % {
            'orbited_url': orbited_url,
            'orbited_port': orbited_port,
            'orbited_host': orbited_host,
            'stomp_host': config.get('stomp_host', 'localhost'),
            'stomp_port': config.get('stomp_port', 61613),
            'stomp_user': config.get('stomp_user', 'guest'),
            'stomp_pass': config.get('stomp_pass', 'guest'),
            }

    def update_params(self, d):
        super(StompWidget, self).update_params(d)
        d.topics = []
        d.onmessageframe = defaultdict(str) # {topic: 'js callbacks'}
        for callback in self.callbacks:
            if len(moksha.stomp[callback]):
                cbs = ''
                if callback == 'onmessageframe':
                    for topic in moksha.stomp[callback]:
                        d.topics.append(topic)
                        for cb in moksha.stomp[callback][topic]:
                            d.onmessageframe[topic] += '%s;' % str(cb)
                else:
                    for cb in moksha.stomp[callback]:
                        if isinstance(cb, (js_callback, js_function)):
                            cbs += '$(%s);' % str(cb)
                        else:
                            cbs += str(cb)
                if cbs:
                    d[callback] = cbs


stomp_widget = StompWidget('stomp')
