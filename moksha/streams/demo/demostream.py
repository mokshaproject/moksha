import math
from random import random
from datetime import timedelta

from moksha.api.widgets.feed import Feed
from moksha.api.streams import PollingDataStream

class MokshaDemoDataStream(PollingDataStream):
    """
    This class provides the default Moksha demo with some fake data to render
    """

    frequency = timedelta(seconds=1)

    # Flot demo specific variables
    offset = 0.0
    skip = 0
    bars = [[0, 3], [4, 8], [8, 5], [9, 13]]
    n = 0

    # Specific to the livegraph demo
    data_vector_length = 10
    delta_weight = 0.1
    max_value = 400 # NB: this in pixels
    data = [int(random()*max_value) for x in xrange(data_vector_length)]

    # Feed demo specific variables
    feed_entries = Feed(url='http://lewk.org/rss').entries()
    i = 0

    def poll(self):
        self.n += 1

        if self.n % 3 == 0:
            self.i += 1
            entry = self.feed_entries[self.n % len(self.feed_entries)]
            self.send_message('feed_demo', [
                {'title': entry['title'], 'link': entry['link'], 'i': self.i},
            ])

        # modify our data elements
        if self.n % 2 == 0: # make the graph look independent of flot
            self.data = [ 
                min(max(datum+(random()-.5)*self.delta_weight*self.max_value ,0),self.max_value)
                for 
                datum in self.data
            ]
            self.send_message('graph_demo', self.data)

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
