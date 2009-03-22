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

class MokshaAppDispatcher(PylonsApp):
    """ Moksha WSGI Application Dispatcher.

    This class handles resolving and dispatching to moksha applications.
    It is instantiated and utilized by the 
    :class:`moksha.middleware.MokshaMiddleware`.
    """
    root = None

    def __init__(self):
        super(MokshaAppDispatcher, self).__init__()
        from moksha.controllers.root import RootController
        self.root = RootController()

    def resolve(self, environ, start_response): 
        """ Uses dispatching information found in
        ``environ['wsgiorg.routing_args']`` to retrieve the application
        name and return the controller instance from the appropriate
        moksha application.

        """
        environ['pylons.routes_dict'] = environ['wsgiorg.routing_args'][1]
        return self.root
