# -*- coding: utf-8 -*-
from paver.easy import *
from paver.setuputils import (setup, find_package_data, find_packages,
                              install_distutils_tasks)
install_distutils_tasks()
from moksha.lib.paver_tasks import *

options(
    setup=Bunch(
        name="moksha.topics",
        version="0.1",
        release="1",
        url="http://moksha.fedorahosted.org",
        description="Describe your package here",
        license="AGPLv3",
        long_description="",
        author="",
        author_email="",
        rpm_name='moksha-topics',
        packages=find_packages(),
        package_data=find_package_data(),
        namespace_packages=[
            'moksha',
            'moksha.apps',
        ],
        install_requires=["Moksha"],
        entry_points={
            'moksha.stream': (
                'topics = moksha.apps.topics.streams:TopicsStream',
            ),
            'moksha.consumer': (
                'topics = moksha.apps.topics.consumers:TopicsConsumer'
            ),
        }
    ),
)
