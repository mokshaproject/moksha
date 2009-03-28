from tw.api import Widget
from tw.jquery import jquery_js
from moksha.lib.helpers import eval_app_config, ConfigWrapper
from tg import config
from tw.api import Widget

from moksha.lib.helpers import eval_app_config, ConfigWrapper

class AppListWidget(Widget):
    template = 'mako:moksha.api.widgets.containers.templates.layout_applist'
    params = ['category']

    def update_params(self, d):
        super(AppListWidget, self).update_params(d)

        # we want to error out if there is no category
        c = d['category']
        if isinstance(c, basestring):
            found = False
            for cat in d['layout']:
                if cat['label'] == c:
                    d['category'] = cat
                    found = True
                    break

            if not found:
                raise IndexError('Category "%s" not found in layout' % c)

applist_widget = AppListWidget('applist');

class DashboardContainer(Widget):
    template = 'mako:moksha.api.widgets.containers.templates.dashboardcontainer'
    params = ['layout', 'applist_widget']
    css = []
    javascript = []
    config_key = None
    layout = []
    applist_widget = applist_widget
    engine_name = 'mako'

    def update_params(self, d):
        super(DashboardContainer, self).update_params(d)
        layout = eval_app_config(config.get(self.config_key, "None"))

        if not layout:
            if isinstance(d.layout, basestring):
                layout = eval_app_config(d.layout)
            else:
                layout = d.layout

        # Filter out any None's in the layout which signify apps which are
        # not allowed to run with the current session's authorization level
        d.layout = ConfigWrapper.process_wrappers(layout, d)

        return d
