"""The application's Globals object"""

import logging

from tg import config
from shove import Shove

from moksha.exc import CacheBackendException
from moksha.lib.cache import Cache


log = logging.getLogger(__name__)

class Globals(object):
    """Globals acts as a container for objects available throughout the
    life of the application
    """

    def __init__(self):
        """One instance of Globals is created during application
        initialization and is available during requests via the 'g'
        variable
        """
        timeout = int(config.get('beaker.cache.timeout', '0'))
        try:
            self.cache = Cache(config['beaker.cache.url'], timeout)
        except CacheBackendException, e:
            log.warning(str(e))
            self.cache = None
