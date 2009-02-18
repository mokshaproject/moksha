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

    def __init__(self, now=True):
        super(PollingDataStream, self).__init__()
        self.timer = LoopingCall(self.poll)
        if isinstance(self.frequency, timedelta):
            seconds = self.frequency.seconds + \
                    (self.frequency.days * 24 * 60 * 60) + \
                    (self.frequency.microseconds / 1000000.0)
        else:
            seconds = self.frequency
        log.debug("Setting a %s second timers" % seconds)
        self.timer.start(seconds, now=now)

    def poll(self):
        raise NotImplementedError

    def stop(self):
        super(PollingDataStream, self).stop()
        self.timer.stop()
