import urllib
import uuid
import re

from decorator import decorator
from webhelpers import date, feedgenerator, html, number, misc, text
from repoze.what.predicates import  (Not, Predicate, All, Any,
                                    has_all_permissions,
                                    has_any_permission, has_permission,
                                    in_all_groups, in_any_group, in_group,
                                    is_user, not_anonymous)

scrub_filter = re.compile('[^_a-zA-Z0-9-]')


def Category(label="", apps=[], auth=[]):
    if not check_predicates(auth):
        return None

    id = uuid.uuid4()
    css_class =  scrub_filter.sub('_', label.lower())

    return {'label': label, 'apps': apps, 'id': id, 'css_class': css_class}

def App(label="", url="", req_params={}, auth=[]):
    if not check_predicates(auth):
        return None

    query_str = ""
    if req_params:
        query_str = "?" + urllib.urlencode(req_params)

    id = uuid.uuid4()

    return {'label': label, 'url': url + query_str, 'id': id}    


def MokshaApp(label="", moksha_app="", req_params={}, auth=[]):
    # FIXME figure out how to pull auth info from an app
    return App(label, '/appz/' + moksha_app, req_params, auth)

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

    if isinstance(predicates, list) or isinstance(predicates, tuple):
        for p in predicates:
            if not p.eval_with_environ(request.environ):
                return False
        return True

    if isinstance(predicates, Predicate):
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
