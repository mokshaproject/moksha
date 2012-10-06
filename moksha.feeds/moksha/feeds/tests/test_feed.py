# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
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

import tw2.core as twc

from moksha.feeds.widgets import Feed

# Monkey-patch moksha.common.utils.feed_cache so we don't have to actually
# fetch any feeds to run them
import moksha.common.utils
class FakeCache(object):
    def fetch(self, url):
        from bunch import Bunch
        feed = Bunch()
        feed.link = 'http://lewk.org/rss'
        feed.title = 'l e w k . o r g'
        feed.status = 200
        feed.feed = feed
        feed.entries = [feed, feed]
        def get(key, *args, **kw):
            return getattr(feed, key, '')
        feed.get = get
        return feed

moksha.common.utils.feed_cache = FakeCache()

class TestFeed(object):

    def test_feed_subclassing(self):
        """ Ensure that we can easily subclass our Feed widget """
        moksha.common.utils.feed_cache = FakeCache()
        class MyFeed(Feed):
            url = 'http://lewk.org/rss'
        feed = MyFeed()
        assert feed.url == 'http://lewk.org/rss'
        assert feed.num_entries() > 0
        for entry in feed.iterentries():
            pass
        for entry in feed.get_entries():
            pass

    def test_widget_children(self):
        """ Ensure that we can easily set Feeds as ToscaWidget children """
        moksha.common.utils.feed_cache = FakeCache()

        class MyWidget(twc.Widget):
            myfeedurl = 'http://lewk.org/rss'
            myfeed = Feed(url=myfeedurl)
            template = "mako:moksha.feeds.tests.templates.myfeed"

        widget = MyWidget
        assert len(widget.children) > 0

        rendered = widget.display()
        print rendered
        assert '<div id="myfeed"' in rendered

    def test_widget_child_with_dynamic_url(self):
        moksha.common.utils.feed_cache = FakeCache()

        class MyWidget(twc.Widget):
            url = twc.Param("a url")
            feed = Feed
            template = "mako:moksha.feeds.tests.templates.dynfeed"

        widget = MyWidget()
        rendered = widget.display(url='http://lewk.org/rss')
        assert '<div id="feed"' in rendered

    # Broken for the moment...
    #def test_genshi_widget(self):
    #    """ Ensure that our Feed widget can be rendered in a Genshi widget """
    #    moksha.common.utils.feed_cache = FakeCache()

    #    class MyWidget(twc.Widget):
    #        myfeed = Feed(url='http://lewk.org/rss')
    #        template = "genshi:moksha.feeds.tests.templates.myfeed"

    #    widget = MyWidget()
    #    rendered = widget.display()
    #    print rendered
    #    assert '<div id="myfeed"' in rendered

    def test_feed_generator(self):
        """ Ensure that our Feed object can return a generator """
        moksha.common.utils.feed_cache = FakeCache()
        feed = Feed(url='http://lewk.org/rss')
        iter = feed.iterentries()
        data = iter.next()
        assert iter.next()

    def test_feed_render_url(self):
        """ Ensure that a generic feed can be rendered with a url """
        moksha.common.utils.feed_cache = FakeCache()
        feed = Feed()
        rendered = feed.display(url='http://lewk.org/rss')
        assert 'l e w k . o r g' in rendered, rendered
