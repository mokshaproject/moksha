TurboGears 2 Configuration
===================================

TurboGears 2 provides a configuration system that attempts to be both extremely flexible for power users and very simple to use for standard projects. 

Overview
--------------------------

Like TurboGears 1, the application configuration is separated from the 
deployment specific information.  In TG2 there is a config module, containing 
several configuration specific python files -- these are done in python not
as INI files, because they actually setup the TG2 application and it's associated WSGI middleware.  And these files are intended to be edited only by application developers, not by those deploying the application.

At the same time the deployment level configuration is done in simple .ini files. 

All of this is similar to Pylons and to TurboGears 1, but slightly different from both.  

Differences from TurboGears 1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Differences from Pylons
~~~~~~~~~~~~~~~~~~~~~~~~~~

TG2 has done quite a bit of work to simplify the config module in a standard pylons quickstart, and to make the configuration in those files 
as declarative as possible.  This makes it easier to make small updates to the config, and allows us to move some of the code into the framework.  This is particularly is important, as it allows the framework to evolve and change the middleware stack without forcing developers to constantly update their code with every release. 



The config module
----------------------
.. tip::
    A good indicator of whether an option should be set in the ``config`` 
    directory code vs. the configuration file is whether or not the option is 
    necessary for the functioning of the application. If the application won't 
    function without the setting, it belongs in the appropriate `config/` 
    directory file. If the option should be changed depending on deployment, 
    it belongs in the ini files.

Our hope is that 90% of applications don't need to edit any of the config module files, but for those who do, the most common file to change is 
``app_config.py`` 

.. code:: wiki_root/trunk/wiki20/config/app_cfg.py
    :language: python
    
app_cfg.py exists primarily so that middleware.py and environment'py can import and use the ``base_config`` object.  

The ``base_config`` object is an ``AppConfig()`` instance which allows you to 
access it's attributes like a normal object, or like a standard python dictorary.  One of the reasons for this is that ``AppConfig()`` provides some defaults in it's ``__init__``.  But equally important it provides us with several methods that work on the config values to produce the two functions that setup your TurboGears app.   Since this is all done in your code, you can subclass or overide ``AppConfig`` to get exactly the setup you want.  

The ``base_config`` object that's created in app_cfg.py should be used to set whatever configuration values that belong to the application itself and are required for all instances of this app, as distinct from the configuration values that you set in the development.ini or production.ini files that are intended to be editable by those who deploy the app. 

As part of the app loading process the ``base_config`` object will be merged in with the config values from the .ini file you're using to launch your app, and placed in in ``pylons.config``. 

As we said, in  addition to the attributes on the ``base_config`` object there are a number of methods which are used to setup the environment for you application, and tocreate the actual Turbogears WSGI application, and all the middleware you need.

You can override base_config's methods to further customize you application's WSGI stack, for various advanced use cases, like adding custom middleware at arbitrary points in the WSGI pipeline, or doing some unanticipated (by us) application environment manipulation.  And we'll look at the details of how that all works in the advanced configuration section of this document. 

Setting up the base configuration for your app
-------------------------------------------------

The most common configuration change you'll likely want to make here is to add 
a second template engine or change the template engine used by your project. 

By default TurboGears sets up the Genshi engine, but we also provide out of 
the box support for Mako and Jinja.   To tell TG to prepare these template 
engines for you all you need to do is append 'mako' or 'jinja' to the 
renderer's list here in app_config. 

To change the default renderer to something other than Genshi, just set the 
default_renderer to the name of the rendering engine.  So, to add Mako to list
of renderers to prepare, and set it to be the default, this is all you'd have
to do::  

  base_config.default_renderer = 'mako'
  base_config.renderers.append('mako')
  

Configuration in the INI files
-------------------------------------------------

A turbogears quickstarted project will contain a couple of  .ini files which
are used to define what WSGI app ought to be run, and to store end-user 
created configuration values, which is just another way of saying that the 
.ini files should contain \deployment specific\ options.

By default TurboGears provides a development.ini, test.ini, and production.ini
files.   These are standard ini file formats. 

Let's take a closer look at the development.ini file:


These files are standard INI files, as used by Paste Deploy.  The individual 
sections are marked of with ``[]``'s.  

There's complete Paste Deploy documentation available at:

http://pythonpaste.org/deploy/



.. code:: wiki_root/trunk/development.ini
    :language: ini
    :section: default

.. seealso::
        Configuration file format **and options** are described in great 
        detail in the `Paste Deploy documentation 
        <http://pythonpaste.org/deploy/>`_.


Advanced Configuration
===================================


Modifying the environment loader and middleware stack
--------------------------------------------------------

We've created a number of methods that you can use to override the way that particular pieces of the TG2 stack are configured.  

.. automodule:: tg.configuration
.. autoclass::  AppConfig
   :members:

Embedding a TG app inside another TG app
-------------------------------------------------

One place where you'll have to be aware of how all of this works is when 
you programatically setup one TurboGears app inside another. 

In that case, you'll need to create your own ``base_config`` like object to usewhen configuring the inside wsgi application instance. 
 
Fortunately, this can be as simple as creating your own ``base_config`` object 
from AppConfig(), creating your own app_conf and global dictionaries, and 
creating an environment loader::

  load_environment = my_conf_object.make_load_environment()
  make_wsgi_app = my_conf_object.setup_tg_wsgi_app(load_environment)
  final_app = make_wsgi_app(global_conf, app_conf)

Using AppConfig outside of a quickstarted project:
------------------------------------------------------



