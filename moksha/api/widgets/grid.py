from tw.api import JSLink
from tw.forms import FormField
from tw.jquery.ui_core import jquery_ui_core_js
from tw.jquery import jQuery, jquery_js
import simplejson as json
import uuid


jquery_json_js = JSLink(filename='public/javascript/jquery.json.js',
                           modname='moksha', javascript=[jquery_js])
jquery_template_js = JSLink(filename='public/javascript/jquery.template.js',
                           modname='moksha', javascript=[jquery_js])
moksha_ui_grid_js = JSLink(filename='public/javascript/ui/moksha.ui.grid.js',
                           modname='moksha',
                           javascript=[jquery_ui_core_js,
                                       jquery_template_js,
                                       jquery_json_js])

class Grid(FormField):
    javascript=[jquery_ui_core_js, moksha_ui_grid_js]
    params= ['rows_per_page', 'page_num', 'total_rows',
            'filters', 'unique_key', 'sort_key', 'sort_order',
            'row_template', 'resource', 'resource_path',
            'loading_throbber', 'uid']
    hidden = True # hide from the moksha main menu

    rows_per_page = 10
    page_num = 1
    total_rows = 0
    filters = {}
    unique_key = None
    sort_key = None
    sort_order = -1
    row_template = None
    resource = None
    resource_path = None
    loading_throbber = None

    def update_params(self, d):
        super(Grid, self).update_params(d)
        if not getattr(d,"id",None):
            raise ValueError, "Moksha Grid is supposed to have id"

        grid_d = {}
        for p in self.params:
            v = d.get(p)
            if v:
                if isinstance(v, dict):
                    v = json.dumps(v)

                grid_d[p] = v

        d['id'] += "-uuid" + str(uuid.uuid4())

        self.add_call(jQuery("#%s" % d['id']).mokshagrid(grid_d))
