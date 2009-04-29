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

from datetime import timedelta
from twisted.internet.task import LoopingCall

from moksha.hub.hub import MokshaHub

log = logging.getLogger('moksha.hub')

class DataStream(object):
    """ The parent DataStream class. """

    def __init__(self):
        self.hub = MokshaHub()

    def send_message(self, topic, message):
        try:
            self.hub.send_message(topic, message)
        except Exception, e:
            log.error('Cannot send message: %s' % e)

    def stop(self):
        self.hub.close()


class PollingDataStream(DataStream):
    """ A self-polling data stream.

    This class represents a data stream that wakes up at a given frequency,
    and calls the :meth:`poll` method.
    """
    frequency = None # Either a timedelta object, or the number of seconds
    now = True

    def __init__(self):
        super(PollingDataStream, self).__init__()
        self.timer = LoopingCall(self.poll)
        if isinstance(self.frequency, timedelta):
            seconds = self.frequency.seconds + \
                    (self.frequency.days * 24 * 60 * 60) + \
                    (self.frequency.microseconds / 1000000.0)
        else:
            seconds = self.frequency
        log.debug("Setting a %s second timers" % seconds)
        self.timer.start(seconds, now=self.now)

    def poll(self):
        raise NotImplementedError

    def stop(self):
        super(PollingDataStream, self).stop()
        self.timer.stop()
