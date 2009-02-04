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
from pylons import config
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
    def __init__(self, application):
        log.info('Creating MokshaConnectorMiddleware')
        self.application = application
        self.connectors = {} # {'connector name': moksha.IConnector class}

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

            response = self._run_connector(s[0], s[1], *s[2:], **params)
        else:
            response = request.get_response(self.application)

        return response(environ, start_response)

    def _run_connector(self, conn, op, *path, **remote_params):
        response = None
        # check last part of path to see if it is json data
        dispatch_params = {};

        p = urllib.unquote_plus(path[-1].lstrip())
        if p.startswith('{'):
            dispatch_params = json.loads(p)
            f = dispatch_params.get('filters')
            if isinstance(f, basestring):
                dispatch_params['filters'] = json.loads(f)
            path = path[:-1]

        # prevent trailing slash
        if not p:
            path = path[:-1]

        path = '/'.join(path)
        conn = self.connectors.get(conn)

        if conn:
            conn_obj = conn['connector_class']()
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
            self.connectors[conn_entry.name] = {
                    'name': conn_entry.name,
                    'connector_class': conn_class,
                    'path': conn_path,
                    }
