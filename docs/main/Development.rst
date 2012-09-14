===================
Hacking with Moksha
===================

Setting up your RPM/virtualenv development environments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:RPM mod_wsgi installation (Red Hat, Fedora, etc.): :doc:`RPMInstallation`
:virtualenv installation (OSX, Ubuntu, etc.): :doc:`VirtualenvInstallation`

Getting the code
~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ git clone git://git.fedorahosted.org/git/moksha
    $ cd moksha/

Bootstrapping Your Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Definitely get and set up the awesome `virtualenvwrapper
<http://pypi.python.org/pypi/virtualenvwrapper>`_ first.

.. code-block:: bash

    $ mkvirtualenv moksha

There is a script called ``moksha/.travis-dev-setup.sh`` that simply loops over
``moksha.common``, ``moksha.hub``, and ``moksha.wsgi`` and runs ``python
setup.py develop`` in each one.

.. code-block:: bash

    $ ./.travis-dev-setup.sh

Run the tests
~~~~~~~~~~~~~

.. code-block:: bash

    $ ./.travis-run-tests.sh

Freezing requirements
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    $ pip freeze -E ~/.virtualenvs/moksha -r requirements.txt production/stable-reqs.txt
