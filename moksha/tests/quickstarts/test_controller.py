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

    def get_entry(self):
        for controller in pkg_resources.working_set.iter_entry_points('moksha.application'):
            controller_class = controller.load()
            if inspect.isclass(controller_class):
                name = controller_class.__name__
            else:
                name = controller_class.__class__.__name__
            if name == 'MokshatestController':
                return controller_class

    def test_entry_point(self):
        assert self.get_entry(), \
                "Cannot find MokshatestController on `moksha.app` entry-point"

    def test_controller_class(self):
        assert isinstance(self.get_entry(), Controller) or \
               issubclass(self.get_entry(), Controller)

    def test_controller_call_index(self):
        controller = self.get_entry()()
        result = controller.index()
        assert result == {'name': 'world'}

    def test_controller_index(self):
        resp = self.app.get('/apps/MokshatestController')
        assert 'Hello' in resp, resp

    def test_controller_index(self):
        resp = self.app.get('/apps/MokshatestController?name=world')
        assert 'Hello world' in resp, resp
