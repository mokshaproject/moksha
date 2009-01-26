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

from random import random
from datetime import timedelta

from tw.api import CSSLink, JSLink, js_function

from moksha.api.widgets import LiveWidget
from moksha.api.streams import PollingDataStream

class LiveGraphWidget(LiveWidget):
    """
    This is an example live graph widget based on Michael Carter's article
    "Scalable Real-Time Web Architecture, Part 2: A Live Graph with Orbited,
    MorbidQ, and js.io".

    http://cometdaily.com/2008/10/10/scalable-real-time-web-architecture-part-2-a-live-graph-with-orbited-morbidq-and-jsio
    """
    params = ['id', 'onconnectedframe', 'onmessageframe']
    topic = 'graph_demo'
    onmessage = 'modify_graph(bars, frame.body)'
    javascript = [JSLink(filename='static/livegraph.js', modname=__name__)]
    css = [CSSLink(filename='static/livegraph.css', modname=__name__)]
    template = '<div id="${id}" />'

    def update_params(self, d):
        super(LiveGraphWidget, self).update_params(d)
        self.add_call(js_function('init_graph')(self.id))



class LiveGraphDataStream(PollingDataStream):
    """
    This is the main data producer for our live graph widget.
    """
    frequency = timedelta(seconds=0.5)

    data_vector_length = 10
    delta_weight = 0.1
    max_value = 400 # NB: this in pixels
    data = [int(random()*max_value) for x in xrange(data_vector_length)]

    def poll(self):
        self.data = [
            min(max(datum + (random() - .5) * self.delta_weight *
                    self.max_value, 0),
                self.max_value)
            for
            datum in self.data
        ]
        self.send_message('graph_demo', self.data)
