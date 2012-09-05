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
    name='moksha.feeds',
    version='1.0.0',
    description='WSGI components for Moksha.',
    author='Luke Macken, John (J5) Palmieri, Mairin Duffy, and Ralph Bean',
    author_email='',
    url='http://moksha.fedorahosted.org',
    install_requires=[
        "moksha.common",
        "moksha.wsgi",
        "shove",
        "feedcache",
        "feedparser",
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    namespace_packages=['moksha'],
    tests_require=[
        'mock',
        'nose',
        'webtest',
        'bunch',
    ],
    message_extractors = {'moksha': [
            ('**.py', 'python', None),
            ('templates/**.mak', 'mako', None),
            ('templates/**.html', 'genshi', None),
            ('public/**', 'ignore', None)]},

    entry_points="""
    # Pulls in all widgets.  Used by the `archive_moksha_resources` command.
    [toscawidgets.widgets]
    widgets = moksha.feeds.widgets

    # Pulls in all widgets.  Used by the `archive_moksha_resources` command.
    [tw2.widgets]
    widgets = moksha.feeds.widgets
    """,

)
