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
#
# Authors: Luke Macken <lmacken@redhat.com>

from moksha.hub.messaging import MessagingHubExtension

class BaseZMQHubExtension(MessagingHubExtension):
    """
    A skeleton class for what we expect from a zeromq implementation.
    This allows us to bounce between different zeromq modules without too much
    pain and suffering.
    """

    def __init__(self):
        super(BaseZMQHubExtension, self).__init__()

    def send_message(self, topic, message, **headers):
        super(BaseZMQHubExtension, self).send_message(topic, message, **headers)

    def subscribe(self, topic, callback):
        super(BaseZMQHubExtension, self).subscribe(topic, callback)

    def unsubscribe(self, callback):
        super(BaseZMQHubExtension, self).unsubscribe(callback)

    def close(self):
        super(BaseZMQHubExtension, self).close()
