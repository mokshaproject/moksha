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
DataStreams that provide live statistics of
Moksha's memory and CPU usage.

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

import subprocess
import logging
import os

from uuid import uuid4
from orbited import json
from tw.api import Widget, JSLink
from tw.jquery.ui import ui_progressbar_js
from tw.jquery.flot import flot_js, excanvas_js, flot_css

from tg import config
from paste.deploy.converters import asbool

from moksha.api.hub import Consumer
from moksha.api.widgets.flot import LiveFlotWidget
#from moksha.api.widgets.jit import LiveAreaChartWidget
from moksha.api.widgets.buttons import buttons_css
from moksha.api.streams import PollingDataStream
from moksha.lib.helpers import defaultdict

log = logging.getLogger('moksha.hub')

### Commented out since there is *only* a tw2 implementation of this
#class TW1MokshaAreaCPUUsageWidget(LiveAreaChartWidget):
#    name = 'CPU Usage (with tw2.jit)'
#    topic = 'moksha_jit_cpu_metrics'
#    width = '300'
#    height = '300'
#    offset = 0
#    type = 'stacked'
#    container_options = {
#        'icon': 'chart.png', 'top': 400, 'left': 80, 'height': 310,
#        'iconize': False, 'minimize': False,
#    }

class TW1MokshaMemoryUsageWidget(LiveFlotWidget):
    name = 'Memory Usage'
    topic = 'moksha_mem_metrics'
    container_options = {
            'icon': 'chart.png', 'top': 400, 'left': 80, 'height': 310,
            'iconize': False, 'minimize': False,
            }

if asbool(config.get('moksha.use_tw2', False)):
    raise NotImplementedError(__name__ + " is not ready for tw2")
else:
    MokshaMemoryUsageWidget = TW1MokshaMemoryUsageWidget

class TW1MokshaCPUUsageWidget(LiveFlotWidget):
    name = 'CPU Usage'
    topic = 'moksha_cpu_metrics'
    container_options = {
            'icon': 'chart.png', 'top': 80, 'left': 80, 'height': 310,
            'iconize': False, 'minimize': False,
            }

if asbool(config.get('moksha.use_tw2', False)):
    raise NotImplementedError(__name__ + " is not ready for tw2")
else:
    MokshaCPUUsageWidget = TW1MokshaCPUUsageWidget


class MokshaMessageMetricsConsumer(Consumer):
    """
    This consumer listens to all messages on the `moksha_message_metrics`
    topic, and relays the messgae to the message['headers']['topic']
    """
    topic = 'moksha_message_metrics'

    def consume(self, message):
        topic = message['headers'].get('topic')
        if topic:
            self.send_message(topic, json.encode(message['body']))
        else:
            log.error('No `topic` specified in moksha_message_metrics message')


class TW1MokshaMessageMetricsWidget(LiveFlotWidget):
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
    css = [flot_css, buttons_css]
    container_options = {'icon': 'chart.png', 'left': 550, 'top': 80,
                         'height': 500}

    def update_params(self, d):
        d.topic = str(uuid4())
        super(TW1MokshaMessageMetricsWidget, self).update_params(d)

if asbool(config.get('moksha.use_tw2', False)):
    raise NotImplementedError(__name__ + " is not ready for tw2")
else:
    MokshaMessageMetricsWidget = TW1MokshaMessageMetricsWidget


PID = 0
NAME = -1
MEM_TOTAL = -2

class MokshaMetricsDataStream(PollingDataStream):
    frequency = 3
    procs = ('orbited', 'paster', 'moksha', 'httpd')
    cpu_usage = defaultdict(list)
    programs = None
    pids = {}
    count = 0

    # Unless we are monitoring apache, only poll for pids once
    poll_for_new_pids = False

    def __init__(self, hub):
        self.programs = self._find_programs()
        self.processors = self._find_processors()
        super(MokshaMetricsDataStream, self).__init__(hub)

    def _find_programs(self):
        programs = []
        for program in self.mem():
            for proc in self.procs:
                if program[NAME].startswith(proc) or proc in program[NAME]:
                    programs.append(program)
                    for pid in program[PID].split(','):
                        self.pids[int(pid)] = program[NAME]
                    if proc == 'httpd':
                        self.poll_for_new_pids = True
        return programs

    def _find_processors(self):
        """ Find the number of processors """
        processors = 0
        for line in file('/proc/cpuinfo').readlines():
            if line.startswith('processor'):
                processors = int(line.split(':')[1])
        return processors + 1

    def poll(self):
        i = 0
        mem_data = {
            'data': [],
            'options': {
                'xaxis': {'ticks': []},
                'legend': {'position': 'nw', 'backgroundColor': 'null'}
            }
        }
        cpu_data = {
            'data': [],
            'options': {
                'xaxis': {'min': 0, 'max': 50},
                'yaxis': {'min': 0, 'max': 100 * self.processors},
                'legend': {
                    'position': 'nw',
                    'backgroundColor': 'null'
                }
            }
        }

        self.count += 1
        if self.poll_for_new_pids and self.count % 10 == 0:
            self.programs = self._find_programs()
            self.count = 0

        for program in self.programs:
            for proc in self.procs:
                if program[NAME].startswith(proc) or proc in program[NAME]:
                    total_mem_usage = float(program[MEM_TOTAL].split()[0])
                    mem_data['data'].append({
                            'data': [[i, total_mem_usage]],
                            'bars': {'show': 'true'},
                            'label': program[NAME],
                            })
                    mem_data['options']['xaxis']['ticks'].append(
                            [i + 0.5, program[NAME]])
                    i += 1

        self.send_message('moksha_mem_metrics', [mem_data])

        # top only allows 20 pids to be specified at a time
        # so make multiple calls if we have to
        out = []
        _pids = []
        _pids.extend(self.pids.keys())
        while _pids:
            cmd = ['/usr/bin/top', '-b', '-n 1']
            for pid in _pids[:20]:
                cmd += ['-p %s' % pid]
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            stdout, stderr = p.communicate()
            stdout = stdout.strip().split('\n')
            for i, line in enumerate(stdout):
                if line.lstrip().startswith('PID'):
                    out += stdout[i+1:]
                    break
            _pids = _pids[20:]

        # Determine the % CPU usage for each pid
        pid_cpu = defaultdict(float)
        for line in out:
            splitline = line.split()
            if not splitline: continue
            pid = int(splitline[0])
            cpu_usage = float(splitline[-4])
            pid_cpu[self.pids[pid]] += cpu_usage

        # Move everything to the left, and append the latest CPU usage.
        for program, cpu_usage in pid_cpu.items():
            for history in self.cpu_usage[program]:
                history[0] -= 1

            self.cpu_usage[program].append([50, cpu_usage])

            # Only store 50 ticks worth of data
            self.cpu_usage[program] = self.cpu_usage[program][-51:]

        for program, history in self.cpu_usage.items():
            cpu_data['data'].append({
                'data': history,
                'lines': {'show': 'true', 'fill': 'true'},
                'label': program.split()[0],
                })

        self.send_message('moksha_cpu_metrics', [cpu_data])

        jit_cpu_data = {
            'label': [],
            'values': [{'label': str(i), 'values': []}
                       for i in range(len(self.cpu_usage.values()[0]))]
        }

        for program, history in self.cpu_usage.items():
            for i in range(len(jit_cpu_data['values'])):
                jit_cpu_data['values'][i]['values'].append(history[i][1])
            jit_cpu_data['label'].append(program.split()[0])

        self.send_message('moksha_jit_cpu_metrics', [jit_cpu_data])


    def mem(self):
        """
        Returns a list of per-program memory usage.

             Private  +  Shared   =  RAM used     Program

           [["39.4 MiB", "10.3 MiB", "49.8 MiB",  "Xorg"],
            ["42.2 MiB", "12.4 MiB", "54.6 MiB",  "nautilus"],
            ["52.3 MiB", "10.8 MiB", "63.0 MiB",  "liferea-bin"]
            ["171.6 MiB", "11.9 MiB", "183.5 MiB", "firefox-bin"]]

        Taken from the ps_mem.py script written by Pádraig Brady.
        http://www.pixelbeat.org/scripts/ps_mem.py
        """
        our_pid=os.getpid()
        results = []
        global have_pss
        have_pss=0

        def kernel_ver():
            """ (major,minor,release) """
            kv=open("/proc/sys/kernel/osrelease").readline().split(".")[:3]
            for char in "-_":
                kv[2]=kv[2].split(char)[0]
            return (int(kv[0]), int(kv[1]), int(kv[2]))

        kv=kernel_ver()

        def getMemStats(pid):
            """ return Private,Shared """
            global have_pss
            Private_lines=[]
            Shared_lines=[]
            Pss_lines=[]
            pagesize=os.sysconf("SC_PAGE_SIZE")/1024 #KiB
            Rss=int(open("/proc/"+str(pid)+"/statm").readline().split()[1])*pagesize
            if os.path.exists("/proc/"+str(pid)+"/smaps"): #stat
                for line in open("/proc/"+str(pid)+"/smaps").readlines(): #open
                    if line.startswith("Shared"):
                        Shared_lines.append(line)
                    elif line.startswith("Private"):
                        Private_lines.append(line)
                    elif line.startswith("Pss"):
                        have_pss=1
                        Pss_lines.append(line)
                Shared=sum([int(line.split()[1]) for line in Shared_lines])
                Private=sum([int(line.split()[1]) for line in Private_lines])
                #Note Shared + Private = Rss above
                #The Rss in smaps includes video card mem etc.
                if have_pss:
                    pss_adjust=0.5 #add 0.5KiB as this average error due to trunctation
                    Pss=sum([float(line.split()[1])+pss_adjust for line in Pss_lines])
                    Shared = Pss - Private
            elif (2,6,1) <= kv <= (2,6,9):
                Shared=0 #lots of overestimation, but what can we do?
                Private = Rss
            else:
                Shared=int(open("/proc/"+str(pid)+"/statm").readline().split()[2])*pagesize
                Private = Rss - Shared
            return (Private, Shared)

        def getCmdName(pid):
            cmd = file("/proc/%d/status" % pid).readline()[6:-1]
            exe = os.path.basename(os.path.realpath("/proc/%d/exe" % pid))
            if exe.startswith(cmd):
                cmd=exe #show non truncated version
                #Note because we show the non truncated name
                #one can have separated programs as follows:
                #584.0 KiB +   1.0 MiB =   1.6 MiB    mozilla-thunder (exe -> bash)
                # 56.0 MiB +  22.2 MiB =  78.2 MiB    mozilla-thunderbird-bin
            return cmd

        cmds={}
        shareds={}
        count={}
        pids = {}

        for pid in os.listdir("/proc/"):
            try:
                pid = int(pid) #note Thread IDs not listed in /proc/ which is good
                #if pid == our_pid: continue
            except:
                continue
            try:
                cmd = getCmdName(pid)
            except Exception, e:
                #permission denied or
                #kernel threads don't have exe links or
                #process gone
                continue
            try:
                private, shared = getMemStats(pid)
            except:
                continue #process gone
            if shareds.get(cmd):
                if have_pss: #add shared portion of PSS together
                    shareds[cmd]+=shared
                elif shareds[cmd] < shared: #just take largest shared val
                    shareds[cmd]=shared
            else:
                shareds[cmd]=shared
            cmds[cmd]=cmds.setdefault(cmd,0)+private
            if count.has_key(cmd):
               count[cmd] += 1
               pids[cmd] += ',%d' % pid
            else:
               count[cmd] = 1
               pids[cmd] = str(pid)

        #Add shared mem for each program
        total=0
        for cmd in cmds.keys():
            cmds[cmd]=cmds[cmd]+shareds[cmd]
            total+=cmds[cmd] #valid if PSS available

        sort_list = cmds.items()
        sort_list.sort(lambda x,y:cmp(x[1],y[1]))
        sort_list=filter(lambda x:x[1],sort_list) #get rid of zero sized processes

        #The following matches "du -h" output
        def human(num, power="Ki"):
            powers=["Ki","Mi","Gi","Ti"]
            while num >= 1000: #4 digits
                num /= 1024.0
                power=powers[powers.index(power)+1]
            return "%.1f %s" % (num,power)

        def cmd_with_count(cmd, count):
            if count>1:
               return "%s (%u)" % (cmd, count)
            else:
               return cmd

        for cmd in sort_list:
            results.append([
                "%s" % pids[cmd[0]],
                "%sB" % human(cmd[1]-shareds[cmd[0]]),
                "%sB" % human(shareds[cmd[0]]),
                "%sB" % human(cmd[1]),
                "%s" % cmd_with_count(cmd[0], count[cmd[0]])
            ])
        if have_pss:
            results.append(["", "", "", "%sB" % human(total)])

        return results


# @@ FIXME: We need to not insert two stomp widgets in this case...
#class TW1MokshaMetricsWidget(Widget):
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

