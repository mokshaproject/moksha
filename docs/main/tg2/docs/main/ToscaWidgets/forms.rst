Using ToscaWidgets to create Forms
==================================

Introduction
------------

One of the most useful features of ToscaWidgets is the ability to create forms with requisite validation with a simple declarative syntax.  Using existing form widgets it is relatively easy to add forms to your application to manage your database interactions.

The overall process for creating a form is as follows:

* create widgets for each field in the form.
* create a form widget passing in the field widgets as children.
* if you are creating an edit form, extract the row data from the database.
* call the widget in your template, passing in row data when appropriate.

An :arch:`example project` has been attached so
that people can try this easily.

Tutorial
-------------------

For this tutorial, we will be implementing a form to add a movie to a movie database.


Let's start with a simple SQLAlchemy model that has a Movie object at the bottom of `model/__init__.py`` like this: 

.. code:: tosca_forms/toscasample/model/__init__.py
  :section: BaseModel

Our movie has a smattering of the different standard data types so that we can show off some simple ToscaWidgets form widgets.

To setup your database you should run the following::

    paster setup-app development.ini

this will create the database schema in the database referenced in your config file.

Basic Form
----------

To create a form for the model add the following code in your root.py, for now you can ignore the validator code, and you can even skip it if you want:

.. code:: tosca_forms/toscasample/controllers/root.py
  :section: MovieForm

In ToscaWidgets, every widget can have child widgets. This is particularly useful for forms, which are generally made up of form filed widgets. 

You can simply add nested classes which become children of the parrent widget. 

Then those child classes will be instantiated and appended to the widget.  In this case, we're adding some fields in a WidgetList to the FormTable widget.

Form Template
-------------
Create a new template in your templates directory, lets call it new_form.html.  Here is what the Genshi template should look like.

.. highlight:: html+genshi
.. code:: tosca_forms/toscasample/templates/new_form.html


The Controller
--------------

To show your form on the screen, we need to add a new controller method that looks like the following

.. highlight:: python

.. code:: tosca_forms/toscasample/controllers/root.py
  :section: New

Run the application, surf to `http://localhost:8080/new/ <http://localhost:8080/new/>`_ You will see a form that looks like this:


.. image:: http://docs.turbogears.org/2.0/RoughDocs/ToscaWidgets/Forms?action=AttachFile&do=get&target=movie_form.png

Advanced Exercise
-----------------

Suppose we wanted to change the 'genre' options on the fly, for example look them up from a DB; you could return this info from the controller (not sure if this should be in form dict?):

::

        ...
        genreOptions = [(rec.id, rec.name) for rec in ImaginaryGeneraModel.query.all()]
        return dict(genreOptions=genreOptions, modelname='Movie')

Then in the template:

::

    ${tmpl_context.form(child_args={'genre': {'options': genreOptions}})}

This is left as an exercise for the reader.


Do More With Forms
------------------

Now, lets take a look at what we can do to customize the form to our liking.  

Field Attributes
~~~~~~~~~~~~~~~~

Each field has a set of attributes which we can change to suit our needs.  For example, perhaps you are not satisfied with the text area which is the default in twForms.  You can change the attributes of the text area simply by passing in a dictionary of attributes to the 'attr' parameter in the field definition.  The code to do this looks something like the following:

::

  description = TextArea(attrs={'rows':3, 'columns':25})

resulting in a field that looks like this:

.. image:: http://docs.turbogears.org/2.0/RoughDocs/ToscaWidgets/Forms?action=AttachFile&do=get&target=text_area.png

Another problem with this form is that if you are using sqlite, the date is in the wrong format.  Lets give the CalendarDatePicker a date_format argument, and then our form will be viable.

::

  release_date = CalendarDatePicker(date_format='%y-%m-%d')

And now our date field has dashes in it instead of slashes:


.. image:: http://docs.turbogears.org/2.0/RoughDocs/ToscaWidgets/Forms?action=AttachFile&do=get&target=date_picker.png


Fields and forms also have a set of shared arguments which you can use to change the display properties.  Here is a table of arguments and how they affect the widgets:

+-----------------+--------------------------------------------------------------------------------+
| *Name*          | *behavior*                                                                     |
+-----------------+--------------------------------------------------------------------------------+
| css_class       | change the class associated with the widget so you can customize look and feel.|
+-----------------+--------------------------------------------------------------------------------+
| *Field Specific parameters*                                                                      |
+-----------------+--------------------------------------------------------------------------------+
| disabled        | the field is shown but not editable                                            |
+-----------------+--------------------------------------------------------------------------------+
| show_error      | should the field show it's error (default is true)                             |
+-----------------+--------------------------------------------------------------------------------+
| label_text      | change the appearance of the text to the left of the field.                    |
+-----------------+--------------------------------------------------------------------------------+
| help_text       | change the tooltips text that appears when the user mouses over your field.    |
+-----------------+--------------------------------------------------------------------------------+
| *Form Specific parameters*                                                                       |
+-----------------+--------------------------------------------------------------------------------+
| submit_text     | change the words that appear on the submit button.                             |
+-----------------+--------------------------------------------------------------------------------+

Sometimes a developer desires to customize the form template to display the form in a certain manner (for instance, if you want two columns of entries)

Form Fields
~~~~~~~~~~~
Here is a quick and dirty list of all form fields that you can use:

TODO: each of these should link to an anchor in another page of form fields.

* BooleanRadioButtonList
* Button
* CalendarDatePicker
* CalendarDateTimePicker
* CheckBox
* CheckBoxList
* CheckBoxTable
* ContainerMixin
* FileField
* HiddenField
* ImageButton
* MultipleSelectField
* PasswordField
* RadioButton
* RadioButtonList
* ResetButton
* SecureTicketField
* SelectionField
* SelectionList
* SingleSelectField
* SingleSelectionMixin
* SubmitButton
* TextArea
* TextField

Form Validation
--------------------
Form validation is a very powerful way to make sure that the data which your user's enter is formatted in a predictable manner long before database interaction happens.  When data entered in to a form does not match that which is required, the user should be redirected back to the form to re-enter their data.  A message indicating the problem should be displayed for all fields which are in error at the same time.  ToscaWidgets take advantage of the work done in FormEncode to do it's validation.  See the docs at  `FormEncode <http://www.formencode.org/>`_ for more information. 

The first thing we need to do is add a validator to each of the fields which we would like validated.  Each InputWidget takes a validator argument.  The form itself is then passed into a method decorator which checks to see if the data coming in from the client matches validates against the validator defined in the widget.  Our new form looks something like this:

::

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

Note that we removed the date format from the CalendarDatePicker. This is
because the DateConverter will take whatever date is entered in the box
and convert it to a datetime object, which is much better understood by the orm
than a date string.

Our controller gets a new validator decorator for the creation of the
movie entry. Don't forget to uncomment the lines::

    from tg import redirect, validate
    from toscasample.model import DBSession, metadata


and to add this new line to the import section::

    from toscasample.model import Movie

    
in the same file or you'll get errors.

::

    @validate(create_movie_form, error_handler=new)
    @expose()
    def create(self, **kw):
        """A movie and save it to the database"""
        movie = Movie()
        movie.title = kw['title']
        movie.year = kw['year']
        movie.release_date = kw['release_date']
        movie.description = kw['description']
        movie.genre = kw['genre']
        DBSession.add(movie)
        flash("Movie was successfully created.")
        raise redirect("list")



And the resulting form on a bad entry will give you a output like this:

.. image:: http://docs.turbogears.org/2.0/RoughDocs/ToscaWidgets/Forms?action=AttachFile&do=get&target=validators.png


In short, there are many things you can do with validators, but that the above example gives you a basic understanding of how validators can be used to check user input.

The handler to display your movie list should look something like this::

    @expose("genshi:toscasample.templates.movielist")
    def list(self, **kw):
        """a simple list for movies"""
        movies = DBSession.query(Movie)
        return dict(movies=movies, page='Movie list')

and you should also have a template named movielist.html in your templates dir
which should contain this::

    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml"
          xmlns:py="http://genshi.edgewall.org/"
          xmlns:xi="http://www.w3.org/2001/XInclude">

    <!-- This line is important, since it will automatically handle including any required resources in the head -->
    <xi:include href="master.html" />

    <head>
      <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
      <title>Movie List</title>
    </head>

    <body>
    <h1>Movie List</h1>

        <ol>
          <li py:for="movie in movies">${movie.title}, ${movie.year}</li>
        </ol>

    <a href="${tg.url('/new')}">Add a Movie</a>
    </body>
    </html>



Available Validators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Attribute
* Bool
* CIDR
* ConfirmType
* Constant
* CreditCardExpires
* CreditCardSecurityCode
* CreditCardValidator
* DateConverter
* DateTime
* DateValidator
* DictConverter
* Email
* Empty
* False
* FancyValidator
* FieldStorageUploadConverter
* FieldsMatch
* FileUploadKeeper
* FormValidator
* IDeclarative
* IPhoneNumberValidator
* ISchema
* IValidator
* Identity
* IndexListConverter
* Int
* Interface
* Invalid
* MACAddress
* MaxLength
* MinLength
* NoDefault
* NotEmpty
* Number
* OneOf
* PhoneNumber
* PlainText
* PostalCode
* Regex
* RequireIfMissing
* RequireIfPresent
* Set
* SignedString
* StateProvince
* String
* StringBool
* StringBoolean
* StripField
* TimeConverter
* True
* URL
* UnicodeString
* Validator
* Wrapper
