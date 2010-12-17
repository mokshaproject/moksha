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

"""The base Controller API

Provides the BaseController class for subclassing.
"""

from tg import TGController, tmpl_context, request, url
from tg.render import render
from pylons.i18n import _, ungettext, N_

import moksha
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

        request.identity = request.environ.get('repoze.who.identity')
        tmpl_context.identity = request.identity

        # we alias this for easy use in templates
        tmpl_context.auth = eval_and_check_predicates

        # url is already taken
        tmpl_context.get_url = url

        # Add our global widget to the template context, and register it's
        # resources
        tmpl_context.moksha_global_resources = moksha.global_resources

        # TGController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict'], which is currently
        # being set in moksha.wsgiapp
        return TGController.__call__(self, environ, start_response)
