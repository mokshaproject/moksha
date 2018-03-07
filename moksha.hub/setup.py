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
import sys

# This is required (oddly) to fix a python 2.7 bug with nose tests.
try:
    import multiprocessing
    import logging
except Exception:
    pass

install_requires = [
    "moksha.common>=1.0.6",
    "Twisted",
    #"stomper>=0.2.9",
    "pyzmq",
    "txZMQ",
    "txWS",
    #"python-daemon",
]

tests_require = [
    'nose',
    'mock',
    'pyzmq',
    'websocket-client',
]

if sys.version_info[0] == 2 and sys.version_info[1] <= 6:
    tests_require.extend([
        'unittest2',
    ])
    install_requires.append('ordereddict')


setup(
    name='moksha.hub',
    version='1.5.4',
    description='Hub components for Moksha.',
    author='Luke Macken, John (J5) Palmieri, Mairin Duffy, and Ralph Bean',
    author_email='',
    url='https://mokshaproject.net',
    install_requires=install_requires,
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    namespace_packages=['moksha'],
    tests_require=tests_require,
    entry_points="""
    [console_scripts]
    moksha-hub = moksha.hub:main
    [moksha.stream]
    monitoring = moksha.hub.monitoring:MonitoringProducer
    """,
)
