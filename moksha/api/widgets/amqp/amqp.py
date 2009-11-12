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
"""
:mod:`moksha.api.widgets.amqp` - An AMQP driven live Moksha socket
==================================================================

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

import moksha

from tg import config
from tw.api import Widget, JSLink, js_callback, js_function
from paste.deploy.converters import asbool

from moksha.api.widgets.orbited import orbited_host, orbited_port, orbited_url
from moksha.api.widgets.orbited import orbited_js
from moksha.lib.helpers import defaultdict
from moksha.widgets.notify import moksha_notify
from moksha.widgets.json import jquery_json_js

from widgets import kamaloka_qpid_js

def amqp_subscribe(topic):
    """ Return a javascript callback that subscribes to a given topic,
        or a list of topics.
    """
    sub = """
        moksha_amqp_queue.subscribe({
            exchange: 'amq.topic',
            remote_queue: moksha_amqp_remote_queue,
            binding_key: '%s',
            callback: moksha_amqp_on_message,
        });
    """
    if isinstance(topic, list):
        sub = ''.join([sub % t for t in topic])
    else:
        sub = sub % topic
    return sub


def amqp_unsubscribe(topic):
    """ Return a javascript callback that unsubscribes to a given topic,
        or a list of topics.
    """
    return ""
    # TODO:
    #sub = "stomp.unsubscribe('%s');"
    #if isinstance(topic, list):
    #    sub = ''.join([sub % t for t in topic])
    #else:
    #    sub = sub % topic
    #return sub


class AMQPSocket(Widget):
    callbacks = ['onconnectedframe', 'onmessageframe']
    javascript = [jquery_json_js, kamaloka_qpid_js]
    params = callbacks[:] + ['topics', 'notify', 'orbited_host',
            'orbited_port', 'orbited_url', 'orbited_js', 'amqp_broker_host',
            'amqp_broker_port', 'amqp_broker_user', 'amqp_broker_pass',
            'send_hook', 'recieve_hook']
    onconnectedframe = ''
    onmessageframe = ''
    send_hook = ''
    recieve_hook = ''

    engine_name = 'mako'
    template = u"""
      <script type="text/javascript">

        if (typeof moksha_amqp_conn == 'undefined') {
            moksha_callbacks = new Object();
            moksha_amqp_remote_queue = null;
            moksha_amqp_queue = null;
            moksha_amqp_on_message = function(msg) {
                console.log('moksha_amqp_on_message(' + msg.body + ')');
                var dest = msg.header.delivery_properties.routing_key;
                var json = $.secureEvalJSON(msg.body);
                if (moksha_callbacks[dest]) {
                    for (var i=0; i < moksha_callbacks[dest].length; i++) {
                        moksha_callbacks[dest][i](json, msg);
                    }
                }
            }
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

        ## Create a new AMQP client
        if (typeof moksha_amqp_conn == 'undefined') {
            document.domain = document.domain;
            $.getScript("${orbited_url}/static/Orbited.js", function() {
                moksha.debug('Got Orbited');
                Orbited.settings.port = ${orbited_port};
                Orbited.settings.hostname = '${orbited_host}';
                Orbited.settings.streaming = true;
                moksha_amqp_conn = new amqp.Connection({
                    host: '${amqp_broker_host}',
                    port: ${amqp_broker_port},
                    username: '${amqp_broker_user}',
                    password: '${amqp_broker_pass}',
                    send_hook: function(data, frame) { ${send_hook} },
                    recive_hook: function(data, frame) { ${recieve_hook} }
                });
                moksha_amqp_conn.start();

                moksha_amqp_session = moksha_amqp_conn.create_session(
                    'moksha_socket_' + (new Date().getTime() + Math.random()));

                moksha_amqp_remote_queue = 'moksha_socket_queue_' +
                        moksha_amqp_session.name;

                moksha_amqp_session.Queue('declare', {
                        queue: moksha_amqp_remote_queue
                });
                moksha_amqp_queue = moksha_amqp_session.create_local_queue({
                        name: 'local_queue'
                });

                ${onconnectedframe}

                moksha_amqp_queue.start();

            });

        } else {
            ## Utilize the existing AMQP connection
            ${onconnectedframe}
        }

      </script>
    """
    hidden = True

    def __init__(self, *args, **kw):
        self.notify = asbool(config.get('moksha.socket.notify', False))
        self.orbited_host = config.get('orbited_host', 'localhost')
        self.orbited_port = config.get('orbited_port', 9000)
        self.orbited_url = 'http://%s:%s' % (self.orbited_host, self.orbited_port)
        self.orbited_js = JSLink(link=self.orbited_url + '/static/Orbited.js')
        self.amqp_broker_host = config.get('amqp_broker_host', 'localhost')
        self.amqp_broker_port = config.get('amqp_broker_port', 5672)
        self.amqp_broker_user = config.get('amqp_broker_user', 'guest')
        self.amqp_broker_pass = config.get('amqp_broker_pass', 'guest')
        super(AMQPSocket, self).__init__(*args, **kw)

    def update_params(self, d):
        super(AMQPSocket, self).update_params(d)
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
