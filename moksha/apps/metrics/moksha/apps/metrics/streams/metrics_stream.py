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

import os
import logging
import subprocess

from tg import config
from paste.deploy.converters import asbool

from moksha.lib.helpers import defaultdict
from moksha.api.hub.producer import PollingProducer

log = logging.getLogger('moksha.hub')

PID = 0
NAME = -1
MEM_TOTAL = -2

class MokshaMetricsProducer(PollingProducer):
    frequency = 3
    procs = ('orbited', 'paster', 'moksha', 'httpd', 'qpidd')
    cpu_usage = defaultdict(list)
    programs = None
    pids = {}
    count = 0

    # Unless we are monitoring apache, only poll for pids once
    poll_for_new_pids = False

    def __init__(self, hub):
        if not asbool(config.get('moksha.metrics_stream', False)):
            log.info('Moksha Metrics Stream disabled')
            return
        self.programs = self._find_programs()
        self.processors = self._find_processors()
        super(MokshaMetricsProducer, self).__init__(hub)

    def _find_programs(self):
        programs = []
        self.pids = {}
        for program in self.mem():
            for proc in self.procs:
                if program[NAME].startswith(proc) or proc in program[NAME]:
                    programs.append(program)
                    for pid in program[PID].split(','):
                        self.pids[int(pid)] = program[NAME]
                    if proc == 'httpd':
                        self.poll_for_new_pids = True
        sorted_programs = []
        for proc in self.procs:
            for program in programs:
                if program[NAME].startswith(proc) or proc in program[NAME]:
                    sorted_programs.append(program)
        return sorted_programs

    def _find_processors(self):
        """ Find the number of processors """
        processors = 0
        for line in file('/proc/cpuinfo').readlines():
            if line.startswith('processor'):
                processors = int(line.split(':')[1])
        return processors + 1

    def poll(self):
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

        for i, program in enumerate(self.programs):
            total_mem_usage = float(program[MEM_TOTAL].split()[0])
            mem_data['data'].append({
                    'data': [[i, total_mem_usage]],
                    'bars': {'show': 'true'},
                    'label': program[NAME],
                    })
            mem_data['options']['xaxis']['ticks'].append(
                    [i + 0.5, program[NAME]])

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
            try:
                stdout, stderr = p.communicate()
            except IOError:
                self.log.warning("Unable to communicate with `top` subprocess")
                return
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
            program = program.split()[0]
            for history in self.cpu_usage[program]:
                history[0] -= 1

            self.cpu_usage[program].append([50, cpu_usage])

            # Only store 50 ticks worth of data
            self.cpu_usage[program] = self.cpu_usage[program][-51:]

        for proc in self.procs:
            for program, history in self.cpu_usage.items():
                if program.startswith(proc) or proc in program:
                    cpu_data['data'].append({
                        'data': history,
                        'lines': {'show': 'true', 'fill': 'true'},
                        'label': program,
                        })

        self.send_message('moksha_cpu_metrics', [cpu_data])

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
