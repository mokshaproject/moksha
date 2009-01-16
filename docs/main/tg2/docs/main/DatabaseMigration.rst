Database Schema Migration in TurboGears 2
=========================================

An automated method of applying database schema migrations helps to
create a robust and reliable upgrade path for an application as it
changes over time.  TurboGears 2 comes with a tool to incrementally
test and automatically deploy schema changes as needed.

TurboGears 2 relies on the `sqlalchemy-migrate`_ project to 
automate database schema migration.

.. _sqlalchemy-migrate: http://code.google.com/p/sqlalchemy-migrate/


Prerequisites
-------------

This document assumes that you have an existing TurboGears 2 project
that uses the built-in support for SQLAlchemy.  If you
are not yet at that stage, you may want to review the following:

* `http://turbogears.org/2.0/docs/main/QuickStart.html`_ - Quickstarting a TurboGears 2 project
* `http://turbogears.org/2.0/docs/main/SQLAlchemy.html`_ - Working with SQLAlchemy and your data model

.. _http://turbogears.org/2.0/docs/main/QuickStart.html: http://turbogears.org/2.0/docs/main/QuickStart.html
.. _http://turbogears.org/2.0/docs/main/SQLAlchemy.html: http://turbogears.org/2.0/docs/main/SQLAlchemy.html

Additionally, it is assumed that you have reached a point in the
development life cycle where a change must be made to your current data
model. This could mean adding a column to an existing table, adding a
table, removing a table, or any number of other database schema
changes.

The examples in this document will be based on the `TurboGears 2 Wiki
Tutorial`_, but the information applies to any TurboGears 2 project.

.. _`TurboGears 2 Wiki Tutorial`: http://turbogears.org/2.0/docs/main/Wiki20/wiki20.html


Getting Started
---------------

The sqlalchemy-migrate library provides a ``migrate`` script that should
be in your path.  The ``migrate`` script wraps several
sqlalchemy-migrate commands much like the ``paster`` script wraps
commands.  You can verify that the migrate script is in your path and
retrieve a list of available commands by running the following::

    $ migrate --help

Two additions to your TurboGears 2 project are required for
sqlalchemy-migrate to manage the database schema:

* A repository on the file system of schema revisions
* A database table for maintaining migration state in the managed database.


Create a Repository
~~~~~~~~~~~~~~~~~~~

To create a repository of schema revisions we issue the following command
in the root of the project::

    $ migrate create migration "Wiki20 Migrations"

The first argument to the ``create`` command, ``migration``, is the
directory that will contain the repository of schema revisions.  The second
argument to the ``create`` command, 'Wiki20 Migrations', is the name of
the newly created migration repository.  The command should return
without generating any output, and a new directory, migration, should
now exist in the project root with the following content::

    __init__.py
    __init__.pyc
    manage.py
    migrate.cfg
    README
    versions


Place the Database under Version Control
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Our repository is ready.  Now we must create a table
for maintaining revision state in our managed database. The ``migrate``
script providesnd for this step as well:

    $ migrate version_control sqlite:///devdata.db migration

The two arguments to the ``version_control`` command are a valid
SQLAlchemy database URL and the path to your sqlalchemy-migrate
revision repository. You will need to run the ``version_control``
command against each database instance for your application.  If you
have a development, test, and production database, all three databases
will need to be placed under version_control.

If you examine your database, you will now find a new table named
``migrate_version``.  It will contain one row::

    sqlite> .headers on
    sqlite> select * from migrate_version;
    repository_id|repository_path|version
    Wiki20 Migrations|migration|0

Note that the ``repository_id`` column should uniquely identify your
project's set of migrations.  Should you happen to deploy multiple
projects in one database, each sqlalchemy-migrate repository will
insert and maintain a row in the ``migrate_version`` table.


Integrating sqlalchemy-migrate in the Development Process
----------------------------------------------------------

With the database under version control and a repository for schema
change scripts, you are ready to begin regular development.  We will
now walk through the process of creating, testing, and applying a
change script for your current database schema.  Repeat these steps as
your data model evolves to keep your databases in sync with your
model.


Create Your First Change Script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``migrate`` script will create an empty change script for you,
automatically naming it and placing it in your repository::

    $ migrate script --repository=migration initial_schema

The command will return without producing any output, but the new script
will be in your repository::

    $ ls migration/versions
    001_initial_schema.py  __init__.py  __init__.pyc


Edit the Script
~~~~~~~~~~~~~~~

Each change script provides an ``upgrade`` and ``downgrade`` method, and
we implement those methods by creating and dropping the ``pages_table``
respectively::

    from sqlalchemy import *
    from migrate import *

    metadata = MetaData(migrate_engine)
    pages_table = Table("pages", metadata,
                        Column("id", Integer, primary_key=True),
                        Column("pagename", Text, unique=True),
                        Column("data", Text)
                        )


    def upgrade():
        # Upgrade operations go here. Don't create your own engine; use the engine
        # named 'migrate_engine' imported from migrate.
        pages_table.create()

    def downgrade():
        # Operations to reverse the above upgrade go here.
        pages_table.drop()


Test the Script
~~~~~~~~~~~~~~~

Anyone who has experienced a failed schema upgrade on a production
database knows how uniquely uncomfortable that situation can be.
Although testing a new change script is optional, it is clearly a good
idea.  After you execute the following test command, you will ideally be
successful::

    $ migrate test migration sqlite:///devdata.db
    Upgrading... done
    Downgrading... done
    Success

If you receive an error while testing your script, one of two issues
is probably the cause:

* There is a bug in the script
* You are testing a script that conflicts with the schema as it currently exists.

If there is a bug in your change script, you can fix the bug and rerun
the test.

If you are working through this document with an existing application,
your database probably already contains the initial schema for your
project.  In this case, you cannot test the change script against your
existing database because it will try to create tables that already
exist.  To test the script while preserving your existing data, you
will need to create a second database, place it under version_control,
and test the script against the new database.  Since your original database
already contains the schema defined in your change script, you will need
to update the ``migrate_version`` table manually to reflect this situation::

    sqlite> update migrate_version set version=1;


Deploy the Script
~~~~~~~~~~~~~~~~~

The script is now ready to be deployed::

    migrate upgrade sqlite:///devdata.db migration

One quirk to note: the arguments to ``upgrade`` are in the opposite
order compared to the ``test`` command.  If your database is already at
the most recent revision, the command will produce no output.  If
migrations are applied, you will see output similar to the following::

    0 -> 1... done


Additional Information and Help
-------------------------------

* The `sqlalchemy-migrate documentation`_.
* The `TurboGears SQLAlchemy documentation`_.

Many of the sqlalchemy-migrate developers are on the SQLAlchemy
mailing list.  Problems integrating sqlalchemy-migrate into a
TurboGears project should be sent to the `TurboGears mailing list`_.

.. _`sqlalchemy-migrate documentation`: http://code.google.com/p/sqlalchemy-migrate/w/list
.. _`TurboGears SQLAlchemy documentation`: http://turbogears.org/2.0/docs/main/SQLAlchemy.html
.. _`TurboGears mailing list`: http://groups.google.com/group/turbogears
