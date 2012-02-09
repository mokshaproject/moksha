import inspect
import pkg_resources

from datetime import timedelta

from moksha.api.hub.producer import PollingProducer
from moksha.pastetemplate import MokshaStreamTemplate

from base import QuickstartTester, setup_quickstart, teardown_quickstart

app = None

def setup():
    template = MokshaStreamTemplate
    templates = ['moksha.stream']
    template_vars = {
            'package': 'mokshatest',
            'project': 'mokshatest',
            'egg': 'mokshatest',
            'egg_plugins': ['Moksha'],
            'topic': 'moksha.topics.test',
    }
    args = {
        'stream': True,
        'stream_name': 'MokshatestStream',
    }
    global app
    app = setup_quickstart(template=template, templates=templates, args=args,
                           template_vars=template_vars)

def teardown():
    teardown_quickstart()



class TestStreamQuickstart(QuickstartTester):

    def setUp(self):
        self.app = app

    def get_stream(self):
        return self.get_entry('moksha.stream')

    def test_index(self):
        resp = self.app.get('/')
        assert '[ Moksha ]' in resp

    def test_entry_point(self):
        assert self.get_stream(), \
                "Cannot find MokshatestStream on `moksha.stream` entry-point"

    def test_polling_datastream(self):
        stream = self.get_stream()
        assert isinstance(stream, PollingProducer) or \
               issubclass(stream, PollingProducer)

    def test_stream_frequency(self):
        stream = self.get_stream()
        assert hasattr(stream, 'frequency'), "No frequency specified"
        assert isinstance(stream.frequency, (int, float, timedelta))

    def test_stream_poll(self):
        stream = self.get_stream()
        assert hasattr(stream, 'poll'), "No poll method specified"
