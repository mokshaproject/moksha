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

"""
:mod:`moksha.widgets.feedtree` - A dynamic feed tree
====================================================

There are currently two implementations of this application, an `ajax` version
and a `live` version.  The ajax version makes a new request to our WSGI server
each time, where as the `live` implementation communicates over a persistent
Stomp-driven Orbited TCPSocket.   The live widget will automatically connect up
to a unique message topic that it uses to communicate with the Moksha Feed
Consumer in the Moksha Hub.

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

import moksha
import logging

from tg import expose, tmpl_context, config
from tw.api import js_callback, Widget, JSLink, CSSLink
from tw.jquery import jquery_js, jQuery
from tw.jquery.dynatree import Dynatree
from uuid import uuid4
from shove import Shove
from pylons import cache
from orbited import json
from formencode import validators

from moksha.lib.base import Controller
from moksha.api.widgets.live import LiveWidget

from moksha.api.hub import Consumer
from moksha.lib.helpers import trace

log = logging.getLogger('moksha.hub')

class MokshaFeedConsumer(Consumer):

    topic = 'feeds'

    def __init__(self):
        super(MokshaFeedConsumer, self).__init__()
        self.feed_storage = Shove(config['feed_cache'], compress=True)

    def consume(self, message):
        log.debug('MokshaFeedConsumer.consume(%s)' % message)
        action = message['headers'].get('action')
        if action and hasattr(self, action):
            getattr(self, action)(message)
        else:
            # new feed found?
            pass

    def get_feed(self, message):
        url = message['body']
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
        self.send_message(message['headers']['topic'],
                json.encode({'entries': entries, 'key': url,
                             'action': 'get_feed'}))

    def get_entry(self, message, **kw):
        key = message['body']
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
                if entry['title'].replace(' ', '') == title:
                    self.send_message(message['headers']['topic'],
                            json.encode({'content': content,
                                         'action': 'get_entry'}))
            raise Exception("Cannot find entry by title: %s" % title)
        else:
            raise Exception("Invalid entry key: %r" % key)


class MokshaAjaxFeedTree(Dynatree):
    title = 'Moksha Ajax Feed Tree'
    rootVisible = True
    persist = True
    initAjax = {
            'url': '/appz/feeds/init_tree',
            'data': {'key': 'root'}
    }
    onActivate = js_callback("""
        function(dtnode) {
          $('#TopPane').load('/appz/feeds/get_entries?key=' + dtnode.data.key.replace(/ /, ''));
        }
    """.replace('\n', ''))


class MokshaAjaxFeedEntriesTree(Dynatree):
    rootVisible = False
    persist = True
    onActivate = js_callback("""function(dtnode) { $('#BottomPane').load('/appz/feeds/get_entry?key=' + dtnode.data.key); }""")


class MokshaLiveFeedTree(Dynatree, LiveWidget):
    title = 'Moksha Live Feed Tree'
    rootVisible = True
    persist = True
    fx = {'height': 'toggle', 'duration': 200}
    initAjax = {
            'url': '/appz/feeds/init_tree',
            'data': {'key': 'root'}
    }
    onActivate = js_callback("function(dtnode) { stomp.send(dtnode.data.key, 'feeds', {topic: moksha_feed_topic, action: 'get_feed'}); }")

    onmessage = """
      if (json.action == 'get_feed') {
          var tree = $("#moksha_feedreader_feed_entries_tree").dynatree("getRoot");
          tree.removeChildren();
          tree.append(json.entries);
      } else if (json.action == 'get_entry') {
          $('#BottomPane').html(json.content);
      } else if (json.action == 'new_entry') {
          /* TODO */
      }
    """

    def __init__(self, *args, **kw):
        Dynatree.__init__(self, *args, **kw)
        self.template += """
            <script>
                var moksha_feed_topic = "${topic}";
            </script>
        """
        LiveWidget.__init__(self, *args, **kw)

    def update_params(self, d):
        # the unique queue to use over our stomp TCPSocket
        d['topic'] = str(uuid4()) 
        Dynatree.update_params(self, d)
        # apparently the dynatree calls our live widget's update_params for us
        #LiveWidget.update_params(self, d)

    #onLazyRead = js_callback("""function(dtnode) {
    #    dtnode.appendAjax({url: '/appz/feeds/get_feed',
    #                       data: {key: dtnode.data.key, mode: 'all'},
    #                       cache: false
    #                      });
    #}""".replace('\n', ''))

class MokshaLiveFeedEntriesTree(Dynatree):
    rootVisible = False
    persist = True
    onActivate = js_callback("""
        function(dtnode) {
            stomp.send(dtnode.data.key, 'feeds',
                       {topic: moksha_feed_topic, action: 'get_entry'});

            /* Unsubscribe from current feed, subscribe to new one */
        }
    """.replace('\n', ''))


## Load our feed tree widgets.
feedtree_engine = config.get('moksha.feedtree.engine', 'live')
if feedtree_engine == 'live':   # Live widgets
    feed_tree = MokshaLiveFeedTree('feed_tree')
    feed_entries_tree = MokshaLiveFeedEntriesTree('feed_entries_tree')
elif feedtree_engine == 'ajax': # Ajax widgets
    feed_tree = MokshaAjaxFeedTree('feed_tree')
    feed_entries_tree = MokshaAjaxFeedEntriesTree('feed_entries_tree')


splitter_js = JSLink(filename='static/splitter.js',
                     javascript=[jquery_js],
                     modname=__name__)

splitter_css = CSSLink(filename='static/main.css',
                       media='all', 
                       modname=__name__)

class MokshaFeedReaderWidget(Widget):
    javascript = [splitter_js]
    css = [splitter_css]
    children = [feed_tree, feed_entries_tree]
    template = """
        <div id="${id}" class="moksha-feedreader">
          <div id="LeftPane">
            ${c.feed_tree()}
          </div>
          <div id="RightPane">
            <div id="TopPane">
              ${c.feed_entries_tree()}
            </div>
            <div id="BottomPane">
            </div>
          </div>
        </div>
    """
    engine_name = 'mako'

    def update_params(self, d):
        super(MokshaFeedReaderWidget, self).update_params(d)
        self.add_call(jQuery('#' + d.id).splitter({
            'splitVertical': True,
            'outline': True,
            'sizeLeft': True,
            'anchorToWindow': True,
            'accessKey': "I",
            }))
        self.add_call(jQuery('#RightPane').splitter({
            'splitHorizontal': True,
            'sizeTop': True,
            'accessKey': "H",
            }))

moksha_feedreader = MokshaFeedReaderWidget('moksha_feedreader')

class FeedController(Controller):

    @expose('mako:moksha.templates.widget')
    def index(self, *args, **kw):
        tmpl_context.widget = moksha_feedreader
        return dict(options={})

    @expose()
    def init_tree(self, key, fresh=False, **kw):
        c = cache.get_cache('feeds')
        if fresh:
            return self._get_feed_titles(fresh=fresh)
        else:
            return c.get_value(key='feed_titles',
                               createfunc=self._get_feed_titles,
                               expiretime=3600)

    def _get_feed_titles(self, fresh=False):
        results = []
        for feed in moksha.feed_storage.keys():
            if not feed:
                raise Exception('None feed?!')
            if fresh:
                feed_data = moksha.feed_cache.fetch(feed)
            else:
                timestamp, feed_data = moksha.feed_storage[feed]
            if not feed_data:
                log.debug("no feed_data, refetching")
                feed_data = moksha.feed_cache.fetch(feed)
                if not feed_data:
                    log.debug("NO FEED DATA AFTER FRESH FETCH!!!!")
                    continue
            channel = feed_data.get('channel')
            if not channel:
                continue
            title = channel.get('title')
            results.append({
                'title': title,
                'key': feed,
                'isLazy': False,
                'isFolder': True,
                })
        return json.encode(results)

    @expose()
    def get_feed(self, key, *args, **kw):
        if '::' in key:
            url, title = key.split('::')
            for entry in moksha.feed_storage[url][1]['entries']:
                content = entry.get('content', entry.get('summary'))
                content = '<span style="line-height:100%%;">%s</span>' % content
                if entry['title'] == title:
                    return json.encode([{'title': content, 'isLazy': False}])
            raise Exception("Cannot find entry by title: %s" % title)

        feed = moksha.feed_storage[key][1]
        entries = []
        for entry in feed['entries']:
            entries.append({
                'title': entry.get('title'),
                'isLazy': True,
                'isFolder': True,
                'key': "%s::%s" % (key, entry.get('title')),
                })
        return json.encode(entries)

    @expose('mako:moksha.templates.widget')
    def get_entries(self, key, **kw):
        tmpl_context.widget = feed_entries_tree
        feed = moksha.feed_storage[key][1]
        entries = []
        for entry in feed['entries']:
            entries.append({
                'title': entry.get('title'),
                'isLazy': False,
                'isFolder': False,
                'rootVisible': False,
                'key': "%s::%s" % (key, entry.get('title','').replace(' ','')),
                })
        return dict(options={'tree_children': entries})

    @expose()
    def get_entry(self, key, **kw):
        if '::' in key:
            url, title = key.split('::')
            for entry in moksha.feed_storage[url][1]['entries']:
                content = entry.get('content', entry.get('summary'))
                if isinstance(content, list):
                    if isinstance(content[0], dict) and \
                       content[0].has_key('value'):
                        content = content[0]['value']
                content = """
                    <blockquote><h3><a href="%s">%s</a></h3><br/>%s</blockquote>
                """ % (entry.get('link', url), entry['title'], content)
                if entry['title'].replace(' ', '') == title:
                    return content
            raise Exception("Cannot find entry by title: %s" % title)
        else:
            raise Exception("Invalid entry key: %r" % key)
