# This file is part of Moksha.
# Copyright (C) 2008-2009  Red Hat, Inc.
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

"""
Here is where we configure which AMQP hub implementation we are going to use.
"""
import logging
log = logging.getLogger(__name__)

try:
    from qpid010 import QpidAMQPHub
    AMQPHub = QpidAMQPHub
except ImportError:
    log.debug("Unable to import qpid module")
    class FakeHub(object):
        pass
    AMQPHub = FakeHub

#from pyamqplib import AMQPLibHub
#AMQPHub = AMQPLibHub
