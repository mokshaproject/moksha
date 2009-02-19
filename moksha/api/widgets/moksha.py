# This file is part of Moksha.
#
# Moksha is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Moksha is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Moksha.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2008, Red Hat, Inc.
# Authors: John (J5) Palmieri <johnp@redhat.com>
from tw.jquery import jquery_js
from tw.api import JSLink
from tw.api import Widget
import tg
import pylons

moksha_js = JSLink(modname="moksha", filename='public/javascript/moksha.js',
                   javascript=[jquery_js])

class MokshaGlobals(Widget):
    javascript = [moksha_js]
    template = """<script type="text/javascript">
moksha_base_url = "${base_url}";
moksha_csrf_token = "${csrf_token}";
moksha_userid = "${user_id}";
</script>
"""
    params = ['base_url', 'csrf_token', 'user_id']
    engine_name = 'mako'

    base_url = '/'
    csrf_token = ''
    user_id = ''

    def update_params(self, d):
        super(MokshaGlobals, self).update_params(d)
        d['base_url'] = tg.url('/')
        identity = pylons.request.environ.get('repoze.who.identity')

        if identity:
            d['csrf_token'] = identity.get('_csrf_token','')
            d['user_id'] = identity.get('user_id', '')

