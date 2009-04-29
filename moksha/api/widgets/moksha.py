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
#
# Authors: John (J5) Palmieri <johnp@redhat.com>

import tg
import pylons

from tw.api import JSLink
from tw.api import Widget
from tw.jquery import jquery_js
from paste.deploy.converters import asbool

moksha_js = JSLink(modname="moksha", filename='public/javascript/moksha.js',
                   javascript=[jquery_js])
moksha_extension_points_js = JSLink(modname="moksha",
                                    filename='public/javascript/moksha.extensions.js',
                                    javascript=[moksha_js])

class MokshaGlobals(Widget):
    javascript = [moksha_js]
    template = """<script type="text/javascript">
moksha_base_url = "${base_url}";
moksha_csrf_token = "${csrf_token}";
moksha_userid = "${user_id}";
moksha_debug = ${debug};
moksha_profile = ${profile};
</script>
"""
    params = ['base_url', 'csrf_token', 'user_id', 'debug', 'profile']
    engine_name = 'mako'

    base_url = '/'
    csrf_token = ''
    user_id = ''
    debug = 'false'
    profile = 'false'

    def __init__(self, *args, **kw):
        super(MokshaGlobals, self).__init__(*args, **kw)
        self.csrf_token_id = tg.config.get('moksha.csrf.token_id', '_csrf_token')
        if asbool(tg.config.get('moksha.extensionpoints', False)):
            self.javascript.append(moksha_extension_points_js)

    def update_params(self, d):
        super(MokshaGlobals, self).update_params(d)

        d['base_url'] = tg.url('/')

        if asbool(pylons.config.get('debug')):
            d['debug'] = 'true'
        if asbool(pylons.config['global_conf'].get('profile')):
            d['profile'] = 'true'

        identity = pylons.request.environ.get('repoze.who.identity')
        if identity:
            d['csrf_token'] = identity.get(self.csrf_token_id, '')
            d['user_id'] = identity.get('user_id', '')
