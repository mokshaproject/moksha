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
# Authors: Luke Macken <lmacken@redhat.com>

from moksha.live import LiveWidget
from moksha.feed import Feed

class LiveFeedWidget(LiveWidget):
    """ A live streaming feed widget """
    topic = 'feed_example'
    template = '${feed()}'
    onmessageframe = """
        $.each(json, function() {
            $("#${id} ul li:last").remove();
            $("<li/>").hide().html(
                $("<a/>")
                  .attr("href", this.link)
                  .text(this.title))
              .prependTo($("#${id} ul"))
              .show();
        });
    """
    view = 'sidebar'
    placement = 'sidebar'

    def update_params(self, d):
        super(LiveFeedWidget, self).update_params(d)
        d['feed'] = Feed(d['id'], url=d.get('url', 'http://lewk.org/rss'))
