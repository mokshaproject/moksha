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
from moksha.api.widgets import LiveWidget

class LiveFlotWidget(LiveWidget):
    """ A live graphing widget """
    topic = 'flot_demo'
    params = ['id', 'data', 'options', 'height', 'width', 'onmessage']
    children = [FlotWidget('flot')]
    onmessage = '$.plot($("#${id}"),json[0]["data"],json[0]["options"])'
    template = '<div id="${id}" style="width:${width};height:${height};" />'
    height = '250px'
    width = '390px'
    options = {}
    data = [{}]
