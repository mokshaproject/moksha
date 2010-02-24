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

import tg
import os.path
import paste.fileapp

from pylons.controllers.util import forward
from pylons.middleware import error_document_template, media_path

from moksha.lib.base import BaseController

class ErrorController(BaseController):
    """Generates error documents as and when they are required.

    The ErrorDocuments middleware forwards to ErrorController when error
    related status codes are returned from the application.

    This behaviour can be altered by changing the parameters to the
    ErrorDocuments middleware in your config/middleware.py file.
    """

    @tg.expose('genshi:moksha.templates.error')
    def document(self, *args, **kwargs):
        """Render the error document"""
        resp = tg.request.environ.get('pylons.original_response')
        default_message = ("<p>We're sorry but we weren't able to process "
        " this request.</p>")
        values = dict(prefix=tg.request.environ.get('SCRIPT_NAME', ''),
                 code=tg.request.params.get('code', resp.status_int),
                 message=tg.request.params.get('message', default_message))
        return values
