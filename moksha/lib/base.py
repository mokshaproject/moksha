"""The base Controller API

Provides the BaseController class for subclassing.
"""

import logging
import pkg_resources

from inspect import isclass
from tw.api import Widget, CSSLink, JSLink
from tg import TGController, tmpl_context, request, url
from tg.render import render
from pylons.i18n import _, ungettext, N_

import moksha.model as model

from moksha.api.widgets.stomp import stomp_widget
from moksha.lib.helpers import eval_and_check_predicates

log = logging.getLogger(__name__)


class GlobalResourceInjectionWidget(Widget):
    """
    Injects all global resources, such as JavaScript and CSS, on every page.
    This widget will pull in all JSLink and CSLink widgets that are listed
    on the `[moksha.global]` entry-point.
    """
    javascript = []
    css = []

    def __init__(self):
        super(GlobalResourceInjectionWidget, self).__init__()
        for widget_entry in pkg_resources.iter_entry_points('moksha.global'):
            log.info('Loading global resource: %s' % widget_entry.name)
            loaded = widget_entry.load()
            if isclass(loaded):
                loaded = loaded(widget_entry.name)
            if isinstance(loaded, JSLink):
                self.javascript.append(loaded)
            elif isinstance(loaded, CSSLink):
                self.css.append(loaded)
            else:
                raise Exception("Unknown global resource: %s.  Should be "
                                "either a JSLink or CSSLink." %
                                widget_entry.name)


global_resources = GlobalResourceInjectionWidget()

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

        # Inject our global resources
        if not request.path.startswith('/appz'):
            global_resources.register_resources()

        return TGController.__call__(self, environ, start_response)
