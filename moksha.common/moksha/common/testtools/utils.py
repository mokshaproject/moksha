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

""" Utilities to make writing tests easier """

import functools
import socket

old_school = False
try:
    # For python-2.6
    import unittest2 as unittest
    old_school = True
except ImportError:
    import unittest

from moksha.common.lib.helpers import get_moksha_appconfig


def crosstest(method):
    @functools.wraps(method)
    def wrapper(self):
        for setup, name in self._setUp():
            def _inner(name):
                if not old_school:
                    setup()
                else:
                    try:
                        setup()
                    except unittest.SkipTest:
                        # For python-2.6
                        # nose doesn't know how to catch this, so we just
                        # return.  The test "passes" which is incorrect.  It
                        # should be skipped.
                        return

                try:
                    return method(self)
                finally:
                    self._tearDown()

            yield _inner, name

    return wrapper

config_sets = {
    'stomp': {
        "moksha.livesocket": "True",
        "moksha.livesocket.backend": "stomp",
        "orbited_host": "localhost",
        "orbited_port": "9000",
        "orbited_scheme": "http",
        "stomp_broker": "localhost",
        "stomp_port": "61613",
        "stomp_user": "guest",
        "stomp_pass": "guest",
    },
    'amqp': {
        "moksha.livesocket": "True",
        "moksha.livesocket.backend": "amqp",
        "orbited_host": "localhost",
        "orbited_port": "9000",
        "orbited_scheme": "http",
        "amqp_broker": "guest/guest@localhost",
        "amqp_broker_host": "localhost",
        "amqp_broker_port": "5672",
        "amqp_broker_user": "guest",
        "amqp_broker_pass": "guest",
        "amqp_broker_ssl": "False",
    },
    'zeromq': {
        "moksha.livesocket": "True",
        "moksha.livesocket.backend": "websocket",
        "moksha.livesocket.websocket.port": "9998",
        "zmq_enabled": "True",
        "zmq_publish_endpoints": "tcp://*:6543",
        "zmq_subscribe_endpoints": "tcp://127.0.0.1:6543",
        "zmq_strict": "True",
    },
}

flash_keys = []
for name, config_set in config_sets.items():
    flash_keys.extend(config_set.keys())

flash_keys = list(set(flash_keys))


def should_skip_config_set(name, config_set):
    if name == 'stomp':
        return True  # TODO - remove this.  This disables all STOMP tests.
        address = (config_set['stomp_broker'],
                   config_set['stomp_port'])
        # If we can connect, then run tests.  If we can't, then don't.
        try:
            s = socket.create_connection(address)
            s.close()
            return False
        except:
            return True
    elif name == 'amqp':
        address = (config_set['amqp_broker_host'],
                   config_set['amqp_broker_port'])

        # If we can't import qpid, then bail... but also:
        # If we can connect, then run tests.  If we can't, then don't.
        try:
            import qpid
            s = socket.create_connection(address)
            s.close()
            return False
        except:
            return True
    elif name == 'zeromq':
        return False
    else:
        raise ValueError("Unknown config set name.")


def make_setup_functions(kernel):
    for name, config_set in config_sets.items():

        def __setup():

            if should_skip_config_set(name, config_set):
                raise unittest.SkipTest("%s is not available." % name)

            config = get_moksha_appconfig()

            for key in flash_keys:
                if key in config:
                    del config[key]

            for key, value in config_set.items():
                config[key] = value

            kernel(config)

        yield __setup, name
