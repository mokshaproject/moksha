#!/usr/bin/env python
import math
from stompservice import StompClientFactory
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from random import random
from orbited import json

DATA_VECTOR_LENGTH = 10
DELTA_WEIGHT = 0.1
MAX_VALUE = 400 # NB: this in pixels
CHANNEL_NAME = "/topic/graph"
#INTERVAL = 1000 # in ms
INTERVAL = 300 # in ms

class DataProducer(StompClientFactory):

    username = 'guest'
    password = 'guest'

    # Flot demo specific variables
    offset = 0.0
    skip = 0
    bars = [[0, 3], [4, 8], [8, 5], [9, 13]]

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
        # modify our data elements
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

reactor.connectTCP('localhost', 61613, DataProducer())
reactor.run()
