from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='WidgetBrowser',
      version=version,
      description="ToscaWidgets browser",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='toscawidgets',
      author='Alberto Valverde Gonzalez',
      author_email='alberto@toscat.net',
      url='http://toscawidgets.org/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          "ToscaWidgets>=0.9.2dev-20080602",
          "Genshi",
          "WebOb",
          "docutils",
      ],
      tests_require = ['nose', 'formencode', 'sphinx'],
      extras_require = {
          'full': ['Sphinx', 'Pygments', 'docutils', 'nose', 'WebTest',
                   'WebError', 'coverage', 'FormEncode'],
      },
      entry_points="""
      [console_scripts]
      twbrowser = widgetbrowser.command:browser_command
      [paste.app_factory]
      main = widgetbrowser.wsgiapp:WidgetBrowser
      [toscawidgets.widgets]
      widgets = widgetbrowser.widgets
      """,
      )
