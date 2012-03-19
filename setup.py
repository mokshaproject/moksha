# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages

setup(
    name='moksha',
    version='0.6.1',
    description='',
    author='',
    author_email='',
    url='http://moksha.fedorahosted.org',
    install_requires=[
        "WebOb==1.0.8",
        "Pylons==1.0",
        "TurboGears2",
        "ToscaWidgets",
        "zope.sqlalchemy",
        #"Shove",
        "feedcache",
        "feedparser",
        "tw.jquery>=0.9.9",
        "orbited==0.7.10",
        #"Twisted",
        "stomper",
        "Sphinx",
        "Paver",
        "tw.forms",
        #"pytz",
        "Babel",
        "pyOpenSSL",
        #"BeautifulSoup",
        "python-daemon",
        "repoze.what-quickstart",
        "repoze.what-pylons",
        "repoze.tm2",
        "Bunch",
        "Mako",
        "Genshi",
        #"repoze.squeeze", # Not hard requirements
        #"repoze.profile", # Not hard requirements
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    #namespace_packages=['moksha'],
    tests_require=['WebTest', 'BeautifulSoup'],
    #package_data=find_package_data(exclude=['ez_setup']),
    message_extractors = {'moksha': [
            ('**.py', 'python', None),
            ('templates/**.mak', 'mako', None),
            ('templates/**.html', 'genshi', None),
            ('public/**', 'ignore', None)]},

    entry_points="""
    [console_scripts]
    moksha-hub = moksha.hub.hub:main
    moksha = moksha.commands.cli:main

    [paste.app_factory]
    main = moksha.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller

    # Pulls in all widgets.  Used by the `archive_tw_resources` command.
    [toscawidgets.widgets]
    widgets = moksha.widgets.all

    [moksha.widget]
    code_widget = moksha.widgets.source:code_widget
    moksha_socket = moksha.api.widgets.live:moksha_socket

    [moksha.global]
    moksha_socket = moksha.api.widgets.live:moksha_socket

    [paste.global_paster_command]
    moksha = moksha.commands.quickstart:MokshaQuickstartCommand

    [paste.paster_create_template]
    moksha.master = moksha.pastetemplate:MokshaMasterTemplate
    moksha.livewidget = moksha.pastetemplate:MokshaLiveWidgetTemplate
    moksha.stream = moksha.pastetemplate:MokshaStreamTemplate
    moksha.consumer = moksha.pastetemplate:MokshaConsumerTemplate
    moksha.connector = moksha.pastetemplate:MokshaConnectorTemplate
    moksha.controller = moksha.pastetemplate:MokshaControllerTemplate

    """,
)
