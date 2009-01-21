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
# Authors: Luke Macken <lmacken@redhat.com>

"""Moksha Administration Controller"""

from tg import expose, flash
from pylons.i18n import ugettext as _
from repoze.what.predicates import has_permission
from moksha.model import DBSession, metadata
from moksha.lib.base import BaseController

class AdminController(BaseController):

    # The predicate that must be met for all the actions in this controller:
    allow_only = has_permission('manage',
            msg=_('Only for people with the "manage" permission'))

    @expose('moksha.templates.index')
    def index(self):
        flash(_("Secure Controller here"))
        return dict(page='index')

    @expose('moksha.templates.index')
    def some_where(self):
        """should be protected because of the require attr
        at the controller level.
        """
        return dict()
