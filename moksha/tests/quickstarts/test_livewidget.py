import inspect
import pkg_resources

from moksha.pastetemplate import MokshaLiveWidgetTemplate

from base import QuickstartTester, setup_quickstart, teardown_quickstart

app = None

def setup():
    template = MokshaLiveWidgetTemplate
    templates = ['moksha.livewidget']
    template_vars = {
            'package': 'mokshatest',
            'project': 'mokshatest',
            'egg': 'mokshatest',
            'egg_plugins': ['Moksha'],
            'topic': 'moksha.topics.test',
    }
    args = {
        'livewidget': True,
        'widget_name': 'MokshatestWidget',
    }

    global app
    app = setup_quickstart(template=template, templates=templates, args=args,
                           template_vars=template_vars)

def teardown():
    teardown_quickstart()

class TestLiveWidgetQuickstart(QuickstartTester):

    def setUp(self):
        self.app = app

    def get_widget(self):
        return self.get_entry('moksha.widget')

    def test_index(self):
        resp = self.app.get('/')
        assert '[ Moksha ]' in resp

    def test_jquery_injection(self):
        """ Ensure jQuery is getting injected on our main dashboard """
        resp = self.app.get('/')
        assert 'jquery' in resp

    def test_global_resources(self):
        """ Ensure we are getting our global resources injected """
        resp = self.app.get('/')
        assert 'moksha_csrf_token' in resp

    def test_menu(self):
        """ Ensure that our default menu is being created """
        resp = self.app.get('/')
        assert 'buildMenu' in resp

    def test_tcpsocket(self):
        """ Ensure our Orbited TCPSocket is getting injected """
        resp = self.app.get('/')
        assert 'TCPSocket' in resp or 'moksha_amqp_conn' in resp

    def test_livewidget(self):
        """ Ensure our LiveWidget is available """
        resp = self.app.get('/widgets/mokshatest')
        assert 'Hello world.' in resp, resp

    def test_livewidget_entry_point(self):
        """ Ensure our widget is available on the `moksha.widget` entry-point """
        assert self.get_widget(), \
                "Cannot find mokshatest on `moksha.widget` entry-point"

    def test_livewidget_topic(self):
        assert hasattr(self.get_widget(), 'topic'), "LiveWidget does not have a `topic`"
