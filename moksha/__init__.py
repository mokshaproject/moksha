from pylons.i18n import ugettext as _
from paste.registry import StackedObjectProxy

# The central feed cache, used by the Feed widget.
feed_cache = None

# All loaded moksha applications
apps = None

# All WSGI applications
wsgiapps = None

# All loaded ToscaWidgets
_widgets = None

# All loaded moksha menus
menus = None

# Per-request stomp callbacks registered by rendered widget
stomp = StackedObjectProxy()

def get_widget(name):
    """ Get a widget by name.

    This method returns a dictionary in the following format:

        { 'name': 'widgetname',
          'widget': <Widget instance>,
          'path': '/path/to/widget' }
    """
    return _widgets[name]['widget']
