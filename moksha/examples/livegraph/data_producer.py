#!/usr/bin/env python
from stompservice import StompClientFactory
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from random import random
from orbited import json

DATA_VECTOR_LENGTH = 10
DELTA_WEIGHT = 0.1
MAX_VALUE = 400 # NB: this in pixels
CHANNEL_NAME = "/topic/graph"
INTERVAL = 1000 # in ms

class DataProducer(StompClientFactory):

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

reactor.connectTCP('localhost', 61613, DataProducer())
reactor.run()
