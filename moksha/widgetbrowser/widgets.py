from tw.api import Widget, JSLink, CSSLink, js_function
from moksha.widgetbrowser import util
import string

__all__ = ['WidgetBrowserTabs']

mod = __name__
#mod = 'widgetbrowser'
flora_all_css = CSSLink(modname=mod, filename="static/themes/flora/flora.all.css")
tabs_css = CSSLink(modname=mod, filename="static/ui.tabs.css")
wb_css = CSSLink(modname=mod, filename="static/widgetbrowser.css")
pygments_css = CSSLink(modname=mod, filename="static/pygments.css")
httprepl_css = CSSLink(modname=mod, filename="static/httprepl.css")
jquery_js = JSLink(modname=mod, filename="static/jquery.js")
# Do not pull jquery as an automatic dependency since Sphinx already includes
# it
ui_base_js = JSLink(modname=mod, filename="static/ui.base.js",
                    location="bodybottom")
ui_tabs_js = JSLink(modname=mod, filename="static/ui.tabs.js",
                    location="bodybottom",
                    javascript=[ui_base_js])
ui_dragabble_js = JSLink(modname=mod, filename="static/ui.draggable.js",
                         location="bodybottom")
ui_resizable_js = JSLink(modname=mod, filename="static/ui.resizable.js",
                         location="bodybottom")
ui_dialog_js = JSLink(modname=mod, filename="static/ui.dialog.js",
                      location="bodybottom",
                      javascript=[ui_base_js, ui_dragabble_js, ui_resizable_js])
widgetbrowser_js = JSLink(modname=mod, filename="static/widgetbrowser.js",
                          javascript=[ui_tabs_js],
                          css=[tabs_css, wb_css, pygments_css],
                          location="bodybottom")

httprepl_js = JSLink(modname=mod, filename='static/httprepl.js',
                     javascript=[ui_dialog_js],
                     css=[httprepl_css],
                     location="bodybottom")

class WidgetBrowserTabs(Widget):
    template = "genshi:moksha.widgetbrowser.templates.widget_browser_tabs"
    params = ["tabs", "prefix", "size", "in_sphinx"]
    in_sphinx = False
    javascript = [widgetbrowser_js]
    size = "small"
    tabs = ['demo', 'demo_source', 'source', 'template', 'parameters']
    prefix = None
     
    def update_params(self, d):
        super(WidgetBrowserTabs, self).update_params(d)
        d.tabs = [(string.capwords(t.replace('_', ' ')), util.widget_url(d.value, t, prefix=d.prefix))
                  for t in d.tabs]
        if not d.in_sphinx:
            # Not displayed inside Sphinx, include jquery and pygments
            jquery_js.inject()
            pygments_css.inject()


class WidgetRepl(Widget):
    template = '<div id="$id" class="$css_class"></div>'
    params = ["prefix"]
    prefix = '/_repl/' # show nicely in the browser tabs
    include_dynamic_js_calls = True
    javascript = [jquery_js, httprepl_js]
    css = [flora_all_css]
    def update_params(self, d):
        super(WidgetRepl, self).update_params(d)
        assert d.id, "This widget needs an id"
        config = dict(prefix=d.prefix)
        call = js_function('HTTPRepl.render')('#'+d.id, config)
        self.add_call("jQuery(function () {%s});" %  call)

repl = WidgetRepl("widgetrepl")
