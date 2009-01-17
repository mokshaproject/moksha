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
import moksha
import logging
import pkg_resources
import simplejson as json
import urllib

from webob import Request, Response
from shove import Shove
from pylons import config
from collections import defaultdict
from pylons.i18n import ugettext
from paste.deploy import appconfig
from genshi.filters import Translator
from sqlalchemy import create_engine
from feedcache.cache import Cache

from moksha.exc import ApplicationNotFound, MokshaException
from moksha.wsgiapp import MokshaApp

log = logging.getLogger(__name__)

class MokshaMiddleware(object):
    """
    A layer of WSGI middleware that is responsible for setting up the moksha
    environment, as well as handling every request/response in the application.

    If a request for an application comes in (/apps/$NAME), it will dispatch to
    the RootController of that application as defined in it's egg-info.

    """
    def __init__(self, application):
        log.info('Creating MokshaMiddleware')
        self.application = application
        self.mokshaapp = MokshaApp()

        self.apps = {}       # {'app name': WSGI Controller}
        self.widgets = {}    # {'widget name': tw.api.Widget}
        self.engines = {}    # {'app name': sqlalchemy.engine.base.Engine}
        self.connectors = {} # {'connector name': moksha.IConnector class}

        self.load_paths()
        self.load_renderers()
        self.load_configs()
        self.load_connectors()
        self.load_applications()
        self.load_widgets()
        self.load_models()

        self.feed_storage = Shove(config['feed_cache'])
        self.feed_cache = Cache(self.feed_storage)

    def __call__(self, environ, start_response):
        environ['paste.registry'].register(moksha.apps, self.apps)
        environ['paste.registry'].register(moksha._widgets, self.widgets)
        environ['paste.registry'].register(moksha.feed_cache, self.feed_cache)
        self.register_stomp(environ)
        request = Request(environ)

        if request.path.startswith('/appz'):
            app = request.path.split('/')[1]
            environ['moksha.apps'] = self.apps
            try:
                response = request.get_response(self.mokshaapp)
            except ApplicationNotFound:
                response = Response(status='404 Not Found')
        elif request.path.startswith('/moksha_connector'):
            # FIXME: this should be separate middleware so other
            #        frameworks can use connectors
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
                    params[k] = params.getall(k)

            response = self._run_connector(s[0], s[1], *s[2:], **params)
        else:
            response = request.get_response(self.application)

        return response(environ, start_response)

    def register_stomp(self, environ):
        environ['paste.registry'].register(moksha.stomp, {
            'onopen': [],
            'onclose': [],
            'onerror': [],
            'onerrorframe': [],
            'onconnectedframe': [],
            'onmessageframe': defaultdict(list) # {topic: [js_callback,]}
        })

    def _run_connector(self, conn, op, *path, **remote_params):
        response = None
        # check last part of path to see if it is json data
        dispatch_params = {};

        p = urllib.unquote_plus(path[-1].lstrip())
        if p.startswith('{'):
            dispatch_params = json.loads(p)
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

    def load_paths(self):
        """ Load the names and paths of all moksha applications and widgets.

        We must do this before actually loading the widgets or applications, to
        ensure that we parse and load each of their configuration files
        beforehand.
        """
        for app_entry in pkg_resources.iter_entry_points('moksha.application'):
            if app_entry.name in self.apps:
                raise MokshaException('Duplicate application name: %s' % 
                                      app_entry.name)
            app_path = app_entry.dist.location
            self.apps[app_entry.name] = {
                    'name': app_entry.name,
                    'path': app_path,
                    }
        for widget_entry in pkg_resources.iter_entry_points('moksha.widget'):
            if widget_entry.name in self.widgets:
                raise MokshaException('Duplicate widget name: %s' % 
                                      widget_entry.name)
            widget_path = widget_entry.dist.location
            self.widgets[widget_entry.name] = {
                    'name': widget_entry.name,
                    'path': widget_path,
                    }

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

    def load_applications(self):
        log.info('Loading moksha applications')
        for app_entry in pkg_resources.iter_entry_points('moksha.application'):
            log.info('Loading %s application' % app_entry.name)
            app_class = app_entry.load()
            app_path = app_entry.dist.location
            self.apps[app_entry.name] = {
                    'name': app_entry.name,
                    'controller': app_class(),
                    'path': app_path,
                    'model': None,
                    }
            try:
                model = __import__('%s.model' % app_entry.name,
                                   fromlist=[app_entry.name])
                self.apps[app_entry.name]['model'] = model
            except ImportError:
                pass

    def load_widgets(self):
        log.info('Loading moksha widgets')
        for widget_entry in pkg_resources.iter_entry_points('moksha.widget'):
            log.info('Loading %s widget' % widget_entry.name)
            widget_class = widget_entry.load()
            widget_path = widget_entry.dist.location
            self.widgets[widget_entry.name] = {
                    'name': widget_entry.name,
                    'widget': widget_class(widget_entry.name),
                    'path': widget_path,
                    }

    def load_renderers(self):
        """ Load our template renderers with our application paths """
        template_paths = config['pylons.paths']['templates']
        moksha_dir = os.path.abspath(__file__ + '/../../../')
        for app in [{'path': moksha_dir}] + self.apps.values():
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

    def load_configs(self):
        """ Load the configuration files for all applications.

        Here we iterate over all applications, loading their configuration
        files and merging their [DEFAULT] configuration into ours.  This
        requires that applications do not have conflicting configuration
        variable names.  To mitigate this, applications should use some basic
        variable namespacing, such as `myapp.myvariable = myvalue`.

        We first make sure to load up Moksha's configuration, for the cases
        where it is being run as WSGI middleware in a different environment.

        """
        moksha_conf = os.path.abspath(__file__ + '/../../../')
        for app in [{'path': moksha_conf}] + self.apps.values():
            for configfile in ('production.ini', 'development.ini'):
                confpath = os.path.join(app['path'], configfile)
                if os.path.exists(confpath):
                    log.debug('Loading configuration: %s' % confpath)
                    conf = appconfig('config:' + confpath)
                    for entry in conf.global_conf:
                        if entry.startswith('_'):
                            continue
                        if entry in config:
                            log.warning('Conflicting variable: %s' % entry)
                            continue
                        else:
                            config[entry] = conf.global_conf[entry]
                            log.debug('Set `%s` in global config' % entry)
                    break

    def load_models(self):
        """ Setup the SQLAlchemy database models for all moksha applications.

        This method will create a SQLAlchemy engine for each application
        that has a model module.  It then takes this engine, binds it to
        the application-specific metadata, and creates all of the tables,
        if they don't already exist.

        """
        for name, app in self.apps.items():
            if app.get('model'):
                log.debug('Creating database engine for %s' % app['name'])
                self.engines[name] = create_engine(config['app_db'] % name)
                app['model'].init_model(self.engines[name])
                app['model'].metadata.create_all(bind=self.engines[name])
