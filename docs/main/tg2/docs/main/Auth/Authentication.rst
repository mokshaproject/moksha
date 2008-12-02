****************************************************************
:mod:`repoze.who` -- Authentication in TurboGears 2 applications
****************************************************************

:Status: Official
:Website: `<http://static.repoze.org/whodocs/>`_

.. module:: repoze.who
    :synopsis: Setup authentication in WSGI applications

.. topic:: Overview

    This document describes how :mod:`repoze.who` is integrated into TurboGears
    and how you make get started with it. For more information, you may want
    to check :mod:`repoze.who`'s website.

:mod:`repoze.who` is a powerful and extensible ``authentication`` package for
arbitrary WSGI applications. Within TurboGears, it's configured through
:mod:`repoze.what`.


How it works
============

It's a WSGI middleware which is able to authenticate the user through the
method you want (e.g., LDAP or HTTP authentication), "remember" the user in
future requests and log the user out.

You can customize the interaction with the user through four kinds of
`plugins`, sorted by the order in which they are run on each request:

* An ``identifier plugin``, with no action required on the user's side, is able
  to tell whether it's possible to authenticate the user (e.g., if it finds
  HTTP Authentication headers in the HTTP request). If so, it will extract the
  data required for the authentication (e.g., username and password, or a
  session cookie). There may be many identifiers and :mod:`repoze.who` will run 
  each of them until one finds the required data to authenticate the user.
* If at least one of the identifiers could find data necessary to authenticate
  the current user, then an ``authenticator plugin`` will try to use the
  extracted data to authenticate the user. There may be many authenticators
  and :mod:`repoze.who` will run each of them until one authenticates the user.
* When the user tries to access a protected area or the login page, a
  ``challenger plugin`` will come up to request an action from the user (e.g.,
  enter a user name and password and then submit the form). The user's response
  will start another request on the application, which should be caught by
  an `identifier` to extract the login data and then such data will be used
  by the `authenticator`.
* For authenticated users, :mod:`repoze.who` provides the ability to load
  related data (e.g., real name, email) in the WSGI environment so that it can
  be easily used in the application. Such a functionality is provided by 
  so-called ``metadata provider plugins``. There may be many metadata providers
  and :mod:`repoze.who` will run them all.

When :mod:`repoze.who` needs to store data about the authenticated user in the 
WSGI environment, it uses its ``repoze.who.identity`` key, which can be 
accessed using the code below::

    from tg import request
    
    # The authenticated user's data kept by repoze.who:
    identity = request.environ.get('repoze.who.identity')

Such a value is a dictionary and is often called "the identity dict". It will 
only be defined if the current user has been authenticated.

The username will be available in ``identity['repoze.who.userid']``.


How it works in TurboGears applications
=======================================

TurboGears itself doesn't deal directly with :mod:`repoze.who`. It's configured
through :mod:`repoze.what` because it has to configure :mod:`repoze.who` in a
special way so that authorization can work.

By default, :mod:`repoze.what` in TG2 configures :mod:`repoze.who` to use its
:class:`repoze.who.plugins.form.RedirectingFormPlugin` as the first
identifier and challenger -- using ``/login`` as the relative URL that will 
display the login form, ``/login_handler`` as the relative URL where the 
form will be sent and ``/logout_handler`` as the relative URL where the 
user will be logged out. The so-called rememberer of such identifier will
be an instance of :class:`repoze.who.plugins.cookie.AuthTktCookiePlugin`.
All these settings can be customized through 
:mod:`repoze.what.plugins.quickstart`.

You don't have to use :mod:`repoze.who` directly either, unless you decide not 
to use it the way TurboGears configures it through :mod:`repoze.what`.


Advanced topics
===============

If you're looking for different authentication methods, you may want to visit
`the repoze.who website <http://static.repoze.org/whodocs/>`_ to check if the
plugin you're looking for is already available or how to create your own plugins.
Then you should also check the :mod:`repoze.what` documentation to learn how to 
setup the new settings.
