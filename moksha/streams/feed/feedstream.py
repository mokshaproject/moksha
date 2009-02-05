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

        - Iterate over all feeds in our global moksha feed cache..
            Problem:: the MokshaHub will not use this unless both it and the
                      Moksha WSGI app are using the same `feed_cache` database.

        - Keep feed caches fresh.
        - Send messages to topics for new entries
            `feed.$NAME` topic ?
            `tag.category
        """
        log.debug('FeedStream.poll()')
        # gather all feed urls... from all moksha.widget Feed objects, and 
        # make sure to search WidgetBunches as well!
        # Parse each feed, and send the data to it's AMQP topic
        # Repeat... but not too fast!
