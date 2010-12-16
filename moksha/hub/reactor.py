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
