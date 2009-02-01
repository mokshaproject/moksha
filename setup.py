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
        "tw.jquery",
        "repoze.squeeze",
        "repoze.profile",
        "orbited",
        "twisted",
        "stomper",
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

    [paste.app_factory]
    main = moksha.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller

    [moksha.stream]
    demo = moksha.streams.demo:MokshaDemoDataStream
    #livegraph = moksha.examples.livegraph:LiveGraphDataStream
    #feed = moksha.streams.feed:FeedStream

    #[moksha.consumer]
    #moksha = moksha.hub.hub:MokshaConsumer

    [moksha.application]
    menu = moksha.api.menus.controllers:MokshaMenuController

    [moksha.widget]
    liveflot = moksha.api.widgets.flot:LiveFlotWidget
    livefeed = moksha.api.widgets.feed.live:LiveFeedWidget
    #chat = moksha.api.widgets.chat:LiveChatWidget
    #livegraph = moksha.examples.livegraph:LiveGraphWidget
    #grid = moksha.api.widgets:Grid

    [moksha.global]
    # The pipeline for our live widgets
    stomp_js = moksha.api.widgets.stomp:stomp_js
    orbited = moksha.api.widgets.orbited:orbited_js

    jquery = tw.jquery:jquery_js
    jquery_ui_core = moksha.widgets.container:ui_core_js
    jquery_ui_draggable = moksha.widgets.container:ui_draggable_js
    jquery_ui_resizable = moksha.widgets.container:ui_resizable_js
    #jquery_ui_tabs = tw.jquery.ui_tabs:jquery_ui_tabs_js
    #jquery_json_js = fedoracommunity.widgets:jquery_json_js
    #jquery_template_js = fedoracommunity.widgets:jquery_template_js

    # Enable support for the Blueprint CSS framework
    blueprint_ie_css = moksha.widgets.blueprint:blueprint_ie_css
    blueprint_screen_css = moksha.widgets.blueprint:blueprint_screen_css
    blueprint_print_css = moksha.widgets.blueprint:blueprint_print_css

    # Blueprint plugins
    blueprint_fancytype_css = moksha.widgets.blueprint:blueprint_plugin_fancytype_css

    [moksha.menu]
    default_menu = moksha.api.menus:MokshaDefaultMenu
    contextual_menu = moksha.api.menus:MokshaContextMenu
    """,
)
