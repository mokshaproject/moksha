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

from tg.controllers import WSGIAppController
from webob import Request, Response
from shove import Shove
from pylons import config
from inspect import isclass
from pylons.i18n import ugettext
from paste.deploy import appconfig
from genshi.filters import Translator
from sqlalchemy import create_engine
from feedcache.cache import Cache

from moksha.exc import ApplicationNotFound, MokshaException
from moksha.lib.helpers import (defaultdict, get_moksha_config_path,
                                get_main_app_config_path)
from moksha.wsgiapp import MokshaAppDispatcher

log = logging.getLogger(__name__)

class MokshaMiddleware(object):
    """
    A layer of WSGI middleware that is responsible for setting up the moksha
    environment, as well as handling every request/response in the application.

    If a request for an application comes in (/apps/$NAME), it will dispatch to
    the RootController of that application as defined in it's egg-info.

    """
    def __init__(self, application):
        log.info('Creating Moksha Middleware')
        self.application = application
        self.mokshaapp = MokshaAppDispatcher()

        moksha.apps = {}        # {'app name': tg.TGController/tg.WSGIAppController}
        moksha._widgets = {}    # {'widget name': tw.api.Widget}
        moksha.menus = {}       # {'menu name': moksha.api.menus.MokshaMenu}
        self.engines = {}       # {'app name': sqlalchemy.engine.base.Engine}

        self.load_paths()
        self.load_renderers()
        self.load_configs()
        self.load_widgets()
        self.load_applications()
        self.load_wsgi_applications()
        self.load_models()
        self.load_menus()

        moksha.feed_storage = Shove(config['feed_cache'], compress=True)
        moksha.feed_cache = Cache(moksha.feed_storage)

    def __call__(self, environ, start_response):
        self.register_stomp(environ)
        request = Request(environ)
        if request.path.startswith('/appz/') or request.path.startswith('/widget') or \
           request.path.startswith('/docs/'):
            response = request.get_response(self.mokshaapp)
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

    def load_paths(self):
        """ Load the names and paths of all moksha applications and widgets.

        We must do this before actually loading the widgets or applications, to
        ensure that we parse and load each of their configuration files
        beforehand.
        """
        for app_entry in pkg_resources.iter_entry_points('moksha.application'):
            if app_entry.name in moksha.apps:
                raise MokshaException('Duplicate application name: %s' %
                                      app_entry.name)
            app_path = app_entry.dist.location
            moksha.apps[app_entry.name] = {
                    'name': app_entry.name,
                    'path': app_path,
                    }
        for widget_entry in pkg_resources.iter_entry_points('moksha.widget'):
            if widget_entry.name in moksha._widgets:
                raise MokshaException('Duplicate widget name: %s' %
                                      widget_entry.name)
            widget_path = widget_entry.dist.location
            moksha._widgets[widget_entry.name] = {
                    'name': widget_entry.name,
                    'path': widget_path,
                    }

    def load_applications(self):
        log.info('Loading moksha applications')
        for app_entry in pkg_resources.iter_entry_points('moksha.application'):
            log.info('Loading %s application' % app_entry.name)
            app_class = app_entry.load()
            app_path = app_entry.dist.location
            moksha.apps[app_entry.name] = {
                    'name': getattr(app_class, 'name', app_entry.name),
                    'controller': app_class(),
                    'path': app_path,
                    'model': None,
                    }
            try:
                model = __import__('%s.model' % app_entry.name,
                                   globals(), locals(),
                                   [app_entry.name])
                moksha.apps[app_entry.name]['model'] = model
            except ImportError:
                pass

    def load_wsgi_applications(self):
        log.info('Loading moksha WSGI applications')
        for app_entry in pkg_resources.iter_entry_points('moksha.wsgiapp'):
            log.info('Loading %s WSGI application' % app_entry.name)
            app_class = app_entry.load()
            app_path = app_entry.dist.location
            moksha.apps[app_entry.name] = {
                    'name': getattr(app_class, 'name', app_entry.name),
                    'controller': WSGIAppController(app_class()),
                    'path': app_path,
                    'model': None,
                    }

    def load_widgets(self):
        log.info('Loading moksha widgets')
        for widget_entry in pkg_resources.iter_entry_points('moksha.widget'):
            log.info('Loading %s widget' % widget_entry.name)
            widget_class = widget_entry.load()
            widget_path = widget_entry.dist.location
            if isclass(widget_class):
                widget = widget_class(widget_entry.name)
            else:
                widget = widget_class
            moksha._widgets[widget_entry.name] = {
                    'name': getattr(widget_class, '__name__',
                                    widget_entry.name),
                    'widget': widget,
                    'path': widget_path,
                    }

        moksha._widgets = moksha._widgets

    def load_menus(self):
        log.info('Loading moksha menus')
        for menu_entry in pkg_resources.iter_entry_points('moksha.menu'):
            log.info('Loading %s menu' % menu_entry.name)
            menu_class = menu_entry.load()
            menu_path = menu_entry.dist.location
            moksha.menus[menu_entry.name] = menu_class(menu_entry.name)

    def load_renderers(self):
        """ Load our template renderers with our application paths.

        We are currently overloading TG2's default Mako renderer because
        the default `escape` filter causes our widgets to show up as escaped HTML.

         """
        #template_paths = config['pylons.paths']['templates']
        #moksha_dir = os.path.abspath(__file__ + '/../../../')
        #for app in [{'path': moksha_dir}] + moksha.apps.values():
        #    if app['path'] not in template_paths:
        #        template_paths.append(app['path'])

        #config['pylons.paths']['templates'] = template_paths

        from mako.template import Template
        from mako.lookup import TemplateLookup
        from tg.util import get_dotted_filename

        class DottedTemplateLookup(object):
            """this is an emulation of the Mako template lookup
            that will handle get_template and support dotted names
            in python path notation to support zipped eggs
            """
            def __init__(self, input_encoding, output_encoding,
                         imports, default_filters):
                self.input_encoding = input_encoding
                self.output_encoding = output_encoding
                self.imports = imports
                self.default_filters = default_filters

            def adjust_uri(self, uri, relativeto):
                """this method is used by mako for filesystem based reasons.
                In dotted lookup land we don't adjust uri so se just return
                the value we are given without any change
                """
                if '.' in uri:
                    """we are in the DottedTemplateLookup system so dots in
                    names should be treated as a python path.
                    Since this method is called by template inheritance we must
                    support dotted names also in the inheritance.
                    """
                    result = get_dotted_filename(template_name=uri,
                                                 template_extension='.mak')

                else:
                    """no dot detected, just return plain name
                    """
                    result = uri

                return result

            def get_template(self, template_name):
                """this is the emulated method that must return a template
                instance based on a given template name
                """
                return Template(open(template_name).read(),
                    input_encoding=self.input_encoding,
                    output_encoding=self.output_encoding,
                    default_filters=self.default_filters,
                    imports=self.imports,
                    lookup=self)

        if config.get('use_dotted_templatenames', True):
            # support dotted names by injecting a slightly different template
            # lookup system that will return templates from dotted template
            # notation.
            config['pylons.app_globals'].mako_lookup = DottedTemplateLookup(
                input_encoding='utf-8', output_encoding='utf-8',
                imports=[], default_filters=[])

        else:
            # if no dotted names support was required we will just setup
            # a file system based template lookup mechanism
            config['pylons.app_globals'].mako_lookup = TemplateLookup(
                directories=self.paths['templates'],
                module_directory=self.paths['templates'],
                input_encoding='utf-8', output_encoding='utf-8',
                filesystem_checks=self.auto_reload_templates)

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
        config_paths = set()
        moksha_config_path = os.path.dirname(get_moksha_config_path())
        main_app_config_path = os.path.dirname(get_main_app_config_path())
        for app in [{'path': moksha_config_path}] + moksha.apps.values():
            if app['path'] != main_app_config_path and \
               app['path'] not in config_paths:
                config_paths.add(app['path'])
        for config_path in config_paths:
            for configfile in ('production.ini', 'development.ini'):
                confpath = os.path.join(config_path, configfile)
                if os.path.exists(confpath):
                    log.info('Loading configuration: %s' % confpath)
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
        for name, app in moksha.apps.items():
            if app.get('model'):
                log.debug('Creating database engine for %s' % app['name'])
                self.engines[name] = create_engine(config['app_db'] % name)
                app['model'].init_model(self.engines[name])
                app['model'].metadata.create_all(bind=self.engines[name])
