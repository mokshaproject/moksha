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

"""
:mod:`moksha.widgets.feedtree.consumer` - The feed consumer
===========================================================

The :class:`MokshaFeedConsumer` listens to all messages on the ``feeds`` topic.
If the ``action`` entry in the message header contains a valid command, it will
execute it.  Most of the time it will perform a specific action, such as getting
entries for a specific feed, and will send the data to the specified ``topic``.

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

from tg import config
from shove import Shove

from moksha.api.hub import Consumer
from moksha.lib.helpers import to_unicode

class MokshaFeedConsumer(Consumer):

    topic = 'moksha.feeds'

    def __init__(self):
        super(MokshaFeedConsumer, self).__init__()
        self.feed_storage = Shove(config.get('feed_store', 'simple://'),
                                  config.get('feed_cache', 'simple://'),
                                  compress=True)

    def consume(self, message):
        self.log.debug('MokshaFeedConsumer.consume(%s)' % message)
        action = message['body'].get('action')
        if action and hasattr(self, action):
            getattr(self, action)(message['body'])
        else:
            # new feed found?
            pass

    def get_feed(self, message):
        url = message['key']
        feed = self.feed_storage[url][1]
        entries = []
        for entry in feed['entries']:
            entries.append({
                'title': entry.get('title'),
                'isLazy': False,
                'isFolder': False,
                'rootVisible': False,
                'key': "%s::%s" % (url, entry.get('title', '').replace(' ','')),
                })
        self.send_message(message['topic'], {
                'entries': entries,
                'key': url,
                'action': 'get_feed'
                })

    def get_entry(self, message, **kw):
        key = message['key']
        if '::' in key:
            url, title = key.split('::')
            for entry in self.feed_storage[url][1]['entries']:
                content = entry.get('content', entry.get('summary'))
                if isinstance(content, list):
                    if isinstance(content[0], dict) and \
                       content[0].has_key('value'):
                        content = content[0]['value']
                content = """
                    <blockquote><h3><a href="%s">%s</a></h3><br/>%s</blockquote>
                """ % (entry.get('link', url), entry['title'], content)
                if entry['title'].replace(' ', '') == to_unicode(title):
                    self.send_message(message['topic'], {
                            'content': content,
                            'action': 'get_entry'
                            })
                    return
            raise Exception("Cannot find entry by title: %s" % title)
        else:
            raise Exception("Invalid entry key: %r" % key)
