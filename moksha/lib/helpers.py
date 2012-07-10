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

import moksha
import moksha.utils
import copy
import time
import urllib
import uuid
import re
import os
import logging
import warnings
from orbited import json

import ConfigParser

from UserDict import DictMixin
from tw2.core import js_callback
from pytz import timezone, utc
from webob import Request
from decorator import decorator
from datetime import datetime
from BeautifulSoup import BeautifulSoup, NavigableString
from webhelpers import date, feedgenerator, html, number, misc, text
from webhelpers.date import distance_of_time_in_words
from repoze.what.authorize import check_authorization, NotAuthorizedError
from repoze.what.predicates import  (Not, Predicate, All, Any,
                                     has_all_permissions, has_any_permission,
                                     has_permission, in_all_groups,
                                     in_any_group, in_group, is_user,
                                     not_anonymous)
from kitchen.text.converters import to_unicode as kitchen_unicode

from moksha.exc import MokshaConfigNotFound

log = logging.getLogger(__name__)
scrub_filter = re.compile('[^_a-zA-Z0-9-]')


def _update_params(params, d):
    p = {}
    if params:
        for k in params.iterkeys():

            if d and (k in d):
                value = d[k]
            else:
                value = params[k]

            # recursive dicts also get updated
            # by the passed params
            if isinstance(value, dict):
                value = _update_params(value, d)
                value = json.encode(value)
            elif isinstance(value, list):
                value = value

            if value != None:
                p[k] = value

    return p


class ConfigWrapper(object):
    """ Base class for container configuration wrappers

    Configuration Wrappers are python objects which can be embedded in
    configuration stores (files and databases) or used directly to
    insert web applications into containers.  Wrappers also integrate
    repoze.what predicates which are checked when the wrapper is processed.
    If the prediates return False the web application is not displayed to
    the user.  This makes it easy to build composite Moksha applications
    where what the user is show is dictated by their authorization level.

    Configuration wrapper are only standard data structures with the ability
    to process predicates.  A container widget is needed to convert the
    configuration into rendered applications on a page.

    Derive from this class to create new configuration syntax

    """

    def _update_nested_dicts(self, dest, source):
        """Recursive helper which updates nested dicts"""

        for key, value in source.iteritems():
            if key in dest:
                if isinstance(dest[key], dict):
                    self._update_nested_dicts(dest[key], value)
                else:
                    dest[key] = value
            else:
                dest[key] = value

    @staticmethod
    def _validate_predicates(predicates):
        if not isinstance(predicates, (list, tuple)):
            predicates = (predicates,)

        for p in predicates:
            if not isinstance(p, Predicate):
                raise AttributeError('"%r" is not a subclass of '
                                     'repoze.who.predicates.Predicate' % p)

    @staticmethod
    def process_wrappers(wrappers, d):
        """ Helper method for evlauating a list of wrappers

        :returns: a list of hashes for each of the application
                  that will be displayed
        """

        result = []
        if isinstance(wrappers, ConfigWrapper):
            w = wrappers.process(d)
            if w:
                result.append(w)
        else:
            for item in wrappers:
                w = item.process(d)
                if w:
                    result.append(w)

        return result

    def process(self, d=None):
        """Override this in derived classes to update the hash representing
        the configuration option
        """
        default_values = dict(query_string='',
                              id='uuid' + str(uuid.uuid4()),
                              type=self.__class__.__name__)

        return default_values


class Category(ConfigWrapper):
    """A configuration wrapper class that displays a list of application
    and/or widget wrappers

    :Example:
        left_column = Category("Left Column Apps",
                               [App(...), App(...)],
                               not_anonymous())
    """

    def __init__(self, label="", apps=None, css_class=None, auth=None,
                default_child_css=None):
        """
        :label: The category heading the container should use when rendering
                a category.  Labels for categories are not rendered in the
                default template. If a css_class is not defined the label
                becomes the css class for the div once it has been scrubbed
                by making it all lower case and replacing illegal characters
                with underscores.
        :apps: A list of wrappers representing application configurations
        :auth: A list of predicates which are evaluate before the wrapper
               is sent to the container.  If it evaluates to False it does not
               get sent.
        :css_class: Either a string or list of strings defining the css class
                    for this category
        :default_child_css: Either a string or list of strings defining the
                            default css for child apps and widgets
        """
        super(Category, self).__init__()

        self.label = label
        self.apps = apps or tuple()
        if not isinstance(self.apps, tuple):
            if not getattr(self.apps, '__iter__', False):
                self.apps = (self.apps,)
            else:
                self.apps = tuple(self.apps)
        self.auth = auth or tuple()

        self._validate_predicates(self.auth)

        if not css_class:
            css_class = scrub_filter.sub('_', self.label.lower())
        elif isinstance(css_class, list) or isinstance(css_class, tuple):
            css_class = ' '.join(css_class)

        self.css_class = css_class

        if isinstance(default_child_css, list) or isinstance(css_class, tuple):
            default_child_css = ' '.join(default_child_css)

        for a in self.apps:
            a.set_default_css(default_child_css)

    def process(self, d=None):
        """Check the predicates and construct the dict

        :returns: a dict with all the configuration data for this category
        """
        results = super(Category, self).process(d)

        if not check_predicates(self.auth):
            return None

        apps = self.process_wrappers(self.apps, d)
        results.update({'label': self.label,
                  'apps': apps,
                  'css_class': self.css_class})

        return results


class App(ConfigWrapper):
    """A configuration wrapper class that displays an application pointed to
    by a url

    :Example:
        hello_app = App('Hello World App',
                        '/apps/moksha.helloworld',
                        params={'greeter_name': 'J5'},
                        auth=not_anonymous())
    """
    def __init__(self, label="", url="", content_id="",
                 params=None, auth=None, css_class=None):
        """
        :label: The title the application should use when rendering
                in a container.  Leave this blank if you do not wish the
                application to be visibly labeled when rendered
        :url: the url to load this application from
        :content_id: the id to use for url navigation and associating the
                     content with a control such as tabs needing to know
                     which div to add the content to when selected. If
                     this is not set we scrub the label of illegal characters
                     lower case it and use that as the content_id
        :params: A dict of request parameters to send to the application
                 when loading it from a url
        :auth: A list of predicates which are evaluate before the wrapper
               is sent to the container.  If it evaluates to False it does not
               get sent.
        :css_class: Either a string or list of strings defining the css class
                    for this wrapper
        """
        super(App, self).__init__()

        self.label = label
        self.url = url
        self.params = params or {}
        self.auth = auth or []
        self.content_id = content_id

        self._validate_predicates(self.auth)

        if isinstance(css_class, list) or isinstance(css_class, tuple):
            css_class = ' '.join(css_class)
        self.css_class = css_class

        if self.label and not self.content_id:
            self.content_id = scrub_filter.sub('_', self.label.lower())

    def clone(self, update_params=None, auth=None,
              content_id=None, label=None):
        if not update_params:
            update_params = {}

        params = copy.deepcopy(self.params)

        self._update_nested_dicts(params, update_params)

        if auth == None:
            auth = self.auth

        if content_id == None:
            content_id == self.content_id

        if label == None:
            label = self.label

        return App(label=label,
                   url=self.url,
                   params=params,
                   auth=auth,
                   content_id=content_id,
                   css_class=self.css_class)

    def set_default_css(self, css):
        """ If we already have css defined ignore, otherwise set our css_class
        """
        if(self.css_class == None):
            self.css_class = css

    def _create_query_string(self, params):
        qlist = []
        for k, i in params.iteritems():
            if isinstance(i, (list, tuple)):
                # break out lists into multiple entries of the same key
                for j in i:
                    s = str(j)
                    s = urllib.quote_plus(s)
                    qlist.append("%s=%s" % (k, s))

            else:
                s = str(i)
                s = urllib.quote_plus(s)

                qlist.append("%s=%s" % (k, s))

        result = ""
        if qlist:
            result = '?' + '&'.join(qlist)

        return result

    def process(self, d=None):
        """Check the predicates and construct the dict

        :returns: a dict with all the configuration data for this application
        """
        if not check_predicates(self.auth):
            return None

        results = super(App, self).process(d)

        css_class = self.css_class
        if css_class == None:
            css_class = ''

        p = _update_params(self.params, d)
        qs = self._create_query_string(p)
        results.update({'label': self.label, 'url': self.url,
                'params': p,
                'json_params': json.encode(p),
                'query_string': qs,
                'content_id': self.content_id + '-' + results['id'],
                'css_class': css_class})

        return results


class StaticLink(App):
    """A configuration wrapper class that shows up as a static link in nav
    elements"""


class MokshaApp(App):
    """A configuration wrapper class that displays a Moksa application
    selected by name. This differes from App in that you don't have to
    know the url, only the name the application is mounted under.  In
    future versions we may also try and get the auth predicated from
    the application's own configuration.

    :Example:
        hello_app = App('Hello World Moksha App',
                        'moksha.helloworld',
                        params={'greeter_name': 'J5'},
                        auth=not_anonymous())

    """
    def __init__(self, label="", moksha_app="", content_id="",
                 params=None, auth=None, css_class=None):
        """
        :label: The title the application should use when rendering
                in a container.  Leave this blank if you do not wish the
                application to be visibly labeled when rendered
        :moksha_app: the name of the entry point registered under the
                     moksha.application section
        :content_id: the id to use for url navigation and associating the
                     content with a control such as tabs needing to know
                     which div to add the content to when selected. If
                     this is not set we scrub the label of illegal characters
                     lower case it and use that as the content_id
        :params: A dict of request parameters to send to the application
                 when loading it
        :auth: A list of predicates which are evaluate before the wrapper
               is sent to the container.  If it evaluates to False it does not
               get sent.
        :css_class: Either a string or list of strings defining the css class
                    for this wrapper
        """
        # FIXME figure out how to pull auth info from an app
        app = moksha_app.split('/')[0]
        self.app = app
        super(MokshaApp, self).__init__(label,
                                        '/apps/' + moksha_app,
                                        content_id,
                                        params, auth, css_class)

    def process(self, d=None):
        # We return a placeholder if the app is not registered
        if not self.app in moksha._apps:
            return MokshaWidget(self.label, 'placeholder',
                                self.content_id,
                                {'appname': self.app},
                                self.auth,
                                self.css_class).process(d)
        else:
            results = super(MokshaApp, self).process(d)
            return results


class Widget(ConfigWrapper):
    """A configuration wrapper class that displays a ToscaWidget.  Use this
    instead of an App when the time it takes to load an application from a url
    is more than the time it takes to just embed it in the template.  Widgets
    also lack the ability to respond to remote requests via controllers.

    :Example:
        class HelloWidget(tw2.core.Widget):
            pass

        hello_widget = Widget('Hello World Widget',
                        HelloWidget(),
                        params={'greeter_name': 'J5'},
                        auth=not_anonymous())

    """
    def __init__(self, label="", widget=None, content_id="",
                 params=None, auth=None, css_class=None):
        """
        :label: The title the widget should use when rendering
                in a container.  Leave this blank if you do not wish the
                widget to be visibly labeled when rendered
        :widget: the ToscaWidget to be rendered
        :content_id: the id to use for url navigation and associating the
                     content with a control such as tabs needing to know
                     which div to add the content to when selected. If
                     this is not set we scrub the label of illegal characters
                     lower case it and use that as the content_id
        :params: A dict of parameters to send to the widgets update_params
                 method when rendering it
        :auth: A list of predicates which are evaluate before the wrapper
               is sent to the container.  If it evaluates to False it does not
               get sent.
        :css_class: Either a string or list of strings defining the css class
                    for this wrapper
        """
        super(Widget, self).__init__()
        self.label = label
        self.widget = widget
        self.params = params or {}
        self.auth = auth or []
        self._validate_predicates(self.auth)

        self.content_id = content_id

        if isinstance(css_class, list) or isinstance(css_class, tuple):
            css_class = ' '.join(css_class)
        self.css_class = css_class

        if self.label and not content_id:
            self.content_id = scrub_filter.sub('_', self.label.lower())

    def clone(self, update_params=None, auth=None, content_id=None):
        if not update_params:
            update_params = {}
        params = copy.deepcopy(self.params)
        self._update_nested_dicts(params, update_params)

        if auth == None:
            auth = self.auth

        if content_id == None:
            content_id = self.content_id

        return Widget(label=self.label,
                   widget=self.widget,
                   params=params,
                   auth=auth,
                   content_id=content_id,
                   css_class=self.css_class)

    def set_default_css(self, css):
        """ If we already have css defined ignore, otherwise set our css_class
        """
        if(self.css_class == None):
            self.css_class = css

    def process(self, d=None):
        if not check_predicates(self.auth):
            return None

        results = super(Widget, self).process(d)

        content_id = self.content_id + '-' + results['id']
        url = '#' + content_id
        results.update({
            'label': self.label, 'url': url, 'widget': self.widget,
            'params': _update_params(self.params, d), 'id': results['id'],
            'content_id': content_id, 'css_class': self.css_class})

        return results


class MokshaWidget(Widget):
    """A configuration wrapper class that displays a ToscaWidget registered
    in Moksha's widget dictionary.

    :Example:
        hello_moksha_widget = Widget('Hello Moksha Widget',
                                     'moksha.hello',
                                     params={'greeter_name': 'J5'},
                                     auth=not_anonymous())

    """
    def __init__(self, label="", moksha_widget="", content_id="",
                 params=None, auth=None, css_class=None):
        """
        :label: The title the widget should use when rendering
                in a container.  Leave this blank if you do not wish the
                widget to be visibly labeled when rendered
        :content_id: the id to use for url navigation and associating the
                     content with a control such as tabs needing to know
                     which div to add the content to when selected. If
                     this is not set we scrub the label of illegal characters
                     lower case it and use that as the content_id
        :moksha_widget: the name of the entry point registered under the
                        moksha.widget section
        :params: A dict of parameters to send to the widgets update_params
                 method when rendering it
        :auth: A list of predicates which are evaluate before the wrapper
               is sent to the container.  If it evaluates to False it does not
               get sent.
        :css_class: Either a string or list of strings defining the css class
                    for this wrapper
        """
        widget = moksha.utils._widgets[moksha_widget]['widget']
        return super(MokshaWidget, self).__init__(
            label=label, widget=widget,
            content_id=content_id, params=params,
            auth=auth,
            css_class=css_class)


class param_contains(Predicate):
    """
    Checks the parameters of the environment and return True if the
    parameter contains the value specified.  If the parameter is a list
    (more than one value) then check each item in the list.
    Note this is the environment params (query string and post file) not the TG
    or ToscaWidget param dicts
    """
    message = u'Parameter "%(param)s" is does not contain value "%(value)s"'

    def __init__(self, param, value, **kwargs):
        super(param_contains, self).__init__(**kwargs)
        self.param = param
        self.value = value

    def evaluate(self, environ, credentials):
        req = Request(environ)
        p = req.params.getall(self.param)

        if not p:
            return self.unmet(param=self.param, value=self.value)

        print p
        for v in p:
            print v, '==', self.value
            if v == self.value:
                return

        return self.unmet(param=self.param, value=self.value)


class param_has_value(Predicate):
    """
    Checks the parameters of the environment and return True if the
    parameter specified holds a value.  Note this is the environment params
    (query string and post file) not the TG or ToscaWidget param dicts
    """
    message = u'Parameter "%(param)s" is not set'

    def __init__(self, param, empty_str_is_valid=False, **kwargs):
        super(param_has_value, self).__init__(**kwargs)
        self.param = param
        self.empty_str_is_valid = empty_str_is_valid

    def evaluate(self, environ, credentials):
        req = Request(environ)
        p = req.params.getall(self.param)

        if not p:
            return self.unmet(param=self.param)

        p = p[0]
        if p == None:
            return self.unmet(param=self.param)

        if not self.empty_str_is_valid and p == '':
            return self.unmet(param=self.param)

        return

# setup the dictionary of acceptable callables when eval'ing predicates from
# a configuration file - this makes up the keywords of the predicate
# configuration format
_safe_predicate_callables = {
                    'Not': Not,
                    'All': All,
                    'Any': Any,
                    'param_has_value': param_has_value,
                    'has_all_permissions': has_all_permissions,
                    'has_any_permission': has_any_permission,
                    'has_permission': has_permission,
                    'in_all_groups': in_all_groups,
                    'in_any_group': in_any_group,
                    'in_group': in_group,
                    'is_user': is_user,
                    'not_anonymous': not_anonymous}

# setup the dictionary of acceptable callables when eval'ing config wrappers
# from a configuration file - this makes up the keywords of the config wrapper
# configuration format
_app_config_callables = {'Category': Category,
                         'MokshaApp': MokshaApp,
                         'Widget': Widget,
                         'App': App,
                         'MokshaWidget': MokshaWidget}

# config wrapper configuration can also utilize predicates
_app_config_callables.update(_safe_predicate_callables)


def eval_app_config(config_str):
    """
    Safely evaluates application configuration strings for storing application
    layout data in a moksha configuration file

    :return: the evaluated configuration wrapper configuration
    """
    return eval(
        config_str, {"__builtins__": None}, _app_config_callables)


def eval_predicates(predicate_str):
    """
    Safely evaluates a string of predicates

    :return: the evaluated predicate configuration
    """
    return eval(
        predicate_str, {"__builtins__": None}, _safe_predicate_callables)


def check_predicates(predicates, request):
    """
    Using the current WSGI environment run a list of predicates.
    This can only be used when inside a WSGI request

    :return: False is any one is False
    :return: True if they are all True
    """

    if(not(isinstance(predicates, list) or isinstance(predicates, tuple))):
        predicates = (predicates,)

    for p in predicates:
        try:
            check_authorization(p, request.environ)
        except NotAuthorizedError, e:
            return False

    return True


def eval_and_check_predicates(predicate_str):
    """
    Using the current WSGI environment evaluate a predicate sting and run
    the resulting predicate list. This can only be used when inside a WSGI
    request

    :return: False is any one is False
    :return: True if they are all True
    """
    p = eval_predicates(predicate_str)
    return check_predicates(p)


@decorator
def trace(f, *args, **kw):
    """ A useful decorator for debugging method parameters and return values
    """
    r = None
    try:
        r = f(*args, **kw)
    finally:
        print "%s(%s, %s) = %s" % (f.func_name, args, kw, r)
    return r


# TODO -- remove this and just get it from pypi
try:
    from collections import defaultdict
except:
    # A pure Python version of Python 2.5's defaultdict
    # http://code.activestate.com/recipes/523034/
    # by Jason Kirtland
    class defaultdict(dict):
        def __init__(self, default_factory=None, *a, **kw):
            if (default_factory is not None and
                not hasattr(default_factory, '__call__')):
                raise TypeError('first argument must be callable')
            dict.__init__(self, *a, **kw)
            self.default_factory = default_factory

        def __getitem__(self, key):
            try:
                return dict.__getitem__(self, key)
            except KeyError:
                return self.__missing__(key)

        def __missing__(self, key):
            if self.default_factory is None:
                raise KeyError(key)
            self[key] = value = self.default_factory()
            return value

        def __reduce__(self):
            if self.default_factory is None:
                args = tuple()
            else:
                args = self.default_factory,
            return type(self), args, None, None, self.items()

        def copy(self):
            return self.__copy__()

        def __copy__(self):
            return type(self)(self.default_factory, self)

        def __deepcopy__(self, memo):
            import copy
            return type(self)(self.default_factory,
                              copy.deepcopy(self.items()))

        def __repr__(self):
            return 'defaultdict(%s, %s)' % (self.default_factory,
                                            dict.__repr__(self))


def cache_rendered_data(data):
    """ A method to cache ``data`` with the current request path as the key.

    This method can be used within TurboGears2 hooks to cache rendered data
    from a given method for a specific URL.  For example, to cache the
    index.html, you could do something like this.

    .. code-block:: python

        from tg.decorators import after_render

        @after_render(cache_rendered_data)
        @expose('mako:moksha.templates.index')
        def index(self):
            return dict()

    :Warning: In this example usage, the method caches the data before it makes
              its way out of the WSGI middleware stack.  Therefore, widget
              resources are not injected, and stored in the cache.

    :Warning: This function only works with pylons.

    """
    import pylons

    if hasattr(pylons.g, 'cache') and pylons.g.cache and \
            pylons.request.environ.get('HTTP_X_FORWARDED_PROTO'):
        pylons.g.cache.set(pylons.request.path_qs, str(data))


@decorator
def cache_rendered(func, *args, **kwargs):
    content = func(*args, **kwargs)
    cache_rendered_data(content)
    return content


def in_full_moksha_stack():
    """
    Figure out if we are running Moksha as WSGI middleware, or in our full
    stack.

    :returns: True if we are currently running in Moksha's full WSGI stack,
              False if we are running Moksha only as WSGI middleware.
    """
    # This is deprecated, since there's no such thing as moksha 'full stack'
    # anymore.
    return False


def get_moksha_config_path():
    """
    :returns: The path to Moksha's configuration file.
    """
    for config_path in ('.', '/etc/moksha/', __file__ + '/../../../'):
        for config_file in ('production.ini', 'development.ini'):
            cfg = os.path.join(os.path.abspath(config_path), config_file)
            if os.path.isfile(cfg):
                return cfg

    log.warn('No moksha configuration file found, make sure the '
             'controlling app is fully configured')

    return None
    # raise MokshaConfigNotFound('Cannot find moksha configuration file!')


def get_moksha_dev_config():
    fname = 'development.ini'
    cfgs = [
        os.path.join(os.path.abspath(__file__ + '/../../../'), fname),
        os.path.join(os.path.abspath(__file__ + '/../../../../'), fname),
        os.path.join(os.getcwd(), fname),
        '/etc/moksha/%s' % fname,
    ]
    for cfg in cfgs:
        if os.path.isfile(cfg):
            return cfg
    log.warn("Cannot find configuration in %r" % cfgs)


def get_moksha_appconfig():
    """ Return the appconfig of Moksha """
    return appconfig('config:' + get_moksha_config_path())


def appconfig(config_path):
    """ Our own reimplementation of paste.deploy.appconfig """

    if config_path.startswith('config:'):
        config_path = config_path[7:]

    here = os.path.abspath(os.path.dirname(config_path))
    parser = ConfigParser.ConfigParser({"here": here})
    parser.read(filenames=[config_path])
    try:
        return dict(parser.items('app:main'))
    except ConfigParser.NoSectionError:
        for section in parser.sections():
            if section.startswith('app:'):
                print "Using %r" % section
                return dict(parser.items(section))

        raise ConfigParser.NoSectionError("Couldn't find app: section.")


def create_app_engine(app, config):
    """ Create a new SQLAlchemy engine for a given app """
    from sqlalchemy import create_engine
    return create_engine(config.get('app_db', 'sqlite:///%s.db') % app)


def to_unicode(obj, encoding='utf-8', errors='replace'):
    """
    :deprecated: by to_unicode in http://python-kitchen.fedorahosted.org
    """
    deprecation("to_unicode is deprecated in favor of "
                "kitchen.text.coverters.to_unicode().")
    return kitchen_unicode(obj, encoding, errors)


def replace_app_header(app, header_name, value):
        from paste.response import replace_header
        if app.headers:
            headers = list(app.headers)
        else:
            headers = []

        replace_header(headers, header_name, value)
        app.headers = headers


class EnumDataObj(dict):
    def __init__(self, code, data):
        super(EnumDataObj, self).__init__(code=code, data=data)

    def __getattribute__(self, name):
        try:
            return super(EnumDataObj, self).__getattribute__(name)
        except AttributeError, e:
            if name in self:
                return self[name]

            raise e

    def replace_app_header(self, app, header_name):
        replace_app_header(app, header_name, self.code)

    def __repr__(self):
        # act as if the user requested the code
        return str(self['code'])


class CategoryEnum(object):
    def __init__(self, prefix, *data):
        self._prefix = prefix
        self._code_map = {}

        for d in data:
            # data should be a tuple of (id, url)
            # id can not have any dots in them
            id = d[0]
            if id.find('.') != -1:
                raise ValueError(
                    'The enumeration id %s can not contain dots', id)

            # code is prefix.id
            code = '%s.%s' % (prefix, d[0])
            dob = EnumDataObj(code, d[1])
            setattr(self, d[0], dob)
            setattr(self, code, dob)
            self._code_map[code] = d[0]

    def is_valid_class(self, code):
        if code.beginswith(self._prefix + '_'):
            return True

        return False

    def code_to_attr(self, code):
        return self._code_map[code]

    def attr_to_code(self, attr):
        return self.__getattribute__(attr).code

    def attr_to_data(self, attr):
        return self.__getattribute__(attr).data

    def get_code(self, attr):
        return self.attr_to_code(attr)

    def get_data(self, attr):
        return self.attr_to_data(attr)

    def get_category(self):
        return self._prefix

    def __call__(self, code):
        return self.get_data(code)


class EnumGroup(object):
    def __init__(self):
        self._enums = {}

    def add(self, enum):
        self._enums[enum.get_category()] = enum

    def __getitem__(self, key):
        (category, enum_id) = key.rsplit('.', 1)
        enum = self._enums[category]
        return enum.get_data(key)


def strip_script(environ):
    """
    Strips the script portion of a url path so the middleware works even
    when mounted under a path other than root.
    """
    path = environ['PATH_INFO']
    if path.startswith('/') and 'SCRIPT_NAME' in environ:
        prefix = environ.get('SCRIPT_NAME')
        if prefix.endswith('/'):
            prefix = prefix[:-1]
        if path.startswith(prefix):
            path = path[len(prefix):]
    return path


def utc_offset(tz):
    """ Return the UTC offset for a given timezone.

        >>> utc_offset('US/Eastern')
        '-4'

    """
    utc_offset = ''
    now = datetime.now(utc)
    now = now.astimezone(timezone(tz))
    offset = now.strftime('%z')
    if offset.startswith('-'):
        offset = offset[1:]
        utc_offset += '-'
    hours = int(offset[:2])
    utc_offset += str(hours)
    # FIXME: account for minutes?
    #minutes = int(offset[2:])
    #if minutes:
    #    utc_offset += '.%d' % ...
    return utc_offset


class DateTimeDisplay(object):
    """
    DateTimeDisplay is an object which takes any number of datetime objects
    and process them for display::

        >>> from datetime import datetime
        >>> now = datetime(2009, 5, 12)
        >>> later = datetime(2009, 5, 13)
        >>> d = DateTimeDisplay(now)
        >>> print d
        2009-05-12 00:00:00
        >>> d.age(later)
        '1 day'
        >>> d.age(datetime(2010, 7, 10, 10, 10), granularity='minute')
        '1 year, 1 month, 29 days, 10 hours and 10 minutes'
        >>> d.age(datetime(2010, 7, 10, 10, 10), tz='Europe/Amsterdam')
        '1 year, 1 month, 29 days and 10 hours'
        >>> d = DateTimeDisplay(datetime(2009, 5, 12, 12, 0, 0))
        >>> d.timestamp
        datetime.datetime(2009, 5, 12, 12, 0)
        >>> d.astimezone('Europe/Amsterdam')
        datetime.datetime(2009, 5, 12, 14, 0, tzinfo=<DstTzInfo 'Europe/Amsterdam' CEST+2:00:00 DST>)

    """
    def __init__(self, timestamp, format='%Y-%m-%d %H:%M:%S'):
        if isinstance(timestamp, basestring) and '.' in timestamp:
            timestamp = timestamp.split('.')[0]
        self.timestamp = timestamp
        if isinstance(timestamp, datetime):
            self.datetime = timestamp
        elif isinstance(timestamp, time.struct_time):
            self.datetime = datetime(*timestamp[:-2])
        elif isinstance(timestamp, basestring):
            if hasattr(datetime, 'strptime'): # Python 2.5+
                self.datetime = datetime.strptime(timestamp, format)
            else: # Python 2.4
                self.datetime = datetime(*time.strptime(timestamp, format)[:-2])
        else:
            raise Exception("You must provide either a datetime object or a"
                            "string, not %s" % type(timestamp))

    def astimezone(self, tz):
        """ Return `self.datetime` as a different timezone """
        timestamp = self.datetime.replace(tzinfo=utc)
        zone = timezone(tz)
        return zone.normalize(timestamp.astimezone(zone))

    def age(self, end=None, tz=None, granularity='hour', general=False):
        """
        Return the distance of time in words from `self.datetime` to `end`.

            >>> start = datetime(1984, 11, 02)
            >>> now = datetime(2009, 5, 22, 12, 11, 10)
            >>> DateTimeDisplay(start).age(now)
            '2 decades, 4 years, 6 months, 20 days and 12 hours'
            >>> DateTimeDisplay(start).age(now, general=True)
            '2 decades'

        """
        start = self.datetime
        if not end:
            end = datetime.utcnow()
        else:
            if isinstance(end, DateTimeDisplay):
                end = end.datetime
        if tz:
            zone = timezone(tz)
            end = end.replace(tzinfo=utc)
            end = zone.normalize(end.astimezone(zone))
            start = self.astimezone(tz)

        age = distance_of_time_in_words(start, end, granularity=granularity)

        if general:
            if not age.startswith('less than'):
                age = age.split('and')[0].split(',')[0]

        return age

    def __str__(self):
        return self.datetime.strftime('%Y-%m-%d %H:%M:%S %Z%z')

    def __repr__(self):
        return "<DateTimeDisplay %r>" % self.datetime


def when_ready(func):
    """
    Takes a js_function and returns a js_callback that will run
    when the document is ready.

        >>> from tw.api import js_function
        >>> print when_ready(js_function('jQuery')('foo').bar({'biz': 'baz'}))
        $(document).ready(function(){jQuery("foo").bar({"biz": "baz"})});
    """
    return js_callback('$(document).ready(function(){' + str(func) + '});')


def get_num_cpus():
    cpus = 1
    for line in open('/proc/cpuinfo'):
        if line.startswith('processor'):
            cpus = int(line.split()[-1]) + 1
    return cpus


def deprecation(message):
    warnings.warn(message, DeprecationWarning)


def listify(something):
    if something:
        return not isinstance(something, list) and [something] or something
    else:
        return []


class odict(DictMixin):

    def __init__(self):
        self._keys = []
        self._data = {}

    def index(self, i):
        k = self._keys[i]
        return self._data[k]

    def key_index(self, i):
        return self._keys[i]

    def __setitem__(self, key, value):
        if key not in self._data:
            self._keys.append(key)

        self._data[key] = value

    def __getitem__(self, key):
        return self._data[key]

    def __delitem__(self, key):
        del self._data[key]
        self._keys.remove(key)

    def __iter__(self):
        for key in self._keys:
            yield key

    def keys(self):
        return list(self._keys)

    def copy(self):
        copyDict = odict()
        copyDict._data = self._data.copy()
        copyDict._keys = self._keys[:]
        return copyDict

    def __repr__(self):
        result = []
        for key in self._keys:
            result.append('(%s, %s)' % (repr(key), repr(self._data[key])))
        return ''.join(['OrderedDict', '([', ', '.join(result), '])'])
