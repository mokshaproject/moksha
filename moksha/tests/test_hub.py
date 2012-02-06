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

"""Test Moksha's Hub """

import moksha

from time import sleep
from uuid import uuid4

from moksha.hub import MokshaHub
from nose.tools import eq_, assert_true, assert_false


# Some constants used throughout the hub tests
sleep_duration = 0.5
secret = "secret_message"


class TestHub:

    def setUp(self):
        self.hub = MokshaHub()
        self.topic = str(uuid4())

    def tearDown(self):
        self.hub.close()

    def test_hub_creation(self):
        assert_true(self.hub)
        eq_(self.hub.topics, {})

    def test_hub_send_recv(self):
        "Test that we can send a message and receive it."

        messages_received = []

        def callback(json):
            messages_received.append(json.body[1:-1])

        self.hub.subscribe(topic=self.topic, callback=callback)
        self.hub.send_message(topic=self.topic, message=secret)
        sleep(sleep_duration)
        eq_(messages_received, [secret])

    def test_hub_no_subscription(self):
        "Test that if we don't receive messages we're not subscribed for."

        messages_received = []

        def callback(json):
            messages_received.append(json.body[1:-1])

        self.hub.send_message(topic=self.topic, message=secret)
        sleep(sleep_duration)
        eq_(messages_received, [])


class TestConsumer:

    def setUp(self):
        self.hub = MokshaHub()
        self.a_topic = a_topic = str(uuid4())

    def tearDown(self):
        self.hub.close()

    def fake_register_consumer(self, cons):
        """ Fake register a consumer, not by entry-point like usual.

        Normally, consumers are identified by the hub by way of entry-points
        Ideally, this test would register the TestConsumer on the
        moksha.consumers entry point, and the hub would pick it up.
        I'm not sure how to do that, so we're going to fake it and manually
        add this consumer to the list of consumers of which the Hub is aware.
        """
        self.hub.topics[cons.topic] = self.hub.topics.get(cons.topic, [])
        self.hub.topics[cons.topic].append(cons().consume)

    def test_abstract(self):
        """ Ensure that conumsers with no consume method raise exceptions. """

        class StillAbstractConsumer(moksha.api.hub.consumer.Consumer):
            pass

        try:
            c = StillAbstractConsumer()
            c.consume("foo")
            assert(False)
        except NotImplementedError as e:
            pass

    def test_receive_without_json(self):
        """ Try sending/receiving messages without jsonifying. """

        messages_received = []

        class TestConsumer(moksha.api.hub.consumer.Consumer):
            jsonify = False
            topic = self.a_topic

            def consume(self, message):
                messages_received.append(message)

        self.fake_register_consumer(TestConsumer)

        # Now, send a generic message to that topic, and see if we get one.
        self.hub.send_message(topic=self.a_topic, message=secret)
        sleep(sleep_duration)
        eq_(len(messages_received), 1)

    def test_receive_str(self):
        """ Send a message  Consume and verify it. """

        messages_received = []

        class TestConsumer(moksha.api.hub.consumer.Consumer):
            topic = self.a_topic

            def consume(self, message):
                messages_received.append(message['body'])

        self.fake_register_consumer(TestConsumer)

        # Now, send a generic message to that topic, and see if the consumer
        # processed it.
        self.hub.send_message(topic=self.a_topic, message=secret)
        sleep(sleep_duration)
        eq_(messages_received, [secret])

    def test_receive_dict(self):
        """ Send a dict with a message.  Consume, extract, and verify it. """

        obj = {'secret': secret}
        messages_received = []

        class TestConsumer(moksha.api.hub.consumer.Consumer):
            topic = self.a_topic

            def consume(self, message):
                obj = message['body']
                messages_received.append(obj['secret'])

        self.fake_register_consumer(TestConsumer)

        # Now, send a generic message to that topic, and see if the consumer
        # processed it.
        self.hub.send_message(topic=self.a_topic, message=obj)
        sleep(sleep_duration)
        eq_(messages_received, [secret])

    def test_receive_n_messages(self):
        """ Send `n` messages, receive `n` messages. """

        n_messages = 10
        messages_received = []

        class TestConsumer(moksha.api.hub.consumer.Consumer):
            topic = self.a_topic

            def consume(self, message):
                messages_received.append(message['body'])

        self.fake_register_consumer(TestConsumer)

        # Now, send n messages and make sure that n messages were consumed.
        for i in range(n_messages):
            self.hub.send_message(topic=self.a_topic, message=secret)

        sleep(sleep_duration)
        eq_(len(messages_received), n_messages)

    def test_receive_n_dicts(self):
        """ Send `n` dicts, receive `n` dicts. """

        n_messages = 10
        obj = {'secret': secret}
        messages_received = []

        class TestConsumer(moksha.api.hub.consumer.Consumer):
            topic = self.a_topic

            def consume(self, message):
                messages_received.append(message['body'])

        self.fake_register_consumer(TestConsumer)

        # Now, send n objects and make sure that n objects were consumed.
        for i in range(n_messages):
            self.hub.send_message(topic=self.a_topic, message=obj)

        sleep(sleep_duration)
        eq_(len(messages_received), n_messages)
