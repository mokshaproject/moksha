"""Main Controller"""
from wiki20.lib.base import BaseController
from tg import expose, flash
from pylons.i18n import ugettext as _
import tg
from tg import redirect, validate
from wiki20.model import DBSession
from wiki20.model.page import Page
import re
from docutils.core import publish_parts
from sqlalchemy.exceptions import InvalidRequestError ######################

wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

class RootController(BaseController):

    @expose('wiki20.templates.page')
    def default(self, pagename="FrontPage"):
        try:
            page = DBSession.query(Page).filter_by(pagename=pagename).one()
        except InvalidRequestError:
            raise tg.redirect("notfound", pagename = pagename)
        content = publish_parts(page.data, writer_name="html")['html_body']
        root = tg.url('/')
        content = wikiwords.sub(r'<a href="%s\1">\1</a>' % root, content)
        return dict(content=content, page=page)

    @expose("wiki20.templates.edit")
    def notfound(self, pagename):
        page = Page(pagename=pagename, data="")
        DBSession.save(page)
        DBSession.commit()
        return dict(page=page)

    @expose(template="wiki20.templates.edit")
    def edit(self, pagename):
        page = DBSession.query(Page).filter_by(pagename=pagename).one()
        return dict(page=page)

    @expose()
    def save(self, pagename, data, submit):
        page = DBSession.query(Page).filter_by(pagename=pagename).one()
        page.data = data
        DBSession.commit() # Tells database to commit changes permanently
        redirect("/"+pagename)

    @expose("wiki20.templates.pagelist")
    def pagelist(self):
        pages = [page.pagename for page in DBSession.query(Page)]
        return dict(pages=pages)
