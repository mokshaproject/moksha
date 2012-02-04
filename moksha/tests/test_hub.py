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


class TestHub:

    def setUp(self):
        self.hub = MokshaHub()

    def tearDown(self):
        self.hub.close()

    def test_hub_creation(self):
        assert_true(self.hub)
        eq_(self.hub.topics, {})

    def test_hub_send_recv(self):
        "Test that we can send a message and receive it."

        secret = str(uuid4())
        messages_received = []

        def callback(json):
            messages_received.append(json.body[1:-1])

        self.hub.subscribe(topic="foobar", callback=callback)
        self.hub.send_message(topic="foobar", message=secret)
        sleep(1)
        eq_(messages_received, [secret])

    def test_hub_no_subscription(self):
        "Test that if we don't receive messages we're not subscribed for."

        secret = str(uuid4())
        messages_received = []

        def callback(json):
            messages_received.append(json.body[1:-1])

        self.hub.send_message(topic="foobar", message=secret)
        sleep(1)
        eq_(messages_received, [])
