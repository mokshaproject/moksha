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

import logging
log = logging.getLogger(__name__)

import urlparse
urlparse.uses_netloc.append('irc')

from tg import expose, tmpl_context, config
from pylons import request

from moksha.lib.base import BaseController
from moksha.api.widgets.chat import LiveChatFrameWidget

chat_frame_widget = LiveChatFrameWidget('chat_frame')


class ChatController(BaseController):

    def __init__(self, *args, **kw):
        super(ChatController, self).__init__(*args, **kw)
        self.config = {}
        backend = config.get('chat.backend')
        if not backend:
            log.info('No `chat.backend` defined; disabling chat functionality')
            return
        backend = urlparse.urlparse(backend)
        self.config['backendProtocol'] = backend.scheme
        self.config['backendAddr'] = [backend.hostname, backend.port]
        self.config['startBuiltin'] = config.get('chat.builtin', False)
        self.config['rooms'] = {}
        display_opts = {
                'floating': True, 'floatingToggle': False, 'width': 400 ,
                'height': 300, 'theme': 'simple', 'resizable': True,
                'greeting': 'Moksha Chat',
                }
        for room in config['chat.rooms'].replace(',', ' ').split():
            self.config['rooms'][room] = {'display': {}}
            for display_opt, default in display_opts.items():
                self.config['rooms'][room]['display'][display_opt] = \
                        config.get('chat.%s.display.%s' % (room, display_opt),
                                   default)
            self.config['rooms'][room]['roomAssignmentMode'] = \
                    config.get('chat.%s.roomAssignmentMode' % room, 'static')
            self.config['rooms'][room]['staticRoomName'] = \
                    config.get('chat.%s.staticRoomName' % room, room)

        log.debug('Chat config = %r' % self.config)

    @expose('mako:moksha.templates.widget')
    def index(self, *args, **kw):
        tmpl_context.widget = chat_frame_widget
        return dict(options={})

    @expose('mako:moksha.api.widgets.chat.templates.bootstrap',
            content_type='text/javascript')
    def bootstrap(self, *args, **kw):
        return dict(host=request.headers['host'])

    @expose('json')
    def rooms(self, roomClass='default', op=None, jsonp=None):
        opts = None
        if op:
            opts = self.jsonp(getattr(self, 'op_%s' % op,
                                      self.op_not_found)(roomClass), jsonp)
        else:
            opts = self.jsonp([False, ["op not specified"]], jsonp)
        return opts

    def jsonp(self, result, jsonp=None):
        result = str(result).replace('True', 'true').replace('False', 'false')
        if jsonp:
            result = jsonp + '(' + result + ')'
        return result

    def op_info(self, roomClass):
        if roomClass not in self.config['rooms']:
            return [False, ['unknown room class: ' + roomClass]]
        info = self.config['rooms'][roomClass]
        displayInfo = info.get('display', {})
        opts = {}
        opts.update(displayInfo)
        mode = info.get('roomAssignmentMode', 'static')
        if mode == 'static':
            opts['roomId'] = info.get('staticRoomName', 'default')
        elif mode == 'referrer':
            opts['roomId'] = request.headers.get('referer', 'default')
        opts['protocol'] = self.config['backendProtocol']
        opts['addr'] = self.config['backendAddr']
        print "op_info returning [True, %r]" % opts
        return [True, opts]

    def op_not_found(self):
        return [False, ['unrecognized op']]
