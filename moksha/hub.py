#!/usr/bin/env python
# This file is part of Moksha.
#
# Moksha is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Moksha is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Moksha.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2008, Red Hat, Inc.
# Authors: Luke Macken <lmacken@redhat.com>

import math

from random import random
from orbited import json
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from stompservice import StompClientFactory

from moksha.api.widgets.feed import Feed

INTERVAL = 300 # in ms

# Specific to the livegraph demo
DATA_VECTOR_LENGTH = 10
DELTA_WEIGHT = 0.1
MAX_VALUE = 400 # NB: this in pixels
CHANNEL_NAME = "/topic/graph"

class MokshaHub(StompClientFactory):
    """
    This module is currently only used for the default Moksha demo,
    but will eventually be a plugin-driven expert system that handles
    hooking into arbitrary events, and polling various resources.
    """
    username = 'guest'
    password = 'guest'

    # Feed demo
    feed_entries = Feed(url='http://lewk.org/blog/index.rss20').entries()

    # Flot demo specific variables
    offset = 0.0
    skip = 0
    bars = [[0, 3], [4, 8], [8, 5], [9, 13]]
    n = 0

    def recv_connected(self, msg):
        print 'Connected; producing data'
        self.data = [ 
            int(random()*MAX_VALUE) 
            for 
            x in xrange(DATA_VECTOR_LENGTH)
        ]
        self.timer = LoopingCall(self.send_data)
        self.timer.start(INTERVAL/1000.0)

    def send_data(self):
        self.n += 1

        if self.n % 3 == 0:
            entry = self.feed_entries[self.n % len(self.feed_entries)]
            self.send('/topic/feed_example', json.encode(
                [{'title': entry['title'], 'link': entry['link']}]))

        # modify our data elements
        if self.n % 2 == 0: # make the graph look independent of flot
            self.data = [ 
                min(max(datum+(random()-.5)*DELTA_WEIGHT*MAX_VALUE,0),MAX_VALUE)
                for 
                datum in self.data
            ]
            self.send(CHANNEL_NAME, json.encode(self.data))

        ## Generate flot data
        d1 = []
        i = 0
        for x in range(26):
            d1.append((i, math.sin(i + self.offset)))
            i += 0.5

        for bar in self.bars:
            bar[1] = bar[1] + (int(random() * 3) - 1)
            if bar[1] <= -5: bar[1] = -4
            if bar[1] >= 15: bar[1] = 15
        d2 = self.bars

        d3 = []
        i = 0
        for x in range(26):
            d3.append((i, math.cos(i + self.offset)))
            i += 0.5
        self.offset += 0.1

        d4 = []
        i = 0
        for x in range(26):
            d4.append((i, math.sqrt(i * 10)))
            i += 0.5

        d5 = []
        i = 0
        for x in range(26):
            d5.append((i, math.sqrt(i * self.offset)))
            i += 0.5

        flot_data = [{'data': [
            {'data': d1, 'lines': {'show': 'true', 'fill': 'true'}},
            {'data': d2, 'bars': {'show': 'true'}},
            {'data': d3, 'points': {'show': 'true'}},
            {'data': d4, 'lines': {'show': 'true'}},
            {'data': d5, 'lines': {'show': 'true'}, 'points' : {'show': 'true'}}
        ], 'options': {'yaxis' : { 'max' : '15' }}
        }]
        self.send('/topic/flot_example', json.encode(flot_data))

reactor.connectTCP('localhost', 61613, MokshaHub())
reactor.run()
