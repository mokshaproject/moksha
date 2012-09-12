""" The Moksha Command-line Interface """

import os
import sys
import signal
import logging
import pkg_resources

from optparse import OptionParser
from twisted.internet import protocol
from twisted.internet import reactor

log = logging.getLogger(__name__)

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
        print "Running %s" % ' '.join(args)
        pp = MokshaProcessProtocol(name=process)
        process = reactor.spawnProcess(pp, process, args,
                env={'PYTHONPATH': os.getcwd()}, **kw)
        pids.append(process.pid)

    def start(self):
        """ Start all of the Moksha components """

        from moksha.lib.helpers import get_moksha_config_path

        orbited = ['orbited']
        if os.path.exists('/etc/moksha/orbited.cfg'):
            orbited += ['-c', '/etc/moksha/orbited.cfg']

        self._exec(*orbited)
        self._exec('paster', 'serve', get_moksha_config_path())
        self._exec('moksha-hub', '-v')

    def list(self):
        """ List all available apps, widgets, producers and consumers """
        entry_points = ('root', 'widget', 'application', 'wsgiapp',
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

    def send(self, topic, message):
        """ Send a message to a topic """
        from moksha.hub.api import MokshaHub, reactor
        hub = MokshaHub()
        print "send_message(%s, %s)" % (topic, message)
        hub.send_message(topic, {'msg': message})

        def stop_reactor():
            hub.close()
            reactor.stop()

        reactor.callLater(0.2, stop_reactor)
        reactor.run()


def get_parser():
    usage = 'usage: %prog [command]'
    parser = OptionParser(usage, description=__doc__)
    parser.add_option('', '--start', action='store_true', dest='start',
                      help='Start Moksha')
    parser.add_option('', '--list', action='store_true', dest='list',
                      help='List all installed Moksha components')
    parser.add_option('', '--send', action='store_true', dest='send',
        help='Send a message to a given topic. Usage: send <topic> <message>')
    return parser


def main():
    parser = get_parser()
    opts, args = parser.parse_args()
    pkg_resources.working_set.add_entry(os.getcwd())

    moksha = MokshaCLI()

    logging.basicConfig(level=logging.INFO, format=
            '%(asctime)s,%(msecs)03d %(levelname)-5.5s [%(name)s] %(message)s')

    stdout = logging.StreamHandler(sys.stdout)
    stdout.setFormatter(logging.Formatter('%(message)s'))
    log.addHandler(stdout)

    if opts.start or 'start' in args:
        print "Starting Moksha..."
        moksha.start()
        try:
            reactor.run()
        except Exception, e:
            print "Caught exception: %s" % str(e)
            moksha.stop()
    elif opts.list or 'list' in args:
        moksha.list()
    elif opts.send or 'send' in args:
        if len(sys.argv) != 4:
            log.error('Usage: moksha send <topic> <message>')
            sys.exit(-1)
        moksha.send(sys.argv[2], sys.argv[3])
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
