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
import tg
import moksha
import moksha.utils
import logging
import pkg_resources
import warnings

from tg.controllers import WSGIAppController
from shove import Shove
from pylons import config
from paste.deploy.converters import asbool
from inspect import isclass
from pylons.i18n import ugettext
from paste.deploy import appconfig
from paste.deploy.converters import asbool
from sqlalchemy import create_engine
from feedcache.cache import Cache

from moksha.exc import MokshaException
from moksha.lib.helpers import (defaultdict, get_moksha_config_path,
                                get_main_app_config_path)
from moksha.wsgiapp import MokshaAppDispatcher

log = logging.getLogger(__name__)

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
    def __init__(self, application):
        log.info('Creating Moksha Middleware')
        self.application = application
        self.mokshaapp = MokshaAppDispatcher(application)

        moksha.utils._apps = {}        # {'app name': tg.TGController/tg.WSGIAppController}
        moksha.utils._widgets = {}    # {'widget name': tw.api.Widget}
        moksha.utils.menus = {}       # {'menu name': moksha.api.menus.MokshaMenu}
        self.engines = {}       # {'app name': sqlalchemy.engine.base.Engine}

        self.load_paths()
        self.load_renderers()
        self.load_configs()
        self.load_widgets()
        self.load_applications()
        self.load_wsgi_applications()
        self.load_models()
        self.load_menus()
        self.load_root()

        try:
            moksha.utils.feed_storage = Shove(config.get('feed_store', 'simple://'),
                                        config.get('feed_cache', 'simple://'),
                                        compress=True)
            moksha.utils.feed_cache = Cache(moksha.utils.feed_storage)
        except Exception, e:
            log.error(str(e))
            log.error("Unable to initialize the Feed Storage")

    def __call__(self, environ, start_response):
        self.register_livewidgets(environ)
        return self.mokshaapp(environ, start_response)

    def register_livewidgets(self, environ):
        """ Register the `moksha.livewidgets` dictionary.

        This is a per-request StackedObjectProxy that is used by the
        LiveWidgets to register their own topic callbacks.  The Moksha Live
        Socket then handles subscribing widgets to their appropriate topics,
        decoding the incoming JSON data, and dispatching messages to them as
        they arrive.
        """
        environ['paste.registry'].register(moksha.utils.livewidgets, {
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
            if app_entry.name in moksha.utils._apps:
                raise MokshaException('Duplicate application name: %s' %
                                      app_entry.name)
            app_path = app_entry.dist.location
            moksha.utils._apps[app_entry.name] = {
                    'name': app_entry.name,
                    'project_name': app_entry.dist.project_name,
                    'path': app_path,
                    }
        for widget_entry in pkg_resources.iter_entry_points('moksha.widget'):
            if widget_entry.name in moksha.utils._widgets:
                raise MokshaException('Duplicate widget name: %s' %
                                      widget_entry.name)
            widget_path = widget_entry.dist.location
            moksha.utils._widgets[widget_entry.name] = {
                    'name': widget_entry.name,
                    'project_name': widget_entry.dist.project_name,
                    'path': widget_path,
                    }

    def load_applications(self):
        log.info('Loading moksha applications')
        for app_entry in pkg_resources.iter_entry_points('moksha.application'):
            log.info('Loading %s application' % app_entry.name)
            app_class = app_entry.load()
            app_path = app_entry.dist.location
            app_name = getattr(app_class, 'name', app_entry.name)
            if isclass(app_class):
                app_class = app_class()
            moksha.utils._apps[app_entry.name].update({
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
                moksha.utils._apps[app_entry.name]['model'] = model
            except ImportError, e:
                log.debug("Cannot find application model: %r" % module)

    def load_wsgi_applications(self):
        log.info('Loading moksha WSGI applications')
        for app_entry in pkg_resources.iter_entry_points('moksha.wsgiapp'):
            log.info('Loading %s WSGI application' % app_entry.name)
            app_path = app_entry.dist.location
            app_class = app_entry.load()
            moksha.utils._apps[app_entry.name] = {
                    'name': getattr(app_class, 'name', app_entry.name),
                    'controller': WSGIAppController(app_class),
                    'path': app_path,
                    'model': None,
                    }

    def load_widgets(self):
        """ Load widgets from entry points intelligently.

        Widgets can be either tw1 widgets or tw2 widgets (with metaclass
        magic).  They can effectively be rendered together and their middlewares
        can live peacefully in the WSGI stack, but their javascript resources
        may fight with one another.  Due to that, we force users to specify
        moksha.use_tw2 = True|False in their .ini configuration.
        """

        log.info('Loading moksha widgets')

        if asbool(config.get('moksha.use_tw2', False)):
            log.info('Preparing for tw2 widgets')
            import tw2.core.widgets
            from moksha.api.widgets.live import LiveWidgetMeta
            def instantiate_widget(cls, name):
                # First, a sanity check
                if not isinstance(cls, tw2.core.widgets.WidgetMeta):
                    warnings.warn("moksha.use_tw2 specified but encountered "+
                                  "non-tw2 widget " + str(cls))
                # TW2 widgets never *really* get instantiated.
                #     The cake is a lie.
                return cls

            def is_live(widget):
                return isinstance(widget, LiveWidgetMeta)
        else:
            log.info('Preparing for tw1 widgets')
            import tw2.core.widgets
            from moksha.api.widgets.live import LiveWidget
            def instantiate_widget(cls, name):
                # Sanity check
                if isinstance(cls, tw2.core.widgets.WidgetMeta):
                    warnings.warn("moksha.use_tw2 is False, but middleware "+
                                  "found a tw2 widget " + str(cls))
                    return cls

                if not isclass(cls):
                    return cls
                return cls(name)

            def is_live(widget):
                return isinstance(widget, LiveWidget)

        for widget_entry in pkg_resources.iter_entry_points('moksha.widget'):
            log.info('Loading %s widget' % widget_entry.name)
            widget_class = widget_entry.load()
            widget_path = widget_entry.dist.location
            widget = instantiate_widget(widget_class, widget_entry.name)
            moksha.utils._widgets[widget_entry.name] = {
                    'name': getattr(widget_class, 'name', widget_entry.name),
                    'widget': widget,
                    'path': widget_path,
                    'live': is_live(widget),
                    }

    def load_menus(self):
        log.info('Loading moksha menus')
        for menu_entry in pkg_resources.iter_entry_points('moksha.menu'):
            log.info('Loading %s menu' % menu_entry.name)
            menu_class = menu_entry.load()
            menu_path = menu_entry.dist.location
            moksha.utils.menus[menu_entry.name] = menu_class(menu_entry.name)

    def load_renderers(self):
        """ Load our template renderers with our application paths.

        We are currently overloading TG2's default Mako renderer because
        the default `escape` filter causes our widgets to show up as escaped HTML.

         """
        from mako.template import Template
        from mako.lookup import TemplateLookup
        try: # TG2.1
            from tg.dottednames.mako_lookup import DottedTemplateLookup
        except ImportError:
            try: # TG2b6
                from tg.dottednamesupport import DottedTemplateLookup
            except: # TG2b5 and earlier
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
            compiled_dir = tg.config.get('templating.mako.compiled_templates_dir', None)

            if not compiled_dir:
                # no specific compile dir give by conf... we expect that
                # the server will have access to the first template dir
                # to write the compiled version...
                # If this is not the case we are doomed and the user should
                # provide us the required config...
                compiled_dir = self.paths['templates'][0]

            # If no dotted names support was required we will just setup
            # a file system based template lookup mechanism.
            compiled_dir = tg.config.get('templating.mako.compiled_templates_dir', None)

            if not compiled_dir:
                # no specific compile dir give by conf... we expect that
                # the server will have access to the first template dir
                # to write the compiled version...
                # If this is not the case we are doomed and the user should
                # provide us the required config...
                compiled_dir = self.paths['templates'][0]

            config['pylons.app_globals'].mako_lookup = TemplateLookup(
                directories=self.paths['templates'],
                module_directory=compiled_dir,
                input_encoding='utf-8', output_encoding='utf-8',
                #imports=['from webhelpers.html import escape'],
                #default_filters=['escape'],
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
        apps = []
        loaded_configs = []
        conf_d = '/etc/moksha/conf.d/%s/'

        moksha_config_path = get_moksha_config_path()
        if moksha_config_path:
            moksha_config_path = os.path.dirname(moksha_config_path)
            apps = [{'path': moksha_config_path}]
        main_app_config_path = os.path.dirname(get_main_app_config_path())

        apps += moksha.utils._apps.values()
        for app in apps:
            for configfile in ('production.ini', 'development.ini'):
                for path in (app['path'], conf_d % app.get('project_name')):
                    confpath = os.path.join(path, configfile)
                    if os.path.exists(confpath):
                        conf = appconfig('config:' + confpath)
                        if app.get('name'):
                            moksha.utils._apps[app['name']]['config'] = conf
                        if app['path'] == main_app_config_path or \
                                confpath in loaded_configs:
                            continue
                        log.info('Loading configuration: %s' % confpath)
                        for entry in conf.global_conf:
                            if entry.startswith('_'):
                                continue
                            if entry in config:
                                log.warning('Conflicting variable: %s' % entry)
                                continue
                            else:
                                config[entry] = conf.global_conf[entry]
                                log.debug('Set `%s` in global config' % entry)
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
        for name, app in moksha.utils._apps.items():
            sa_url = app.get('config', {}).get('sqlalchemy.url', None)
            app_db = config.get('app_db', 'sqlite:///%s.db')
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
        for root_entry in pkg_resources.iter_entry_points('moksha.root'):
            log.info('Loading the root of the project: %r' %
                     root_entry.dist.project_name)
            if root_entry.name == 'root':
                root_class = root_entry.load()
                moksha.utils.root = root_class

                # TODO: support setting a root widget
                #if issubclass(root_class, Widget):
                #    widget = root_class(root_class.__name__)
                #    moksha.utils._widgets[root_entry.name] = {
                #        'name': getattr(root_class, 'name', widget_entry.name),
                #        'widget': widget,
                #        'path': root_entry.dist.location,
                #        }

                # TODO: handle root wsgi apps
            else:
                log.error('Ignoring [moksha.root] entry %r')
                log.error('Please expose at most 1 object on this entry-point,'
                          ' named "root".')


def make_moksha_middleware(app):

    if asbool(config.get('moksha.connectors', True)):
        from moksha.middleware import MokshaConnectorMiddleware
        app = MokshaConnectorMiddleware(app)
    if asbool(config.get('moksha.extensionpoints', True)):
        from moksha.middleware import MokshaExtensionPointMiddleware
        app = MokshaExtensionPointMiddleware(app)

    app = MokshaMiddleware(app)

    if asbool(config.get('moksha.csrf_protection', True)):
        from moksha.middleware.csrf import CSRFProtectionMiddleware
        app = CSRFProtectionMiddleware(
                app,
                csrf_token_id=config.get('moksha.csrf.token_id', '_csrf_token'),
                clear_env=config.get('moksha.csrf.clear_env',
                    'repoze.who.identity repoze.what.credentials'),
                token_env=config.get('moksha.csrf.token_env', 'CSRF_TOKEN'),
                auth_state=config.get('moksha.csrf.auth_state',
                                      'CSRF_AUTH_STATE'),
                )

    return app
