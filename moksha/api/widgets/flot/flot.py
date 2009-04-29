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

from tw.jquery.flot import flot_js, excanvas_js, flot_css
from moksha.api.widgets import LiveWidget

class LiveFlotWidget(LiveWidget):
    """ A live graphing widget """
    topic = None
    params = ['id', 'data', 'options', 'height', 'width', 'onmessage']
    onmessage = '$.plot($("#${id}"),json[0]["data"],json[0]["options"])'
    template = '<div id="${id}" style="width:${width};height:${height};" />'
    javascript = [flot_js, excanvas_js]
    css = [flot_css]
    height = '250px'
    width = '390px'
    options = {}
    data = [{}]
