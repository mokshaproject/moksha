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
    name = 'Chat'
    params = ['bootstrap']
    bootstrap = JSLink(link='/apps/chat/bootstrap')
    template = '<div id="willowchat" reposition="true">${bootstrap}</div>'
    visible = False


class LiveChatFrameWidget(Widget):
    template = 'mako:moksha.apps.chat.templates.chat'
    javascript = [orbited_js, willowchat_js, irc2_js, gui_js, jquery_js]
    css = [willowchat_css]
