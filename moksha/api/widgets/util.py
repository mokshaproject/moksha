from tw.api import Widget
from pylons import tmpl_context

class ContextAwareWidget(Widget):
    '''Inherit from this widget class if you want your widget
       to automatically get the pylons.tmpl_context in its dictionary
    '''
     
    def update_params(self, d):
        super(ContextAwareWidget, self).update_params(d)
         
        d['tmpl_context'] = tmpl_context