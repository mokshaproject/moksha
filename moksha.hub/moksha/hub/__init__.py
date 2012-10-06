# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
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

import logging
import signal
import sys
import os

from moksha.common.lib.helpers import appconfig
from moksha.common.lib.helpers import get_moksha_config_path

log = logging.getLogger('moksha.hub')

NO_CONFIG_MESSAGE = """
  Cannot find Moksha configuration!  Place a development.ini or production.ini
  in /etc/moksha or in the current directory.
"""

from moksha.hub.hub import CentralMokshaHub


def setup_logger(verbose):
    global log
    sh = logging.StreamHandler()
    level = verbose and logging.DEBUG or logging.INFO
    log.setLevel(level)
    sh.setLevel(level)
    format = logging.Formatter(
        '[moksha.hub] %(levelname)s %(asctime)s %(message)s')
    sh.setFormatter(format)
    log.addHandler(sh)


def main(options=None, consumers=None, producers=None):
    """ The main MokshaHub method """
    setup_logger('-v' in sys.argv or '--verbose' in sys.argv)

    config = {}

    if not options:
        if sys.argv[-1].endswith('.ini'):
            config_path = os.path.abspath(sys.argv[-1])
        else:
            config_path = get_moksha_config_path()

        if not config_path:
            print NO_CONFIG_MESSAGE
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
    reactor.run(installSignalHandlers=False)
    log.info("MokshaHub reactor stopped")
