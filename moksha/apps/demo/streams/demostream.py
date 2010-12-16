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
:deprecated: This module was used for some very early Moksha demos, and generates a lot of useless data.  This has since been deprecated by a more useful, self-aware, Moksha demo.

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

import math
from random import random
from datetime import timedelta

from moksha.api.widgets.feed import Feed
from moksha.api.streams import PollingDataStream

class MokshaDemoDataStream(PollingDataStream):
    """
    This class provides the default Moksha demo with some fake data to render
    """

    frequency = timedelta(seconds=0.5)

    # Flot demo specific variables
    offset = 0.0
    skip = 0
    bars = [[0, 3], [4, 8], [8, 5], [9, 13]]
    n = 0

    # Feed demo specific variables
    i = 0

    def __init__(self, *args, **kw):
        self.feed = Feed(url='http://doggdot.us/rss')
        self.feed_entries = self.feed.entries()
        super(MokshaDemoDataStream, self).__init__(*args, **kw)

    def poll(self):
        self.n += 1

        if self.n % 3 == 0:
            self.i += 1
            entry = self.feed_entries[self.n % len(self.feed_entries)]
            self.send_message('feed_demo', [
                {'title': entry['title'], 'link': entry['link'], 'i': self.i},
            ])

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

        self.send_message('flot_demo', flot_data)

    def stop(self):
        self.feed.close()
        super(MokshaDemoDataStream, self).stop()
