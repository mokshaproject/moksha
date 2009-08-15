# This file is part of Moksha.
# Copyright (C) 2008-2009  Red Hat, Inc.
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
from moksha import version

setup(
    name='moksha',
    version=version,
    description='',
    author='',
    author_email='',
    url='http://moksha.fedorahoted.org',
    install_requires=[
        "TurboGears2",
        "ToscaWidgets >= 0.9.1",
        "zope.sqlalchemy",
        "Shove",
        "feedcache",
        "feedparser",
        "tw.jquery>=0.9.4.1",
        #"repoze.squeeze", # Not hard requirements
        #"repoze.profile", # Not hard requirements
        "orbited",
        #"Twisted",
        "stomper",
        "Sphinx",
        "Paver",
        "tw.forms",
        #"WidgetBrowser", # not in PyPi yet
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

    """,
)
