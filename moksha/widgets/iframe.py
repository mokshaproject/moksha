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

"""
:mod:`moksha.widgets.iframe` - An IFrame Widget
===============================================

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

from tw.api import Widget

class IFrameWidget(Widget):
    params = ['id', 'url', 'title', 'height', 'width']
    template = """
      <h1>${title}</h1>
      <iframe id="${id}" src="${url}" width="${width}" height="${height}">
        <p>Your browser does not support iframes.</p>
      </iframe>
    """
    title = ''
    height = width = '100%'
    engine_name = 'mako'

iframe_widget = IFrameWidget('iframe_widget')
