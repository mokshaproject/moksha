from feed import Feed
from paste.registry import StackedObjectProxy

# The central feed cache, used by the Feed widget.
feed_cache = StackedObjectProxy()

# All loaded moksha applications
apps = StackedObjectProxy()
