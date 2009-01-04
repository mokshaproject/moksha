Web Session Usage
=====================

:Status: Work in progress

Why use sessions?
-----------------

Sessions are a common way to keep simple browsing data
attached to a user's browser. This is generally used to
store simple data that do not need to be persisted in a database.

Sessions in TurboGears can be backed by the filesystem, memcache, the database or by hashed cookie values.  By default the filesystem is used, but in high traffic websites hashed cookies provide a great system for small bits of session data.   If you are storing lots of data in the session, memcache is recommended. 

How to use sessions?
--------------------

If you just quickstarted a TurboGears 2 application, the session system is pre-configured and ready to be used.

By default we are using the Beaker session system. This system is configured
to use file system based storage. 

Each time a client connects, the session middleware (Beaker) will inspect the
cookie using the cookie name we have defined in the configuration file.

If the cookie is not found it will be set in the browser. On all subsequent
visits, the middleware will find the cookie and make use of it.

In the cookie beaker stores, a large random key which was set
at the first visit and which as been associated behind the scene to a file
in the file system cache.  In all but the cookie based backends, this key is then used to lookup and retrieve the session data from the proper datastore. 

OK, enough with theory! Let's get to some real life (sort of) examples.
Open up your root controller and add the following import at
the top the file::

    from tg import session

What you get is a Session instance that is always request-local, in other words, it's the session for this particular user.  The session can be manipulated in much the same way as a standard python dictionnary. 

Here is how you search for a key in the session::

    if session.get('mysuperkey', None):
        # do something intelligent
        pass

and here is how to set a key in the session::

    session['mysuperkey'] = 'some python data I need to store'
    session.save()

You should note that you need to explicitly save the session in order for your
keys to be stored in the session. 

