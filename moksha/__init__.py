from pylons.i18n import ugettext as _
from paste.registry import StackedObjectProxy

# The central feed cache, used by the Feed widget.
feed_cache = None

# A dict-like persistent backing store
feed_storage = None

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
    """ Get a widget instance by name """
    return _widgets[name]['widget']

def shutdown():
    """ Called when Moksha shuts down """
    if feed_storage:
        feed_storage.close()
