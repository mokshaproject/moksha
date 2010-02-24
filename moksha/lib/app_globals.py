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

"""The application's Globals object"""

#import logging
#import inspect

#from tg import config
#from shove import Shove

#from moksha.exc import CacheBackendException
#from moksha.lib.cache import Cache

#log = logging.getLogger('moksha')

class Globals(object):
    """Globals acts as a container for objects available throughout the
    life of the application
    """

    def __init__(self):
        """One instance of Globals is created during application
        initialization and is available during requests via the 'g'
        variable
        """
        #timeout = int(config.get('beaker.cache.timeout', '0'))
        #try:
        #    self.cache = Cache(config['beaker.cache.url'], timeout)
        #except (CacheBackendException, KeyError), e:
        #    log.warning(str(e))
        #    self.cache = None
