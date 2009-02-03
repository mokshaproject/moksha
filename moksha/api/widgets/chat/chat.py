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

from tw.api import Widget, JSLink, CSSLink
from tw.jquery import jquery_js

from moksha.api.widgets.orbited import orbited_js

irc2_js = JSLink(filename='static/irc2.js',
                 javascript=[orbited_js],
                 modname=__name__)

willowchat_js = JSLink(filename='static/willowchat.js',
                       javascript=[jquery_js, irc2_js],
                       modname=__name__)

gui_js = JSLink(filename='static/gui.js',
                javascript=[willowchat_js],
                modname=__name__)

willowchat_css = CSSLink(filename='static/style.css', modname=__name__)


class LiveChatWidget(Widget):
    params = ['bootstrap']
    bootstrap = JSLink(link='/appz/chat/bootstrap')
    template = '<div id="willowchat" reposition="true">${bootstrap}</div>'
    visible = False


class LiveChatFrameWidget(Widget):
    template = 'mako:moksha.api.widgets.chat.templates.chat'
    javascript = [orbited_js, willowchat_js, irc2_js, gui_js, jquery_js]
    css = [willowchat_css]
