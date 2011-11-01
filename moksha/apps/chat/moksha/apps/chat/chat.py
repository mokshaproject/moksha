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

from tg import config
from paste.deploy.converters import asbool

import tw.api
import tw.jquery
import tw2.core as twc
import tw2.jquery

from moksha.api.widgets.orbited import tw1_orbited_js, tw2_orbited_js

tw1_irc2_js = tw.api.JSLink(
    filename='static/irc2.js',
    javascript=[tw1_orbited_js],
    modname=__name__)
tw1_willowchat_js = tw.api.JSLink(
    filename='static/willowchat.js',
    javascript=[tw.jquery.jquery_js, tw1_irc2_js],
    modname=__name__)
tw1_gui_js = tw.api.JSLink(
    filename='static/gui.js',
    javascript=[tw1_willowchat_js],
    modname=__name__)
tw1_willowchat_css = tw.api.CSSLink(
    filename='static/style.css',
    modname=__name__)

tw2_irc2_js = twc.JSLink(
    filename='static/irc2.js',
    javascript=[tw2_orbited_js],
    modname=__name__)
tw2_willowchat_js = twc.JSLink(
    filename='static/willowchat.js',
    javascript=[tw2.jquery.jquery_js, tw2_irc2_js],
    modname=__name__)
tw2_gui_js = twc.JSLink(
    filename='static/gui.js',
    javascript=[tw2_willowchat_js],
    modname=__name__)
tw2_willowchat_css = twc.CSSLink(
    filename='static/style.css',
    modname=__name__)


class TW1LiveChatWidget(tw.api.Widget):
    name = 'Chat'
    params = ['bootstrap']
    bootstrap = tw.api.JSLink(link='/apps/chat/bootstrap')
    template = "mako:moksha.apps.chat.templates.simple"
    visible = False


class TW1LiveChatFrameWidget(tw.api.Widget):
    template = 'mako:moksha.apps.chat.templates.chat'
    javascript = [tw1_orbited_js, tw1_willowchat_js, tw1_irc2_js, tw1_gui_js,
                  tw.jquery.jquery_js]
    css = [tw1_willowchat_css]


class TW2LiveChatWidget(twc.Widget):
    name = 'Chat'
    params = ['bootstrap']
    bootstrap = twc.JSLink(link='/apps/chat/bootstrap')
    template = "mako:moksha.apps.chat.templates.simple"
    visible = False


class TW2LiveChatFrameWidget(twc.Widget):
    template = 'mako:moksha.apps.chat.templates.chat'
    resources = [
        tw2_orbited_js,
        tw2_willowchat_js,
        tw2_irc2_js,
        tw2_gui_js,
        tw2.jquery.jquery_js,
        tw2_willowchat_css,
    ]


if asbool(config.get('moksha.use_tw2', False)):
    LiveChatWidget = TW2LiveChatWidget
    LiveChatFrameWidget = TW2LiveChatFrameWidget
else:
    LiveChatWidget = TW1LiveChatWidget
    LiveChatFrameWidget = TW1LiveChatFrameWidget
