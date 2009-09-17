import sys
import os, shutil
import subprocess
import pkg_resources

from webtest import TestApp
from paste.deploy import loadapp
from paste.script.create_distro import CreateDistroCommand

from moksha.commands.quickstart import MokshaQuickstartCommand
from moksha.pastetemplate import MokshaLiveWidgetTemplate

testDataPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')

class Options(object):
    simulate = False
    overwrite = True
    templates = ['moksha.master']
    output_dir = testDataPath
    list_templates = False
    list_variables = False
    config = None
    inspect_files = False
    svn_repository = None


class QuickstartTester(object):

    def setUp(self):
        command = CreateDistroCommand('MokshaQuickStartUnitTest')
        command.verbose = False
        command.simulate = False
        command.options = Options()
        command.interactive=False
        command.args=[
                'mokshatest', '--package=mokshatest',
                '--template=moksha.master',
                ]
        for template in self.templates:
            command.args.append('--template=%s' % template)

        for arg in self.args:
            command.args.append('%s=%s' % (arg, self.args[arg]))

        proj_dir = os.path.join(testDataPath, 'mokshatest')
        command.create_template(
                self.template('mokshatest'),
                proj_dir,
                self.template_vars)
        command.command()

        cwd = os.getcwd()
        os.chdir(proj_dir)
        subprocess.Popen('paver egg_info', shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE).communicate()
        os.chdir(cwd)

        pkg_resources.working_set.add_entry(proj_dir)

        self.app = loadapp('config:/srv/moksha/development.ini',
                           relative_to=proj_dir)
        self.app = TestApp(self.app)

    def tearDown(self):
        shutil.rmtree(testDataPath, ignore_errors=True)


class TestLiveWidgetQuickstart(QuickstartTester):

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
            'livewidget': True,
            'widget_name': 'MokshatestWidget',
        }
        self.template = MokshaLiveWidgetTemplate
        self.templates = ['moksha.livewidget']

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
        assert 'TCPSocket' in resp

    def test_livewidget(self):
        """ Ensure our LiveWidget is available """
        resp = self.app.get('/widgets/MokshatestWidget')
        assert 'Hello world.' in resp, resp


if __name__ == '__main__':
    import nose
    cls = TestQuickStart()
    cls.setUp()
    testspath = os.path.join(testDataPath,'mokshatest','mokshatest','tests')
    nose.main(argv=['-w',testspath],exit=False)
    cls.tearDown()
