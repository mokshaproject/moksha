import inspect
import pkg_resources

from datetime import timedelta

from moksha.api.hub import Consumer
from moksha.pastetemplate import MokshaConsumerTemplate

from base import QuickstartTester, setup_quickstart, teardown_quickstart

app = None

def setup():
    template = MokshaConsumerTemplate
    templates = ['moksha.consumer']
    template_vars = {
            'package': 'mokshatest',
            'project': 'mokshatest',
            'egg': 'mokshatest',
            'egg_plugins': ['Moksha'],
            'topic': 'moksha.topics.test',
    }
    args = {
        'consumer': True,
        'consumer_name': 'MokshatestConsumer',
    }
    global app
    app = setup_quickstart(template=template, templates=templates, args=args,
                           template_vars=template_vars)


def teardown():
    teardown_quickstart()


class TestConsumerQuickstart(QuickstartTester):

    def setUp(self):
        self.app = app

    def get_consumer(self):
        return self.get_entry('moksha.consumer')

    def test_entry_point(self):
        assert self.get_consumer(), \
                "Cannot find mokshatest on `moksha.consumer` entry-point"

    def test_polling_dataconsumer(self):
        consumer = self.get_consumer()
        print consumer
        assert isinstance(consumer, Consumer) or \
               issubclass(consumer, Consumer)

    def test_consumer_topic(self):
        """ Ensure the Consumer has a topic """
        consumer = self.get_consumer()
        assert hasattr(consumer, 'topic')

    def test_consumer_consume(self):
        """ Ensure our Consumer has a `consume` method """
        consumer = self.get_consumer()
        assert hasattr(consumer, 'consume')
