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
#
# Authors: Luke Macken <lmacken@redhat.com>

"""
Choses the best platform-specific Twisted reactor
"""

import sys

try:
    if 'linux' in sys.platform:
        from twisted.internet import epollreactor
        epollreactor.install()
    elif 'freebsd' in sys.platform or 'darwin' in sys.platform:
        from twisted.internet import kqreactor
        kqreactor.install()
    elif 'win' in sys.platform:
        from twisted.internet import iocpreactor
        iocpreactor.install()
except (ImportError, AssertionError): # reactor already installed
    pass

from twisted.internet import reactor
