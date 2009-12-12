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
#
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
feed_storage = None
feed_cache = None

class Feed(Widget):
    """
    The Moksha Feed object.

    A Feed is initialized with an id and a url, and automatically handles the
    fetching, parsing, and caching of the data.

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

        :deprecated: This is old, and will be going away soon
        """
        view = kw.get('view', False)
        if not view:
            view = getattr(cls, 'view', False)
        if view:
            class AlternateFeedView(cls):
                template = 'mako:moksha.feed.templates.feed_%s' % view
            return super(Feed, cls).__new__(AlternateFeedView, *args, **kw)
        return super(Feed, cls).__new__(cls, *args, **kw)

    def iterentries(self, d=None, limit=None):
        url = self.url or d.get('url')
        id = d and d.get('id', self.id) or self.id
        if moksha.feed_cache:
            feed = moksha.feed_cache.fetch(url)
        else:
            # MokshaMiddleware not running, so setup our own feed cache.
            # This allows us to use this object outside of WSGI requests.
            global feed_cache, feed_storage
            if not feed_cache:
                feed_storage = Shove('sqlite:///feeds.db', compress=True)
                feed_cache = Cache(feed_storage)
            feed = feed_cache.fetch(url)
        if not (200 <= feed.get('status', 200) < 400):
            log.warning('Got %s status from %s: %s' % (
                        feed['status'], url, feed.headers.get('status')))
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
        for i, entry in enumerate(feed.get('entries', [])):
            entry['uid'] = '%s_%d' % (id, i)
            entry['link'] = entry.get('link')
            if i == limit:
                break
            yield entry

    def get_entries(self, url=None):
        d = {}
        if url:
            d['url'] = url
        return [entry for entry in self.iterentries(d=d)]

    def num_entries(self):
        return len(self.get_entries())

    def update_params(self, d):
        super(Feed, self).update_params(d)
        d['entries'] = []
        limit = d.get('limit')
        for entry in self.iterentries(d, limit=limit):
            d['entries'].append(entry)

    def close(self):
        global feed_storage
        try:
            feed_storage.close()
        except:
            pass
