"""Main Controller"""
from moksha.lib.base import BaseController
from tg import expose, flash, require
from pylons.i18n import ugettext as _
#from tg import redirect, validate
#from moksha.model import DBSession, metadata
#from dbsprockets.dbmechanic.frameworks.tg2 import DBMechanic
#from dbsprockets.saprovider import SAProvider
from repoze.what import predicates
from moksha.controllers.secc import Secc

class RootController(BaseController):
    #admin = DBMechanic(SAProvider(metadata), '/admin')
    secc = Secc()

    @expose('moksha.templates.index')
    def index(self):
        return dict(page='index')

    @expose('moksha.templates.about')
    def about(self):
        return dict(page='about')

    @expose('moksha.templates.index')
    @require(predicates.has_permission('manage'))
    def manage_permission_only(self, **kw):
        return dict(page='managers stuff')

    @expose('moksha.templates.index')
    @require(predicates.is_user('editor'))
    def editor_user_only(self, **kw):
        return dict(page='editor stuff')

    @expose('moksha.templates.login')
    def login(self, **kw):
        came_from = kw.get('came_from', '/')
        return dict(page='login', header=lambda *arg: None,
                    footer=lambda *arg: None, came_from=came_from)
