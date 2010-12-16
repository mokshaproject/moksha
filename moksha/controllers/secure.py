# -*- coding: utf-8 -*-
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
