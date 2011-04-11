from fabric.api import run, sudo, env
from fabric.context_managers import prefix, settings, cd, hide
from fabric.colors import red, green, cyan, magenta
import decorator

VENV = 'moksha'
SRC_DIR = '/'.join(env['real_fabfile'].split('/')[:-1])
APPS_DIR = 'moksha/apps'

def with_virtualenv(func, *args, **kwargs):
    with prefix('workon {venv}'.format(venv=VENV)):
        return func(*args, **kwargs)

def in_srcdir(func, *args, **kwargs):
    with cd(SRC_DIR):
        return func(*args, **kwargs)

def reporter(func, *args, **kwargs):
    print "[moksha fabric] Running", func.__name__, "with",
    print "args:", cyan(str(args)) + " and kw:" + cyan(str(kwargs))
    try:
        output = func(*args, **kwargs)
    except Exception:
        print "[moksha fabric] [ " + red('FAIL') + " ]", func.__name__
        raise
    print "[moksha fabric] [  " + green('OK') + "  ]", func.__name__
    return output
        

with_virtualenv = decorator.decorator(with_virtualenv)
in_srcdir = decorator.decorator(in_srcdir)
reporter = decorator.decorator(reporter)

@with_virtualenv
def wtf():
    print "hai"

@reporter
def bootstrap():
    sudo('yum install -y python-setuptools python-qpid qpid-cpp-server orbited')
    sudo('easy_install pip')
    sudo('pip install virtualenv')
    sudo('pip install virtualenvwrapper')
    
    shellrc_lookup = {
        # TODO -- add other shells (zsh) here if need be
        '/bin/bash -l -c' : '~/.bashrc',
    }
    shellrc = shellrc_lookup[env['shell']]
    shellrc_snippet = """ "
# virtualenv stuff (put here by the moksha fabric bootstrap process)
export WORKON_HOME=$HOME/.virtualenvs;
source /usr/bin/virtualenvwrapper.sh;
" """
    cmd="grep {test} {shellrc} || echo {payload} >> {shellrc}".format(
        test="virtualenvwrapper.sh", payload=shellrc_snippet, shellrc=shellrc)
    run(cmd)
    run('mkdir -p $WORKON_HOME')
    rebuild()

@reporter
def rebuild():
    with settings(warn_only=True):
        run('rmvirtualenv %s' % VENV)
    run('mkvirtualenv --distribute --no-site-packages %s' % VENV)
    install()

@reporter
@with_virtualenv
def install():
    install_hacks()
    with cd(SRC_DIR):
        run('python setup.py install')
    install_apps()
    link_qpid_libs()

@reporter
@with_virtualenv
def install_hacks():
    run('pip install Extremes')
    tg_url = "http://www.turbogears.org/2.1/downloads/current/index"
    run('pip install -i {tg_url} tg.devtools'.format(tg_url=tg_url))

@reporter
@with_virtualenv
@in_srcdir
def install_apps():
    with cd(APPS_DIR):
        dnames = [d for d in run('ls -F').split() if d.endswith('/')]
        for d in dnames:
            install_app(app=d)


@reporter
@with_virtualenv
def install_app(app):
    with cd("/".join([SRC_DIR, APPS_DIR, app])):
        run('rm -rf dist')
        run('paver bdist_egg')
        run('easy_install -Z dist/*.egg')




pid_files = ['paster.pid', 'orbited.pid', 'moksha-hub.pid']
def file_exists(fname):
    with settings(hide('warnings', 'running', 'stdout', 'stderr'),
                  warn_only=True):
        return 'No such file' not in run('ls {fname}'.format(fname=fname))

@reporter
@with_virtualenv
@in_srcdir
def start():
    def start_service(name, cmd):
        print "[moksha fabric] Starting " + magenta(name)
        run(cmd)
        run("echo $! >> {name}.pid".format(name=name))

    if any(map(file_exists, pid_files)):
        raise ValueError, "some .pid file exists"
    start_service(name='paster', cmd='paster serve development.ini')
    start_service(name='orbited', cmd='orbited -c orbited.cfg')
    start_service(name='moksha-hub', cmd='moksha-hub -v')

@reporter
@with_virtualenv
@in_srcdir
def stop():
    for fname in pid_files:
        if not file_exists(fname):
            print "[moksha fabric] [ " + red('FAIL') + " ]",
            print fname, "does not exist."
            continue
        try:
            cmd = 'kill $(cat %s)' % fname
            run(cmd)
            run('rm %s' % fname)
            print "[moksha fabric] [  " + green('OK') + "  ]", cmd
        except:
            print "[moksha fabric] [ " + red('FAIL') + " ]", cmd

@reporter
@with_virtualenv
def restart():
    stop()
    start()

@reporter
@with_virtualenv
def reload():
    stop()
    with cd(SRC_DIR):
        run('python setup.py develop install')
    start()
