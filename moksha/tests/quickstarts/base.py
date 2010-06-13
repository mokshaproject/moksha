import os
import shutil
import subprocess
import pkg_resources

from webtest import TestApp
from paste.deploy import loadapp
from paste.script.create_distro import CreateDistroCommand

from moksha.lib.helpers import get_moksha_dev_config

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

old_cwd = None

def setup_quickstart(template, templates, template_vars, args):
    command = CreateDistroCommand('MokshaQuickStartUnitTest')
    command.verbose = False
    command.simulate = False
    command.options = Options()
    command.interactive=False
    command.args=[
            'mokshatest', '--package=mokshatest',
            '--template=moksha.master',
            ]
    for t in templates:
        command.args.append('--template=%s' % t)

    for arg in args:
        command.args.append('%s=%s' % (arg, args[arg]))

    proj_dir = os.path.join(testDataPath, 'mokshatest')
    command.create_template(
            template('mokshatest'),
            proj_dir,
            template_vars)
    command.command()

    subprocess.Popen('paver egg_info', shell=True, stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE,
                     cwd=proj_dir).communicate()

    pkg_resources.working_set.add_entry(proj_dir)
    reload(pkg_resources)

    app = loadapp('config:%s' % get_moksha_dev_config(),
                  relative_to=proj_dir)
    return TestApp(app)

def teardown_quickstart():
    shutil.rmtree(testDataPath, ignore_errors=True)


class QuickstartTester(object):

    def get_entry(self, entry_point):
        for entry in pkg_resources.working_set.iter_entry_points(entry_point):
            if entry.name == 'mokshatest':
                return entry.load()

