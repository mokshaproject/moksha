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

from feed import Feed
from moksha.wsgi.widgets.api.live import LiveWidget
import tw2.core as twc


class LiveFeedWidget(LiveWidget):
    """ A live streaming feed widget """

    url = twc.Param("The feed URL")
    topic = twc.Param("A topic or list of topics to subscribe to")
    feed = twc.Param("A moksha Feed object")
    d = twc.Param("The widget data")
    limit = twc.Param("The number of entries to display")

    template = "mako:mako:moksha.feeds.widgets.templates.live"
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
        super(LiveFeedWidget, self).prepare()
        self.d = self  # Wha?
