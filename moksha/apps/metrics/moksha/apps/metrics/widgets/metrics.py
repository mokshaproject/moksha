# -*- coding: utf-8 -*-
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
:mod:`moksha.widgets.metrics` -- Moksha Metrics
===============================================

This module contains Moksha-specific widgets and
Producers that provide live statistics of
Moksha's memory and CPU usage.

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

from tg import config
from paste.deploy.converters import asbool

from uuid import uuid4

import tw.jquery.ui
import tw.jquery.flot

import tw2.jqplugins.flot
import tw2.excanvas


from moksha.api.widgets.flot import TW1LiveFlotWidget, TW2LiveFlotWidget
#from moksha.api.widgets.jit import LiveAreaChartWidget
from moksha.api.widgets.buttons import tw1_buttons_css, tw2_buttons_css

#import tw2.core.resources as res
#class MokshaTW2CPUUsageWidget(LiveAreaChartWidget):
#    name = 'CPU Usage (with tw2.jit)'
#    topic = 'moksha_jit_cpu_metrics'
#
#    width='400px'
#    height='300px'
#    offset = 0
#    showAggregates = False
#    showLabels = False
#    animate = False
#    type = 'stacked'
#    Tips = {
#        'enable': True,
#        'onShow' : res.JSSymbol(src="""
#        (function(tip, elem) {
#            tip.innerHTML = "<b>" + elem.name + "</b>: " + elem.value;
#        })""")
#    }
#
#    container_options = { 'icon': 'chart.png', 'height' : 325 }
#    data = {'labels': [], 'values': []}


class TW1MokshaMemoryUsageWidget(TW1LiveFlotWidget):
    name = 'Memory Usage'
    topic = 'moksha_mem_metrics'
    javascript = TW1LiveFlotWidget.javascript + [
        tw.jquery.ui.ui_draggable_js,
        tw.jquery.ui.ui_resizable_js,
    ]
    container_options = {
            'icon': 'chart.png', 'top': 400, 'left': 80, 'height': 325,
            }


class TW1MokshaCPUUsageWidget(TW1LiveFlotWidget):
    name = 'CPU Usage'
    topic = 'moksha_cpu_metrics'
    javascript = TW1LiveFlotWidget.javascript + [
        tw.jquery.ui.ui_draggable_js,
        tw.jquery.ui.ui_resizable_js,
    ]
    container_options = {
            'icon': 'chart.png', 'top': 80, 'left': 80, 'height': 325,
            }


class TW2MokshaMemoryUsageWidget(TW2LiveFlotWidget):
    name = 'Memory Usage'
    topic = 'moksha_mem_metrics'
    container_options = {
            'icon': 'chart.png', 'top': 400, 'left': 80, 'height': 325,
            }


class TW2MokshaCPUUsageWidget(TW2LiveFlotWidget):
    name = 'CPU Usage'
    topic = 'moksha_cpu_metrics'
    container_options = {
            'icon': 'chart.png', 'top': 80, 'left': 80, 'height': 325,
            }


class TW1MokshaMessageMetricsWidget(TW1LiveFlotWidget):
    """ A Moksha Message Benchmarking Widget.

    This widget will fire off a bunch of messages to a unique message topic.
    The MokshaMessageMetricsConsumer, being run in the Moksha Hub, will
    echo these messages back to the sender.  This widget will then graph
    the round-trip results.

    TODO:
    - display the latency
    """
    name = 'Message Metrics'
    template = "mako:moksha.apps.metrics.widgets.templates.metrics"
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
    javascript = [
        tw.jquery.flot.excanvas_js,
        tw.jquery.flot.flot_js,
        tw.jquery.ui.ui_draggable_js,
        tw.jquery.ui.ui_resizable_js,
        tw.jquery.ui.ui_progressbar_js
    ]
    css = [
        tw.jquery.flot.flot_css,
        tw1_buttons_css
    ]
    container_options = {'icon': 'chart.png', 'left': 550, 'top': 80,
                         'height': 500}

    def update_params(self, d):
        d.topic = str(uuid4())
        super(TW1MokshaMessageMetricsWidget, self).update_params(d)


class TW2MokshaMessageMetricsWidget(TW2LiveFlotWidget):
    """ A Moksha Message Benchmarking Widget.

    This widget will fire off a bunch of messages to a unique message topic.
    The MokshaMessageMetricsConsumer, being run in the Moksha Hub, will
    echo these messages back to the sender.  This widget will then graph
    the round-trip results.

    TODO:
    - display the latency
    """
    name = 'Message Metrics'
    template = "mako:moksha.apps.metrics.widgets.templates.metrics"
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
    resources = [
        tw2.excanvas.excanvas_js,
        tw2.jquery.jquery_js,
        tw2.jqplugins.flot.flot_js,
        tw2_buttons_css,
    ]
    container_options = {'icon': 'chart.png', 'left': 550, 'top': 80,
                         'height': 500}

    def prepare(self):
        self.topic = str(uuid4())
        super(TW2MokshaMessageMetricsWidget, self).prepare()


if asbool(config.get('moksha.use_tw2', False)):
    MokshaCPUUsageWidget = TW2MokshaCPUUsageWidget
    MokshaMemoryUsageWidget = TW2MokshaMemoryUsageWidget
    MokshaMessageMetricsWidget = TW2MokshaMessageMetricsWidget
else:
    MokshaCPUUsageWidget = TW1MokshaCPUUsageWidget
    MokshaMemoryUsageWidget = TW1MokshaMemoryUsageWidget
    MokshaMessageMetricsWidget = TW1MokshaMessageMetricsWidget
