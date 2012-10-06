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
#
# Authors: Luke Macken <lmacken@redhat.com>

import moksha.common.utils
import logging
import uuid

import tw2.core as twc

from shove import Shove
from feedcache.cache import Cache

log = logging.getLogger(__name__)

# An in-memory sqlite feed cache.  Utilized when the moksha WSGI middleware
# is unavailable.  By default, it will try and use the centralized
# moksha.common.utils.feed_cache, which is setup by the middleware, but will
# gracefully fallback to this cache.
feed_storage = None
feed_cache = None


class Feed(twc.Widget):
    """
    The Moksha Feed object.

    A Feed is initialized with an id and a url, and automatically handles the
    fetching, parsing, and caching of the data.

    """
    url = None
    template = 'mako:moksha.feeds.widgets.templates.feed_home'
    title = twc.Param("The title of this feed")
    link = twc.Param("The url to the site that this feed is for")
    entries = twc.Param("A list of feed entries", default=[])
    limit = twc.Param("A limit on the number of entries", default=None)

    @classmethod
    def iterentries(cls, limit=None):
        if not hasattr(cls, 'id'):
            cls.id = str(uuid.uuid4())
        id = cls.id
        url = cls.url
        if moksha.common.utils.feed_cache:
            feed = moksha.common.utils.feed_cache.fetch(url)
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

            cls.title = feed.headers.get('status')
            cls.link = feed.feed.get('link')
            return
        cls.link = feed.feed.get('link')
        try:
            cls.title = feed.feed.title
        except AttributeError:
            cls.title = 'Unable to parse feed'
            return

        for i, entry in enumerate(feed.get('entries', [])):
            entry['uid'] = '%s_%d' % (id, i)
            entry['link'] = entry.get('link')
            if i == limit:
                break
            yield entry

    @classmethod
    def get_entries(cls, url=None):
        if url:
            cls.url = url
        return [entry for entry in cls.iterentries()]

    @classmethod
    def num_entries(cls):
        return len(cls.get_entries())

    def prepare(self):
        super(Feed, self).prepare()
        for entry in type(self).iterentries(limit=self.limit):
            self.entries.append(entry)

    @classmethod
    def close(cls):
        global feed_storage
        try:
            feed_storage.close()
        except:
            pass
