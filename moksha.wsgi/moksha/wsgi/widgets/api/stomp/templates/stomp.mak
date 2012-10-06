<%namespace name="tw" module="tw2.core.mako_util"/>
<script type="text/javascript">
if (typeof TCPSocket == 'undefined') {
	moksha_callbacks = new Object();
	moksha_socket_busy = false;
}

## Register our topic callbacks
% for topic in tw._('topics'):
	var topic = "${topic}";
	if (!moksha_callbacks[topic]) {
		moksha_callbacks[topic] = [];
	}
	moksha_callbacks[topic].push(function(json, frame) {
		${tw._('onmessageframe')[topic]}
	});
% endfor

function setup_moksha_socket(){
	${unicode(tw._('before_open'))}
	Orbited.settings.port = ${tw._('orbited_port')};
	Orbited.settings.hostname = '${tw._('orbited_host')}';
	Orbited.settings.streaming = true;
	TCPSocket = Orbited.TCPSocket;
	$.getScript("${tw._('orbited_url')}/static/protocols/stomp/stomp.js",
	function(){
		## Create a new TCPSocket & Stomp client
		stomp = new STOMPClient();
		stomp.onopen = function(e) { ${unicode(tw._('onopen'))} }
		stomp.onclose = function(e) { ${unicode(tw._('onclose'))} }
		stomp.onerror = function(e) { ${unicode(tw._('onerror'))} }
		stomp.onerrorframe = function(e) { ${unicode(tw._('onerrorframe'))} }
		stomp.onconnectedframe = function(){
			moksha_socket_busy = false;
			$('body').triggerHandler('moksha.socket_ready');
			${unicode(tw._('onconnectedframe'))}
		};
		stomp.onmessageframe = function(f){
			var dest = f.headers.destination;
			var json = null;
			try {
				var json = JSON.parse(f.body);
			} catch(err) {
				moksha.error("Unable to decode JSON message body");
				moksha.error(msg);
			}
			if (moksha_callbacks[dest]) {
				for (var i=0; i < moksha_callbacks[dest].length; i++) {
					moksha_callbacks[dest][i](json, f);
				}
			}
		};

		stomp.connect('${tw._("stomp_broker")}', ${tw._("stomp_port")},
					  '${tw._("stomp_user")}','${tw._("stomp_pass")}');
	});
}

if (typeof TCPSocket == 'undefined') {
	document.domain = document.domain;
	moksha_socket_busy = true;
	$.getScript("${tw._('orbited_url')}/static/Orbited.js", setup_moksha_socket);

} else {
	## Utilize the existing stomp connection
	if (moksha_socket_busy) {
		$('body').bind('moksha.socket_ready', function() {
			${tw._("onconnectedframe")}
		});
	} else {
		${tw._("onconnectedframe")}
	}
}

window.onbeforeunload = function() {
	if (typeof stomp != 'undefined') {
		stomp.reset();
	}
}

if (typeof moksha == 'undefined') {
	moksha = {
		/* Send a STOMP message to a given topic */
		send_message: function(topic, body) {
			stomp.send(JSON.stringify(body), topic)
		}
	}
}
</script>
