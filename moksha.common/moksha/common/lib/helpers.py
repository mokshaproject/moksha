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

import moksha.common.utils
import copy
import time
import urllib
import uuid
import re
import os
import logging
import warnings
import json

import ConfigParser

from UserDict import DictMixin
from pytz import timezone, utc
from decorator import decorator
from kitchen.text.converters import to_unicode as kitchen_unicode

from moksha.common.exc import MokshaConfigNotFound
from moksha.common.lib.dates import DateTimeDisplay, utc_offset

log = logging.getLogger(__name__)
scrub_filter = re.compile('[^_a-zA-Z0-9-]')


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
    return create_engine(config.get('app_db', 'sqlite:///%s.db' % app))


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
