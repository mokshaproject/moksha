from webhelpers import date, feedgenerator, html, number, misc, text

from repoze.what.predicates import  (Not, Predicate, All, Any, has_all_permissions, 
                                    has_any_permission, has_permission, 
                                    in_all_groups, in_any_group, in_group, 
                                    is_user, not_anonymous)

import urllib
import uuid
import re

from decorator import decorator

scrub_filter = re.compile('[^_a-zA-Z0-9-]')

class ConfigWrapper(object):
    @staticmethod
    def process_wrappers(wrappers):
        result = []
        if isinstance(wrappers, ConfigWrapper):
            w = wrappers.process()
            if w:
                result.append(w)
        else:
            for item in wrappers:
                w = item.process()
                if w:
                    result.append(w)
                    
        return result
        
    def process(self):
        return None

class Category(ConfigWrapper):
    def __init__(self, label="", apps=None, auth=None):
        self.label = label
        self.apps = apps or []
        self.auth = auth or []
    
    def process(self):    
        if not check_predicates(self.auth):
            return None
    
        id = uuid.uuid4()
        css_class =  scrub_filter.sub('_', self.label.lower())

        apps = self.process_wrappers(self.apps)
        return {'label': self.label, 'apps': apps, 'id': id, 'css_class': css_class}

class App(ConfigWrapper):
    def __init__(self, label="", url="", req_params=None, auth=None):
        self.label = label
        self.url = url
        self.req_params = req_params or {}
        self.auth = auth or []
        
    def process(self):
        if not check_predicates(self.auth):
            return None
    
        apps = self.process_wrappers(self.apps)
        return {'label': self.label, 'apps': apps, 'id': id, 'css_class': css_class}

class App(ConfigWrapper):
    def __init__(self, label="", url="", req_params=None, auth=None):
        self.label = label
        self.url = url
        self.req_params = req_params or {}
        self.auth = auth or []
        
    def process(self):
        if not check_predicates(self.auth):
            return None
    
        query_str = ""
        if self.req_params:
            query_str = "?" + urllib.urlencode(self.req_params)

        id = uuid.uuid4()

        return {'label': self.label, 'url': self.url + query_str, 'id': id}    

class MokshaApp(App):
    def __init__(self, label="", moksha_app="", req_params=None, auth=None):
        # FIXME figure out how to pull auth info from an app
        super(MokshaApp, self).__init__(label, '/appz/' + moksha_app, req_params, auth)

_safe_predicate_callables = {
                    'Not': Not,
                    'All': All,
                    'Any': Any, 
                    'has_all_permissions': has_all_permissions, 
                    'has_any_permission': has_any_permission, 
                    'has_permission': has_permission, 
                    'in_all_groups': in_all_groups, 
                    'in_any_group': in_any_group, 
                    'in_group': in_group, 
                    'is_user': is_user, 
                    'not_anonymous': not_anonymous}

_app_config_callables = {'Category': Category,
                         'MokshaApp': MokshaApp,
                         'App': App}

_app_config_callables.update(_safe_predicate_callables)


def eval_app_config(config_str):
    """
    Safely evaluates application configuration strings for storing application
    layout data in a moksha configuration file
    """
    return eval(config_str, {"__builtins__":None}, _app_config_callables)


def eval_predicates(predicate_str):
    """ 
    Safely evaluates a string of predicates
    """
    return eval(predicate_str, {"__builtins__":None}, _safe_predicate_callables)


def check_predicates(predicates):
    """
    Using the current WSGI environment evaluate a list of predicates.  
    This can only be used when inside a WSGI request

    Return False is any one is False 
    Return True if they are all True
    """

    from pylons import request

    if(isinstance(predicates, list) or isinstance(predicates, tuple)):
        for p in predicates:
            if not p.eval_with_environ(request.environ):
                return False
        return True

    
    if(isinstance(predicates, Predicate)):
        return predicates.eval_with_environ(request.environ)

    return False


def eval_and_check_predicates(predicate_str):
    p = eval_predicates(predicate_str)
    return check_predicates(p)


@decorator
def trace(f, *args, **kw):
    """ A useful decorator for debugging method parameters and return values """
    r = None
    try:
        r = f(*args, **kw)
    finally:
        print "%s(%s, %s) = %s" % (f.func_name, args, kw, r)
    return r


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
