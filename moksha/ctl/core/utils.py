""" Various moksha-ctl utils.  Mostly context managers. """

import os
import subprocess
import sys


def install_distributions(distributions):
    """ Installs distributions with pip! """

    pipsecutable = os.path.sep.join(
        sys.executable.split(os.path.sep)[:-1] + ['pip'])
    cmd = '%s install %s' % (pipsecutable, ' '.join(distributions))
    status = subprocess.call(cmd, shell=True)


class DirectoryContext(object):
    """ Context manager for changing the path working directory """
    def __init__(self, directory):
        self.dirname = directory
        self.old_path = None

    def __enter__(self):
        if self.old_path:
            raise ValueError("Weird.  old_path should be None")
        self.old_path = os.getcwd()
        os.chdir(self.dirname)

    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.old_path)
        self.old_path = None
