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

from tw.jquery.flot import FlotWidget
from tw.api import js_callback
from moksha.live import LiveWidget
from moksha.stomp import stomp_subscribe

class LiveFlotWidget(LiveWidget):
    """ A live graphing widget """
    children = [FlotWidget('flot')]
    params = ['id', 'data', 'options', 'height', 'width',
              'onconnectedframe', 'onmessageframe']
    onconnectedframe = stomp_subscribe('/topic/flot_example')
    onmessageframe = js_callback("""function(frame){
            var data = JSON.parse(frame.body)[0];
            $.plot($("#liveflot_flot"), data["data"], data["options"]);
    }""")
    template = "${c.flot(data=data,options=options,height=height,width=width)}"
    engine_name = 'mako'
    height = '250px'
    width = '390px'
    data = [{}]
    options = {}
