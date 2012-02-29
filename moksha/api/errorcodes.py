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
