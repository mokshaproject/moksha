from webhelpers import date, feedgenerator, html, number, misc, text

from repoze.what.predicates import  (Predicate, All, Any, has_all_permissions, 
                                    has_any_permission, has_permission, 
                                    in_all_groups, in_any_group, in_group, 
                                    is_user, not_anonymous)

import urllib

def App(label="", url="", req_params={}, auth=[]):
    if not check_predicates(auth):
        return None
    
    query_str = ""
    if req_params:
        query_str = "?" + urllib.urlencode(req_params)

    return (label, url + query_str)    

def MokshaApp(label="", moksha_app="", req_params={}, auth=[]):
    # FIXME figure out how to pull auth info from an app
    return App(label, '/appz/' + moksha_app, req_params, auth)

_safe_predicate_callables = {
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

_app_config_callables = {'MokshaApp': MokshaApp,
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