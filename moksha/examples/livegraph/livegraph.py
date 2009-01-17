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

from tw.api import Widget, CSSLink, JSLink, js_function
from moksha.widgets import LiveWidget
from moksha.widgets.stomp import stomp_subscribe

class LiveGraphWidget(LiveWidget):
    """
    This is an example live graph widget based on Michael Carter's article
    "Scalable Real-Time Web Architecture, Part 2: A Live Graph with Orbited,
    MorbidQ, and js.io".

    http://cometdaily.com/2008/10/10/scalable-real-time-web-architecture-part-2-a-live-graph-with-orbited-morbidq-and-jsio
    """
    params = ['id', 'onconnectedframe', 'onmessageframe']
    topic = 'graph'
    onmessageframe = 'modify_graph(bars, frame.body)'
    javascript = [JSLink(filename='static/livegraph.js', modname=__name__)]
    css = [CSSLink(filename='static/livegraph.css', modname=__name__)]
    template = '<div id="${id}" />'

    def update_params(self, d):
        super(LiveGraphWidget, self).update_params(d)
        self.add_call(js_function('init_graph')(self.id))
