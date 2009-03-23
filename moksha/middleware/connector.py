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
# Authors: John (J5) Palmieri <johnp@redhat.com>

import logging
import pkg_resources
import simplejson as json
import urllib

from webob import Request, Response
from pylons import config, request
from pylons.i18n import ugettext

from moksha.exc import ApplicationNotFound, MokshaException

log = logging.getLogger(__name__)

class MokshaConnectorMiddleware(object):
    """
    A layer of WSGI middleware that is responsible for handling every
    moksha_connector requests.

    If a request for a connector comes in (/moksha_connector/$name), it will
    run that connector as defined in it's egg-info.

    """

    _connectors = {}

    def __init__(self, application):
        log.info('Creating MokshaConnectorMiddleware')
        self.application = application
        self.load_connectors()

    def __call__(self, environ, start_response):

        request = Request(environ)

        if request.path.startswith('/moksha_connector'):
            s = request.path.split('/')[2:]

            # since keys are not unique we need to condense them
            # into an actual dictionary with multiple entries becoming lists
            p = request.params
            params = {}
            for k in p.iterkeys():
                if k == '_cookies':
                    # reserved parameter
                    # FIXME: provide a proper error response
                    return Response(status='404 Not Found')

                if k not in params:
                    params[k] = p.getall(k)
                    if params[k] and len(params[k]) == 1:
                        params[k] = params[k][0]

            response = self._run_connector(environ, request,
                                           s[0], s[1], *s[2:],
                                           **params)
        else:
            response = request.get_response(self.application)

        return response(environ, start_response)

    def _run_connector(self, environ, request,
                       conn, op, *path,
                       **remote_params):
        response = None
        # check last part of path to see if it is json data
        dispatch_params = {};

        p = urllib.unquote_plus(path[-1].lstrip())
        if p.startswith('{'):
            dp = json.loads(p)

            f = dp.get('filters')
            if isinstance(f, basestring):
                dp['filters'] = json.loads(f)
            path = path[:-1]

            # scrub dispatch_params keys of unicode so we can pass as keywords
            for (k, v) in dp.iteritems():
                dispatch_params[str(k)] = v

        # prevent trailing slash
        if not p:
            path = path[:-1]

        path = '/'.join(path)
        conn = self._connectors.get(conn)

        if conn:
            conn_obj = conn['connector_class'](environ, request)
            r = conn_obj._dispatch(op, path, remote_params, **dispatch_params)
            if not isinstance(r, str):
                r = json.dumps(r, separators=(',',':'))
            response = Response(r)
        else:
            response = Response(status='404 Not Found')

        return response

    def load_connectors(self):
        log.info('Loading moksha connectors')
        for conn_entry in pkg_resources.iter_entry_points('moksha.connector'):
            log.info('Loading %s connector' % conn_entry.name)
            conn_class = conn_entry.load()
            # call the register class method
            # FIXME: Should we pass some resource in?
            conn_class.register()
            conn_path = conn_entry.dist.location
            self._connectors[conn_entry.name] = {
                    'name': conn_entry.name,
                    'connector_class': conn_class,
                    'path': conn_path,
                    }

def _get_connector(name):
    # TODO: having a connection pool might be nice
    c = MokshaConnectorMiddleware._connectors[name]

    return c['connector_class'](request.environ, request)