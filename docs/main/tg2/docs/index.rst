TurboGears Documentation:
=============================

TurboGears 2 is a reinvention of the TurboGears project to take advantage of 
new components, and to provide a fully customizable WSGI (Web Server Gateway 
Interface) stack.  From the beginning TurboGears was designed to be a Full 
Stack framework built from best-of-breed components. New components have been 
released which improved on the ones in the original TGstack, and the Python 
web world has been increasingly designed around WSGI.  

This has enabled a whole new world of reuse, and TG2 is designed to 
take advantage of this fact in order to make a framework which provides 
easy to use,  productive defaults, while still providing flexibility where it's useful.  

TG2 represents a change from some of the components in TurboGears 1, but we're now invested in a set of components that we think will continue to be at 
the center of python web development for years to come. 

Getting Started with TurboGears
==================================

Get TurboGears 2 installed, learn how to create a new TurboGears project in a 
single command, and of course explore the obligatory "Hello World" example, 
with a few fun treats thrown in.

.. toctree::
   :maxdepth: 2

   main/DownloadInstall
   main/QuickStart

Tutorials
===========

Are you the type who learns by doing?   If so this section is for you.  Our 
ultimate goal is to provide several tutorials on TG2 including everything 
from the basics, to advanced topics.

.. toctree::
   :maxdepth: 2
   
   main/Wiki20/wiki20
   main/ToscaWidgets/forms
   main/Auth/index

What's new in TG2
===================

.. toctree::
   :maxdepth: 2

   main/WhatsNew

General Reference for MVC Components
======================================

.. toctree::
   :maxdepth: 2

   main/Controllers
   main/Genshi
   main/SQLAlchemy

Validation, Form handling and form widgets
===========================================

.. toctree::
   :maxdepth: 2

   main/FormBasics
   main/Validation
   main/ToscaWidgets/forms
   main/ToscaWidgets/ToscaWidgets


Recipes for Installation and Deployment
========================================

.. toctree::
   :maxdepth: 2

   main/OfflineInstall
   main/Deployment
   main/Deployment/ModProxy
   main/Deployment/modwsgi+virtualenv


Development Tools
======================

.. toctree::
   :maxdepth: 2

   main/ToolBox
   main/CommandLine
   main/Profile


TG2 Extensions
==============

.. toctree::
   :maxdepth: 2

   main/Extensions/SilverPlate/index
   main/Extensions/Geo/index


Other TG Tools
=====================

.. toctree::
   :maxdepth: 2
   
   main/Config
   main/Caching
   main/LogSetup
   main/Internationalization



Recipes
======================

.. toctree::
   :maxdepth: 2

   main/Auth/Authentication
   main/TGandPyAMF
   main/RoutesIntegration
   main/StaticFile
   main/Mako
   main/Jinja

Performance and optimization:
===============================

Not all sites are going to be performance constrained, and not all performance
constraints are created equal.   Premature optimization can get you into a lot 
of trouble if you're not careful, but knowing and doing a few simple things up front can help you to handle huge traffic loads when they come.   

These guides are not intended to be exhaustive descriptions of web-application
performance and scalability issues, but rather to provide some simple advice
for those who are expecting large traffic loads. 

.. toctree::
   :maxdepth: 2
   
   main/GeneralPerformance
   main/TemplatePerformance
   main/DatabasePerformance



General Project Information
=======================================

.. toctree::
   :maxdepth: 2

   main/TG2Philosophy
   main/DevStatus
   main/Contributing
   main/License
   main/TGandPylons

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

