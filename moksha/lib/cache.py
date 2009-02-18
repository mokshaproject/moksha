import logging
log = logging.getLogger(__name__)

from moksha.exc import CacheBackendException

class Cache(object): 
    """ A memcached-specific caching interface """

    def __init__(self, url, timeout=None, prefix=None):
        self.create_memcached_cache()

    def create_memcached_cache(self):
        try:
            import memcache
        except ImportError:
            log.warning('Cannot import the `memcache` module.  Install the '
                        'python-memcached package to enable Mokshas memcached '
                        'integration.')
            return
        self.mc = memcache.Client([url])
        self.timeout = timeout or 300
        self.prefix = prefix
        if not self.mc.set('x', 'x', 1):
            raise CacheBackendException("Cannot connect to Memcached")

    def get(self, key):
        return self.mc.get(key) 

    def set(self, key, value, timeout=None):
        if self.prefix:
            key = self.prefix + key
        self.mc.set(key, value, timeout or self.timeout)
