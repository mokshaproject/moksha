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
