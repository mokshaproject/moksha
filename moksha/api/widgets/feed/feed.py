# This file is part of Moksha.
#
# Moksha is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Moksha is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Moksha.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2008, Red Hat, Inc.
# Authors: Luke Macken <lmacken@redhat.com>

import moksha
import logging

from tw.api import Widget
from shove import Shove
from feedcache.cache import Cache

log = logging.getLogger(__name__)

# An in-memory sqlite feed cache.  Utilized when the moksha WSGI middleware
# is unavailable.  By default, it will try and use the centralized
# moksha.feed_cache, which is setup by the middleware, but will gracefully
# fallback to this cache.
cache = None

class Feed(Widget):
    """ A powerful Feed object.

    A Feed is initialized with an id and a url, and automatically handles the
    fetching, parsing, and caching of the data.

    Ways of creating utilizing the Feed widget:

       0) Specifying the URL render-time

         feed = Feed()
         feed(url='http://foo.com/feed.xml')

       1) Subclassing

          class MyFeed(Feed):
              url = 'http://foo.com/feed.xml'

          myfeed = MyFeed()
          myfeed() # renders the widget, usually done in the template

       2) As ToscaWidget children

          class MyWidget(Widget):
              myfeedurl = 'http://foo.com/feed.xml'
              children = [Feed('myfeed', url=myfeedurl)]
              template = "${c.myfeed()}"

        3) As a generator

            feed = Feed(url='http://foo.com/feed.xml')
            for entry in feed.iterentries():
                print entry.title

    """
    url = None
    template = 'mako:moksha.api.widgets.feed.templates.feed_home'
    params = {
            'title': 'The title of this feed',
            'link': 'The url to the site that this feed is for',
            'entries': 'A list of feed entries',
    }

    def __new__(cls, *args, **kw):
        """ If we're instantiated with a specific view, then use the 
        appropriate template 
        Available views: home, canvas, profile
        """
        view = kw.get('view', False)
        if not view:
            view = getattr(cls, 'view', False)
        if view:
            class AlternateFeedView(cls):
                template = 'mako:moksha.feed.templates.feed_%s' % view
            return super(Feed, cls).__new__(AlternateFeedView, *args, **kw)
        return super(Feed, cls).__new__(cls, *args, **kw)

    def iterentries(self, d=None):
        url = self.url or d.get('url')
        if moksha.feed_cache:
            feed = moksha.feed_cache.fetch(url)
        else:
            # MokshaMiddleware not running, so setup our own feed cache.
            # This allows us to use this object outside of WSGI requests.
            global cache
            if not cache:
                cache = Cache(Shove('sqlite:///feeds.db'))
            feed = cache.fetch(url)
        if not (200 <= feed.status < 400):
            log.warning('Got %s status from %s: %s' % (
                        feed.status, url, feed.headers.get('status')))
            d['title'] = feed.headers.get('status')
            d['link'] = feed.feed.get('link')
            return
        if d:
            d['link'] = feed.feed.get('link')
            try:
                d['title'] = feed.feed.title
            except AttributeError:
                d['title'] = 'Unable to parse feed'
                return
        for i, entry in enumerate(feed.entries):
            entry['uid'] = '%s_%d' % (self.id, i)
            entry['link'] = entry.get('link')
            yield entry

    def entries(self):
        return [entry for entry in self.iterentries()]

    def num_entries(self):
        return len(self.entries())

    def update_params(self, d):
        super(Feed, self).update_params(d)
        d['entries'] = []
        limit = d.get('show')
        if limit:
            for i, entry in enumerate(self.iterentries(d)):
                if i >= limit:
                    break
                d['entries'].append(entry)
        else:
            for entry in self.iterentries(d):
                d['entries'].append(entry)
