# -*- coding: utf-8 -*-
from paver.easy import *
from paver.setuputils import (setup, find_package_data, find_packages,
                              install_distutils_tasks)
install_distutils_tasks()
from moksha.lib.paver_tasks import *

options(
    setup=Bunch(
        name="moksha.jit",
        version="0.1",
        release="1",
        url="http://moksha.fedorahosted.org",
        description="Describe your package here",
        license="AGPLv3",
        long_description="",
        author="",
        author_email="",
        rpm_name='mokshajit',
        packages=find_packages(),
        package_data=find_package_data(),
        namespace_packages=[
            'moksha',
            'moksha.apps',
            'moksha.widgets',
        ],
        install_requires=["Moksha"],
        entry_points={
            #'moksha.stream': (
            #    'mokshajit = moksha.apps.mokshajit.streams:MokshaJitStream',
            #),
            'moksha.widget': (
                'mokshajit = moksha.widgets.mokshajit.widgets:MokshaJitWidget',
                'moksha.jit.hypertree = moksha.widgets.mokshajit.hypertree:HyperTree',
            ),
            'moksha.application': (
                'mokshajit = moksha.apps.mokshajit.controllers.root:MokshajitController'
            ),
        }
    ),
)
