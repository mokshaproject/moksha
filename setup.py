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

setup(
    name='moksha',
    version='0.1',
    description='',
    author='',
    author_email='',
    #url='',
    install_requires=[
        "TurboGears2",
        "ToscaWidgets >= 0.9.1",
        "zope.sqlalchemy",
        "Shove",
        "feedcache",
        "feedparser",
        "tw.jquery>=0.9.4.1",
        "repoze.squeeze",
        "repoze.profile",
        "orbited",
        "twisted",
        "stomper",
        "Sphinx",
        "Paver",
        "tw.forms",
        #"WidgetBrowser", # not in PyPi yet
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['WebTest', 'BeautifulSoup'],
    package_data={'moksha': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 'public/*/*']},
    message_extractors = {'moksha': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
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

    [moksha.stream]
    #demo = moksha.streams.demo:MokshaDemoDataStream
    feed = moksha.streams.feed:FeedStream
    #livegraph = moksha.examples.livegraph:LiveGraphDataStream
    moksha_metrics = moksha.widgets.metrics:MokshaMetricsDataStream

    [moksha.consumer]
    feeds = moksha.widgets.feedtree.consumer:MokshaFeedConsumer
    moksha_message_metrics = moksha.widgets.metrics:MokshaMessageMetricsConsumer

    #[moksha.wsgiapp]
    # Use this entry point to mount WSGI applications, which can then be
    # accessed the same as regular apps, through the `/appz/name` url.

    [moksha.application]
    menu = moksha.api.menus.controllers:MokshaMenuController
    chat = moksha.api.widgets.chat.controllers:ChatController
    feeds = moksha.widgets.feedtree.controllers.feed:FeedController

    [moksha.widget]
    chat = moksha.api.widgets.chat:LiveChatWidget
    #livefeed_demo = moksha.widgets.demos:LiveFeedDemo
    #liveflot = moksha.api.widgets.flot:LiveFlotWidget
    #livegraph = moksha.examples.livegraph:LiveGraphWidget
    grid = moksha.api.widgets:Grid
    ptd = moksha.widgets.misc.ptd:ProcessedTowerDefense
    placeholder = moksha.api.widgets:Placeholder
    moksha_container = moksha.widgets.container.container:container
    feeds = moksha.widgets.feedtree:moksha_feedreader
    #moksha_feedreader = moksha.controllers.apps:MokshaFeedReader
    MokshaMemoryUsageWidget = moksha.widgets.metrics:MokshaMemoryUsageWidget
    MokshaCPUUsageWidget = moksha.widgets.metrics:MokshaCPUUsageWidget
    MokshaMessageMetricsWidget = moksha.widgets.metrics:MokshaMessageMetricsWidget

    [moksha.global]

    # The pipeline for our live widgets
    stomp_js = moksha.api.widgets.stomp:stomp_js
    orbited = moksha.api.widgets.orbited:orbited_js

    #jquery = tw.jquery:jquery_js
    #jquery_ui_core = tw.jquery.ui:ui_core_js
    #jquery_ui_dialog = tw.jquery.ui:ui_dialog_min_js
    jquery_ui_draggable = tw.jquery.ui:ui_draggable_min_js
    jquery_ui_resizable = tw.jquery.ui:ui_resizable_min_js
    #jquery_ui_tabs = tw.jquery.ui_tabs:jquery_ui_tabs_js
    #jquery_json_js = fedoracommunity.widgets:jquery_json_js
    #jquery_template_js = fedoracommunity.widgets:jquery_template_js
    #jquery_ui_css = moksha.widgets.jquery_ui_theme:JQueryUITheme

    # Enable support for the Blueprint CSS framework
    #blueprint_ie_css = moksha.widgets.blueprint:blueprint_ie_css
    #blueprint_screen_css = moksha.widgets.blueprint:blueprint_screen_css
    #blueprint_print_css = moksha.widgets.blueprint:blueprint_print_css
    #blueprint_fancytype_css = moksha.widgets.blueprint:blueprint_plugin_fancytype_css

    # up up down down left right left right b a
    konami_js = moksha.widgets.misc.ptd:konami

    [moksha.menu]
    default_menu = moksha.api.menus:MokshaDefaultMenu
    #contextual_menu = moksha.api.menus:MokshaContextMenu
    """,
)
