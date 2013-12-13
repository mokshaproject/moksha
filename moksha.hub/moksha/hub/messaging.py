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

class MessagingHubExtension(object):
    """
    A generic messaging hub.

    This class represents the base functionality of the protocol-level hubs.
    """

    def __init__(self):
        pass

    def send_message(self, topic, message, **headers):
        pass

    def subscribe(self, topic, callback):
        pass

    def unsubscribe(self, callback):
        pass
