JQPlot Demo
===========

This is a basic TurboGears2 application that demos the
:class:`tw.jquery.jqplot.AsynchronousJQPlotWidget`

Installation and Setup
======================

Install ``JQPlotDemo`` using the setup.py script::

    $ cd JQPlotDemo
    $ python setup.py install

Start the paste http server::

    $ paster serve development.ini

While developing you may want the server to reload after changes in package files (or its dependencies) are saved. This can be achieved easily by adding the --reload option::

    $ paster serve --reload development.ini

Then you are ready to go.
