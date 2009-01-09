"""The base Controller API

Provides the BaseController class for subclassing.
"""
from tg import TGController, tmpl_context, request
from tg.render import render
from tw.api import WidgetBunch
from pylons.i18n import _, ungettext, N_

import moksha.model as model

from moksha.live.stomp import stomp_widget


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
        tmpl_context.identity = request.environ.get('repoze.who.identity')
        return TGController.__call__(self, environ, start_response)
class SecureController(BaseController):
    """SecureController implementation for the repoze.what extension.
    
    it will permit to protect whole controllers with a single predicate
    placed at the controller level.
    The only thing you need to have is a 'require' attribute which must
    be a callable. This callable will only be authorized to return True
    if the user is allowed and False otherwise. This may change to convey info
    when securecontroller is fully debugged...
    """

    def check_security(self):
        errors = []
        environ = request.environ
        if not hasattr(self, "require") or \
            self.require is None or \
            self.require.eval_with_environ(environ, errors):
            return True

        # if we did not return this is an error :)
        # TODO: do something with the errors variable like informing our user...
        return False
