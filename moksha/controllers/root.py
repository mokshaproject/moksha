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

import moksha
import pylons
import os

from tg import config, url
from tg import expose, flash, require, tmpl_context, redirect, validate
from tg.controllers import WSGIAppController
from tg.decorators import after_render

from repoze.what import predicates
from pkg_resources import resource_filename
from widgetbrowser import WidgetBrowser
from pylons.i18n import ugettext as _, lazy_ugettext as l_

from moksha import _
from moksha.model import DBSession
from moksha.lib.base import BaseController
from moksha.lib.helpers import cache_rendered_data
from moksha.exc import ApplicationNotFound
from moksha.controllers.error import ErrorController
from moksha.controllers.apps import AppController
from moksha.controllers.widgets import WidgetController
from moksha.controllers.secure import SecureController

# So we can mount the WidgetBrowser as /docs
os.environ['TW_BROWSER_PREFIX'] = '/docs'

class RootController(BaseController):

    appz = AppController()
    widgets = WidgetController()
    error = ErrorController()
    moksha_admin = SecureController()

    # ToscaWidgets WidgetBrowser integration
    docs = WSGIAppController(
                WidgetBrowser(
                    template_dirs=[
                        resource_filename('moksha','templates/widget_browser')],
                    docs_dir=config.get('docs_dir', 'docs'),
                    full_stack=False))

    #@after_render(cache_rendered_data)
    @expose('mako:moksha.templates.index')
    def index(self):
        tmpl_context.menu_widget = moksha.menus['default_menu']
        #tmpl_context.contextual_menu_widget = moksha.menus['contextual_menu']
        return dict(title='[ Moksha ]')

    @expose()
    def lookup(self, *remainder):
        """
        Moksha's default lookup method, called by the
        :class:`MokshaMiddleware`.  This currently dispatches to our
        WidgetBrowser when Moksha is being used as WSGI middleware in another
        application.
        """
        if pylons.request.path.startswith('/docs/'):
            return self.docs, remainder

    @expose('mako:moksha.templates.login')
    def login(self, came_from=url('/')):
        """Start the user login."""
        login_counter = pylons.request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)

    @expose()
    def post_login(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not pylons.request.identity:
            login_counter = pylons.request.environ['repoze.who.logins'] + 1
            redirect(url('/login', came_from=came_from, __logins=login_counter))
        userid = pylons.request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        redirect(came_from)
