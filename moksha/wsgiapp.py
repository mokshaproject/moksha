# This file is part of Moksha.
# Copyright (C) 2008-2009  Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors: Luke Macken <lmacken@redhat.com>

from pylons import request
from pylons.wsgiapp import PylonsApp

from moksha.lib.helpers import strip_script

class MokshaAppDispatcher(PylonsApp):
    """ Moksha WSGI Application Dispatcher.

    This class handles resolving and dispatching to moksha applications.
    It is instantiated and utilized by the 
    :class:`moksha.middleware.MokshaMiddleware`.
    """
    root = None

    def __init__(self, application):
        super(MokshaAppDispatcher, self).__init__()
        from moksha.controllers.root import RootController
        self.root = RootController
        self.application = application

    def resolve(self, environ, start_response): 
        """ Uses dispatching information found in
        ``environ['wsgiorg.routing_args']`` to retrieve the application
        name and return the controller instance from the appropriate
        moksha application.

        """
        environ['pylons.routes_dict'] = environ['wsgiorg.routing_args'][1]
        path = strip_script(environ)
        if path.startswith('/apps/') or \
           path.startswith('/widget') or \
           path.startswith('/moksha_admin/'):
            return self.root()
        else:
            return self.application
