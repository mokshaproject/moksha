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

from nose.tools import raises


class TestFeed(object):

    def test_feed_subclassing(self):
        """ Ensure that we can easily subclass our Feed widget """
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
        class MyWidget(twc.Widget):
            url = twc.Param("a url")
            feed = Feed
            template = "mako:moksha.feeds.tests.templates.dynfeed"

        widget = MyWidget()
        rendered = widget.display(url='http://lewk.org/rss')
        assert '<div id="feed"' in rendered

    def test_feed_generator(self):
        """ Ensure that our Feed object can return a generator """
        feed = Feed(url='http://lewk.org/rss')
        iter = feed.iterentries()
        data = iter.next()
        assert iter.next()

    def test_feed_render_url(self):
        """ Ensure that a generic feed can be rendered with a url """
        feed = Feed()
        rendered = feed(url='http://lewk.org/rss').display()
        assert 'l e w k . o r g' in rendered, rendered

    @raises(ValueError)
    def test_feed_demands_url(self):
        """ Ensure that Feeds require a url """
        Feed().display()
