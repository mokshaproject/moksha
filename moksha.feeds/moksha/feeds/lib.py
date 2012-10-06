from feedcache.cache import Cache
from shove import Shove

import moksha.common.utils

def initialize_feed_storage(config):
    moksha.common.utils.feed_storage = Shove(
        config.get('feed_store', 'simple://'),
        config.get('feed_cache', 'simple://'),
        compress=True)
    moksha.common.utils.feed_cache = Cache(moksha.common.utils.feed_storage)


