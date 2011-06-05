""" Functions for moksha-ctl """
import decorator
import subprocess
import os
import shutil

from moksha.ctl.core.utils import (
    VirtualEnvContext,
    DirectoryContext,
)

import colors as c

VENV = 'moksha'

### TODO -- use configparser or yaml to get this from ~/.something.rc
##SRC_DIR_KEY = 'moksha_source_location'
##if not SRC_DIR_KEY in env:
##    prompt('Enter ' + SRC_DIR_KEY + ' (can be specified in ~/.fabricrc):',
##           key=SRC_DIR_KEY)
##
##SRC_DIR = env[SRC_DIR_KEY]
# XXX - remove this
SRC_DIR = "/home/rjbpop/devel/moksha"

APPS_DIR = 'moksha/apps'
pid_files = ['paster.pid', 'orbited.pid', 'moksha-hub.pid']

def _with_virtualenv(func, *args, **kwargs):
    with VirtualEnvContext(VENV):
        return func(*args, **kwargs)

def _in_srcdir(func, *args, **kwargs):
    with DirectoryContext(SRC_DIR):
        return func(*args, **kwargs)

def _reporter(func, *args, **kwargs):
    print "[" + c.magenta("moksha-ctl") + "] ",
    print "Running", func.__name__, "with",
    print "args:", c.cyan(str(args)) + " and kw:" + c.cyan(str(kwargs))
    try:
        output = func(*args, **kwargs)
    except Exception:
        print "[" + c.magenta("moksha-ctl") + "] ",
        print "[ " + c.red('FAIL') + " ]", func.__name__
        raise
    print "[" + c.magenta("moksha-ctl") + "] ",
    print "[  " + c.green('OK') + "  ]", func.__name__
    return output

def _warn_only(func, *args, **kwargs):
    # TODO -- evaluate this for removal.  It might be old news.
    return func(*args, **kwargs)
    #with settings(hide('warnings', 'running', 'stdout', 'stderr'),
    #              warn_only=True):
    #    return func(*args, **kwargs)

_with_virtualenv = decorator.decorator(_with_virtualenv)
_in_srcdir = decorator.decorator(_in_srcdir)
_reporter = decorator.decorator(_reporter)
_warn_only = decorator.decorator(_warn_only)

def _use_yum():
    return os.path.exists('/etc/redhat-release')

@_reporter
def bootstrap():
    """ Should only be run once.  First-time moksha setup. """
    if _use_yum():
        reqs = [
            'python-setuptools', 'python-qpid', 'qpid-cpp-server',
            'orbited',
            'ccze',  # ccze is awesome
        ]
        os.system('sudo yum install -q -y ' + ' '.join(reqs))
    else:
        # No orbited or qpid on ubuntu as far as I can tell
        # TODO -- how should we work this?
        os.system('sudo apt-get install -y python-setuptools')

    os.system('sudo easy_install -q pip')
    os.system('sudo pip -q install virtualenv')
    os.system('sudo pip -q install virtualenvwrapper')

    shellrc_snippet = """
# virtualenv stuff
export WORKON_HOME=$HOME/.virtualenvs;
source /usr/bin/virtualenvwrapper.sh;
"""
    try:
        os.mkdir(os.path.expanduser('~/.virtualenvs'))
    except OSError as e:
        if "File exists" in str(e):
            pass
        else:
            raise e

    print "[" + c.magenta("moksha-ctl") + "] ",
    print "Done-ski."
    print "You should definitely add the following to your ~/.bashrc."
    print
    print "*" * 60
    print shellrc_snippet
    print "*" * 60
    print
    print "Then please run 'moksha-ctl.py rebuild'"


def _do_virtualenvwrapper_command(cmd):
    """ This is tricky, because all virtualenwrapper commands are
    actually bash functions, so we can't call them like we would
    other executables.
    """

    print "Trying '%s'" % cmd
    out, err = subprocess.Popen(
        ['bash', '-c', '. /usr/bin/virtualenvwrapper.sh; %s' % cmd ],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).communicate()
    print out
    print err

@_reporter
def rebuild():
    """ Completely destroy and rebuild the virtualenv. """
    try:
        _do_virtualenvwrapper_command('rmvirtualenv %s' % VENV)
    except Exception as e:
        print str(e)

    cmd = 'mkvirtualenv --distribute --no-site-packages %s' % VENV
    _do_virtualenvwrapper_command(cmd)

    install()

@_reporter
@_with_virtualenv
def install():
    """ Install moksha and all its dependencies. """
    import pip
    print pip.__file__
    sys.exit(0)
    install_hacks()
    with DirectoryContext(SRC_DIR):
        # `install` instead of `develop` to avoid weird directory vs. egg
        # namespace issues
        os.system('python setup.py install')
    install_apps()
    link_qpid_libs()
    develop()

@_reporter
@_with_virtualenv
def install_hacks():
    """ Install dependencies with weird workarounds. """

    # TODO -- here, even though we're in the virtualenv, pip is still
    # referring to the system-wide pip.  We need to replace it with
    # something like
    # >>> import pip.commands.install
    # >>> c = pip.commands.install.InstallCommand()
    # >>> c.run({}, 'Extremes')

    os.system('pip -q install Extremes')

    os.system('pip -q install tg.devtools')

    # Here we install Orbited ourselves (instead of through `python setup.py
    # develop`) because we need to specify --use-mirrors since orbited's website
    # is often down and breaks the build process.
    os.system('pip -q install --use-mirrors orbited')

@_reporter
@_with_virtualenv
@_in_srcdir
def install_apps():
    """ Install *all* the moksha `apps`. """

    with DirectoryContext(APPS_DIR):
        dnames = [d for d in os.listdir('.') if os.path.isdir(d)]
        for d in dnames:
            install_app(app=d)

@_reporter
@_with_virtualenv
def install_app(app):
    """ Install a particular app.  $ fab install_app:metrics """

    with DirectoryContext("/".join([SRC_DIR, APPS_DIR, app])):
        fnames = os.listdir('.')
        if not 'pavement.py' in fnames:
            print "No `pavement.py` found for app '%s'.  Skipping." % app
            return
        shutil.rmtree('dist')
        os.system('paver bdist_egg')
        os.system('easy_install -Z dist/*.egg')

@_reporter
@_with_virtualenv
@_in_srcdir
@_warn_only
def link_qpid_libs():
    """ Link qpid and mllib in from the system site-packages. """
    location = 'lib/python*/site-packages'
    template = 'ln -s /usr/{location}/{lib} $WORKON_HOME/{VENV}/{location}/'
    for lib in ['qpid', 'mllib']:
        cmd = template.format(location=location, VENV=VENV, lib=lib)
        out = os.system(cmd)

@_reporter
@_with_virtualenv
@_in_srcdir
def start(service=None):
    """ Start paster, orbited, and moksha-hub. """

    def start_service(name):
        print "[moksha fabric] Starting " + c.magenta(name)
        os.system('.scripts/start-{name}'.format(name=name), pty=False)


    if service:
        pid_file = service + '.pid'
        if os.path.exists(pid_file):
            raise ValueError, "%s file exists" % pid_file
        start_service(name=service)
    else:
        if any(map(os.path.exists, pid_files)):
            raise ValueError, "some .pid file exists"
        start_service(name='paster')
        start_service(name='orbited')
        start_service(name='moksha-hub')

@_reporter
@_with_virtualenv
@_in_srcdir
@_warn_only
def stop(service=None):
    """ Stop paster, orbited, and moksha-hub.  """
    _pid_files = pid_files

    if service:
        _pid_files = [service+'.pid']

    for fname in _pid_files:
        if not os.path.exists(fname):
            print "[moksha fabric] [ " + c.red('FAIL') + " ]",
            print fname, "does not exist."
            continue
        try:
            cmd = 'kill $(cat %s)' % fname
            os.system(cmd)
            print "[moksha fabric] [  " + c.green('OK') + "  ]", cmd
        except:
            print "[moksha fabric] [ " + c.red('FAIL') + " ]", cmd
        finally:
            os.system('rm %s' % fname)
@_reporter
@_with_virtualenv
@_in_srcdir
def develop():
    """ `python setup.py develop` """
    os.system('python setup.py install')
    os.system('python setup.py develop')

@_reporter
@_with_virtualenv
def restart():
    """ Stop, `python setup.py develop`, start.  """
    stop()
    develop()
    start()

@_reporter
@_with_virtualenv
def egg_info():
    """ Rebuild egg_info. """
    with cd(SRC_DIR):
        os.system('python setup.py egg_info')


# --
# Below here follows the *giant* 'wtf' block.  Add things to it as necessary.
# --

def _wtfwin(msg):
    print "[wtf] [  " + c.green('OK') + "  ]", msg

def _wtffail(msg):
    print "[wtf] [ " + c.red('FAIL') + " ]", msg

@_in_srcdir
@_warn_only
def wtf():
    """ Debug a busted moksha environment. """
    wtfwin, wtffail = _wtfwin, _wtffail

    output = os.system('echo $WORKON_HOME')
    if not output:
        wtffail('$WORKON_HOME is not set.')
    else:
        wtfwin('$WORKON_HOME is set to ' + output)
        if os.path.exists('$WORKON_HOME'):
            wtfwin(output + ' exists.')
        else:
            wtffail(output + ' does not exist.')

    out = os.system('python -c "import qpid"')
    if not out:
        wtfwin('system-wide python-qpid is installed.')
    else:
        wtffail('system-wide python-qpid not installed.')

    # Proceed along the rest of the way, but with the virtualenv enabled.
    _wtf_rest()

@_with_virtualenv
def _wtf_rest():
    wtfwin, wtffail = _wtfwin, _wtffail

    out = os.system('python -c "import qpid"')
    if not out:
        wtfwin('virtualenv python-qpid is linked.')
    else:
        wtffail('virtualenv python-qpid not linked.')

    for pid_file in pid_files:
        prog = pid_file[:-4]

        pid = None
        if os.path.exists(pid_file):
            pid = os.system('cat ' + pid_file)
        else:
            wtffail(pid_file + ' does not exist.')

        out = os.system('pgrep ' + prog).split()

        if not out:
            if pid:
                wtffail(prog + ' is not running BUT it has a pid file!')
            else:
                wtffail(prog + ' is not running.')
        else:
            if len(out) > 1:
                wtffail(prog + ' has more than one instance running.')
            else:
                if out[0] != pid:
                    wtffail('pid of ' + prog + " doesn't match pid-file")
                else:
                    wtfwin(prog + ' is running and healthy.')
