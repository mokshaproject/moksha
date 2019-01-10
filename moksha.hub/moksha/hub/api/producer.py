# This file is part of Moksha.
# Copyright (C) 2008-2014  Red Hat, Inc.
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
:mod:`moksha.hub.api.producer - The Moksha Producer API
=======================================================
"""

import logging
import time

from datetime import timedelta

import moksha.hub.reactor
from moksha.common.lib.helpers import create_app_engine

log = logging.getLogger('moksha.hub')


class Producer(object):
    """ The parent Producer class. """

    # Internal use only
    _initialized = False
    _exception_count = 0

    def __init__(self, hub):
        self.hub = hub
        self.log = log

        # If the stream specifies an 'app', then setup `self.engine` to
        # be a SQLAlchemy engine for that app, along with a configured
        # DBSession
        app = getattr(self, 'app', None)
        self.engine = self.DBSession = None
        if app:
            log.debug("Setting up individual engine for producer")
            from sqlalchemy.orm import sessionmaker
            self.engine = create_app_engine(app)
            self.DBSession = sessionmaker(bind=self.engine)()

        self._initialized = True

    def __json__(self):
        return {
            "name": type(self).__name__,
            "module": type(self).__module__,
            "initialized": self._initialized,
            "exceptions": self._exception_count,
        }

    def send_message(self, topic, message):
        try:
            self.hub.send_message(topic, message)
        except Exception as e:
            log.error('Cannot send message: %s' % e)

    def stop(self):
        if hasattr(self, 'hub') and self.hub:
            self.hub.close()
        if hasattr(self, 'DBSession') and self.DBSession:
            self.DBSession.close()


class PollingProducer(Producer):
    """ A self-polling producer

    This class represents a data stream that wakes up at a given frequency,
    and calls the :meth:`poll` method.
    """
    frequency = None  # Either a timedelta object, or the number of seconds
    now = False
    die = False

    def __init__(self, hub):
        super(PollingProducer, self).__init__(hub)

        if isinstance(self.frequency, timedelta):
            self.frequency = self.frequency.seconds + \
                (self.frequency.days * 24 * 60 * 60) + \
                (self.frequency.microseconds / 1000000.0)

        self._last_ran = None
        # This is used to determine if the configured frequency has been meet,
        # and the poller should run. This allows the poller to check if
        # self.die is True more frequently.
        self._until_next_poll = self.frequency

        log.debug("Setting a %s second timer" % self.frequency)
        moksha.hub.reactor.reactor.callInThread(self._work)

    def __json__(self):
        data = super(PollingProducer, self).__json__()
        data.update({
            "frequency": self.frequency,
            "now": self.now,
            "last_ran": self._last_ran,
        })
        return data

    def poll(self):
        raise NotImplementedError

    def _poll(self):
        self._last_ran = time.time()
        try:
            self.poll()
            self._exception_count = 0  # Reset to 0 if things are gravy
        except Exception:
            # Otherwise, keep track of how many exceptions we hit in a row
            self._exception_count = self._exception_count + 1
            # And re-raise the exception so it can be logged.
            raise

    def _work(self):
        # If asked to, we can fire immediately at startup
        if self.now:
            self._poll()

        while not self.die:
            if not self.frequency:
                # If no frequency is set, just continuously poll
                self._poll()
                continue

            # If _until_next_poll is less than or equal to 0, that means
            # the frequency has been met and the poller needs to run again
            if self._until_next_poll <= 0:
                self._poll()
                # Reset _until_next_poll so that polling doesn't happen
                # until the frequency is met again
                self._until_next_poll = self.frequency
            else:
                # Only sleep 5 seconds (or _until_next_poll if it's shorter) at
                # a time since we want to check if the poller should die
                # frequently. Otherwise, you'll end up with Moksha Hub in a
                # state where the hub is stopped but the poller is still
                # sleeping until the frequency is met
                sleep_time = min((5, self._until_next_poll))
                time.sleep(sleep_time)
                self._until_next_poll -= sleep_time

    def stop(self):
        super(PollingProducer, self).stop()
        self.die = True
