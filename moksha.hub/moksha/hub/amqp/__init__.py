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

"""
Here is where we configure which AMQP hub implementation we are going to use.
"""

import logging
log = logging.getLogger("moksha.hub")

try:
    from moksha.hub.amqp.qpid010 import QpidAMQPHubExtension
    AMQPHubExtension = QpidAMQPHubExtension
except ImportError:
    log.warning("Cannot find qpid python module. Make sure you have python-qpid installed.")
    try:
        from moksha.hub.amqp.pyamqplib import AMQPLibHubExtension
        AMQPHubExtension = AMQPLibHubExtension
    except ImportError:
        log.warning("Cannot find pyamqplib")
        log.warning("Using FakeHub AMQP broker. Don't expect AMQP to work")
        class FakeHub(object):
            pass
        AMQPHub = FakeHub

