import logging

from orbited import json
from datetime import timedelta
from twisted.internet.task import LoopingCall

from moksha.hub import MokshaHub
from moksha.api.hub import Consumer

log = logging.getLogger(__name__)

# setup.py
# [moksha.stream]
# feed = moksha.streams.feed:FeedStream

"""
Data Streams
============

Data streams in moksha are simply data generators that publish data
to an AMQP message queue.


What can they do?
- Poll data resources, feeds, connectors, API's etc.
    - Sends AMQP messages for new entries
    - Can keep various caches warm, such as the feed cache.
    - Can manipulate database models
    - Pull & Commit git repositories

"""

class DataStream(object):
    """ The parent DataStream class. """

    def __init__(self):
        self.hub = MokshaHub()

    def send_message(self, topic, message):
        """ Send a `message` to a specific `topic` """

        # Automatically encode non-strings to JSON
        if not isinstance(message, basestring):
            message = json.encode(message)

        self.hub.send_message(message, routing_key=topic)

    def stop(self):
        self.hub.stop()


class PollingDataStream(DataStream):
    """ A self-polling data stream.

    This class represents a data stream that wakes up at a given frequency,
    and calls the :meth:`poll` method.
    """
    frequency = None # Either a timedelta object, or the number of seconds

    def __init__(self):
        self.timer = LoopingCall(self.poll)
        if isinstance(self.frequency, timedelta):
            seconds = self.frequency.seconds + (self.frequency.days*24*60*60) + \
                    (self.frequency.microseconds / 1000000.0)
        else:
            seconds = self.frequency
        log.debug("Setting a %s second timers" % seconds)
        self.timer.start(seconds, now=False)

    def poll(self):
        raise NotImplementedError
