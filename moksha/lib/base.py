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


            # Add our global widget to the template context, and register it's resources
        tmpl_context.moksha_global_resources = global_resources

            # This is normally done when the widget is rendered, but we cannot assume that
            # moksha apps are going to be using our master index template, which renders
            # this widget for us.
        global_resources.register_resources()

        return TGController.__call__(self, environ, start_response)
