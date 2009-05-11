# This file is part of Moksha.
# Copyright (C) 2008-2009  Red Hat, Inc.
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

from tw.api import Widget
from moksha.api.widgets.feed import Feed

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
        class MyWidget(Widget):
            myfeedurl = 'http://lewk.org/rss'
            children = [Feed('myfeed', url=myfeedurl)]
            engine_name = 'mako'
            template = "${c.myfeed()}"
        widget = MyWidget()
        assert widget.c.myfeed
        rendered = widget()
        assert '<div id="myfeed"' in rendered

    def test_widget_child_with_dynamic_url(self):
        class MyWidget(Widget):
            params = ['url']
            children = [Feed('feed')]
            template = "${c.feed(url=url)}"
            engine_name = 'mako'
        widget = MyWidget()
        rendered = widget(url='http://lewk.org/rss')
        assert '<div id="feed"' in rendered

    def test_genshi_widget(self):
        """ Ensure that our Feed widget can be rendered in a Genshi widget """
        class MyWidget(Widget):
            children = [Feed('myfeed', url='http://lewk.org/rss')]
            engine_name = 'genshi'
            template = """
            <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
              "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
              <html xmlns="http://www.w3.org/1999/xhtml"
                    xmlns:py="http://genshi.edgewall.org/"
                    xmlns:xi="http://www.w3.org/2001/XInclude">
                ${c.myfeed()}
             </html>
            """
        widget = MyWidget()
        rendered = widget()
        print rendered
        assert '<div id="myfeed"' in rendered

    def test_feed_generator(self):
        """ Ensure that our Feed object can return a generator """
        feed = Feed(url='http://lewk.org/rss')
        iter = feed.iterentries()
        data = iter.next()
        assert iter.next()

    def test_feed_render_url(self):
        """ Ensure that a generic feed can be rendered with a url """
        feed = Feed()
        rendered = feed(url='http://lewk.org/rss')
        assert 'l e w k . o r g' in rendered
