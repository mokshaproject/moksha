# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

# This is required to avert a strange python 2.7 bug
import multiprocessing, logging

setup(
    name='JQPlotDemo',
    version='0.2',
    description='',
    author='Ralph Bean, Luke Macken',
    author_email='',
    #url='',
    install_requires=[
        "TurboGears2 >= 2.0b7",
        #"Catwalk >= 2.0.2",
        "Babel >=0.9.4",
        "ToscaWidgets>=0.9.8dev",
        "zope.sqlalchemy >= 0.4 ",
        "repoze.tm2 >= 1.0a4",
        "tw.jquery>=0.9.8dev",
    ],
    setup_requires=["PasteScript >= 1.7"],
    paster_plugins=['PasteScript', 'Pylons', 'TurboGears2', 'tg.devtools'],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['WebTest', 'BeautifulSoup'],
    package_data={'jqplotdemo': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 'public/*/*']},
    message_extractors={'jqplotdemo': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
            ('templates/**.html', 'genshi', None),
            ('public/**', 'ignore', None)]},

    entry_points="""
    [paste.app_factory]
    main = jqplotdemo.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller

    [moksha.stream]
    jqplot_stream = jqplotdemo.streams:JQPlotDemoStream

    # We only enable this when running this app *in* Moksha.
    # If we're running this app stand-alone, then we must have
    # the MokshaMiddleware attached.
    #[moksha.wsgiapp]
    #jqplotdemo = jqplotdemo.wsgi:application

    [moksha.global]
    moksha_socket = moksha.api.widgets:moksha_socket

    [moksha.widget]
    jqplot_pie_widget = jqplotdemo.widgets:pie_widget
    jqplot_plot_widget = jqplotdemo.widgets:plot_widget

    """,
)
