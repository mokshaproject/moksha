# -*- coding: utf-8 -*-
from paver.easy import *
from paver.setuputils import (setup, find_package_data, find_packages,
                              install_distutils_tasks)
install_distutils_tasks()
from moksha.lib.paver_tasks import *

options(
    setup=Bunch(
        name="moksha.feeds",
        version="0.1",
        release="1",
        url="http://moksha.fedorahosted.org",
        description="Describe your package here",
        license="AGPLv3",
        long_description="",
        author="",
        author_email="",
        rpm_name='moksha-feeds',
        packages=find_packages(),
        package_data=find_package_data(),
        namespace_packages=[
            'moksha',
            'moksha.apps',
            'moksha.widgets',
        ],
        install_requires=["Moksha"],
        entry_points={
            'moksha.producer': (
                'feeds = moksha.apps.feeds.streams:MokshaFeedStream',
            ),
            'moksha.consumer': (
                'feeds = moksha.apps.feeds.consumer:MokshaFeedConsumer'
            ),
            'moksha.application': (
                'feeds = moksha.apps.feeds.controllers:FeedController'
            ),
            'moksha.widget': (
                'feeds = moksha.widgets.feeds.widgets:moksha_feedreader'
            ),
        }
    ),
)
