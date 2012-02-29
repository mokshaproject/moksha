# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
log = logging.getLogger(__name__)

from moksha.exc import CacheBackendException

class Cache(object):
    """ A memcached-specific caching interface """

    def __init__(self, url, timeout=None, prefix=None):
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
