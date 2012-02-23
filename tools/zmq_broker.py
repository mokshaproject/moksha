#!/usr/bin/env python
""" This is a dummy ZMQ "broker" for use in the speed test.

It is really not a broker, but more a 'repeater'.  It simply listens on one
port and echos those messages back out another port.

    Author: Ralph Bean <rbean@redhat.com>
"""

import zmq

def main():
    context = zmq.Context(1)
    subscriber = context.socket(zmq.SUB)
    subscriber.connect("tcp://127.0.0.1:6500")
    subscriber.setsockopt(zmq.SUBSCRIBE, "")

    publisher = context.socket(zmq.PUB)
    publisher.bind("tcp://*:9500")

    try:
        while True:
            msg = subscriber.recv_multipart()
            publisher.send_multipart(msg)

    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        subscriber.close()
        publisher.close()
        context.term


if __name__ == '__main__':
    main()


