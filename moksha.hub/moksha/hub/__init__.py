# This file is part of Moksha.
# Copyright (C) 2008-2014  Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import logging
import signal
import sys
import os

try:
    from twisted.internet.error import ReactorNotRunning
except ImportError:  # Twisted 8.2.0 on RHEL5
    class ReactorNotRunning(object):
        pass

from moksha.common.lib.helpers import appconfig
from moksha.common.lib.helpers import get_moksha_config_path

log = logging.getLogger('moksha.hub')

NO_CONFIG_MESSAGE = """
  Cannot find Moksha configuration!  Place a development.ini or production.ini
  in /etc/moksha or in the current directory.
"""

from moksha.hub.hub import CentralMokshaHub


def setup_logger(verbose):
    logging.basicConfig()
    root = logging.getLogger()
    handler = root.handlers[0]
    level = verbose and logging.DEBUG or logging.INFO
    root.setLevel(level)
    format = logging.Formatter(
        '[%(name)12s] %(levelname)s %(asctime)s %(message)s')
    handler.setFormatter(format)


def main(options=None, consumers=None, producers=None, framework=True):
    """ The main MokshaHub method """

    # If we're running as a framework, then we're strictly calling other
    # people's code.  So, as the outermost piece of software in the stack, we're
    # responsible for setting up logging.
    # If we're not running as a framework, but as a library, then someone else
    # is calling us.  Therefore, we'll let them set up the logging themselves.
    if framework:
        setup_logger('-v' in sys.argv or '--verbose' in sys.argv)

    config = {}

    if not options:
        if sys.argv[-1].endswith('.ini'):
            config_path = os.path.abspath(sys.argv[-1])
        else:
            config_path = get_moksha_config_path()

        if not config_path:
            print(NO_CONFIG_MESSAGE)
            return

        cfg = appconfig('config:' + config_path)
        config.update(cfg)
    else:
        config.update(options)

    hub = CentralMokshaHub(config, consumers=consumers, producers=producers)
    global _hub
    _hub = hub

    def handle_signal(signum, stackframe):
        from moksha.hub.reactor import reactor
        if signum in [signal.SIGHUP, signal.SIGINT]:
            hub.stop()
            try:
                reactor.stop()
            except ReactorNotRunning:
                pass

    signal.signal(signal.SIGHUP, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    log.info("Running the MokshaHub reactor")
    from moksha.hub.reactor import reactor

    threadcount = config.get('moksha.threadpool_size', None)
    if not threadcount:
        N = int(config.get('moksha.workers_per_consumer', 1))
        threadcount = 1 + hub.num_producers + hub.num_consumers * N

    threadcount = int(threadcount)
    log.info("Suggesting threadpool size at %i" % threadcount)
    reactor.suggestThreadPoolSize(threadcount)

    reactor.run(installSignalHandlers=False)
    log.info("MokshaHub reactor stopped")
