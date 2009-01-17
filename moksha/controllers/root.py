import moksha

from tg import expose, flash, require, tmpl_context, redirect, validate
from repoze.what import predicates

from moksha import _
from moksha.model import DBSession
from moksha.lib.base import BaseController
from moksha.controllers.secc import AdminController
from moksha.api.widgets.layout import LayoutWidget

layout_widget = LayoutWidget('layout')

class RootController(BaseController):

    admin = AdminController()

    @expose('moksha.templates.widget')
    def index(self):
        tmpl_context.widget = layout_widget
        return dict()

    @expose('moksha.templates.widget')
    def widget(self, name):
        """ Display a widget by name """
        tmpl_context.widget = moksha.get_widget(name)
        return dict()

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
