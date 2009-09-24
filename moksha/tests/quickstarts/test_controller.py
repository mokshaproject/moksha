import inspect
import pkg_resources

from datetime import timedelta
from moksha.pastetemplate import MokshaControllerTemplate
from base import QuickstartTester

from moksha.lib.base import Controller

class TestControllerQuickstart(QuickstartTester):

    def __init__(self,**options):
        self.app = None
        self.template_vars = {
                'package': 'mokshatest',
                'project': 'mokshatest',
                'egg': 'mokshatest',
                'egg_plugins': ['Moksha'],
        }
        self.args = {
            'controller': True,
            'controller_name': 'MokshatestController',
        }
        self.template = MokshaControllerTemplate
        self.templates = ['moksha.controller']

    def get_controller(self):
        return self.get_entry('moksha.application')

    def test_entry_point(self):
        assert self.get_controller(), \
                "Cannot find mokshatest on `moksha.app` entry-point"

    def test_controller_class(self):
        assert isinstance(self.get_controller(), Controller) or \
               issubclass(self.get_controller(), Controller)

    def test_controller_call_index(self):
        controller = self.get_controller()()
        result = controller.index()
        assert result == {'name': 'world'}

    def test_controller_index(self):
        resp = self.app.get('/apps/mokshatest')
        assert 'Hello' in resp, resp

    def test_controller_index(self):
        resp = self.app.get('/apps/mokshatest?name=world')
        assert 'Hello world' in resp, resp
