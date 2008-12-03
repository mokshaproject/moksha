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
# Authors: Luke Macken <lmacken@redhat.com>

from pylons.wsgiapp import PylonsApp
from moksha.exc import ApplicationNotFound

class MokshaApp(PylonsApp):
    """ Moksha WSGI Application.

    This class handles resolving and dispatching to moksha applications.
    It is instantiated and utilized by the 
    :class:`moksha.middleware.MokshaMiddleware`.
    """
    def resolve(self, environ, start_response): 
        """ Uses dispatching information found in
        ``environ['wsgiorg.routing_args']`` to retrieve the application
        name and return the controller instance from the appropriate
        moksha application.

        """
        # Update the Routes config object in case we're using Routes
        # (Do we even need/want this routes configuration?)
        #config = request_config()
        #config.redirect = self.redirect_to
        # http://www.wsgi.org/wsgi/Specifications/routing_args
        match = environ['wsgiorg.routing_args'][1]

        app = match['url'].split('/')[1]
        if not app in environ['moksha.apps']:
            raise ApplicationNotFound(app)

        # Remaining arguments
        match['url'] = '/'.join(match['url'].strip('/').split('/')[2:])

        environ['pylons.routes_dict'] = match

        return environ['moksha.apps'][app]['controller']
