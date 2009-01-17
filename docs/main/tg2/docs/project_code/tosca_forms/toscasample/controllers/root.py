"""Main Controller"""
from toscasample.lib.base import BaseController
from tg import expose, flash, require
from pylons.i18n import ugettext as _
from tg import redirect, validate
from toscasample.model import DBSession, metadata
#from dbsprockets.dbmechanic.frameworks.tg2 import DBMechanic
#from dbsprockets.saprovider import SAProvider
from repoze.what import predicates
from toscasample.controllers.secc import Secc
from tw.api import WidgetsList
import pylons
from formencode.validators import Int, NotEmpty, DateConverter, DateValidator
from toscasample.model import Movie

##{MovieForm}

from tw.forms import TableForm, TextField, CalendarDatePicker, SingleSelectField, TextArea
from formencode.validators import Int, NotEmpty, DateConverter, DateValidator

class MovieForm(TableForm):
    # This WidgetsList is just a container
    class fields(WidgetsList):
        title = TextField(validator=NotEmpty)
        year = TextField(size=4, validator=Int(min=1900, max=2100))
        release_date = CalendarDatePicker(validator=DateConverter())
        genrechoices = ((1,"Action & Adventure"),
                         (2,"Animation"),
                         (3,"Comedy"),
                         (4,"Documentary"),
                         (5,"Drama"),
                         (6,"Sci-Fi & Fantasy"))
        genre = SingleSelectField(options=genrechoices)
        description = TextArea(attrs=dict(rows=3, cols=25))

#then, we create an instance of this form
create_movie_form = MovieForm("create_movie_form", action='create')
##

class RootController(BaseController):
    #admin = DBMechanic(SAProvider(metadata), '/admin')
    secc = Secc()

    @expose('toscasample.templates.index')
    def index(self):
        return dict(page='index')

    @expose('toscasample.templates.about')
    def about(self):
        return dict(page='about')

    @expose('toscasample.templates.authentication')
    def auth(self):
        return dict(page='auth')

    @expose('toscasample.templates.index')
    @require(predicates.has_permission('manage'))
    def manage_permission_only(self, **kw):
        return dict(page='managers stuff')

    @expose('toscasample.templates.index')
    @require(predicates.is_user('editor'))
    def editor_user_only(self, **kw):
        return dict(page='editor stuff')

    @expose('toscasample.templates.login')
    def login(self, **kw):
        came_from = kw.get('came_from', '/')
        return dict(page='login', header=lambda *arg: None,
                    footer=lambda *arg: None, came_from=came_from)
    ##{New}
    # we tell expose which template to use to display the form
    @expose("genshi:toscasample.templates.new_form")
    def new(self, **kw):
        """Form to add new record"""
        pylons.c.form = create_movie_form
        return dict(modelname='Movie', page='ToscaTuto')
    ##

    @validate(create_movie_form, error_handler=new)
    @expose()
    def create(self, **kw):
        """A movie and save it to the database"""
        movie = Movie()
        movie.title = kw['title']
        movie.year = kw['year']
        movie.release_date = kw['release_date']
        movie.descrpition = kw['description']
        movie.genre = kw['genre']
        DBSession.add(movie)
        flash("Movie was successfully created.")
        raise redirect("list")

    @expose("genshi:toscasample.templates.movielist")
    def list(self, **kw):
        """a simple list for movies"""
        movies = DBSession.query(Movie)
        return dict(movies=movies, page='Movie list')


