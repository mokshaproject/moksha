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

"""The base Controller API

Provides the BaseController class for subclassing.
"""

from tg import TGController, tmpl_context, request, url
from tg.render import render
from pylons.i18n import _, ungettext, N_

import moksha.model as model

from moksha.api.widgets.stomp import stomp_widget
from moksha.api.widgets.global_resources import global_resources
from moksha.lib.helpers import eval_and_check_predicates


class Controller(object):
    """Base class for a web application's controller.

    Currently, this provides positional parameters functionality
    via a standard default method.
    """

class BaseController(TGController):
    """Base class for the root of a web application.

    Your web application should have one of these. The root of
    your application is used to compute URLs used by your app.
    """

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # TGController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        tmpl_context.stomp = stomp_widget
        request.identity = request.environ.get('repoze.who.identity')
        tmpl_context.identity = request.identity

        # we alias this for easy use in templates
        tmpl_context.auth = eval_and_check_predicates

        # url is already taken
        tmpl_context.get_url = url

        # Add our global widget to the template context, and register it's
        # resources
        tmpl_context.moksha_global_resources = global_resources

        # This is normally done when the widget is rendered, but we cannot
        # assume that moksha apps are going to be using our master index
        # template, which renders this widget for us.
        global_resources.register_resources()

        return TGController.__call__(self, environ, start_response)
