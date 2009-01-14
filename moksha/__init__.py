from pylons.i18n import ugettext as _
from paste.registry import StackedObjectProxy
from feed import Feed

# The central feed cache, used by the Feed widget.
feed_cache = StackedObjectProxy()

# All loaded moksha applications
apps = StackedObjectProxy()

# All loaded ToscaWidgets
_widgets = StackedObjectProxy()

# Per-request stomp callbacks registered by rendered widget
stomp = StackedObjectProxy()
