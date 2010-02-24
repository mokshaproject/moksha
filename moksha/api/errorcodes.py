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

from paste.response import replace_header
from moksha.lib.helpers import CategoryEnum

class ErrEnum(CategoryEnum):
    def attr_to_message(self, attr):
        return self.attr_to_data(attr)

    def get_message(self, attr):
        return self.get_data(attr)

login_err = ErrEnum ('login_err',
                     ('USERNAME_PASSWORD_ERROR',
                      ('The username or password you entered is not valid. Please '
                       'try again.')
                     ),
                     ('UNKNOWN_AUTH_ERROR',
                      ('An unknown error occurred while trying to log you in. '
                       'Please try again later or notify an admin if the problem '
                       'persists')
                     )
                    )
