"""Test Moksha's Hub """

from nose.tools import eq_, assert_true
from moksha.hub import MokshaHub

class TestHub:

    def setUp(self):
        self.hub = MokshaHub()

    def tearDown(self):
        self.hub.close()

    def test_creating_queue(self):
        self.hub.create_queue('test')
        eq_(len(self.hub.queues), 1)

    def test_delete_queue(self):
        """ Test deleting a queue """
    def test_subscription(self):
        """ Test subscribing to a queue """
    def test_unsubscribing(self):
        """ Test unsubscribing to a queue """
    def test_sending_message(self):
        """ Test sending a simple message """
    def test_receiving_message(self):
        """ Test receiving a message """
    def test_query(self):
        """ Test querying queues """
