moksha = {
    /* Send an AMQP message to a given topic */
    send_message: function(topic, body) {
        moksha_amqp_session.Message('transfer', {
            accept_mode: 1,
            acquire_mode: 1, 
            destination: 'amq.topic',
% if json:
            _body: JSON.stringify(body),
% else:
            _body: body,
% endif
            _header: {
                delivery_properties: {
                    routing_key: topic
                }
            }
        });
    },
}

if (typeof moksha_amqp_conn == 'undefined') {
    moksha_callbacks = new Object();
    moksha_amqp_remote_queue = null;
    moksha_amqp_queue = null;
    moksha_amqp_on_message = function(msg) {
        var dest = msg.header.delivery_properties.routing_key;
        var json = msg.body;
% if json:
        try {
            var json = JSON.parse(msg.body);
        } catch(err) {
            console.log("Unable to decode JSON message body:");
            console.log(f.body);
        }
% endif
        if (moksha_callbacks[dest]) {
            for (var i=0; i < moksha_callbacks[dest].length; i++) {
                moksha_callbacks[dest][i](json);
            }
        }
    }
}

## Register our topic callbacks
var topic = "${topic}";
if (!moksha_callbacks[topic]) {
    moksha_callbacks[topic] = [];
}
moksha_callbacks[topic].push(function(frame) {
    ${callback}(frame);
});

## Create a new AMQP client
if (typeof moksha_amqp_conn == 'undefined') {
    document.domain = document.domain;
    $.getScript("${orbited_url}/static/Orbited.js", function() {
        Orbited.settings.port = ${orbited_port};
        Orbited.settings.hostname = '${orbited_host}';
        Orbited.settings.streaming = true;
        $.getScript('${server}/resources/moksha.api.widgets.amqp.widgets/static/amqp.protocol.js', function() {
            $.getScript('${server}/resources/moksha.api.widgets.amqp.widgets/static/amqp.protocol_0_10.js', function() {
                $.getScript('${server}/resources/moksha.api.widgets.amqp.widgets/static/qpid_amqp.js', function() {
                    moksha_amqp_conn = new amqp.Connection({
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

                    moksha_amqp_queue.subscribe({
                        exchange: 'amq.topic',
                        remote_queue: moksha_amqp_remote_queue,
                        binding_key: '${topic}',
                        callback: moksha_amqp_on_message,
                    });

                    moksha_amqp_queue.start();
                });
            });
        });
    });
} else {
    ## Utilize the existing Moksha AMQP socket connection
    moksha_amqp_queue.subscribe({
        exchange: 'amq.topic',
        remote_queue: moksha_amqp_remote_queue,
        binding_key: '${topic}',
        callback: moksha_amqp_on_message,
    });
    moksha_amqp_queue.start();
}
