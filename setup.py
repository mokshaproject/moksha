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

# This is required (oddly) to fix a python 2.7 bug with nose tests.
try:
    import multiprocessing, logging
except Exception:
    pass

setup(
    name='moksha',
    version='0.8.8',
    description='A platform for creating real-time web applications',
    author='Luke Macken, John (J5) Palmieri, Mairin Duffy, and Ralph Bean',
    author_email='',
    url='http://moksha.fedorahosted.org',
    install_requires=[
        "sqlalchemy",
        "psutil",
        "Shove",
        "feedcache",
        "feedparser",
        "orbited==0.7.10",
        "Twisted",
        "stomper",
        "txZMQ>=0.5.0",
        "txWS",
        "Sphinx",
        "fabulous",
        "Paver",
        "pytz",
        "Babel",
        "pyOpenSSL",
        #"BeautifulSoup",
        "python-daemon",
        "Bunch",
        "kitchen",
        "Mako",
        "Genshi",
        "tw2.core>=2.0.0",
        "tw2.forms",
        "tw2.jquery>=2.0b6",
        "tw2.jqplugins.ui",
        "tw2.jqplugins.flot>=2.0a4",
        "tw2.jqplugins.gritter>=2.0b4",
        "tw2.jit",
        "tw2.excanvas",
        #"repoze.squeeze", # Not hard requirements
        #"repoze.profile", # Not hard requirements
        "paste",
        "PasteDeploy",
        "WebHelpers",
        "repoze.what",
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    #namespace_packages=['moksha'],
    tests_require=[
        'WebTest',
        'BeautifulSoup',
        'nose',
        'coverage',
    ],
    #package_data=find_package_data(exclude=['ez_setup']),
    message_extractors = {'moksha': [
            ('**.py', 'python', None),
            ('templates/**.mak', 'mako', None),
            ('templates/**.html', 'genshi', None),
            ('public/**', 'ignore', None)]},

    entry_points="""
    [console_scripts]
    moksha-hub = moksha.hub:main
    moksha = moksha.commands.cli:main

    # Pulls in all widgets.  Used by the `archive_moksha_resources` command.
    [toscawidgets.widgets]
    widgets = moksha.widgets.all

    # Pulls in all widgets.  Used by the `archive_moksha_resources` command.
    [tw2.widgets]
    widgets = moksha.widgets.all

    [distutils.commands]
    archive_moksha_resources = moksha.distutils.command:archive_moksha_resources

    [moksha.widget]
    code_widget = moksha.widgets.source:code_widget
    moksha_socket = moksha.api.widgets.live:get_moksha_socket

    [moksha.global]
    moksha_socket = moksha.api.widgets.live:get_moksha_socket

    [paste.global_paster_command]
    moksha = moksha.commands.quickstart:MokshaQuickstartCommand

    [paste.paster_create_template]
    moksha.master = moksha.pastetemplate:MokshaMasterTemplate
    moksha.livewidget = moksha.pastetemplate:MokshaLiveWidgetTemplate
    moksha.stream = moksha.pastetemplate:MokshaStreamTemplate
    moksha.consumer = moksha.pastetemplate:MokshaConsumerTemplate
    moksha.controller = moksha.pastetemplate:MokshaControllerTemplate

    [paste.filter_app_factory]
    middleware = moksha.middleware:make_moksha_middleware

    """,
)
