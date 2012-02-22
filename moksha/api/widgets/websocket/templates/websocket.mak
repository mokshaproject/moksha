<%namespace name="tw" module="moksha.utils.mako"/>
<script type="text/javascript">
$(document).ready(function() {

if (typeof moksha_callbacks == 'undefined') { moksha_callbacks = {}; }

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

if (typeof raw_msg_callback == 'undefined') {
	raw_msg_callback = function(e) {
		var data, json, topic, body;

		data = e.data;
		json = JSON.parse(data);
		topic = json.topic;
		body = json.body;

		if (moksha_callbacks[topic]) {
			$.each(moksha_callbacks[topic], function (i, callback) {
				callback(body);
			});
		}
    }
}

## Cross-browser compat.
## If we're in chrome, we're fine.
## If we're in Firefox, reassign.
## Opera and IE not supported.
if (typeof WebSocket == 'undefined') { WebSocket = MozWebSocket; }

## Create a singleton pattern for a websocket
if (typeof moksha_websocket == 'undefined') {
  ## Create a new websocket for every connection
  moksha_websocket = new WebSocket(
  	'ws://${tw._("ws_host")}:${tw._("ws_port")}'
  );
  
  ## Attach all the callbacks for that websocket
  % for callback in ['onopen', 'onerror', 'onclose']:
  % if tw._(callback):
  moksha_websocket.${callback} = ${unicode(tw._(callback))};
  % endif
  % endfor

  moksha_websocket.onmessage = raw_msg_callback;
} else {
  $(${unicode(tw._("onconnectedframe"))});
}

## Extend the moksha object
if (typeof moksha == 'undefined') {moksha = {};}

moksha.send_message = function(topic, body) {
	moksha_websocket.send(
		JSON.stringify({topic: topic, body: body})
	);
}

moksha.topic_subscribe = function(topic) {
	moksha.send_message('__topic_subscribe__', topic);
}

});
</script>
