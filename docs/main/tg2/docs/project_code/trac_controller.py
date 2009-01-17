from webob.exc import status_map
from tg.controllers import WSGIAppController
from trac.web.api import HTTPException
from trac.web.main import dispatch_request as trac_app

class TracController(WSGIAppController):
    """
    Mounts a Trac instance inside a TG app.

    Example::

        class RootController(BaseController):
            trac = TracController(env_path='/home/tracs/myproject')

    The trac can be protected by TG's authorization framework::

        from repoze.what import prediactes

        is_manager = predicates.has_permission(
            'manage',
            msg=_('Only for people with the "manage" permission')
            )

        class RootController(BaseController):
            trac = TracController(is_manager, env_path='/home/tracs/myproject')
    """
    def __init__(self, allow_only=None, **trac_config):
        self.trac_config = dict(
            ('trac.'+k, v) for k,v in trac_config.iteritems()
            )
        super(TracController, self).__init__(trac_app, allow_only)

    def delegate(self, environ, start_response):
        environ.update(self.trac_config)
        try:
            return super(TracController, self).delegate(environ, start_response)
        except HTTPException, e:
            # Translate Trac's HTTP codes to webob.exc.HTTPExceptions
            resp = status_map[e.code](str(e))
            return resp(environ, start_response)
