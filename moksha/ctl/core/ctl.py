""" Functions for moksha-ctl """
import decorator
import subprocess
import os
import sys
import shutil

# Local imports
import config
import colors as c
import utils

ctl_config = config.load_config()

pid_files = ['paster.pid', 'orbited.pid', 'moksha-hub.pid']

def _with_virtualenv(func, *args, **kwargs):
    with utils.VirtualenvContext(ctl_config['VENV']):
        return func(*args, **kwargs)

def _in_srcdir(func, *args, **kwargs):
    with utils.DirectoryContext(ctl_config['SRC_DIR']):
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

_with_virtualenv = decorator.decorator(_with_virtualenv)
_in_srcdir = decorator.decorator(_in_srcdir)
_reporter = decorator.decorator(_reporter)


@_reporter
def bootstrap():
    """ Should only be run once.  First-time moksha setup. """
    if os.path.exists('/etc/redhat-release'):
        reqs = [
            'python-setuptools', 'python-qpid', 'qpid-cpp-server',
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
        _do_virtualenvwrapper_command('rmvirtualenv %s' % ctl_config['VENV'])
    except Exception as e:
        print str(e)

    cmd = 'mkvirtualenv --distribute --no-site-packages %s' % ctl_config['VENV']
    _do_virtualenvwrapper_command(cmd)

    install()

@_reporter
@_with_virtualenv
def install():
    """ Install moksha and all its dependencies. """
    install_hacks()
    with utils.DirectoryContext(ctl_config['SRC_DIR']):
        # `install` instead of `develop` to avoid weird directory vs. egg
        # namespace issues
        os.system('%s setup.py install' % sys.executable )
    install_apps()
    link_qpid_libs()
    develop()

@_reporter
@_with_virtualenv
def install_hacks():
    """ Install dependencies with weird workarounds. """

    distributions = [
        'Extremes',
        'tg.devtools',
        'orbited',
    ]

    # This automatically uses --use-mirrors
    for dist in distributions:
        print "[" + c.magenta("moksha-ctl") + "] ",
        print "pip installing", c.yellow(dist), "with --use-mirrors"
        utils.install_distributions([dist])

@_reporter
@_with_virtualenv
@_in_srcdir
def install_apps():
    """ Install *all* the moksha `apps`. """

    with utils.DirectoryContext(ctl_config['APPS_DIR']):
        dnames = [d for d in os.listdir('.') if os.path.isdir(d)]
        for d in dnames:
            install_app(app=d)

@_reporter
@_with_virtualenv
def install_app(app):
    """ Install a particular app.  $ fab install_app:metrics """

    dirname = "/".join([ctl_config['SRC_DIR'], ctl_config['APPS_DIR'], app])
    with utils.DirectoryContext(dirname):
        fnames = os.listdir('.')
        if not 'pavement.py' in fnames:
            print "No `pavement.py` found for app '%s'.  Skipping." % app
            return
        try:
            shutil.rmtree('dist')
        except OSError as e:
            pass # It's cool.
        os.system('%s bdist_egg' % sys.executable.split('/')[:-1] + '/paver')
        #os.system('easy_install -Z dist/*.egg')

@_reporter
@_with_virtualenv
@_in_srcdir
def link_qpid_libs():
    """ Link qpid and mllib in from the system site-packages. """
    location = 'lib/python{major}.{minor}/site-packages'.format(
        major=sys.version_info.major,minor=sys.version_info.minor)
    template = 'ln -s /usr/{location}/{lib} {workon}/{VENV}/{location}/'
    for lib in ['qpid', 'mllib']:
        cmd = template.format(
            location=location, VENV=ctl_config['VENV'], lib=lib,
            workon=os.getenv("WORKON_HOME"))
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
    with cd(ctl_config['SRC_DIR']):
        os.system('python setup.py egg_info')


# --
# Below here follows the *giant* 'wtf' block.  Add things to it as necessary.
# --

def _wtfwin(msg):
    print "[wtf] [  " + c.green('OK') + "  ]", msg

def _wtffail(msg):
    print "[wtf] [ " + c.red('FAIL') + " ]", msg

@_in_srcdir
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
