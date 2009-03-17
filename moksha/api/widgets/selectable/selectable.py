from tw.api import JSLink, Widget
from tw.jquery.ui_core import jquery_ui_core_js
from tw.jquery import jQuery, jquery_js
from uuid import uuid4


moksha_ui_selectable_js = JSLink(modname='moksha', filename='public/javascript/ui/moksha.ui.selectable.js',
                              javascript=[jquery_ui_core_js])

class Selectable(Widget):
    template = 'mako:moksha.api.widgets.selectable.templates.selectable'
    javascript = [moksha_ui_selectable_js]

    def update_params(self, d):
        super(Selectable, self).update_params(d)
        content_id = d.id + '-uuid' + str(uuid4())
        d['content_id'] = content_id

        self.add_call(jQuery("#%s" % d.content_id).moksha_selectable())

