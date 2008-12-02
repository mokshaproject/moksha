Customizing authentication and authorization
============================================

.. module:: repoze.what.plugins.quickstart
    :synopsis: Configuring the repoze.what quickstart

:Status: Official

Here you will learn how to customize the way TurboGears configures
:mod:`repoze.what` (and thus :mod:`repoze.who` indirectly) for you, using the
:mod:`repoze.what` SQL plugin. This is all done from
``{yourproject}.config.app_cfg``.


Customizing authentication settings
-----------------------------------

It's very easy for you to customize authentication and identification settings
in :mod:`repoze.who` from ``{yourproject}.config.app_cfg.sa_auth``. The 
available directives are all optional:

* ``form_plugin``: An instance of your custom :mod:`repoze.who` challenger.
* ``form_identifies`` (bool): Whether your custom challenger should also be
  used as an identifier (e.g., an instance of 
  :mod:`repoze.who.plugins.form.RedirectingFormPlugin`).
* ``identifiers``: Set of secondary :mod:`repoze.who` identifiers.
* ``authenticators``: Set of secondary :mod:`repoze.who` authenticators.
* ``challengers``: Set of secondary :mod:`repoze.who` challengers.
* ``mdproviders``: Set of secondary :mod:`repoze.who` metadata providers.

Customizing the model structure assumed by the quickstart
---------------------------------------------------------

Your auth-related model doesn't `have to` be like the default one, where the
class for your users, groups and permissions are, respectively, ``User``,
``Group`` and ``Permission``, and your users' user name is available in
``User.user_name``. What if you prefer ``Member`` and ``Team`` instead of
``User`` and ``Group``, respectively? Or what if you prefer ``Group.members``
instead of ``Group.users``? Read on!

Changing class names
~~~~~~~~~~~~~~~~~~~~

Changing the name of an auth-related class (``User``, ``Group`` or ``Permission``)
is a rather simple task. Just rename it in your model, and then make sure to
update ``{yourproject}.config.app_cfg`` accordingly.

For example, if you renamed ``User`` to ``Member``, ``{yourproject}.config.app_cfg``
should look like this::

    # ...
    from yourproject import model
    # ...
    base_config.sa_auth.user_class = model.Member
    # ...

Changing attribute names
~~~~~~~~~~~~~~~~~~~~~~~~

You can also change the name of the attributes assumed by
:mod:`repoze.what` in your auth-related classes, such as renaming
``User.groups`` by ``User.memberships``.

Changing such values is what :mod:`repoze.what` calls "translating".
You may set the translations for the attributes of the models
:mod:`repoze.what` deals with in ``{yourproject}.config.app_cfg``. For
example, if you want to replace ``Group.users`` by ``Group.members``, you may
set the following translation in that file::

    base_config.sa_auth.translations.users = 'members'

These are the translations you may set in ``base_config.sa_auth.translations``:
    * ``user_name``: The translation for the attribute in ``User.user_name``.
    * ``users``: The translation for the attribute in ``Group.users``.
    * ``group_name``: The translation for the attribute in ``Group.group_name``.
    * ``groups``: The translation for the attribute in ``User.groups`` and
      ``Permission.groups``.
    * ``permission_name``: The translation for the attribute in
      ``Permission.permission_name``.
    * ``permissions``: The translation for the attribute in ``User.permissions``
      and ``Group.permissions``.
    * ``validate_password``: The translation for the method in
      ``User.validate_password``.


.. _implementing:

Enabling the quickstart in an existing project
----------------------------------------------

To enable authentication and authorization via :mod:`repoze.what`'s
quickstart, you should follow the instructions described in this section:

    #. Go to ``{yourproject}.config.app_cfg`` and define the following settings:
        * ``base_config.auth_backend``: The name of the 
          authentication/authorization backend. Set it to "sqlalchemy".
        * ``base_config.sa_auth.dbsession``: Your model's SQLAlchemy session.
        * ``base_config.sa_auth.user_class``: Your user class.
        * ``base_config.sa_auth.group_class``: Your group class.
        * ``base_config.sa_auth.permission_class``: Your permission class.
       
       It may look like this::
           
           # ...
           from yourproject import model
           # ...
           base_config.auth_backend = 'sqlalchemy'
           base_config.sa_auth.dbsession = model.DBSession
           base_config.sa_auth.user_class = model.User
           base_config.sa_auth.group_class = model.Group
           base_config.sa_auth.permission_class = model.Permission
           # ...

    #. Now define your auth-related data model in, say, 
       ``{yourproject}.model.auth``, with at least the definitions below (you
       may add more columns if you want)::
        
        import md5
        import sha
        from datetime import datetime
        
        from tg import config
        from sqlalchemy import Table, ForeignKey, Column
        from sqlalchemy.types import String, Unicode, UnicodeText, Integer, DateTime, \
                                     Boolean, Float
        from sqlalchemy.orm import relation, backref, synonym
        
        from yourproject.model import DeclarativeBase, metadata, DBSession
        
        
        # This is the association table for the many-to-many relationship between
        # groups and permissions.
        group_permission_table = Table('tg_group_permission', metadata,
            Column('group_id', Integer, ForeignKey('tg_group.group_id',
                onupdate="CASCADE", ondelete="CASCADE")),
            Column('permission_id', Integer, ForeignKey('tg_permission.permission_id',
                onupdate="CASCADE", ondelete="CASCADE"))
        )
        
        # This is the association table for the many-to-many relationship between
        # groups and members - this is, the memberships.
        user_group_table = Table('tg_user_group', metadata,
            Column('user_id', Integer, ForeignKey('tg_user.user_id',
                onupdate="CASCADE", ondelete="CASCADE")),
            Column('group_id', Integer, ForeignKey('tg_group.group_id',
                onupdate="CASCADE", ondelete="CASCADE"))
        )
        
        # auth model
        
        class Group(DeclarativeBase):
            """An ultra-simple group definition.
            """
            __tablename__ = 'tg_group'
        
            group_id = Column(Integer, autoincrement=True, primary_key=True)
        
            group_name = Column(Unicode(16), unique=True)
        
            display_name = Column(Unicode(255))
        
            created = Column(DateTime, default=datetime.now)
        
            users = relation('User', secondary=user_group_table, backref='groups')
        
            def __repr__(self):
                return '<Group: name=%s>' % self.group_name
        
        
        class User(DeclarativeBase):
            """Reasonably basic User definition. Probably would want additional
            attributes.
            """
            __tablename__ = 'tg_user'
        
            user_id = Column(Integer, autoincrement=True, primary_key=True)
        
            user_name = Column(Unicode(16), unique=True)
        
            email_address = Column(Unicode(255), unique=True)
        
            display_name = Column(Unicode(255))
        
            _password = Column('password', Unicode(40))
        
            created = Column(DateTime, default=datetime.now)
        
            def __repr__(self):
                return '<User: email="%s", display name="%s">' % (
                        self.email_address, self.display_name)
        
            @property
            def permissions(self):
                perms = set()
                for g in self.groups:
                    perms = perms | set(g.permissions)
                return perms
        
            def _set_password(self, password):
                """encrypts password on the fly using the encryption
                algo defined in the configuration
                """
                algorithm = self.get_encryption_method()
                self._password = self.__encrypt_password(algorithm, password)
        
            def _get_password(self):
                """returns password
                """
                return self._password
        
            password = synonym('password', descriptor=property(_get_password,
                                                               _set_password))
        
            def __encrypt_password(self, algorithm, password):
                """Hash the given password with the specified algorithm. Valid values
                for algorithm are 'md5' and 'sha1'. All other algorithm values will
                be essentially a no-op."""
                hashed_password = password
        
                if isinstance(password, unicode):
                    password_8bit = password.encode('UTF-8')
        
                else:
                    password_8bit = password
        
                if "md5" == algorithm:
                    hashed_password = md5.new(password_8bit).hexdigest()
        
                elif "sha1" == algorithm:
                    hashed_password = sha.new(password_8bit).hexdigest()
        
                # TODO: re-add the possibility to provide own hasing algo
                # here... just get the real config...
        
                #elif "custom" == algorithm:
                #    custom_encryption_path = turbogears.config.get(
                #        "auth.custom_encryption", None )
                #
                #    if custom_encryption_path:
                #        custom_encryption = turbogears.util.load_class(
                #            custom_encryption_path)
        
                #    if custom_encryption:
                #        hashed_password = custom_encryption(password_8bit)
        
                # make sure the hased password is an UTF-8 object at the end of the
                # process because SQLAlchemy _wants_ a unicode object for Unicode columns
                if not isinstance(hashed_password, unicode):
                    hashed_password = hashed_password.decode('UTF-8')
        
                return hashed_password
        
            def get_encryption_method(self):
                """returns the encryption method from the config
                If None is set, or auth is disabled this will return None
                """
                auth_system = config.get('sa_auth', None)
                if auth_system is None:
                    # if auth is not activated in the config we should warn
                    # the admin through the logs... and return None
                    return None
        
                return auth_system.get('password_encryption_method', None)
        
            def validate_password(self, password):
                """Check the password against existing credentials.
                this method _MUST_ return a boolean.
        
                @param password: the password that was provided by the user to
                try and authenticate. This is the clear text version that we will
                need to match against the (possibly) encrypted one in the database.
                @type password: unicode object
                """
                algorithm = self.get_encryption_method()
                return self.password == self.__encrypt_password(algorithm, password)
        
        
        class Permission(DeclarativeBase):
            """A relationship that determines what each Group can do"""
            __tablename__ = 'tg_permission'
        
            permission_id = Column(Integer, autoincrement=True, primary_key=True)
        
            permission_name = Column(Unicode(16), unique=True)
        
            description = Column(Unicode(255))
        
            groups = relation(Group, secondary=group_permission_table,
                              backref='permissions')

       Finally, make sure these classes are imported at the end of your
       ``{yourproject}/model/__init__.py``::
       
           from auth import User, Group, Permission

    #. Finally, you may want to create some default users, groups and permissions
       to try authorization in your application. In ``{yourproject}.websetup``
       you may add a code like this in your ``setup_config()`` function::
       
            # ...
            
            model.metadata.create_all(bind=config['pylons.app_globals'].sa_engine)
            
            u = model.User()
            u.user_name = u'manager'
            u.display_name = u'Example manager'
            u.email_address = u'manager@somedomain.com'
            u.password = u'managepass'
        
            model.DBSession.save(u)
        
            g = model.Group()
            g.group_name = u'managers'
            g.display_name = u'Managers Group'
        
            g.users.append(u)
        
            model.DBSession.save(g)
        
            p = model.Permission()
            p.permission_name = u'manage'
            p.description = u'This permission give an administrative right to the bearer'
            p.groups.append(g)
        
            model.DBSession.save(p)
            model.DBSession.flush()
        
            u1 = model.User()
            u1.user_name = u'editor'
            u1.display_name = u'Exemple editor'
            u1.email_address = u'editor@somedomain.com'
            u1.password = u'editpass'
        
            model.DBSession.save(u1)
            model.DBSession.flush()
            
            transaction.commit()
            print "Successfully setup"

       And then populate your test database with these rows. To do so, first
       delete the file ``devdata.db`` from your project's root directory, and
       finally run the command below from the same directory::
       
           paster setup-app development.ini


Disabling authentication and authorization
------------------------------------------

If you need more flexibility than that provided by the quickstart, or you are 
not going to use :mod:`repoze.who` and :mod:`repoze.what`, you should prevent
TurboGears from dealing with authentication/authorization by removing (or 
commenting) the following line from 
``{yourproject}.config.app_cfg``::

    base_config.auth_backend = '{whatever you find here}'

Then you may also want to delete those settings like ``base_config.sa_auth.*``
-- they'll be ignored.
