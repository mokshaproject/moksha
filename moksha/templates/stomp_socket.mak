moksha = {
    /* Send a STOMP message to a given topic */
    send_message: function(topic, body) {
		stomp.send($.toJSON(body), topic)
    },
}

if (typeof TCPSocket == 'undefined') {
    moksha_callbacks = new Object();
    moksha_socket_busy = false;
}

## Register our topic callbacks
var topic = "${topic}";
if (!moksha_callbacks[topic]) {
    moksha_callbacks[topic] = [];
}
moksha_callbacks[topic].push(function(frame) {
    ${callback}(frame);
});

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
            stomp.onopen = function(){};
            stomp.onclose = function(c){};
            stomp.onerror = function(error){};
            stomp.onerrorframe = function(f){};
            stomp.onconnectedframe = function(){ 
                moksha_socket_busy = false;
                $('body').triggerHandler('moksha.socket_ready');
                stomp.subscribe('${topic}')
            };
            stomp.onmessageframe = function(f){
                var dest = f.headers.destination;
/*
                var json = null;
                try {
                    var json = $.parseJSON(f.body);
                } catch(err) {
                    console.log("Unable to decode JSON message body:");
                    console.log(f.body);
                }
*/
                if (moksha_callbacks[dest]) {
                    for (var i=0; i < moksha_callbacks[dest].length; i++) {
                        moksha_callbacks[dest][i](f.body);
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
            stomp.subscribe('${topic}')
        });
    } else {
        stomp.subscribe('${topic}')
    }
}

window.onbeforeunload = function() {
    if (typeof stomp != 'undefined') {
        stomp.reset();
    }
}
