.. _commandline-reference:

TurboGears2 delegates it's command line tasks to Paste, in TG1.x this was a build in command which was drop in favor of the more robust Paste infraestructure. 

What is PasteScript?
====================

PasteScript is a part of the Paste group of libraries, which provides the very basic foundation on which TurboGears and Pylons are build on. You can think of Paste as a very useful group of things.
http://pythonpaste.org/

As for PasteScript it is composed of two parts Templates and Commands, the first takes care of code generation tasks (like quickstart), the second is an extensible command line utility (like tginfo)
http://pythonpaste.org/script/

If you are interesting in learning how to build your own Paster command please visit http://pythonpaste.org/script/developer.html

How it integrates with TurboGears 2?
=====================================

PasteScript provides a single command line script named ``paster``, which is build to be self-explanatory, try it out on the command line. It should give you a big list of commands. There is also a ``paster help <command>`` command that will give you additional information about all commands that support it.

Using a setuptools mechanism know as "entry point" TurboGears, as well as any other project that uses PasteScript, is able to add extensions to the paster command, for example if you execute paster with no parameters you will see a "TurboGears2" section.

Which are the TurboGears commands?
==================================

Please note that not all paster commands are expected to work with a TG2 project, that said if you experience an error we encourage you to report it. Below is a list of the most important commands you will use in your journey in the world of TG2. Be sure to run ``paster help`` on each of them to get all the possible command line switches.

paster quickstart
------------------

This is probably the first command you will encounter when developing on TurboGears, it will create a base project for you with everything you need to get started and explanations for everything. In case you are wondering this is a small wrapper around ``paster create`` to provide a TG1-like command. 

paster serve
------------

This is used to start the built-in server, which is a very robust implementation (multi-threaded, SSL support, etc.) which means a several people use it in production. That say you should take a look at our deployment docs. The most common usage for this command is:

.. code-block:: bash

     $ paster serve --reload development.ini

The above command will enable the reloading of the server every time you save a file, which is a very nice feature :)

paster tginfo
--------------

This command is designed to display a rather big chuck of information regarding your TurboGears installation, and it's designed to troubleshoot installation problems. Therefore it should be the first thing you should run to be certain your system is healthy. 

paster shell
-------------

This enables a python shell with your TurboGears application loaded, the most important bit here is that your model is also loaded therefore you can experiment with your database.

paster setup-app
----------------

This command is designed to bootstrap your database by executing your websetup.py file.
