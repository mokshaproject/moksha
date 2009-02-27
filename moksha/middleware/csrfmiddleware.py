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

from webob import Request, Response
from hashlib import sha1

from paste.request import construct_url
from paste.httpexceptions import HTTPFound
from paste.request import parse_formvars, parse_dict_querystring
from paste.response import replace_header

from urlparse import urlparse, urlunparse

log = logging.getLogger(__name__)

class CSRFProtectionMiddleware(object):
    """
    A layer of WSGI middleware that is responsible for making sure authenticated
    requests originated from the user inside of the app's domain
    and not a malicious website

    This middleware works with Repoze.who and Repoze.what auth middleware
    and must be run right before the who middleware and as a metadata plugin
    for repoze.who.  If the user is authenticated
    and the csrf token is not the sha1 hash of the session id or
    environ['CSRF_AUTH_SESSION_ID'] we clear environ['repoze.who.identity'] and
    environ['repoze.what.credentials']

    If the check succeeds we add the sha1 hash to the identity hash as
    {self.csrf_token: sessionid_sha1_hash}
    """

    _connectors = {}

    def __init__(self,
                 session_cookie='tg-visit',
                 session_env='CSRF_AUTH_SESSION_ID',
                 token_env='CSRF_TOKEN',
                 csrf_token_id = '_csrf_token',
                 clear_env = ['repoze.who.identity', 'repoze.what.credentials']):
        log.info('Creating CSRFProtectionMiddleware')
        self.application = None
        self.session_cookie = session_cookie
        self.session_env = session_env
        self.csrf_token_id = csrf_token_id
        self.clear_env = clear_env
        self.token_env = token_env

    def register_application(self, app):
        self.application = app

    def __call__(self, environ, start_response):
        """ Clear out the csrf token and place it in the environ

        This middleware must be placed before the repoze.who middleware
        """
        request = Request(environ)

        csrf_token = None
        d = parse_dict_querystring(environ)
        if self.csrf_token_id in d:
            csrf_token= d.getone(self.csrf_token_id)
            d.__delitem__(self.csrf_token_id)

            qs = []
            for k in d:
                qs.append('%s=%s'%(k,d[k]))

            qs = '&'.join(qs)
            environ['QUERY_STRING'] = qs

        d = parse_formvars(environ, False)
        if self.csrf_token_id in d:
            csrf_token = d.getone(self.csrf_token_id)
            d.__delitem__(self.csrf_token_id)
            environ['paste.parsed_formvars'] = d

        environ[self.token_env] = csrf_token

        response = request.get_response(self.application)
        return response(environ, start_response)

    def add_metadata(self, environ, identity):
        """
        Repoze.who metadata pluging.  This must be placed as the last
        metadata plugin to run.  It clears the identity and credentials
        if the csrf check fails.  The Repoze.who Auth plugin must also
        set CSRF_AUTH_SESSION_ID in the environ so we don't clear
        in the initial authorization stage
        """
        request = Request(environ)

        session_id = environ.get(self.session_env, None)
        auth_state = True
        if not session_id:
            auth_state = False
            session_id = request.cookies.get(self.session_cookie)

        token = None
        if session_id:
            token = sha1(session_id)
            token = token.hexdigest()
            info = {self.csrf_token_id: token}
            identity.update(info)

        # check for csrf
        if (auth_state):
            app = environ['repoze.who.application']
            p = list(urlparse(app.location()))
            p[4] += '&' + self.csrf_token_id + '=' + token
            replace_header(app.headers, 'location', urlunparse(tuple(p)))
        elif not token or token != environ.get(self.token_env):
            for k in self.clear_env:
                if k in environ:
                    del environ[k]
