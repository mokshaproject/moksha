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
:mod:`moksha.widgets.feedtree` - A dynamic feed tree
====================================================

There are currently two implementations of this application, an `ajax` version
and a `live` version.  The ajax version makes a new request to our WSGI server
each time, where as the `live` implementation communicates over a persistent
Stomp-driven Orbited TCPSocket.   The live widget will automatically connect up
to a unique message topic that it uses to communicate with the Moksha Feed
Consumer in the Moksha Hub.  It also listens for changes in the feeds that
it is viewing.

.. widgetbrowser:: moksha.widgets.feedtree.moksha_feedreader
   :tabs: demo, source, template
   :size: x-large

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

from tg import config
from tw.api import js_callback, Widget, JSLink, CSSLink
from tw.jquery import jquery_js, jQuery
from tw.jquery.dynatree import Dynatree
from uuid import uuid4

from moksha.api.widgets.live import LiveWidget

class MokshaAjaxFeedTree(Dynatree):
    title = 'Moksha Ajax Feed Tree'
    rootVisible = True
    persist = True
    initAjax = {
            'url': '/apps/feeds/init_tree',
            'data': {'key': 'root'}
    }
    onActivate = js_callback("""
        function(dtnode) {
          $('#TopPane').load('/apps/feeds/get_entries?key=' + dtnode.data.key.replace(/ /, ''));
        }
    """.replace('\n', ''))


class MokshaAjaxFeedEntriesTree(Dynatree):
    rootVisible = False
    persist = True
    onActivate = js_callback("""function(dtnode) { $('#BottomPane').load('/apps/feeds/get_entry?key=' + dtnode.data.key); }""")


class MokshaLiveFeedTree(Dynatree, LiveWidget):
    title = 'Moksha Live Feed Tree'
    rootVisible = True
    persist = True
    fx = {'height': 'toggle', 'duration': 200}
    initAjax = {
            'url': '/apps/feeds/init_tree',
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
    #    dtnode.appendAjax({url: '/apps/feeds/get_feed',
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
    name = 'Moksha Feed Reader'
    template = 'mako:moksha.widgets.feedtree.templates.feedreader'
    children = [feed_tree, feed_entries_tree]
    javascript = [splitter_js]
    css = [splitter_css]
    container_options = {
            'top': 80,
            'left': 80,
            'height': 600,
            'width': 900,
            'icon': 'browser.png',
            }

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
