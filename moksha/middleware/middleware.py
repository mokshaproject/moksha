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

import os
import sys
import moksha
import logging
import pkg_resources

from pylons import config
from webob import Request, Response
from shove import Shove
from feedcache.cache import Cache

from moksha.wsgiapp import MokshaApp

log = logging.getLogger(__name__)

class MokshaMiddleware(object):
    """
    A layer of WSGI middleware that is responsible for setting up the moksha
    environment, as well as handling every request/response in the application.
    
    If a request for an application comes in (/apps/$NAME), it will dispatch to
    the RootController of that application as defined in it's egg-info.

    Creating a new moksha application requires adding the ``moksha.application``
    setuptools entry-point to your setup.py

    """
    def __init__(self, application):
        log.info('Creating MokshaMiddleware')
        self.application = application
        self.mokshaapp = MokshaApp()
        self.feed_storage = Shove('file://' + config['feed_cache'])
        self.feed_cache = Cache(self.feed_storage)
        self.plugins = {}
        self.load_plugins()

    def __call__(self, environ, start_response):
        environ['paste.registry'].register(moksha.feed_cache, self.feed_cache)
        request = Request(environ)
        if request.path.startswith('/appz'):
            app = request.path.split('/')[1]
            environ['moksha.plugins'] = self.plugins
            response = request.get_response(self.mokshaapp)
        else:
            response = request.get_response(self.application)
        return response(environ, start_response)

    def load_plugins(self):
        log.info('Loading Moksha plugins')
        for plugin_entry in pkg_resources.iter_entry_points('moksha.plugin'):
            if not plugin_entry.name in self.plugins:
                log.info('Loading %s plugin' % plugin_entry.name)
                plugin_class = plugin_entry.load()
                self.plugins[plugin_entry.name] = plugin_class()
