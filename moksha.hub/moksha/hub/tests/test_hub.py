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

import threading
import moksha

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from time import sleep, time
from uuid import uuid4
from kitchen.iterutils import iterate

import moksha.common.testtools.utils as testutils

import moksha.hub.api
from moksha.hub.hub import MokshaHub, CentralMokshaHub
from moksha.hub.reactor import reactor as _reactor
from nose.tools import (eq_, assert_true, assert_false)


# Some constants used throughout the hub tests
sleep_duration = 0.25
secret = "secret_message"


def simulate_reactor(duration=sleep_duration):
    """ Simulate running the reactor for `duration` milliseconds """
    global _reactor
    start = time()
    while time() - start < duration:
        _reactor.doPoll(0.0001)
        _reactor.runUntilCurrent()


class TestHub(unittest.TestCase):

    def _setUp(self):
        def kernel(config):
            self.hub = MokshaHub(config=config)
            self.topic = str(uuid4())

        for __setup, name in testutils.make_setup_functions(kernel):
            yield __setup, name

    def _tearDown(self):
        self.hub.close()

    @testutils.crosstest
    def test_hub_creation(self):
        """ Test that we can simply create the hub. """
        assert_true(self.hub)
        eq_(self.hub.topics, {})

    @testutils.crosstest
    def test_hub_send_recv(self):
        "Test that we can send a message and receive it."

        messages_received = []

        def callback(json):
            messages_received.append(json.body[1:-1])

        self.hub.subscribe(topic=self.topic, callback=callback)
        sleep(sleep_duration)

        self.hub.send_message(topic=self.topic, message=secret)

        simulate_reactor(sleep_duration)
        sleep(sleep_duration)

        eq_(messages_received, [secret])

    @testutils.crosstest
    def test_hub_no_subscription(self):
        "Test that we don't receive messages we're not subscribed for."

        messages_received = []

        def callback(json):
            messages_received.append(json.body[1:-1])

        self.hub.send_message(topic=self.topic, message=secret)
        simulate_reactor(sleep_duration)
        sleep(sleep_duration)
        eq_(messages_received, [])


class TestConsumer:

    def _setUp(self):
        def kernel(config):
            self.hub = MokshaHub(config=config)
            self.a_topic = str(uuid4())

        for __setup, name in testutils.make_setup_functions(kernel):
            yield __setup, name

    def _tearDown(self):
        self.hub.close()

    def fake_register_consumer(self, cons):
        """ Fake register a consumer, not by entry-point like usual.

        Normally, consumers are identified by the hub by way of entry-points
        Ideally, this test would register the TestConsumer on the
        moksha.consumers entry point, and the hub would pick it up.
        I'm not sure how to do that, so we're going to fake it and manually
        add this consumer to the list of consumers of which the Hub is aware.
        """
        consume = cons(self.hub).consume
        for topic in iterate(cons.topic):
            self.hub.topics[topic] = self.hub.topics.get(topic, [])
            if consume not in self.hub.topics[topic]:
                print('registering fake topic %r' % topic)
                self.hub.topics[topic].append(consume)
        sleep(sleep_duration)

    @testutils.crosstest
    def test_abstract(self):
        """ Ensure that conumsers with no consume method raise exceptions. """

        class StillAbstractConsumer(moksha.hub.api.consumer.Consumer):
            pass

        try:
            c = StillAbstractConsumer(self.hub)
            c.consume("foo")
            assert(False)
        except NotImplementedError as e:
            pass

    @testutils.crosstest
    def test_receive_without_json(self):
        """ Try sending/receiving messages without jsonifying. """

        messages_received = []

        class TestConsumer(moksha.hub.api.consumer.Consumer):
            jsonify = False
            topic = self.a_topic

            def _consume(self, message):
                messages_received.append(message)

        self.fake_register_consumer(TestConsumer)

        # Now, send a generic message to that topic, and see if we get one.
        self.hub.send_message(topic=self.a_topic, message=secret)
        simulate_reactor(sleep_duration)
        sleep(sleep_duration)
        eq_(len(messages_received), 1)

    @testutils.crosstest
    def test_receive_str(self):
        """ Send a message  Consume and verify it. """

        messages_received = []

        class TestConsumer(moksha.hub.api.consumer.Consumer):
            topic = self.a_topic

            def _consume(self, message):
                messages_received.append(message['body'])

        self.fake_register_consumer(TestConsumer)

        # Now, send a generic message to that topic, and see if the consumer
        # processed it.
        self.hub.send_message(topic=self.a_topic, message=secret)
        simulate_reactor(sleep_duration)
        sleep(sleep_duration)
        eq_(messages_received, [secret])

    @testutils.crosstest
    def test_receive_str_double(self):
        """ Send a message.  Have two consumers consume it. """

        messages_received = []

        class TestConsumer1(moksha.hub.api.consumer.Consumer):
            topic = self.a_topic

            def _consume(self, message):
                messages_received.append(message['body'])

        class TestConsumer2(moksha.hub.api.consumer.Consumer):
            topic = self.a_topic

            def _consume(self, message):
                messages_received.append(message['body'])

        self.fake_register_consumer(TestConsumer1)
        self.fake_register_consumer(TestConsumer2)

        # Now, send a generic message to that topic, and see if the consumer
        # processed it.
        self.hub.send_message(topic=self.a_topic, message=secret)
        simulate_reactor(sleep_duration)
        sleep(sleep_duration)
        eq_(messages_received, [secret, secret])

    @testutils.crosstest
    def test_receive_str_near_miss(self):
        """ Send a message.  Three consumers.  Only one receives. """

        messages_received = []

        class BaseConsumer(moksha.hub.api.consumer.Consumer):
            topic = self.a_topic

            def _consume(self, message):
                messages_received.append(message['body'])

        class Consumer1(BaseConsumer):
            pass

        class Consumer2(BaseConsumer):
            topic = BaseConsumer.topic[:-1]

        class Consumer3(BaseConsumer):
            topic = BaseConsumer.topic + "X"

        self.fake_register_consumer(Consumer1)
        self.fake_register_consumer(Consumer2)
        self.fake_register_consumer(Consumer3)

        # Now, send a generic message to that topic, and see if Consumer1
        # processed it but that Consumer2 and Consumer3 didn't
        self.hub.send_message(topic=self.a_topic, message=secret)
        simulate_reactor(sleep_duration)
        sleep(sleep_duration)
        eq_(messages_received, [secret])

    @testutils.crosstest
    def test_receive_dict(self):
        """ Send a dict with a message.  Consume, extract, and verify it. """

        obj = {'secret': secret}
        messages_received = []

        class TestConsumer(moksha.hub.api.consumer.Consumer):
            topic = self.a_topic

            def _consume(self, message):
                obj = message['body']
                messages_received.append(obj['secret'])

        self.fake_register_consumer(TestConsumer)

        # Now, send a generic message to that topic, and see if the consumer
        # processed it.
        self.hub.send_message(topic=self.a_topic, message=obj)
        simulate_reactor(sleep_duration)
        sleep(sleep_duration)
        eq_(messages_received, [secret])

    @testutils.crosstest
    def test_receive_n_messages(self):
        """ Send `n` messages, receive `n` messages. """

        n_messages = 10
        messages_received = []

        class TestConsumer(moksha.hub.api.consumer.Consumer):
            topic = self.a_topic

            def _consume(self, message):
                messages_received.append(message['body'])

        self.fake_register_consumer(TestConsumer)

        # Now, send n messages and make sure that n messages were consumed.
        for i in range(n_messages):
            self.hub.send_message(topic=self.a_topic, message=secret)

        simulate_reactor(sleep_duration)
        sleep(sleep_duration)

        eq_(len(messages_received), n_messages)

    @testutils.crosstest
    def test_receive_n_dicts(self):
        """ Send `n` dicts, receive `n` dicts. """

        n_messages = 10
        obj = {'secret': secret}
        messages_received = []

        class TestConsumer(moksha.hub.api.consumer.Consumer):
            topic = self.a_topic

            def _consume(self, message):
                messages_received.append(message['body'])

        self.fake_register_consumer(TestConsumer)

        # Now, send n objects and make sure that n objects were consumed.
        for i in range(n_messages):
            self.hub.send_message(topic=self.a_topic, message=obj)

        simulate_reactor(sleep_duration)
        sleep(sleep_duration)

        eq_(len(messages_received), n_messages)

    @testutils.crosstest
    def test_multiple_topics(self):
        """ Send a message to multiple topics. """
        n_messages = 2
        obj = {'secret': secret}
        messages_received = []
        b_topic = str(uuid4())

        class TestConsumer(moksha.hub.api.consumer.Consumer):
            topic = [self.a_topic, b_topic]

            def _consume(self, message):
                messages_received.append(message['body'])

        self.fake_register_consumer(TestConsumer)

        self.hub.send_message(topic=self.a_topic, message=obj)
        self.hub.send_message(topic=b_topic, message=obj)

        simulate_reactor(sleep_duration)
        sleep(sleep_duration)

        eq_(len(messages_received), n_messages)

    @testutils.crosstest
    def test_dynamic_topic(self):
        """ Test that a topic can be set at runtime (not import time) """

        class TestConsumer(moksha.hub.api.consumer.Consumer):
            topic = "bad topic"

            def __init__(self, *args, **kw):
                super(TestConsumer, self).__init__(*args, **kw)
                self.topic = "good topic"

            def _consume(self, message):
                pass

        # Just a little fake config.
        config = dict(
            zmq_enabled=True,
            zmq_subscribe_endpoints='',
            zmq_published_endpoints='',
        )
        central = CentralMokshaHub(config, [TestConsumer], [])

        # Guarantee that "bad topic" is not in the topics list.
        eq_(list(central.topics.keys()), ["good topic"])

    @testutils.crosstest
    def test_open_and_close(self):
        """ Test that a central hub with a consumer can be closed.. ;) """

        class TestConsumer(moksha.hub.api.consumer.Consumer):
            topic = "whatever"

            def _consume(self, message):
                pass

        # Just a little fake config.
        config = dict(
            zmq_enabled=True,
            zmq_subscribe_endpoints='',
            zmq_published_endpoints='',
        )
        central = CentralMokshaHub(config, [TestConsumer], [])
        central.close()


class TestProducer:
    def _setUp(self):
        def kernel(config):
            self.hub = MokshaHub(config=config)
            self.a_topic = a_topic = str(uuid4())

        for __setup, name in testutils.make_setup_functions(kernel):
            yield __setup, name

    def _tearDown(self):
        self.hub.close()

    def fake_register_producer(self, prod):
        """ Fake register a producer, not by entry-point like usual.

        Registering producers is a little easier than registering consumers.
        The MokshaHub doesn't even keep track of the .poll method callbacks.
        We simply instantiate the producer (and it registers itself with the
        hub).
        """
        return prod(self.hub)

    @testutils.crosstest
    def test_produce_ten_strs(self):
        """ Produce ten-ish strings. """

        messages_received = []

        class TestProducer(moksha.hub.api.producer.PollingProducer):
            topic = self.a_topic
            frequency = sleep_duration / 10.9
            called = 0

            def poll(self):
                self.called = self.called + 1

        # Ready?
        prod = self.fake_register_producer(TestProducer)

        def killer():
            sleep(sleep_duration)
            prod.die = True

        threading.Thread(target=killer).start()
        prod._work()

        # Finally, the check.  Did we get our ten messages? (or about as much)
        assert prod.called > 8
        assert prod.called < 12

    @testutils.crosstest
    def test_idempotence(self):
        """ Test that running the same test twice still works. """
        return self.test_produce_ten_strs()
