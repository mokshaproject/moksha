""" Various moksha-ctl utils.  Mostly context managers. """

import os
import sys
import ihooks
import warnings
import imp

def install_distributions(distributions):
    """ Installs distributions with pip! """

    import pip.commands.install

    command = pip.commands.install.InstallCommand()
    opts, args = command.parser.parse_args()

    opts.use_mirrors = True
    opts.mirrors = [
        'b.pypi.python.org',
        'c.pypi.python.org',
        'd.pypi.python.org',
        'e.pypi.python.org',
    ]
    opts.build_dir = os.path.expanduser('~/.pip/build')
    try:
        os.mkdir(opts.build_dir)
    except OSError as e:
        pass

    requirement_set = command.run(opts, distributions)
    foo = requirement_set.install([])

class DirectoryContext(object):
    """ Context manager for changing the path working directory """
    def __init__(self, directory):
        self.dirname = directory
        self.old_path = None

    def __enter__(self):
        if self.old_path:
            raise ValueError, "Weird.  old_path should be None"
        self.old_path = os.getcwd()
        os.chdir(self.dirname)

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.old_path)
        self.old_path = None

def _silent_load_source(name, filename, file=None):
    """ Helper function.  Overrides a import hook.  Suppresses warnings. """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return imp.load_source(name, filename, file)

class VenvModuleLoader(ihooks.ModuleLoader):
    """ Overridden ModuleLoader.

    Checks for a virtualenv first and remembers imports.
    """

    remembered = []

    def __init__(self, venv, verbose=0):
        self.venv = venv
        ihooks.ModuleLoader.__init__(self, verbose=verbose)
        self.hooks.load_source = _silent_load_source

    def default_path(self):
        workon = os.getenv("WORKON_HOME", None)
        venv_location = "/".join([
            workon, self.venv, 'lib/python2.7/site-packages'])
        full = lambda i : "/".join([venv_location, i])
        venv_path = [venv_location] + [
            full(item) for item in os.listdir(venv_location)
            if os.path.isdir(full(item))] + sys.path
        return venv_path + sys.path

    def load_module(self, name, stuff):
        """ Overloaded just to remember what we load """
        file, filename, info = stuff
        (suff, mode, type) = info
        self.remembered.append(name)
        return ihooks.ModuleLoader.load_module(self, name, stuff)

class VirtualenvContext(object):
    """ Context manager for entering a virtualenv """

    def __init__(self, venv_name):
        self.venv = venv_name
        self.loader = VenvModuleLoader(venv=self.venv)
        self.importer = ihooks.ModuleImporter(loader=self.loader)

    def __enter__(self):
        # Install our custom importer
        self.importer.install()

        # Pretend like our exectuable is really somewhere else
        self.old_exe = sys.executable
        workon = os.getenv("WORKON_HOME", None)
        sys.executable = "/".join([workon, self.venv, 'bin/python'])

    def __exit__(self, exc_type, exc_value, traceback):
        # Uninstall our custom importer
        self.importer.uninstall()

        # Reset our executable
        sys.exectuable = self.old_exe

        # Unload anything loaded while inside the context
        for name in self.importer.loader.remembered:
            if not name in sys.modules:
                continue
            del sys.modules[name]
        self.importer.loader.remembered = []
        sys.path_importer_cache.clear()

