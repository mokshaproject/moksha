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

from tg import config
from paste.deploy.converters import asbool

from feed import Feed
from moksha.api.widgets.live import TW1LiveWidget, TW2LiveWidget
import tw2.core as twc


class TW1LiveFeedWidget(TW1LiveWidget):
    """ A live streaming feed widget """
    params = {
            'url': 'The feed URL',
            'topic': 'A topic or list of topics to subscribe to',
            'feed': 'A moksha Feed object',
            'd': 'The widget data',
            'limit': 'The number of entries to display',
    }
    template = "mako:moksha.api.widgets.feed.templates.live"
    onmessage = """
        $.each(json, function() {
            $("#${id} ul li:last").remove();
            $("<li/>").html(
                $("<a/>")
                  .attr("href", this.link)
                  .text(this.title))
              .prependTo($("#${id} ul"));
        });
    """
    feed = Feed()
    topic = None
    limit = 10

    def update_params(self, d):
        if not d.get('topic'):
            d['topic'] = 'feed.%s' % d.get('url', self.url)
        super(TW1LiveFeedWidget, self).update_params(d)
        d.d = d


class TW2LiveFeedWidget(TW2LiveWidget):
    """ A live streaming feed widget """

    url = twc.Param("The feed URL")
    topic = twc.Param("A topic or list of topics to subscribe to")
    feed = twc.Param("A moksha Feed object")
    d = twc.Param("The widget data")
    limit = twc.Param("The number of entries to display")

    template = "mako:moksha.api.widgets.feed.templates.live"
    onmessage = """
        $.each(json, function() {
            $("#${id} ul li:last").remove();
            $("<li/>").html(
                $("<a/>")
                  .attr("href", this.link)
                  .text(this.title))
              .prependTo($("#${id} ul"));
        });
    """
    feed = Feed()
    topic = None
    limit = 10

    def prepare(self):
        if not getattr(self, 'topic', None):
            self.topic = 'feed.%s' % d.get('url', self.url)
        super(TW2LiveFeedWidget, self).prepare()
        self.d = self  # Wha?

if asbool(config.get('moksha.use_tw2', False)):
    LiveFeedWidget = TW2LiveFeedWidget
else:
    LiveFeedWidget = TW1LiveFeedWidget
