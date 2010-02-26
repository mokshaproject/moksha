# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
from paver.setuputils import find_package_data

setup(
    name='moksha',
    version='0.4.4',
    description='',
    author='',
    author_email='',
    url='http://moksha.fedorahosted.org',
    install_requires=[
        "TurboGears2",
        "ToscaWidgets >= 0.9.1",
        "zope.sqlalchemy",
        #"Shove",
        "feedcache",
        "feedparser",
        "tw.jquery",
        "orbited",
        "Twisted",
        "stomper",
        "Sphinx",
        "Paver",
        "tw.forms",
        "pytz",
        "Babel"
        #"repoze.squeeze", # Not hard requirements
        #"repoze.profile", # Not hard requirements
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    #namespace_packages=['moksha'],
    tests_require=['WebTest', 'BeautifulSoup'],
    package_data=find_package_data(exclude=['ez_setup']),
    #package_data={'moksha': ['i18n/*/LC_MESSAGES/*.mo',
    #                         'public/favicon',
    #                         'public/css/*.css',
    #                         'public/images/*.png',
    #                         'public/images/*.gif',
    #                         'public/images/*.jpg',
    #                         'public/javascript/*.js',
    #                         'templates/*.html',
    #                         'templates/*.mak',
    #                         'public/javascript/ui/*.js']},
    message_extractors = {'moksha': [
            ('**.py', 'python', None),
            ('templates/**.mak', 'mako', None),
            ('templates/**.html', 'genshi', None),
            ('public/**', 'ignore', None)]},

    entry_points="""
    [console_scripts]
    moksha-hub = moksha.hub.hub:main

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
