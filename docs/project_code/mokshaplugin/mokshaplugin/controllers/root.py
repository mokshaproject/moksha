"""Main Controller"""
from tg import expose, flash, require, tmpl_context, config
from moksha import _, Feed
from moksha.layout import LayoutWidget
from mokshaplugin.lib.base import BaseController

layout_widget = LayoutWidget('layout')

class ObamaFeed(Feed):
    """ The Obama Feed Widget.

    This widget resides on the ``moksha.widget`` entry point, and is
    automatically rendered by the moksha layout engine.
    """
    url = 'http://www.theobamafeed.com/feed'

class RootController(BaseController):

    @expose('genshi:mokshaplugin.templates.index')
    def default(self, *args, **kw):
        print "mokshaplugin.default(%s, %s)" % (args, kw)
        return dict(page='foo')

    @expose('mako:mokshaplugin.templates.mako')
    def foo(self, *args, **kw):
        tmpl_context.layout = layout_widget
        return dict()
