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

import logging
log = logging.getLogger(__name__)

import urlparse
urlparse.uses_netloc.append('irc')

from tg import expose, tmpl_context, config
from pylons import request

from moksha.lib.base import BaseController
from moksha.apps.chat import LiveChatFrameWidget

chat_frame_widget = LiveChatFrameWidget(id='chat_frame')

class ChatController(BaseController):

    def __init__(self, *args, **kw):
        super(ChatController, self).__init__(*args, **kw)
        self.config = {}
        backend = config.get('chat.backend')
        if not backend:
            log.info('No `chat.backend` defined; disabling chat functionality')
            return
        backend = urlparse.urlparse(backend)
        if hasattr(backend, 'scheme'): # Python 2.5+
            self.config['backendProtocol'] = backend.scheme
            self.config['backendAddr'] = [backend.hostname, backend.port]
        else: # Python 2.4
            self.config['backendProtocol'] = backend[0]
            host, port = backend[1].split(':')
            self.config['backendAddr'] = [host, port]
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

    @expose('mako:moksha.apps.chat.templates.bootstrap',
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
        return [True, opts]

    def op_not_found(self):
        return [False, ['unrecognized op']]
