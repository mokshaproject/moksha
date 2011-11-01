<%namespace name="tw" module="moksha.utils.mako"/>
Messages sent: <span id="metrics_msg_sent">0</span><br/>
<div id="metrics_sent_progress"></div>
Messages received: <span id="metrics_msg_recv">0</span><br/>
<div id="metrics_recv_progress"></div>
<br/>
<script>
	var NUM_MESSAGES = 100;
	var accum = 0.0;
	var flot_data = [];
	var x = 0;
	var start_time = 0;

	$('#metrics_sent_progress').progressbar({value: 0});
	$('#metrics_recv_progress').progressbar({value: 0});

	function run_message_metrics() {
		$('#metrics_sent_progress').progressbar('option', 'value', 0);
		$('#metrics_recv_progress').progressbar('option', 'value', 0);
		$('#metrics_msg_sent').text("0");
		$('#metrics_msg_recv').text("0");

		flot_data = [];
		x = 0;
		accum = 0.0;

		for (var i = 0; i < NUM_MESSAGES; i++) {
			var start = new Date();
			start_time = start.getTime();
			/* Eventually, once our AMQP bindings don't explode, send
			   the messages directly to the AMQP queue, instead of going
			   through a consumer.  it would be nice to benchmark both.
			moksha.send_message('${tw._("topic")}', start.getTime() + '');
			   */
			moksha.send_message('moksha_message_metrics', {
					data: start.getTime() + '',
					topic: '${tw._("topic")}'
			});
			$('#metrics_sent_progress').progressbar('option', 'value', i+1)
			$('#metrics_msg_sent').text(i + 1 + '');
		}
		moksha.send_message('moksha_message_metrics', {
				data: 'done',
				topic: '${tw._("topic")}'
		});
	}

</script>
<div id="metrics_flot" style="width:390px;height:250px;" />
<div id="metrics_avg"></div>
<div id="metrics_msg_sec"></div>
<br/>
<center>
  <a href="#" class="opaquebutton" onclick="run_message_metrics(); return false"><span>Send 100 Messages</span></a>
</center>



