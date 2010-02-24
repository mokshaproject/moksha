# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
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
from sqlalchemy.orm import sessionmaker
from twisted.internet.task import LoopingCall

from moksha.hub.hub import MokshaHub
from moksha.lib.helpers import create_app_engine

log = logging.getLogger('moksha.hub')

class DataStream(object):
    """ The parent DataStream class. """

    def __init__(self):
        self.hub = MokshaHub()
        self.log = log

        # If the stream specifies an 'app', then setup `self.engine` to
        # be a SQLAlchemy engine for that app, along with a configured DBSession
        app = getattr(self, 'app', None)
        self.engine = self.DBSession = None
        if app:
            self.engine = create_app_engine(app)
            self.DBSession = sessionmaker(bind=self.engine)()

    def send_message(self, topic, message):
        try:
            self.hub.send_message(topic, message)
        except Exception, e:
            log.error('Cannot send message: %s' % e)

    def stop(self):
        self.hub.close()
        if self.DBSession:
            self.DBSession.close()


class PollingDataStream(DataStream):
    """ A self-polling data stream.

    This class represents a data stream that wakes up at a given frequency,
    and calls the :meth:`poll` method.
    """
    frequency = None # Either a timedelta object, or the number of seconds
    now = False

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
        try:
            self.timer.stop()
        except Exception, e:
            self.log.warn(e)
