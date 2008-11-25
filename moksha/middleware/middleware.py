import logging
log = logging.getLogger(__name__)

from webob import Request, Response

class MokshaMiddleware(object):

    def __init__(self, application):
        log.info('Creating MokshaMiddleware')
        self.application = application
        self.feed_cache

    def __call__(self, environ, start_response):
        log.debug('MokshaMiddleware.__call__(%s, %s)' %(environ,start_response))
        #environ['paste.registry'].register(moksha.{cache,hub,etc?}
        request = Request(environ)
        log.debug("request = %s" % request)
        response = request.get_response(self.application)
        log.debug("response = %s" % response)
        return response(environ, start_response)
