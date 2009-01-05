import moksha

from tg import expose, flash, require, tmpl_context, redirect, validate
from repoze.what import predicates
from moksha.controllers.secc import AdminController
from moksha.lib.base import BaseController
from moksha.layout import LayoutWidget
from moksha.model import DBSession
from moksha import _

## Widgets
layout_widget = LayoutWidget('layout')

from moksha.examples.livegraph import LiveGraphWidget
live_graph = LiveGraphWidget('livegraph')

from moksha.examples.livegraph import LiveFlotWidget
live_flot = LiveFlotWidget('liveflot')

class RootController(BaseController):

    admin = AdminController()

    @expose('moksha.templates.widget')
    def index(self):
        tmpl_context.widget = layout_widget
        return dict()

    @expose('moksha.templates.widget')
    def widget(self, name):
        """ Display a widget by name """
        tmpl_context.widget = moksha.widgets[name]
        return dict()

    @expose('moksha.templates.widget')
    def stomp(self):
        #tmpl_context.widget = live_graph
        tmpl_context.widget = live_flot
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
