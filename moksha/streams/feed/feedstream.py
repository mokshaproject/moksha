import logging

from datetime import timedelta

from moksha.api.streams import PollingDataStream

log = logging.getLogger(__name__)

class FeedStream(PollingDataStream):
    """
    If you expose your feed widget on the moksha.widget entry point,
    then Moksha will automatically handle polling it.  Upon new entries,
    AMQP messages will be sent to the `feeds.$URL` queue.
    """

    frequency = timedelta(minutes=15)

    def poll(self):
        """ Poll all known feeds.

        - Keep feed caches fresh.
        - Send AMQP messages for new entries
        """
        log.debug('FeedStream.poll()')
        # gather all feed urls... from all moksha.widget Feed objects, and 
        # make sure to search WidgetBunches as well!
        # Parse each feed, and send the data to it's AMQP topic
        # Repeat... but not too fast!
