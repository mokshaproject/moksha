import os
import shutil
import subprocess
import pkg_resources

from webtest import TestApp
from paste.deploy import loadapp
from paste.script.create_distro import CreateDistroCommand

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

        self.oldcwd = os.getcwd()
        os.chdir(proj_dir)
        subprocess.Popen('paver egg_info', shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE).communicate()

        pkg_resources.working_set.add_entry(proj_dir)
        reload(pkg_resources)

        self.app = loadapp('config:/srv/moksha/development.ini',
                           relative_to=proj_dir)
        self.app = TestApp(self.app)

    def tearDown(self):
        shutil.rmtree(testDataPath, ignore_errors=True)
        os.chdir(self.oldcwd)
