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
from moksha.api.widgets import LiveWidget

class LiveFeedWidget(LiveWidget):
    """ A live streaming feed widget """
    params = {
            'url': 'The feed URL',
            'topic': 'A topic or list of topics to subscribe to',
            'feed': 'A moksha Feed object',
            'd': 'The widget data',
            'limit': 'The number of entries to display',
    }
    template = '${feed(id=id, url=url, limit=limit)}'
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
        super(LiveFeedWidget, self).update_params(d)
        d.d = d
