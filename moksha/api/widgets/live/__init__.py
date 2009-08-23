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

from live import LiveWidget

# At the moment we're using the StompWidget as our primary publish/subscribe
# messaging standard.  If we want to change the default to an AMQP widget
# down the road, we would change it here so we have a consistent API to
# develop against.
from moksha.api.widgets.stomp import stomp_widget
moksha_socket = stomp_widget
