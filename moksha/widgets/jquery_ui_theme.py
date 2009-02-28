"""
:mod:`moksha.widgets.jquery_ui_theme` - jQuery UI Theme
=======================================================

.. moduleauthor:: Luke Macken <lmacken@redhat.com>
"""

from tw.api import Widget, CSSLink, CSSLink

ui_theme_css = CSSLink(link='/css/jquery-ui/ui.theme.css', modname=__name__)
ui_base_css = CSSLink(link='/css/jquery-ui/ui.base.css',
                      css=[ui_theme_css],
                      modname=__name__)
