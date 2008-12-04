"""Main Controller"""
from mokshaplugin.lib.base import BaseController
from tg import expose, flash, require, tmpl_context
from pylons.i18n import ugettext as _

from moksha.widgets.layout import LayoutWidget
layout_widget = LayoutWidget('layout')

from myfedora.widgets.feed import Feed

class ObamaFeed(Feed):
    url = 'http://www.theobamafeed.com/feed'

class RootController(BaseController):

    @expose('genshi:mokshaplugin.templates.index')
    def default(self, *args, **kw):
        print "mokshaplugin.default(%s, %s)" % (args, kw)
        return dict(page='foo')

    @expose('mako:mokshaplugin.templates.mako')
    def foo(self, *args, **kw):
        print "FOO!"
        tmpl_context.layout = layout_widget
        return dict()
