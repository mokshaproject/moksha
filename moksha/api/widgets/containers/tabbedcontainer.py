from tw.jquery.ui_tabs import JQueryUITabs
from pylons import config, request
from repoze.what import predicates
from moksha.lib.helpers import eval_app_config

import urllib

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
        
        tabs = eval_app_config(config.get(self.config_key, "None"))
        if not tabs:
            if isinstance(self.tabs, str):
                tabs = eval_app_config(self.tabs)
            else:
                tabs = self.tabs

        # Filter out any None's in the list which signify apps which are
        # not allowed to run with the current session's authorization level
        tabs = filter(lambda x: x, tabs)
        d['tabs'] = tabs
