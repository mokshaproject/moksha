# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
