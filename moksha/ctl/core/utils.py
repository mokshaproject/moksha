""" Various moksha-ctl utils.  Mostly context managers. """

import os
import sys
import site

class VirtualEnvContext(object):
    """ Context manager for entering a virtualenv """
    entered = False

    def __init__(self, venv_name):
        self.VENV = venv_name

    def __enter__(self):
        if self.entered:
            # Skip out early so we don't enter twice ;)
            return
        self.entered = True

        # TODO -- save state so we can undo it afterwards
        workon_home = os.getenv('WORKON_HOME')
        if not workon_home:
            raise ValueError, "$WORKON_HOME is not defined.  " + \
                    "Install virtualenvwrapper."
        base = workon_home + '/' + self.VENV
        site_packages = os.path.join(
            base, 'lib', 'python%s' % sys.version[:3], 'site-packages')
        prev_sys_path = list(sys.path)
        site.addsitedir(site_packages)
        sys.real_prefix = sys.prefix
        sys.prefix = base
        # Move the added items to the front of the path:
        new_sys_path = []
        for item in list(sys.path):
            if item not in prev_sys_path:
                new_sys_path.append(item)
                sys.path.remove(item)
        sys.path[:0] = new_sys_path

    def __exit__(self, exc_type, exc_value, traceback):
        # TODO -- do cleanup here
        self.entered = False


class DirectoryContext(object):
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
