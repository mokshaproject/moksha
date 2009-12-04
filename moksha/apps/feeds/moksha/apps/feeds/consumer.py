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
        self.feed_storage = Shove(config['feed_cache'], compress=True)

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
        print "Sending response! back to %s" % message['topic']
        print len(entries)
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
