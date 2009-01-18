from tw.jquery.ui_tabs import JQueryUITabs
from pylons import config, request
from repoze.what import predicates

import urllib

def App(label="", url="", req_params={}, predicates=[]):
    if predicates:
        for p in predicates:
            if not p.eval_with_environ(request.environ):
                return None
    
    return (label, url + "?" + urllib.urlencode(req_params))    

def MokshaApp(label="", moksha_app="", req_params={}, predicates=()):
    # FIXME figure out how to pull auth info from an app
    return App(label, '/appz/' + moksha_app, req_params, predicates)

""" 
:Name: TabbedContainer
:Type: Container

:Notes:  We may need to create a tab javascript object that inherits from
         jQuery.ui.tabs
""" 
class TabbedContainer(JQueryUITabs):
    """
    :tabs: An ordered list of application tabs to display
           Application descriptors can come is a couple of forms
           
           * tuple - (label, url, {request parameters})
           * App class - App(label = label, 
                             url = url, 
                             req_params = {request parameters})
           * MokshaApp class - MokshaApp(label = label,
                                         application = moksha app name,
                                         req_params = {request parameters})
    """
    css=[] # remove the default css
    template = 'mako:moksha.api.widgets.containers.templates.tabbedcontainer'
    config_key = None # if set load config
    tabs = ()
            
    def update_params(self, d):
        
        super(TabbedContainer, self).update_params(d)
        
        tabs = eval(config.get(self.config_key, "None"), {"__builtins__":None}, {'MokshaApp': MokshaApp, 
                                                                                 'App': App,
                                                                                 'predicates': predicates})
        if not tabs:
            if isinstance(self.tabs, str):
                tabs = eval(self.tabs, {"__builtins__":None}, {'MokshaApp': MokshaApp,
                                                               'App': App,
                                                               'predicates': predicates})
            else:
                tabs = self.tabs

        # Filter out any None's in the list which signify apps which are
        # not allowed to run with the current session's authorization level
        tabs = filter(lambda x: x, tabs)
        d['tabs'] = tabs
