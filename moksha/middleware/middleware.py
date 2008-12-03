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

from webob import Request, Response
from shove import Shove
from pylons import config
from feedcache.cache import Cache

from moksha.exc import ApplicationNotFound
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
        self.apps = {} # {'appname': {'controller': RootController, ... }}
        self.load_applications()
        self.load_renderers()

    def __call__(self, environ, start_response):
        environ['paste.registry'].register(moksha.apps, self.apps)
        environ['paste.registry'].register(moksha.feed_cache, self.feed_cache)
        request = Request(environ)
        if request.path.startswith('/appz'):
            app = request.path.split('/')[1]
            environ['moksha.apps'] = self.apps
            try:
                response = request.get_response(self.mokshaapp)
            except ApplicationNotFound:
                response = Response(status='404 Not Found')
        else:
            response = request.get_response(self.application)
        return response(environ, start_response)

    def load_applications(self):
        log.info('Loading moksha applications')
        for app_entry in pkg_resources.iter_entry_points('moksha.application'):
            if not app_entry.name in self.apps:
                log.info('Loading %s application' % app_entry.name)
                app_class = app_entry.load()

                try:
                    app_path = pkg_resources.resource_filename(app_entry.name,
                                                               None)
                except ImportError:
                    log.warning('%s app does not contain egg-info!  Skipping.' %
                                app_entry.name)
                    continue

                self.apps[app_entry.name] = {
                        'controller': app_class(),
                        'path': os.path.dirname(app_path),
                }

                # setup static paths for applications
                #   the StatiURLParser middleware only accepts 1 path?!
                # setup template directories for applications

    def load_renderers(self):
        """ Load our template renderers with our application paths """
        template_paths = config['pylons.paths']['templates']
        for app in self.apps.values():
            if app['path'] not in template_paths:
                template_paths.append(app['path'])

        from mako.lookup import TemplateLookup
        config['pylons.app_globals'].mako_lookup = TemplateLookup(
            directories=template_paths, module_directory=template_paths,
            input_encoding='utf-8', output_encoding='utf-8',
            imports=['from webhelpers.html import escape'],
            default_filters=['escape'], filesystem_checks=False)
        
        from genshi.template import TemplateLoader
        def template_loaded(template):
            "Plug-in our i18n function to Genshi."
            template.filters.insert(0, Translator(ugettext))
        config['pylons.app_globals'].genshi_loader = TemplateLoader(
            search_path=template_paths, auto_reload=False,
            callback=template_loaded)
