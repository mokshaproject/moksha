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
"""
:mod:`moksha.api.widgets.amqp` - An AMQP driven live Moksha socket
==================================================================

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

import moksha
import moksha.utils

from tg import config
from paste.deploy.converters import asbool

from tw.api import Widget, JSLink, js_callback, js_function

from moksha.api.widgets.orbited import orbited_host, orbited_port, orbited_url
from moksha.api.widgets.orbited import orbited_js
from moksha.lib.helpers import defaultdict, listify
from moksha.widgets.moksha_js import moksha_js
from moksha.widgets.notify import moksha_notify
from moksha.widgets.json import jquery_json_js

from widgets import kamaloka_qpid_js

def amqp_subscribe(topic):
    """ Return a javascript callback that subscribes to a given topic,
        or a list of topics.
    """
    sub = """
        moksha.debug("Subscribing to the '%(topic)s' topic");
        moksha_amqp_queue.subscribe({
            exchange: 'amq.topic',
            remote_queue: moksha_amqp_remote_queue,
            binding_key: '%(topic)s',
            callback: moksha_amqp_on_message,
        });
    """
    return ''.join([sub % {'topic': t} for t in listify(topic)])


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


class TW1AMQPSocket(Widget):
    callbacks = ['onconnectedframe', 'onmessageframe']
    javascript = [jquery_json_js, moksha_js, kamaloka_qpid_js]
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
                var dest = msg.header.delivery_properties.routing_key;
                var json = null;
                try {
                    var json = $.parseJSON(msg.body);
                } catch(err) {
                    moksha.error("Unable to decode JSON message body");
                    moksha.error(msg);
                }
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
                Orbited.settings.port = ${orbited_port};
                Orbited.settings.hostname = '${orbited_host}';
                Orbited.settings.streaming = true;
                moksha_amqp_conn = new amqp.Connection({
                    % if send_hook:
                        send_hook: function(data, frame) { ${send_hook} },
                    % endif
                    % if recieve_hook:
                        recive_hook: function(data, frame) { ${recieve_hook} },
                    % endif
                    host: '${amqp_broker_host}',
                    port: ${amqp_broker_port},
                    username: '${amqp_broker_user}',
                    password: '${amqp_broker_pass}',
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

                % if onconnectedframe:
                    ${onconnectedframe}
                    moksha_amqp_queue.start();
                % endif

            });

        } else {
            ## Utilize the existing Moksha AMQP socket connection
            ${onconnectedframe}
            moksha_amqp_queue.start();
        }

        if (typeof moksha == 'undefined') {
            moksha = {
                /* Send an AMQP message to a given topic */
                send_message: function(topic, body) {
                    moksha_amqp_session.Message('transfer', {
                        accept_mode: 1,
                        acquire_mode: 1, 
                        destination: 'amq.topic',
                        _body: $.toJSON(body),
                        _header: {
                            delivery_properties: {
                                routing_key: topic
                            }
                        }
                    });
                },
            }
        }
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
        self.amqp_broker_host = config.get('amqp_broker_host', 'localhost')
        self.amqp_broker_port = config.get('amqp_broker_port', 5672)
        self.amqp_broker_user = config.get('amqp_broker_user', 'guest')
        self.amqp_broker_pass = config.get('amqp_broker_pass', 'guest')
        super(TW1AMQPSocket, self).__init__(*args, **kw)

    def update_params(self, d):
        super(TW1AMQPSocket, self).update_params(d)
        d.topics = []
        d.onmessageframe = defaultdict(str) # {topic: 'js callbacks'}
        for callback in self.callbacks:
            if len(moksha.utils.livewidgets[callback]):
                cbs = ''
                if callback == 'onmessageframe':
                    for topic in moksha.utils.livewidgets[callback]:
                        d.topics.append(topic)
                        for cb in moksha.utils.livewidgets[callback][topic]:
                            d.onmessageframe[topic] += '%s;' % str(cb)
                else:
                    for cb in moksha.utils.livewidgets[callback]:
                        if isinstance(cb, (js_callback, js_function)):
                            cbs += '$(%s);' % str(cb)
                        else:
                            cbs += str(cb)
                if cbs:
                    d[callback] = cbs

if asbool(config.get('moksha.use_tw2', False)):
    raise NotImplementedError(__name__ + " not ready for tw2")
else:
    AMQPSocket = TW1AMQPSocket
