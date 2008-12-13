from tw.api import Widget
from moksha.feed import Feed

class TestFeed(object):

    def test_feed_subclassing(self):
        class MyFeed(Feed):
            url = 'http://lewk.org/rss'
        feed = MyFeed()
        assert feed.url == 'http://lewk.org/rss'
        assert feed.num_entries() > 0
        for entry in feed.iterentries():
            pass
        for entry in feed.entries():
            pass

    def test_widget_children(self):
        class MyWidget(Widget):
            myfeedurl = 'http://lewk.org/rss'
            children = [Feed('myfeed', url=myfeedurl)]
            template = "mako:${c.myfeed()}"
        widget = MyWidget()
        assert widget.c.myfeed

    def test_feed_generator(self):
        feed = Feed(url='http://lewk.org/rss')
        iter = feed.iterentries()
        data = iter.next()
        assert iter.next()
