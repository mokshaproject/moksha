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

import moksha
import pylons

from tg import url, config
from tg import expose, flash, tmpl_context, redirect
from tg.decorators import override_template
from pylons.i18n import ugettext as _

from moksha.lib.base import BaseController
from moksha.controllers.error import ErrorController
from moksha.controllers.apps import AppController
from moksha.controllers.widgets import WidgetController
from moksha.controllers.secure import SecureController

class DefaultRootController(BaseController):

    @expose('mako:moksha.templates.index')
    def index(self, *args, **kw):
        if 'default_menu' in moksha.menus:
            tmpl_context.menu_widget = moksha.menus['default_menu']
        else:
            tmpl_context.menu_widget = lambda: ''
        #tmpl_context.contextual_menu_widget = moksha.menus['contextual_menu']
        return dict(title='[ Moksha ]')


class RootController(BaseController):

    apps = AppController()
    widgets = WidgetController()
    error = ErrorController()
    moksha_admin = SecureController()

    @expose()
    def _lookup(self, *remainder):
        if moksha.root:
            return moksha.root(), remainder
        else:
            # If we're running moksha without a root specified on the
            # moksha.root entry-point, then redirect to a moksha logo
            return DefaultRootController(), remainder

    @expose()
    def livesocket(self, topic=None, callback=None):
        """Returns a raw Moksha live socket, for use in non-Moksha apps.

        <script> function bar(msg) { alert('bar(' + msg + ')'); } </script>
        <script type="text/javascript"
                src="http://localhost:8080/livesocket?topic=foo&callback=bar">
        </script>

        """
        data = {'topic': topic, 'callback': callback}
        backend = config.get('moksha.livesocket.backend', 'stomp').lower()
        if backend == 'stomp':
            override_template(self.livesocket, 'mako:moksha.templates.stomp_socket')
            data['stomp_host'] = config.get('stomp_host', 'localhost')
            data['stomp_port'] = config.get('stomp_port', 61613)
            data['stomp_user'] = config.get('stomp_user', 'guest')
            data['stomp_pass'] = config.get('stomp_pass', 'guest')
        elif backend == 'amqp':
            override_template(self.livesocket, 'mako:moksha.templates.amqp_socket')
            data['amqp_broker_host'] = config.get('amqp_broker_host', 'localhost')
            data['amqp_broker_port'] = config.get('amqp_broker_port', 5672)
            data['amqp_broker_user'] = config.get('amqp_broker_user', 'guest')
            data['amqp_broker_pass'] = config.get('amqp_broker_pass', 'guest')
            # TODO: dynamic widget url 
            #  'toscawidgets.prefix': '/toscawidgets',

        data['orbited_host'] = config.get('orbited_host', 'localhost')
        data['orbited_port'] = config.get('orbited_port', 9000)
        data['orbited_scheme'] = config.get('orbited_scheme', 'http')
        data['orbited_url'] = '%s://%s:%s' % (data['orbited_scheme'],
                data['orbited_host'], data['orbited_port'])

        return data

    @expose('mako:moksha.templates.login')
    def login(self, came_from=None):
        """Start the user login."""
        if not came_from:
            came_from = url('/')
        login_counter = pylons.request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)

    @expose()
    def post_login(self, came_from=None):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not came_from:
            came_from = url('/')
        if not pylons.request.identity:
            login_counter = pylons.request.environ['repoze.who.logins'] + 1
            redirect(url('/login', came_from=came_from, __logins=login_counter))
        userid = pylons.request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=None):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        if not came_from:
            came_from = url('/')
        redirect(came_from)
