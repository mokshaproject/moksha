#!/usr/bin/env python

from moksha.hub import MokshaHub, find_hub_extensions
from moksha.tests.test_hub import simulate_reactor

from pprint import pprint
import time

if __name__ == '__main__':
    print "Benchmarking MokshaHub with the following parents:"
    pprint(find_hub_extensions())

    delta_time = 0.00001

    hub = MokshaHub()
    received = []
    def callback(msg):
        received.append(msg)

    print "Subscribing consumer callback."
    hub.subscribe("foo", callback)
    simulate_reactor(1)

    n = 10000
    print "Sending", n, "messages."
    t1 = time.time()
    for i in range(n):
        hub.send_message("foo", str(i))

    t2 = time.time()
    while len(received) < n:
        print "waiting.", len(received)
        simulate_reactor(delta_time)

    t3 = time.time()

    hub.close()

    print '-' * 40
    d1 = t2 - t1
    d2 = t3 - t1
    print d1, "seconds to send", n, "messages.", n / d1, "msgs per second."
    print d2, "seconds from until last message received.",
    print n / d2, "msgs per second."

