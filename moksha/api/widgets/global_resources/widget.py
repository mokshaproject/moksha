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

import logging
import pkg_resources

from tg import config, url
from tw.api import Widget, CSSLink, JSLink
from tw.jquery import jquery_js
from paste.deploy.converters import asbool
from pylons import request
from inspect import isclass

log = logging.getLogger(__name__)

moksha_js = JSLink(modname="moksha", filename='public/javascript/moksha.js',
                   javascript=[jquery_js])
moksha_extension_points_js = JSLink(modname="moksha", javascript=[moksha_js],
        filename='public/javascript/moksha.extensions.js')


class GlobalResourceInjectionWidget(Widget):
    """
    This widget will pull in all JSLink, CSSLink, and Widget resources that
    are listed on the `[moksha.global]` entry-point.

    :Note: Global Widget injection will only work when the global_resource
           widget is actually rendered in the template.  Otherwise, only JS
           and CSS resources will get injected.  Moksha's index.mak template
           handles this for us, otherwise you can import the `global_resources`
           widget from this module and do it yourself.
    """
    javascript = [moksha_js]
    children = []
    css = []
    template = """
        % for child in c:
            ${child()}
        % endfor
        <script type="text/javascript">
          moksha_base_url = "${base_url}";
          moksha_csrf_token = "${csrf_token}";
          moksha_csrf_trusted_domains = ${csrf_trusted_domains};
          moksha_userid = "${user_id}";
          moksha_debug = ${debug};
          moksha_profile = ${profile};
        </script>
        """
    engine_name = 'mako'

    params = ['base_url', 'csrf_token', 'user_id', 'debug', 'profile', 'csrf_trusted_domains']
    base_url = '/'
    csrf_token = ''
    user_id = ''
    debug = 'false'
    profile = 'false'

    def __init__(self):
        super(GlobalResourceInjectionWidget, self).__init__()
        for widget_entry in pkg_resources.iter_entry_points('moksha.global'):
            log.info('Loading global resource: %s' % widget_entry.name)
            loaded = widget_entry.load()
            if isclass(loaded):
                loaded = loaded(widget_entry.name)
            if isinstance(loaded, JSLink):
                self.javascript.append(loaded)
            elif isinstance(loaded, CSSLink):
                self.css.append(loaded)
            elif isinstance(loaded, Widget):
                if loaded in self.children:
                    log.debug("Skipping duplicate global widget: %s" %
                              widget_entry.name)
                else:
                    self.children.append(loaded)
            else:
                raise Exception("Unknown global resource: %s.  Should be "
                                "either a JSLink or CSSLink." %
                                widget_entry.name)

        self.csrf_token_id = config.get('moksha.csrf.token_id', '_csrf_token')
        if asbool(config.get('moksha.extensionpoints', False)):
            self.javascript.append(moksha_extension_points_js)

    def update_params(self, d):
        super(GlobalResourceInjectionWidget, self).update_params(d)

        d['base_url'] = url('/')

        if asbool(config.get('debug')):
            d['debug'] = 'true'
        if asbool(config['global_conf'].get('profile')):
            d['profile'] = 'true'

        d['csrf_trusted_domains'] = config.get('moksha.csrf.trusted_domains', '').split(',')

        identity = request.environ.get('repoze.who.identity')
        if identity:
            d['csrf_token'] = identity.get(self.csrf_token_id, '')
            d['user_id'] = identity.get('user_id', '')

global_resources = GlobalResourceInjectionWidget()
