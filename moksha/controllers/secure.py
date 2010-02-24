# -*- coding: utf-8 -*-
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

"""Sample controller with all its actions protected."""
from tg import expose, flash, redirect, validate, tmpl_context
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what.predicates import has_permission

import moksha
from moksha.lib.base import BaseController
#from moksha.model import DBSession, metadata

__all__ = ['SecureController']


class SecureController(BaseController):
    """Sample controller-wide authorization"""

    # The predicate that must be met for all the actions in this controller:
    allow_only = has_permission('manage',
                                msg=l_('Only for people with the "manage" permission'))

    @expose('moksha.templates.index')
    def index(self):
        """Let the user know that's visiting a protected controller."""
        flash(_("Secure Controller here"))
        if 'default_menu' in moksha.menus:
            tmpl_context.menu_widget = moksha.menus['default_menu']
        else:
            tmpl_context.menu_widget = lambda: ''
        return dict(title='Moksha Administrator Controller')

    @expose('moksha.templates.index')
    def some_where(self):
        """Let the user know that this action is protected too."""
        return dict(page='some_where')
