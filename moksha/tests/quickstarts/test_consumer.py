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

    def get_entry(self):
        for consumer in pkg_resources.working_set.iter_entry_points('moksha.consumer'):
            consumer_class = consumer.load()
            if inspect.isclass(consumer_class):
                name = consumer_class.__name__
            else:
                name = consumer_class.__class__.__name__
            if name == 'MokshatestConsumer':
                return consumer_class

    def test_entry_point(self):
        assert self.get_entry(), \
                "Cannot find MokshatestConsumer on `moksha.consumer` entry-point"

    def test_polling_dataconsumer(self):
        consumer = self.get_entry()
        assert isinstance(consumer, Consumer) or \
               issubclass(consumer, Consumer)

    def test_consumer_topic(self):
        """ Ensure the Consumer has a topic """
        consumer = self.get_entry()
        assert hasattr(consumer, 'topic')

    def test_consumer_consume(self):
        """ Ensure our Consumer has a `consume` method """
        consumer = self.get_entry()
        assert hasattr(consumer, 'consume')
