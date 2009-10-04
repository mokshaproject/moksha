from tw.api import JSLink, CSSLink, Widget
from tw.jquery import jquery_js

jquery_jgrowl_js = JSLink('jquery_jgrowl_js',
                          filename='static/jquery.jgrowl.js',
                          javascript=[jquery_js],
                          modname=__name__)
jquery_jgrowl_css = CSSLink('jquery_jgrowl_css', 
                            filename='static/jquery.jgrowl.css',
                            modname=__name__)


class MokshaNotificationWidget(Widget):
    javascript = [jquery_jgrowl_js]
    css = [jquery_jgrowl_css]

moksha_notify = MokshaNotificationWidget('moksha_notify')
