# -*- coding: utf-8 -*-
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
        tmpl_context.menu_widget = moksha.menus['default_menu']
        return dict(title='Moksha Administrator Controller')

    @expose('moksha.templates.index')
    def some_where(self):
        """Let the user know that this action is protected too."""
        return dict(page='some_where')
