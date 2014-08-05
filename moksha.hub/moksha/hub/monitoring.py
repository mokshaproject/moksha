# This file is part of Moksha.
# Copyright (C) 2014  Red Hat, Inc.
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
#
# Authors: Ralph Bean  <rbean@redhat.com>

from moksha.hub.api import PollingProducer
import os
import string
import zmq
import json

import logging
log = logging.getLogger(__name__)


class MonitoringProducer(PollingProducer):
    frequency = 5

    ctx = None
    socket = None

    def __init__(self, hub, *args, **kwargs):

        key = 'moksha.monitoring.socket'
        endpoint = hub.config.get(key)
        if not endpoint:
            log.info("No %r defined.  Monitoring disabled." % key)
            return

        log.info("Establishing monitor sock at %r" % endpoint)

        # Set up a special socket for ourselves
        self.ctx = zmq.Context()
        self.socket = self.ctx.socket(zmq.PUB)
        self.socket.bind(endpoint)

        # If this is a unix socket (which is almost always is) then set some
        # permissions so that whatever monitoring service is deployed can talk
        # to us.
        mode = hub.config.get('moksha.monitoring.socket.mode')
        if endpoint.startswith("ipc://") and mode:
            mode = string.atoi(mode, base=8)
            path = endpoint.split("ipc://")[-1]
            os.chmod(path, mode)

        super(MonitoringProducer, self).__init__(hub, *args, **kwargs)

    def serialize(self, obj):
        if isinstance(obj, list):
            return [self.serialize(item) for item in obj]
        elif isinstance(obj, dict):
            return dict([(k, self.serialize(v)) for k, v in obj.items()])
        elif hasattr(obj, '__json__'):
            return obj.__json__()
        return obj

    def poll(self):
        data = {
            "consumers": self.serialize(self.hub.consumers),
            "producers": self.serialize(self.hub.producers),
        }
        if self.socket:
            self.socket.send(json.dumps(data))

    def stop(self):
        super(MonitoringProducer, self).stop()
        if self.socket:
            self.socket.close()
            self.socket = None

        if self.ctx:
            self.ctx.term()
            self.ctx = None
