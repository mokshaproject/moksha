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


class TestWebSocketServer(unittest.TestCase):

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

        if hasattr(self.hub, 'websocket_server'):
            retval = self.hub.websocket_server.stopListening()

        # It can take some time to unregister our WS server from its port
        simulate_reactor(sleep_duration)

    def test_ws_subscribe_and_recv(self):
        """ Test that we can subscribe for and receive a message. """

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
                message = ws.recv().decode('utf-8')
                self.received_message = json.loads(message)['body']
                ws.close()

        client = client_thread()
        client.start()

        # Process the connection from the client-thread.
        simulate_reactor(sleep_duration)
        sleep(sleep_duration)
        simulate_reactor(sleep_duration)

        # Now, send a message...
        self.hub.send_message(
            topic=self.topic,
            message=secret,
        )

        # Process the sending of our special message.
        simulate_reactor(sleep_duration)
        sleep(sleep_duration)
        simulate_reactor(sleep_duration)

        client.join()
        eq_(self.received_message, secret)

    def test_ws_subscribe_multiple(self):
        """ Test that we can subscribe to a few different topics. """

        self.received_messages = []
        import threading

        num_topics = 3

        class client_thread(threading.Thread):
            def run(thread):
                ws = websocket.WebSocket()
                ws.settimeout(5)
                ws.connect("ws://127.0.0.1:{port}/".format(
                    port=self.hub.config['moksha.livesocket.websocket.port'],
                ))

                for i in range(num_topics):
                    ws.send(json.dumps(dict(
                        topic="__topic_subscribe__",
                        body=self.topic + "_" + str(i),
                    )))

                # Receive that..
                for i in range(num_topics):
                    try:
                        self.received_messages.append(
                            json.loads(ws.recv().decode('utf-8'))['body']
                        )
                    except Exception:
                        pass

                ws.close()

        client = client_thread()
        client.start()

        # Process the connection from the client-thread.
        simulate_reactor(sleep_duration)
        sleep(sleep_duration)
        simulate_reactor(sleep_duration)

        # Now, send a message...
        for i in range(num_topics):
            self.hub.send_message(
                topic=self.topic + "_" + str(i),
                message=secret,
            )

        # Process the sending of our special message.
        simulate_reactor(sleep_duration)
        sleep(sleep_duration)
        simulate_reactor(sleep_duration)

        client.join()
        eq_(self.received_messages, [secret] * num_topics)

    def test_ws_subscribe_filter(self):
        """ Test that the WS server only sends desired topics. """

        self.received_messages = []
        import threading

        num_topics = 1

        class client_thread(threading.Thread):
            def run(thread):
                ws = websocket.WebSocket()
                ws.settimeout(5)
                ws.connect("ws://127.0.0.1:{port}/".format(
                    port=self.hub.config['moksha.livesocket.websocket.port'],
                ))

                for i in range(num_topics):
                    ws.send(json.dumps(dict(
                        topic="__topic_subscribe__",
                        body=self.topic + "_" + str(i),
                    )))

                # Receive that..
                for i in range(num_topics + 1):
                    try:
                        self.received_messages.append(
                            json.loads(ws.recv().decode('utf-8'))['body']
                        )
                    except Exception:
                        pass

                ws.close()

        client = client_thread()
        client.start()

        # Process the connection from the client-thread.
        simulate_reactor(sleep_duration)
        sleep(sleep_duration)
        simulate_reactor(sleep_duration)

        # Now, send a message...
        for i in range(num_topics + 1):
            self.hub.send_message(
                topic=self.topic + "_" + str(i),
                message=secret,
            )

        # Process the sending of our special message.
        simulate_reactor(sleep_duration)
        sleep(sleep_duration)
        simulate_reactor(sleep_duration)

        client.join()
        eq_(self.received_messages, [secret] * num_topics)

    def test_ws_multiple_clients_different_topics(self):
        """ Test that the WS server can differentiate clients. """

        import threading

        num_topics = 2

        class client_thread(threading.Thread):
            def run(thread):
                thread.received_messages = []
                ws = websocket.WebSocket()
                ws.settimeout(5)
                ws.connect("ws://127.0.0.1:{port}/".format(
                    port=self.hub.config['moksha.livesocket.websocket.port'],
                ))

                for i in range(num_topics):
                    ws.send(json.dumps(dict(
                        topic="__topic_subscribe__",
                        body=thread.topic + "_" + str(i),
                    )))

                # Receive that..
                for i in range(num_topics + 2):
                    try:
                        thread.received_messages.append(
                            json.loads(ws.recv().decode('utf-8'))['body']
                        )
                    except Exception:
                        pass

                ws.close()

        client1 = client_thread()
        client2 = client_thread()
        client1.topic = self.topic + "_topic_1"
        client2.topic = self.topic + "_topic_2"
        client1.received_messages = []
        client2.received_messages = []
        client1.start()
        client2.start()

        # Process the connection from the client-thread.
        simulate_reactor(sleep_duration)
        sleep(sleep_duration)
        simulate_reactor(sleep_duration)

        # Now, send a message...
        for i in range(num_topics):
            self.hub.send_message(
                topic=self.topic + "_topic_1" + "_" + str(i),
                message=secret + "_1",
            )
            self.hub.send_message(
                topic=self.topic + "_topic_2" + "_" + str(i),
                message=secret + "_2",
            )

        # Process the sending of our special message.
        simulate_reactor(sleep_duration)
        sleep(sleep_duration)
        simulate_reactor(sleep_duration)

        client1.join()
        client2.join()
        eq_(client1.received_messages, [secret + "_1"] * num_topics)
        eq_(client2.received_messages, [secret + "_2"] * num_topics)


if __name__ == '__main__':
    unittest.main()
