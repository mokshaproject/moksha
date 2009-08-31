# -*- coding: utf-8 -*-
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
:mod:`moksha.widgets.metrics` -- Moksha Metrics
===============================================

This module contains Moksha-specific widgets and
DataStreams that provide live statistics of
Moksha's memory and CPU usage.

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

from uuid import uuid4
from tw.jquery.ui import ui_progressbar_js
from tw.jquery.flot import flot_js, excanvas_js, flot_css

from moksha.api.widgets.flot import LiveFlotWidget
from moksha.api.widgets.buttons import buttons_css
from moksha.widgets.jquery_ui_theme import ui_base_css

class MokshaMemoryUsageWidget(LiveFlotWidget):
    name = 'Memory Usage'
    topic = 'moksha_mem_metrics'
    container_options = {
            'icon': 'chart.png', 'top': 400, 'left': 80, 'height': 325,
            }


class MokshaCPUUsageWidget(LiveFlotWidget):
    name = 'CPU Usage'
    topic = 'moksha_cpu_metrics'
    container_options = {
            'icon': 'chart.png', 'top': 80, 'left': 80, 'height': 325,
            }


class MokshaMessageMetricsWidget(LiveFlotWidget):
    """ A Moksha Message Benchmarking Widget.

    This widget will fire off a bunch of messages to a unique message topic.
    The MokshaMessageMetricsConsumer, being run in the Moksha Hub, will
    echo these messages back to the sender.  This widget will then graph
    the round-trip results.

    TODO:
    - display the latency
    """
    name = 'Message Metrics'
    template = """
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
                    stomp.send(start.getTime() + '', 'moksha_message_metrics',
                               {topic: '${topic}'});
                    $('#metrics_sent_progress').progressbar('option', 'value', i+1)
                    $('#metrics_msg_sent').text(i + 1 + '');
                }
                stomp.send('done', 'moksha_message_metrics',
                           {topic: '${topic}'});
            }

        </script>
        <div id="metrics_flot" style="width:390px;height:250px;" />
        <div id="metrics_avg"></div>
        <div id="metrics_msg_sec"></div>
        <br/>
        <center>
          <a href="#" class="opaquebutton" onclick="run_message_metrics(); return false"><span>Send 100 Messages</span></a>
        </center>
    """
    onmessage = """
        if (json == 'done') {
            avg = accum / (NUM_MESSAGES * 1.0);
            $('#metrics_recv_progress').progressbar('option', 'value', x+1)
            $.plot($('#metrics_flot'), [{data: flot_data, lines: {show: true}}]);
            $('#metrics_avg').text('Average round trip: ' + avg + ' seconds.');
            var start = new Date();
            seconds = (start.getTime() - start_time) / 1000.0;
            $('#metrics_msg_sec').text('Messages per second: ' + NUM_MESSAGES / seconds);
        } else {
            var now = new Date();
            seconds = (now.getTime() - json) / 1000.0;
            accum = accum + seconds;
            flot_data.push([x, seconds]);
            $('#metrics_recv_progress').progressbar('option', 'value', x+1)
            $('#metrics_msg_recv').text(x + 1 + '');
            x = x + 1;
        }
    """
    javascript = [excanvas_js, flot_js, ui_progressbar_js]
    css = [ui_base_css, flot_css, buttons_css]
    container_options = {'icon': 'chart.png', 'left': 550, 'top': 80,
                         'height': 500}

    def update_params(self, d):
        d.topic = str(uuid4())
        super(MokshaMessageMetricsWidget, self).update_params(d)


# @@ FIXME: We need to not insert two stomp widgets in this case...
#class MokshaMetricsWidget(Widget):
#    children = [MokshaCPUUsageWidget('moksha_cpu'),
#                MokshaMemoryUsageWidget('moksha_mem')]
#    template = """
#        <center>${c.moksha_cpu.label}</center>
#        ${c.moksha_cpu()}
#        <br/>
#        <center>${c.moksha_mem.label}</center>
#        ${c.moksha_mem()}
#    """
#    engine_name = 'mako'
