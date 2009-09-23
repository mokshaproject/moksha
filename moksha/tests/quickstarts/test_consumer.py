import inspect
import pkg_resources

from datetime import timedelta

from moksha.api.hub import Consumer
from moksha.pastetemplate import MokshaConsumerTemplate

from base import QuickstartTester

class TestConsumerQuickstart(QuickstartTester):

    def __init__(self,**options):
        self.app = None
        self.template_vars = {
                'package': 'mokshatest',
                'project': 'mokshatest',
                'egg': 'mokshatest',
                'egg_plugins': ['Moksha'],
                'topic': 'moksha.topics.test',
        }
        self.args = {
            'consumer': True,
            'consumer_name': 'MokshatestConsumer',
        }
        self.template = MokshaConsumerTemplate
        self.templates = ['moksha.consumer']

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
