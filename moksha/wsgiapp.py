# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
