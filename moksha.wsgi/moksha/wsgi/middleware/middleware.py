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

import os
import moksha.common.utils
import logging
import pkg_resources
import warnings
import types

from paste.deploy.converters import asbool
from inspect import isclass
from sqlalchemy import create_engine

from moksha.common.exc import MokshaException
from moksha.common.lib.helpers import (defaultdict, get_moksha_config_path)
from moksha.common.lib.helpers import appconfig

log = logging.getLogger(__name__)

# A list of all the entry points
APPS = 'moksha.application'
WIDGETS = 'moksha.widget'
ROOT = 'moksha.root'
MENUS = 'moksha.menu'


class MokshaMiddleware(object):
    """
    A layer of WSGI middleware that is responsible for setting up the moksha
    environment, as well as handling every request/response in the application.

    If a request for an application comes in (/apps/$NAME), it will dispatch to
    the WSGI Application or RootController of that application as defined in
    it's egg-info entry-points.

    This middleware also sets up the `moksha.livewidgets` StackedObjectProxy,
    which acts as a registry for Moksha LiveWidget topic callbacks.

    """
    def __init__(self, application, config):
        log.info('Creating Moksha Middleware')
        self.application = application
        self.config = config

        moksha.common.utils._apps = {}
        moksha.common.utils._widgets = {}  # {'widget name': tw.api.Widget}
        moksha.common.utils.menus = {}  # {'menu name': moksha.api.menus.MokshaMenu}
        self.engines = {}  # {'app name': sqlalchemy.engine.base.Engine}

        self.load_paths()
        self.load_configs()
        self.load_widgets()
        self.load_applications()
        self.load_models()
        self.load_menus()
        self.load_root()

    def __call__(self, environ, start_response):
        self.register_livewidgets(environ)
        return self.application(environ, start_response)

    def register_livewidgets(self, environ):
        """ Register the `moksha.livewidgets` dictionary.

        This is a per-request StackedObjectProxy that is used by the
        LiveWidgets to register their own topic callbacks.  The Moksha Live
        Socket then handles subscribing widgets to their appropriate topics,
        decoding the incoming JSON data, and dispatching messages to them as
        they arrive.
        """
        environ['paste.registry'].register(moksha.common.utils.livewidgets, {
            'onopen': [],
            'onclose': [],
            'onerror': [],
            'onerrorframe': [],
            'onconnectedframe': [],
            'onmessageframe': defaultdict(list)  # {topic: [js_callback,]}
        })

    def load_paths(self):
        """ Load the names and paths of all moksha applications and widgets.

        We must do this before actually loading the widgets or applications, to
        ensure that we parse and load each of their configuration files
        beforehand.
        """
        for app_entry in pkg_resources.iter_entry_points(APPS):
            if app_entry.name in moksha.common.utils._apps:
                raise MokshaException('Duplicate application name: %s' %
                                      app_entry.name)
            app_path = app_entry.dist.location
            moksha.common.utils._apps[app_entry.name] = {
                    'name': app_entry.name,
                    'project_name': app_entry.dist.project_name,
                    'path': app_path,
                    }
        for widget_entry in pkg_resources.iter_entry_points(WIDGETS):
            if widget_entry.name in moksha.common.utils._widgets:
                raise MokshaException('Duplicate widget name: %s' %
                                      widget_entry.name)
            widget_path = widget_entry.dist.location
            moksha.common.utils._widgets[widget_entry.name] = {
                    'name': widget_entry.name,
                    'project_name': widget_entry.dist.project_name,
                    'path': widget_path,
                    }

    def load_applications(self):
        log.info('Loading moksha applications')
        for app_entry in pkg_resources.iter_entry_points(APPS):
            log.info('Loading %s application' % app_entry.name)
            app_class = app_entry.load()
            app_path = app_entry.dist.location
            app_name = getattr(app_class, 'name', app_entry.name)
            if isclass(app_class):
                app_class = app_class()
            moksha.common.utils._apps[app_entry.name].update({
                    'name': app_name,
                    'controller': app_class,
                    'path': app_path,
                    'model': None,
                    })
            try:
                # Try to import the 'model' module alongside its 'controllers'
                module = '.'.join(app_class.__module__.split('.')[:-2] +
                                  ['model'])
                model = __import__(module, globals(), locals(),
                                   [app_entry.name])
                moksha.common.utils._apps[app_entry.name]['model'] = model
            except ImportError, e:
                log.debug("Cannot find application model: %r" % module)

    def load_widgets(self):
        """ Load widgets from entry points. """

        log.info('Loading moksha widgets')

        import tw2.core.widgets
        from moksha.wsgi.widgets.api.live import LiveWidgetMeta

        def is_live(widget):
            return isinstance(widget, LiveWidgetMeta)

        for widget_entry in pkg_resources.iter_entry_points(WIDGETS):
            log.info('Loading %s widget' % widget_entry.name)

            widget_class = widget_entry.load()
            if isinstance(widget_class, types.FunctionType):
                widget_class = widget_class(config=self.config)

            widget_path = widget_entry.dist.location
            moksha.common.utils._widgets[widget_entry.name] = {
                    'name': getattr(widget_class, 'name', widget_entry.name),
                    'widget': widget_class,
                    'path': widget_path,
                    'live': is_live(widget_class),
                    }

    def load_menus(self):
        log.info('Loading moksha menus')
        for menu_entry in pkg_resources.iter_entry_points(MENUS):
            log.info('Loading %s menu' % menu_entry.name)
            menu_class = menu_entry.load()
            menu_path = menu_entry.dist.location
            moksha.common.utils.menus[menu_entry.name] = menu_class(menu_entry.name)

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
        apps = []
        loaded_configs = []
        conf_d = '/etc/moksha/conf.d/%s/'

        moksha_config_path = get_moksha_config_path()
        if moksha_config_path:
            moksha_config_path = os.path.dirname(moksha_config_path)
            apps = [{'path': moksha_config_path}]

        apps += moksha.common.utils._apps.values()
        for app in apps:
            for configfile in ('production.ini', 'development.ini'):
                for path in (app['path'], conf_d % app.get('project_name')):
                    confpath = os.path.join(path, configfile)
                    if os.path.exists(confpath):
                        conf = appconfig('config:' + confpath)
                        if app.get('name'):
                            moksha.common.utils._apps[app['name']]['config'] = conf
                        if confpath in loaded_configs:
                            continue
                        log.info('Loading configuration: %s' % confpath)
# This is leftover from the days of using paste.deploy.appconfig.  Is anything
# using this?
#                       for entry in conf.global_conf:
#                           if entry.startswith('_'):
#                               continue
#                           if entry in config:
#                               log.warning('Conflicting variable: %s' % entry)
#                               continue
#                           else:
#                               config[entry] = conf.global_conf[entry]
#                               log.debug('Set `%s` in global config' % entry)
                        loaded_configs.append(confpath)
                        break

    def load_models(self):
        """ Setup the SQLAlchemy database models for all moksha applications.

        This method first looks to see if your application has a
        ``sqlalchemy.url`` set in it's configuration file, and will create a
        SQLAlchemy engine with it.  If it does not exist, Moksha will create an
        engine for your application based on the ``app_db`` configuration,
        which defaults to ``sqlite:///$APPNAME.db``.

        It will then bind the engine to your model's
        :class:`sqlalchemy.MetaData`, and initialize all of your tables,
        if they don't already exist.

        """
        for name, app in moksha.common.utils._apps.items():
            sa_url = app.get('config', {}).get('sqlalchemy.url', None)
            app_db = self.config.get('app_db', 'sqlite:///%s.db')
            if sa_url:
                if app['config']['__file__'] == get_moksha_config_path():
                    # Moksha's apps don't specify their own SA url
                    self.engines[name] = create_engine(app_db % name)
                else:
                    # App has specified its own engine url
                    self.engines[name] = create_engine(sa_url)

            # If a `model` module exists in the application, call it's
            # `init_model` method,and bind the engine to it's `metadata`.
            if app.get('model'):
                if not sa_url:
                    self.engines[name] = create_engine(app_db % name)
                log.debug('Creating database engine for %s' % app['name'])
                app['model'].init_model(self.engines[name])
                app['model'].metadata.create_all(bind=self.engines[name])

    def load_root(self):
        """ Load the root controller.

        This allows developers to configure Moksha to directly hit their
        TurboGears controller or WSGI app.  You can also have the root of your
        website be a single widget.

        This is an example entry-point in your setup.py/pavement.py::

            [moksha.root]
            root = myproject.controllers.root:RootController

        """
        root = None
        for root_entry in pkg_resources.iter_entry_points(ROOT):
            log.info('Loading the root of the project: %r' %
                     root_entry.dist.project_name)
            if root_entry.name == 'root':
                root_class = root_entry.load()
                moksha.common.utils.root = root_class

               # TODO: support setting a root widget
               #if issubclass(root_class, Widget):
               #    widget = root_class(root_class.__name__)
               #    moksha.common.utils._widgets[root_entry.name] = {
               #        'name': getattr(root_class, 'name', widget_entry.name),
               #        'widget': widget,
               #        'path': root_entry.dist.location,
               #        }

               # TODO: handle root wsgi apps
            else:
                log.error('Ignoring [moksha.root] entry %r')
                log.error('Please expose at most 1 object on this entry-point,'
                          ' named "root".')


def make_moksha_middleware(app, config):
    if asbool(config.get('moksha.connectors', False)):
        raise NotImplementedError(
            "moksha.connectors has moved to fedora-community"
        )

    if asbool(config.get('moksha.extensionpoints', True)):
        from moksha.wsgi.middleware import MokshaExtensionPointMiddleware
        app = MokshaExtensionPointMiddleware(app, config)

    app = MokshaMiddleware(app, config)

    if asbool(config.get('moksha.csrf_protection', False)):
        raise NotImplementedError(
            "moksha.csrf_protection has been moved to python-fedora")

    if asbool(config.get('moksha.registry', True)):
        from paste.registry import RegistryManager
        app = RegistryManager(app)

    return app
