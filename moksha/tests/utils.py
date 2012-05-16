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

import unittest
import functools

from moksha.lib.helpers import get_moksha_appconfig


def crosstest(method):
    @functools.wraps(method)
    def wrapper(self):
        for setup, name in self._setUp():
            def _inner(name):
                setup()
                try:
                    return method(self)
                finally:
                    self._tearDown()

            yield _inner, name

    return wrapper

flash_list = [
    "stomp_broker",
    "stomp_port",
    "stomp_user",
    "stomp_pass",
    "amqp_broker",
    "amqp_broker_host",
    "amqp_broker_port",
    "amqp_broker_user",
    "amqp_broker_pass",
    "amqp_broker_ssl",
    "zmq_enabled",
    "zmq_publish_endpoints",
    "zmq_subscribe_endpoints",
    "zmq_strict",
    "zmq_subscribe_method",
]

config_sets = {
    'stomp': dict(
        stomp_broker="localhost",
        stomp_port="61613",
        stomp_user="guest",
        stomp_pass="guest",
    ),
    'amqp': dict(
        amqp_broker="guest/guest@localhost",
        amqp_broker_host="localhost",
        amqp_broker_port="5672",
        amqp_broker_user="guest",
        amqp_broker_pass="guest",
        amqp_broker_ssl="False",
    ),
    'zeromq': dict(
        zmq_enabled="True",
        zmq_publish_endpoints="tcp://*:6543",
        zmq_subscribe_endpoints="tcp://127.0.0.1:6543",
        zmq_strict="True",
    ),
}


def should_skip_config_set(name, config_set):
    # TODO -- write code to detect if qpid or orbited are running
    if name in ['amqp', 'stomp']:
        return True
    else:
        return False


def make_setup_functions(kernel):
    for name, config_set in config_sets.items():

        def __setup():

            if should_skip_config_set(name, config_set):
                raise unittest.SkipTest("%s is not available." % name)

            config = get_moksha_appconfig()

            for key in flash_list:
                if key in config:
                    del config[key]

            for key, value in config_set.items():
                config[key] = value

            kernel(config)

        yield __setup, name
