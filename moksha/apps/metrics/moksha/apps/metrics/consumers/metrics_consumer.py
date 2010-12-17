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
Moksha Metrics Consumer
=======================

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

from moksha.api.hub import Consumer

class MokshaMessageMetricsConsumer(Consumer):
    """
    This consumer listens to all messages on the `moksha_message_metrics`
    topic, and relays the message to the message.body['topic'] topic.
    """
    topic = 'moksha_message_metrics'

    def consume(self, message):
        self.send_message(message['body']['topic'], message['body']['data'])
