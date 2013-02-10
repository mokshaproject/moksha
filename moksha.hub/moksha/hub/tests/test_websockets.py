# This file is part of Moksha.
# Copyright (C) 2008-2013  Red Hat, Inc.
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

""" Test Moksha's Websocket Server.

ZeroMQ only for now.
"""

import moksha
import json
import websocket
import copy

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from time import sleep, time
from uuid import uuid4

from moksha.hub.hub import CentralMokshaHub
from moksha.hub.reactor import reactor as _reactor
from nose.tools import eq_, assert_true, assert_false, raises


# TODO -- these are duplicated in test_hub.. they should be imported
# Some constants used throughout the hub tests
sleep_duration = 0.25
secret = "secret_message"


# TODO -- this is duplicated in test_hub.  It should be imported from a common
# place.
def simulate_reactor(duration=sleep_duration):
    """ Simulate running the reactor for `duration` milliseconds """
    global _reactor
    start = time()
    while time() - start < duration:
        _reactor.doPoll(0.0001)
        _reactor.runUntilCurrent()


class TestWat(unittest.TestCase):

    def setUp(self):
        config = {
            'moksha.livesocket': True,
            'moksha.livesocket.backend': 'websocket',
            'moksha.socket.notify': True,
            'moksha.livesocket.websocket.port': 8009,
            "zmq_publish_endpoints": "tcp://*:6543",
            "zmq_subscribe_endpoints": "tcp://127.0.0.1:6543",
            "zmq_enabled": True,
            'zmq_strict': False,
        }
        self.hub = CentralMokshaHub(config=config)
        self.topic = str(uuid4())

    def tearDown(self):
        self.hub.close()

    def test_ws_subscribe_and_recv(self):
        """ Test that we can subscribe for and receive a message. """

        # Do this in order to process the connection
        simulate_reactor(sleep_duration)

        self.received_message = None
        import threading

        class client_thread(threading.Thread):
            def run(thread):
                ws = websocket.WebSocket()
                ws.settimeout(5)
                ws.connect("ws://127.0.0.1:{port}/".format(
                    port=self.hub.config['moksha.livesocket.websocket.port'],
                ))

                ws.send(json.dumps(dict(
                    topic="__topic_subscribe__",
                    body=self.topic,
                )))

                # Receive that..
                self.received_message = json.loads(ws.recv())['body']
                ws.close()

        client = client_thread()
        client.start()

        # Process the connection from the client-thread.
        simulate_reactor(sleep_duration)

        # Now, send a message...
        self.hub.send_message(
            topic=self.topic,
            message=secret,
        )

        # Process the sending of our special message.
        simulate_reactor(sleep_duration)

        client.join()
        eq_(self.received_message, secret)


if __name__ == '__main__':
    unittest.main()
