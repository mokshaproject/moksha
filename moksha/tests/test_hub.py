"""Test Moksha's Hub """

from nose.tools import eq_, assert_true
from moksha import hub

class TestHub:

    def setUp(self):
        self.hub = moksha.hub.MokshaHub()

    def tearDown(self):
        self.hub.close()

    def test_hub_creation(self):
        assert_true(self.hub)
        eq_(self.hub.topics, {})
