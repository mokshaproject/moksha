# This file is part of Moksha.
# Copyright (C) 2008-2009  Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

from orbited import json
from moksha.api.hub import Consumer

log = logging.getLogger('moksha.hub')

class MokshaMessageMetricsConsumer(Consumer):
    """
    This consumer listens to all messages on the `moksha_message_metrics`
    topic, and relays the messgae to the message['headers']['topic']
    """
    topic = 'moksha_message_metrics'

    def consume(self, message):
        topic = message['headers'].get('topic')
        if topic:
            self.send_message(topic, json.encode(message['body']))
        else:
            log.error('No `topic` specified in moksha_message_metrics message')
