# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
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
from paste.deploy.converters import asbool

from moksha.api.widgets.orbited import orbited_host, orbited_port, orbited_url
from moksha.api.widgets.orbited import orbited_js
from moksha.lib.helpers import defaultdict
from moksha.widgets.notify import moksha_notify
from moksha.widgets.json import jquery_json_js

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
    javascript = [jquery_json_js]
    params = callbacks[:] + ['topics', 'notify', 'orbited_host',
            'orbited_port', 'orbited_url', 'orbited_js', 'stomp_host',
            'stomp_port', 'stomp_user', 'stomp_pass']
    onopen = js_callback('function(){}')
    onerror = js_callback('function(error){}')
    onclose = js_callback('function(c){}')
    onerrorframe = js_callback('function(f){}')
    onmessageframe = ''
    onconnectedframe = ''

    # Popup notification bubbles on socket state changes
    notify = False

    engine_name = 'mako'
    template = u"""
      <script type="text/javascript">
        if (typeof TCPSocket == 'undefined') {
            moksha_callbacks = new Object();
            moksha_socket_busy = false;
        }

        ## Register our topic callbacks
        % for topic in topics:
            var topic = "${topic}";
            if (!moksha_callbacks[topic]) {
                moksha_callbacks[topic] = [];
            }
            moksha_callbacks[topic].push(function(json, frame) {
                ${onmessageframe[topic]}
            });
        % endfor

        if (typeof TCPSocket == 'undefined') {
            document.domain = document.domain;
            moksha_socket_busy = true;
            $.getScript("${orbited_url}/static/Orbited.js", function(){
                Orbited.settings.port = ${orbited_port};
                Orbited.settings.hostname = '${orbited_host}';
                Orbited.settings.streaming = true;
                TCPSocket = Orbited.TCPSocket;
                $.getScript("${orbited_url}/static/protocols/stomp/stomp.js", function(){
                    ## Create a new TCPSocket & Stomp client
                    stomp = new STOMPClient();
                    stomp.onopen = ${onopen};
                    stomp.onclose = ${onclose};
                    stomp.onerror = ${onerror};
                    stomp.onerrorframe = ${onerrorframe};
                    stomp.onconnectedframe = function(){ 
                        moksha_socket_busy = false;
                        $('body').triggerHandler('moksha.socket_ready');
                        ${onconnectedframe}
                    };
                    stomp.onmessageframe = function(f){
                        var dest = f.headers.destination;
                        var json = null;
                        try {
                            var json = $.secureEvalJSON(f.body);
                        } catch(err) {
                            moksha.error("Unable to decode JSON message body");
                            moksha.debug(msg);
                        }
                        if (moksha_callbacks[dest]) {
                            for (var i=0; i < moksha_callbacks[dest].length; i++) {
                                moksha_callbacks[dest][i](json, f);
                            }
                        }
                    };

                    stomp.connect('${stomp_host}', ${stomp_port},
                                  '${stomp_user}', '${stomp_pass}');
                });
            });

        } else {
            ## Utilize the existing stomp connection
            if (moksha_socket_busy) {
                $('body').bind('moksha.socket_ready', function() {
                    ${onconnectedframe}
                });
            } else {
                ${onconnectedframe}
            }
        }

        window.onbeforeunload = function() {
            if (typeof stomp != 'undefined') {
                stomp.reset();
            }
        }

        % if notify:
            $.jGrowl.defaults.position = 'bottom-right';
        % endif
      </script>
    """
    hidden = True

    def __init__(self, *args, **kw):
        self.notify = asbool(config.get('moksha.socket.notify', False))
        self.orbited_host = config.get('orbited_host', 'localhost')
        self.orbited_port = config.get('orbited_port', 9000)
        self.orbited_scheme = config.get('orbited_scheme', 'http')
        self.orbited_url = '%s://%s:%s' % (self.orbited_scheme,
                self.orbited_host, self.orbited_port)
        self.orbited_js = JSLink(link=self.orbited_url + '/static/Orbited.js')
        self.stomp_host = config.get('stomp_host', 'localhost')
        self.stomp_port = config.get('stomp_port', 61613)
        self.stomp_user = config.get('stomp_user', 'guest')
        self.stomp_pass = config.get('stomp_pass', 'guest')
        super(StompWidget, self).__init__(*args, **kw)

    def update_params(self, d):
        super(StompWidget, self).update_params(d)
        d.topics = []
        d.onmessageframe = defaultdict(str) # {topic: 'js callbacks'}
        for callback in self.callbacks:
            if len(moksha.livewidgets[callback]):
                cbs = ''
                if callback == 'onmessageframe':
                    for topic in moksha.livewidgets[callback]:
                        d.topics.append(topic)
                        for cb in moksha.livewidgets[callback][topic]:
                            d.onmessageframe[topic] += '%s;' % str(cb)
                else:
                    for cb in moksha.livewidgets[callback]:
                        if isinstance(cb, (js_callback, js_function)):
                            cbs += '$(%s);' % str(cb)
                        else:
                            cbs += str(cb)
                if cbs:
                    d[callback] = cbs

        if d.notify:
            moksha_notify.register_resources()
            d.onopen = js_callback('function() { $.jGrowl("Moksha live socket connected") }')
            d.onerror = js_callback('function(error) { $.jGrowl("Moksha Live Socket Error: " + error) }')
            d.onerrorframe = js_callback('function(f) { $.jGrowl("Error frame received from Moksha Socket: " + f) }')
            d.onclose = js_callback('function(c) { $.jGrowl("Moksha Socket Closed") }')
