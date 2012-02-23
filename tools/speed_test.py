#!/usr/bin/env python
""" Speed test script for evaluating amqp and zmq.

Run this with amqp enabled in `development.ini` and again with zmq enabled.
At the time this script was authored, zmq appeared to be (in the raw) ~85 times
faster than amqp.

In order to make things 'fair', you can stand up and run the
``tools/zmq_broker.py`` script to act as a zmq repeater (a fake broker) for the
moksha-hub.  This way, twice as many zmq messages need to be sent (as is the
case in amqp where the broker (qpidd) is mandatory).  In this case, zmq appeared
to be ~65 times faster than amqp.

    Author: Ralph Bean <rbean@redhat.com>

"""

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

