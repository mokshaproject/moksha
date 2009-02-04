from moksha.api.widgets.feed import Feed

class FeedDemo(Feed):
    url = 'http://feeds.arstechnica.com/arstechnica/index'

from moksha.api.widgets.feed.live import LiveFeedWidget

class LiveFeedDemo(LiveFeedWidget):
    url = 'http://feeds.arstechnica.com/arstechnica/index'
    topic = 'feed_demo'
