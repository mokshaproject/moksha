import pkg_resources
import re
import optparse
import os
import stat
import sys
import imp

from paste.script import command
from paste.script import create_distro

beginning_letter = re.compile(r"^[^a-z]*")
valid_only = re.compile(r"[^a-z0-9_]")

class MokshaQuickstartCommand(command.Command):
    """Create new Moksha components.

Create a new Moksha App with this command.

Example usage::

    $ paster moksha yourproject

    """
    version = pkg_resources.get_distribution('moksha.common').version
    max_args = 3
    min_args = 0
    summary = __doc__.splitlines()[0]
    usage = '\n' + __doc__
    group_name = "Moksha"
    name = None
    package = None
    svn_repository = None
    templates = "moksha.master"
    #dry_run = False
    #no_input = False

    livewidget = False
    consumer = False
    stream = False

    topic = 'moksha.test'

    parser = command.Command.standard_parser(quiet=True)
    parser = optparse.OptionParser(
                    usage="%prog moksha [options] [project name]",
                    version="%prog " + version)
    parser.add_option("-l", "--livewidget",
            help='Create an example Moksha LiveWidget',
            action="store_true", dest="livewidget")
    parser.add_option("-u", "--consumer",
            help='Create an example Moksha Consumer',
            action="store_true", dest="consumer")
    parser.add_option("-C", "--controller",
            help='Create an example Moksha Controller',
            action="store_true", dest="controller")
    parser.add_option("-P", "--producer",
            help='Create an example Moksha Producer',
            action="store_true", dest="stream")
    parser.add_option("-p", "--package",
            help="package name for the code",
            dest="package")
    parser.add_option("-t", "--topic",
            help="The Moksha topic to utilize",
            dest="topic")
    #parser.add_option("--dry-run",
    #        help="dry run (don't actually do anything)",
    #        action="store_true", dest="dry_run")
    #parser.add_option("--noinput",
    #        help="no input (don't ask any questions)",
    #        action="store_true", dest="no_input")

    def command(self):
        """Quickstarts the new project."""

        self.__dict__.update(self.options.__dict__)

        if self.args:
            self.name = self.args[0]

        while not self.name:
            self.name = raw_input("Enter project name: ")

        package = self.name.lower()
        package = beginning_letter.sub("", package)
        package = valid_only.sub("", package)
        if package:
            self.package = package
        else:
            self.package = None
            while not self.package:
                self.package = raw_input(
                    "Enter package name [%s]: " % package).strip() or package

        self.name = pkg_resources.safe_name(self.name).replace('-', '_')
        self.rpm_name = self.package.replace('.', '-')

        env = pkg_resources.Environment()
        if self.name.lower() in env:
            print 'The name "%s" is already in use by' % self.name,
            for dist in env[self.name]:
                print dist
                return

        try:
            if imp.find_module(self.package):
                print 'The package name "%s" is already in use' % self.package
                return
        except ImportError:
            pass

        if os.path.exists(self.name):
            print 'A directory called "%s" already exists. Exiting.' % self.name
            return

        command = create_distro.CreateDistroCommand("create")
        cmd_args = ['--template=moksha.master']
        if self.livewidget:
            cmd_args.append('--template=moksha.livewidget')
        if self.stream:
            cmd_args.append('--template=moksha.stream')
        if self.consumer:
            cmd_args.append('--template=moksha.consumer')
        if self.controller:
            cmd_args.append('--template=moksha.controller')

        #if self.dry_run:
        #    cmd_args.append("--simulate")
        #    cmd_args.append("-q")
        cmd_args.append(self.name)
        cmd_args.append("livewidget=%s" % self.livewidget)
        cmd_args.append("consumer=%s" % self.consumer)
        cmd_args.append("controller=%s" % self.controller)
        cmd_args.append("stream=%s" % self.stream)
        cmd_args.append("package=%s" % self.package)
        cmd_args.append("widget_name=%s" % self.package.title() + 'Widget')
        cmd_args.append("stream_name=%s" % self.package.title() + 'Stream')
        cmd_args.append("consumer_name=%s" % self.package.title() + 'Consumer')
        cmd_args.append("controller_name=%s" % self.package.title() + 'Controller')
        command.run(cmd_args)

        #if not self.dry_run:
        #    os.chdir(self.name)

        #    startscript = "start-%s.py" % self.package
        #    if os.path.exists(startscript):
        #        oldmode = os.stat(startscript).st_mode
        #        os.chmod(startscript, oldmode | stat.S_IXUSR)

        #    os.system('paver egg_info')

        #    # dirty hack to allow "empty" dirs
        #    for base, path, files in os.walk("./"):
        #        for file in files:
        #            if file == "empty":
        #                os.remove(os.path.join(base, file))
