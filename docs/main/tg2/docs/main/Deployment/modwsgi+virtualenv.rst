mod_wsgi
==========

The mod_wsgi site documents how to use virtualenv:

http://code.google.com/p/modwsgi/wiki/VirtualEnvironments

You can then deploy your TG2 app as described here:

http://code.google.com/p/modwsgi/wiki/IntegrationWithPylons


Deployment using mod_wsgi and apache. Below instructions will tell you how to quickly deploy your turbogears2 app using mod_wsgi.

Install modwsgideploy
---------------------

PYPI
~~~~

You can install modwsgideploy from PyPi::

 easy_install modwsgideploy

Done.

Source Install
~~~~~~~~~~~~~~

You also have a choice of getting the source and installing it.
You should use this in a virtual environment, for example::

 virtalenv --no-site-packages BASELINE
 source BASELINE/bin/activate

Install [:Bazaar:] if its not already installed on your system::

 easy_install bzr

Branch out the code. This will pull all the revision history. If you want just the recent one use checkout::

 bzr branch https://code.launchpad.net/~szybalski/modwsgideploy/trunk/ modwsgideploy_code

Install it::

 cd modwsgideploy_code/trunk
 python setup.py develop

Run modwsgi_deploy 
------------------

Go into your python application project folder and type in::

 paster modwsgi_deploy


Example
-------

Here is a typical installation, from start to finish on Debian Linux. Installing apache is an OS specific activity, and is better documented elsewhere. But here's the outline of what we'll be doing

1) Install apache and modwsgi
2) Setup virtual environment and install tg2
3) Create tg2 app 'myapp'
4) Install modwsgideploy and tweak wsgi settings to fit your needs or use default settings.
5) Check if everything is running properly.

On Debian you can install Apache like this::

 aptitude install apache2
 aptitude install libapache2-mod-wsgi

Next we create a virtual environment: 

 virtualenv --no-site-packages BASELINE
 source BASELINE/bin/activate
 easy_install -i http://www.turbogears.org/2.0/downloads/current/index tg.devtools
 paster quickstart myapp

 
Then we install a little helper app modwsgideploy::

 easy_install modwsgideploy

Go into your application directory and run modwsgi_deploy command::

 cd myapp
 paster modwsgi_deploy

You should see an apache folder like this inside 'myapp'::

 myapp
 |-- apache
 |   |-- README.txt
 |   |-- myapp
 |   |-- myapp.wsgi
 |   `-- test.wsgi
 

1. Read the README.txt
2. myapp is a apache configuration file that you need to copy into your apache configuration folder after all the settings are set.
3. myapp.wsgi is an modwsgi script that is called from myapp apache file
4. test.wsgi is a test script that you can call to see if you modwsgi was properly installed and working.

Edit myapp file to change any paths and/or apache configurations. Then copy to apache folder. 

On debian::

 cp ./apache/myapp /etc/apache2/sites-available/

Enable the website::

 a2ensite myapp
 /etc/init.d/apache restart

Of course you can create the myapp.wsgi and test.wsgi files manually as well. 

Possible gotchas  
====================

In multiple process load balanced deployments (such as this one) it is very possible that a given request will pull resources from multiple processes.  

You may want to make sure that the TG controllers are loaded up even 
before the first request comes in to handle this, so you should add::

  import paste.fixture
  app = paste.fixture.TestApp(application)
  app.get("/")

to the end of the wsgi-script that starts your application.  
    
This will fetch the index page of your app, thus assuring that it's ready to handle all of your requests immediately.  This avoids a problem where your controller page is not yet  loaded so widgets aren't initialized, but a request comes in for a widget resource the ToscaWidgets middleware doesn't have the widget registered yet. 