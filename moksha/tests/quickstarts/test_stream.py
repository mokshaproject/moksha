import inspect
import pkg_resources

from datetime import timedelta

from moksha.api.streams import PollingDataStream
from moksha.pastetemplate import MokshaStreamTemplate

from base import QuickstartTester

class TestStreamQuickstart(QuickstartTester):

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
            'stream': True,
            'stream_name': 'MokshatestStream',
        }
        self.template = MokshaStreamTemplate
        self.templates = ['moksha.stream']

    def test_index(self):
        resp = self.app.get('/')
        assert '[ Moksha ]' in resp

    def get_entry(self):
        for stream in pkg_resources.working_set.iter_entry_points('moksha.stream'):
            stream_class = stream.load()
            if inspect.isclass(stream_class):
                name = stream_class.__name__
            else:
                name = stream_class.__class__.__name__
            if name == 'MokshatestStream':
                return stream_class

    def test_entry_point(self):
        assert self.get_entry(), \
                "Cannot find MokshatestStream on `moksha.stream` entry-point"

    def test_polling_datastream(self):
        stream = self.get_entry()
        assert isinstance(stream, PollingDataStream) or \
               issubclass(stream, PollingDataStream)

    def test_stream_frequency(self):
        stream = self.get_entry()
        assert hasattr(stream, 'frequency'), "No frequency specified"
        assert isinstance(stream.frequency, (int, float, timedelta))

    def test_stream_poll(self):
        stream = self.get_entry()
        assert hasattr(stream, 'poll'), "No poll method specified"
