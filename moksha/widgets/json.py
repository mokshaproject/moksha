from tw.api import JSLink
from tw.jquery import jquery_js

jquery_json_js = JSLink(modname=__name__,
        filename='static/jquery.json.js',
        javascript=[jquery_js])
