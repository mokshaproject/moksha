#!/usr/bin/env python
""" The Moksha Command-line Interface """

import os
import sys
import signal
import pkg_resources

from optparse import OptionParser
from subprocess import Popen, PIPE
from setuptools.command import easy_install
from twisted.internet import protocol
from twisted.internet import reactor

pids = []

class MokshaProcessProtocol(protocol.ProcessProtocol):
    def __init__(self, name):
        self.name = name
    def connectionMade(self):
        pass
    def outReceived(self, data):
        sys.stdout.write(data)
    def errReceived(self, data):
        sys.stderr.write(data)
    def inConnectionLost(self):
        pass
    def outConnectionLost(self):
        pass
    def errConnectionLost(self):
        pass
    def processEnded(self, status_object):
        print "Process %r quit with status %d" % (
                self.name, status_object.value.exitCode)
        reactor.stop()
        for pid in pids:
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass


class MokshaCLI(object):

    def _exec(self, process, *args, **kw):
        args = args and [process] + list(args) or [process]
        print "Running %s %s" % (process, ' '.join(args))
        pp = MokshaProcessProtocol(name=process)
        orbited = reactor.spawnProcess(pp, process, args, **kw)
        pids.append(orbited.pid)

    def start(self):
        """ Start all of the Moksha components """
        # Try to import moksha.   If you can, move on.
        # If not, setup a virtualenv if one doesn't already exist

        self._exec('orbited')
        self._exec('paster', 'serve', 'development.ini')
        self._exec('moksha-hub')

    def list(self):
        """ List all available apps, widgets, producers and consumers """
        entry_points = ('widget', 'application', 'wsgiapp',
                        'producer', 'consumer')
        for entry in entry_points:
            print "[moksha.%s]" % entry
            for obj_entry in pkg_resources.iter_entry_points('moksha.' + entry):
                print " * %s" % obj_entry.name
            print


    def install(self):
        """ Install a Moksha component """

    def uninstall(self):
        """ Uninstall a Moksha component """

    def quickstart(self):
        """ Create a new Moksha component """
        # If no arguments given, run `paster moksha --help`


def get_parser():
    usage = 'usage: %prog [command]'
    parser = OptionParser(usage)
    parser.add_option('', '--start', action='store_true', dest='start',
                      help='Start Moksha')
    parser.add_option('', '--list', action='store_true', dest='list',
                      help='List all installed Moksha components')
    return parser


def main():
    parser = get_parser()
    opts, args = parser.parse_args()
    moksha = MokshaCLI()

    if opts.start:
        print "Starting Moksha..."
        moksha.start()
        try:
            reactor.run()
        except Exception, e:
            print "Caught exception: %s" % str(e)
            moksha.stop()
    elif opts.list:
        moksha.list()


if __name__ == '__main__':
    main()
