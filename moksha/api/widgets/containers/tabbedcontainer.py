from tw.jquery.ui_tabs import JQueryUITabs
from pylons import config
import urllib

def App(label="", url="", auth_levels=[], req_params={}):
    # FIXME implement authentication checking
    #       and enhance load to be able to do PUSH instead of GET
    return (label, url + "?" + urllib.urlencode(req_params))    

def MokshaApp(label="", moksha_app="", req_params={}):
    # FIXME figure out how to pull auth info from an app
    return App(label, '/appz/' + moksha_app, req_params)

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
        
        tabs = eval(config.get(self.config_key, "None"), {"__builtins__":None}, {'MokshaApp': MokshaApp, 'App': App})
        if not tabs:
            tabs = self.tabs

        d['tabs'] = tabs
