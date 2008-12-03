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
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['WebTest', 'BeautifulSoup'],
    package_data={'moksha': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 'public/*/*']},
    #message_extractors = {'moksha': [
    #        ('**.py', 'python', None),
    #        ('templates/**.mako', 'mako', None),
    #        ('templates/**.html', 'genshi', None),
    #        ('public/**', 'ignore', None)]},

    entry_points="""
    [paste.app_factory]
    main = moksha.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)
