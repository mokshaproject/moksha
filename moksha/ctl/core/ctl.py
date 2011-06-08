""" Functions for moksha-ctl """
import decorator
import subprocess
import os
import sys
import shutil
import psutil

# Local imports
import config
import colors as c
import utils

ctl_config = config.load_config()

pid_files = ['paster.pid', 'orbited.pid', 'moksha-hub.pid']

PRETTY_PREFIX = "[" + c.magenta("moksha-ctl") + "] "


def _with_virtualenv(func, *args, **kwargs):
    with utils.VirtualenvContext(ctl_config['VENV']):
        return func(*args, **kwargs)


def _in_srcdir(func, *args, **kwargs):
    with utils.DirectoryContext(ctl_config['SRC_DIR']):
        return func(*args, **kwargs)


def _reporter(func, *args, **kwargs):
    descriptor = ":".join([func.__name__] + [a for a in args if a])
    print PRETTY_PREFIX, "Running:", descriptor
    output = None
    try:
        output = func(*args, **kwargs)
        if not output:
            raise Exception
        print PRETTY_PREFIX, "[  " + c.green('OK') + "  ]", descriptor
    except Exception:
        print PRETTY_PREFIX, "[ " + c.red('FAIL') + " ]", descriptor
    return output

_with_virtualenv = decorator.decorator(_with_virtualenv)
_in_srcdir = decorator.decorator(_in_srcdir)
_reporter = decorator.decorator(_reporter)


@_reporter
def bootstrap():
    """ Should only be run once.  First-time moksha setup. """
    ret = True
    if os.path.exists('/etc/redhat-release'):
        reqs = [
            'python-setuptools', 'python-qpid', 'qpid-cpp-server',
            'python-psutil', 'ccze',  # ccze is awesome
        ]
        ret = ret and not os.system(
            'sudo yum install -q -y ' + ' '.join(reqs))
    else:
        # No orbited or qpid on ubuntu as far as I can tell
        # TODO -- how should we work this?
        ret = ret and not os.system(
            'sudo apt-get install -y python-setuptools')

    ret = ret and not os.system('sudo easy_install -q pip')
    ret = ret and not os.system('sudo pip -q install virtualenv')
    ret = ret and not os.system('sudo pip -q install virtualenvwrapper')
    ret = ret and not os.system('sudo pip -q install fabulous')

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

    # TODO -- auto-insert virtualenv snippet into ~/.bashrc if its not already
    # there.
    print PRETTY_PREFIX, "Done-ski."
    print "You should definitely add the following to your ~/.bashrc."
    print
    print "*" * 60
    print shellrc_snippet
    print "*" * 60
    print
    print "Then please run 'moksha-ctl.py rebuild'"
    return ret


def _do_virtualenvwrapper_command(cmd):
    """ This is tricky, because all virtualenwrapper commands are
    actually bash functions, so we can't call them like we would
    other executables.
    """

    print "Trying '%s'" % cmd
    out, err = subprocess.Popen(
        ['bash', '-c', '. /usr/bin/virtualenvwrapper.sh; %s' % cmd],
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

    cmd = 'mkvirtualenv --no-site-packages %s' % ctl_config['VENV']
    _do_virtualenvwrapper_command(cmd)

    return install()


@_reporter
@_with_virtualenv
def install():
    """ Install moksha and all its dependencies. """
    ret = True
    ret = ret and install_hacks()
    with utils.DirectoryContext(ctl_config['SRC_DIR']):
        # `install` instead of `develop` to avoid weird directory vs. egg
        # namespace issues
        ret = ret and not os.system('%s setup.py install' % sys.executable)
    ret = ret and install_apps()
    ret = ret and link_qpid_libs()
    ret = ret and develop()
    return ret


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
        print PRETTY_PREFIX, "pip installing", c.yellow(dist)
        utils.install_distributions([dist])

    # TODO -- test to see if the installs worked.
    return True


@_reporter
@_with_virtualenv
@_in_srcdir
def install_apps():
    """ Install *all* the moksha `apps`. """

    with utils.DirectoryContext(ctl_config['APPS_DIR']):
        dnames = [d for d in os.listdir('.') if os.path.isdir(d)]
        for d in dnames:
            install_app(app=d)
    return True


@_reporter
@_with_virtualenv
def install_app(app):
    """ Install a particular app.  $ fab install_app:metrics """

    dirname = "/".join([ctl_config['SRC_DIR'], ctl_config['APPS_DIR'], app])
    with utils.DirectoryContext(dirname):
        fnames = os.listdir('.')
        if not 'pavement.py' in fnames:
            print "No `pavement.py` found for app '%s'.  Skipping." % app
            return False
        try:
            shutil.rmtree('dist')
        except OSError as e:
            pass  # It's cool.
        base = '/'.join(sys.executable.split('/')[:-1])
        cmd = '%s/paver bdist_egg > /dev/null 2>&1' % base
        if os.system(cmd):
            return False
        cmd = '%s/easy_install -Z dist/*.egg > /dev/null 2>&1' % base
        if os.system(cmd):
            return False
    return True


@_reporter
@_with_virtualenv
@_in_srcdir
def link_qpid_libs():
    """ Link qpid and mllib in from the system site-packages. """
    location = 'lib/python{major}.{minor}/site-packages'.format(
        major=sys.version_info.major, minor=sys.version_info.minor)
    template = 'ln -s /usr/{location}/{lib} {workon}/{VENV}/{location}/'
    for lib in ['qpid', 'mllib']:
        cmd = template.format(
            location=location, VENV=ctl_config['VENV'], lib=lib,
            workon=os.getenv("WORKON_HOME"))
        out = os.system(cmd)

    # TODO -- test for success
    return True


@_reporter
@_with_virtualenv
@_in_srcdir
def start(service=None):
    """ Start paster, orbited, and moksha-hub. """

    def start_service(name):
        print PRETTY_PREFIX, "Starting " + c.yellow(name)
        return not os.system('.scripts/start-{name} {venv}'.format(
            name=name, venv=ctl_config['VENV']))

    ret = True
    if service:
        pid_file = service + '.pid'
        if os.path.exists(pid_file):
            raise ValueError("%s file exists" % pid_file)
        ret = ret and start_service(name=service)
    else:
        if any(map(os.path.exists, pid_files)):
            raise ValueError("some .pid file exists")
        ret = ret and start_service(name='paster')
        ret = ret and start_service(name='orbited')
        ret = ret and start_service(name='moksha-hub')

    print " * Log files are in logs/<service>.log.  Run:"
    print "     $ tail -f logs/paster.log | ccze"
    return ret


@_reporter
@_with_virtualenv
@_in_srcdir
def stop(service=None):
    """ Stop paster, orbited, and moksha-hub.  """

    def stopfail(msg):
        print PRETTY_PREFIX + " [ " + c.red('FAIL') + " ]", msg

    def stopwin(msg):
        print PRETTY_PREFIX + " [  " + c.green('OK') + "  ]", msg

    _pid_files = pid_files

    if service:
        _pid_files = [service + '.pid']

    ret = True
    processes = psutil.get_process_list()
    for fname in _pid_files:
        if not os.path.exists(fname):
            stopfail(fname + " does not exist.")
            continue

        pid = None
        try:
            with open(fname) as f:
                pid = int(f.read())
        except IOError:
            stopfail(fname + " does not exist.")
            ret = False
            continue
        except ValueError:
            stopfail(fname + " is corrupt.")
            ret = False
            continue

        instances = [p for p in processes if p.pid == pid]
        if len(instances) == 0:
            stopfail("No such process with pid: " + str(pid))
            ret = False
            os.remove(fname)
            continue

        proc = instances[0]
        result = proc.kill()
        stopwin("Killed %i %s" % (proc.pid, proc.name))
        os.remove(fname)

    return ret


@_reporter
@_with_virtualenv
@_in_srcdir
def develop():
    """ `python setup.py develop` """
    ret = True
    ret = ret and not os.system('%s setup.py install' % sys.executable)
    ret = ret and not os.system('%s setup.py develop' % sys.executable)
    return ret


@_reporter
@_with_virtualenv
def restart():
    """ Stop, `python setup.py develop`, start.  """
    stop()  # We don't care if this fa
    return start()


@_reporter
@_with_virtualenv
def egg_info():
    """ Rebuild egg_info. """
    with cd(ctl_config['SRC_DIR']):
        os.system('%s setup.py egg_info' % sys.executable)


# --
# Below here follows the *giant* 'wtf' block.  Add things to it as necessary.
# --

WTF_PREFIX = PRETTY_PREFIX + "[" + c.magenta('wtf') + "]"


def _wtfwin(msg):
    print WTF_PREFIX, "[  " + c.green('OK') + "  ]", msg


def _wtffail(msg):
    print WTF_PREFIX, "[ " + c.red('FAIL') + " ]", msg


@_in_srcdir
def wtf():
    """ Debug a busted moksha environment. """
    wtfwin, wtffail = _wtfwin, _wtffail

    workon = os.getenv('WORKON_HOME')
    if not workon:
        wtffail('$WORKON_HOME is not set.')
    else:
        wtfwin('$WORKON_HOME is set to ' + workon)
        if os.path.exists(os.path.expanduser(workon)):
            wtfwin(workon + ' exists.')
        else:
            wtffail(workon + ' does not exist.')

    with utils.VirtualenvContext(ctl_config['VENV']):
        try:
            import qpid
            if not qpid.__file__.startswith(os.path.expanduser(workon)):
                raise ImportError
            wtfwin('virtualenv python-qpid is installed.')
        except Exception as e:
            wtffail('virtualenv python-qpid not installed.')

    try:
        import qpid
        if not qpid.__file__.startswith('/usr/'):
            raise ImportError
        wtfwin('system-wide python-qpid is installed.')
    except ImportError as e:
        wtffail('system-wide python-qpid not installed.')

    with utils.VirtualenvContext(ctl_config['VENV']):
        all_processes = psutil.get_process_list()
        for pid_file in pid_files:
            prog = pid_file[:-4]

            instances = [p for p in all_processes if prog in p.name]
            pid = None
            try:
                with open(pid_file) as f:
                    pid = int(f.read())
            except IOError:
                wtffail(pid_file + ' does not exist.')
            except ValueError:
                wtffail(pid_file + ' is corrupt.')

            if not psutil.pid_exists(pid):
                if pid and len(instances) == 0:
                    wtffail(prog + ' is not running BUT it has a pid file!')
                elif len(instances) != 0:
                    wtffail(prog + " appears to be running, " +
                            "but pidfile doesn't match")
                else:
                    wtffail(prog + ' is not running.')
            else:
                if len(instances) > 1:
                    wtffail(prog + ' has multiple instances running.')
                elif len(instances) == 0:
                    wtffail(prog + ' not running.  ' +
                            'But pidfile points to ANOTHER process!')
                elif instances[0].pid != pid:
                    wtffail('pid of ' + prog + " doesn't match pid-file")
                else:
                    wtfwin(prog + ' is running and healthy.')
