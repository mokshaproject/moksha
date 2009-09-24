import inspect
import simplejson
import pkg_resources

from datetime import timedelta
from moksha.pastetemplate import MokshaConnectorTemplate
from base import QuickstartTester

class TestConnectorQuickstart(QuickstartTester):

    def __init__(self,**options):
        self.app = None
        self.template_vars = {
                'package': 'mokshatest',
                'project': 'mokshatest',
                'egg': 'mokshatest',
                'egg_plugins': ['Moksha'],
        }
        self.args = {
            'connector': True,
            'connector_name': 'MokshatestConnector',
        }
        self.template = MokshaConnectorTemplate
        self.templates = ['moksha.connector']

    def get_connector(self):
        return self.get_entry('moksha.connector')

    def test_entry_point(self):
        assert self.get_connector(), \
                "Cannot find mokshatest on `moksha.connector` entry-point"

    def test_connector_call(self):
        resp = self.app.get('/moksha_connector/mokshatest/call/foo')
        assert "MokshatestConnector.call('foo')" in resp, resp.body

    def test_failed_connector_call(self):
        self.app.get('/moksha_connector/foo', status=404)

    def test_connector_query(self):
        """ Ensure we can perform a basic connector query """
        resp = self.app.get('/moksha_connector/mokshatest/query/query_stuff/')
        json = simplejson.loads(resp.body)
        assert 'rows_per_page' in json
        assert len(json['rows']) == json['total_rows']
        assert json['rows'][0]['id'] == 1
        assert json['rows'][0]['name'] == 'bar'

    def test_connector_query_sorting(self):
        """ Ensure we can perform a basic connector query and sort the results  """
        resp = self.app.get('/moksha_connector/mokshatest/query/query_stuff/{"sort_order":1}')
        json = simplejson.loads(resp.body)
        assert json['rows'][0]['id'] == 0
        assert json['rows'][0]['name'] == 'foo'

    def test_connector_query_filters(self):
        """ Ensure we can perform a basic connector query with a simple filter """
        resp = self.app.get('/moksha_connector/mokshatest/query/query_stuff/{"filters":{"argument":"biz"}}')
        json = simplejson.loads(resp.body)
        assert json['rows'][0]['id'] == 2
        assert json['rows'][0]['name'] == 'biz'

    def test_connector_search(self):
        """ Ensure we can perform a basic connector search """
        resp = self.app.get('/moksha_connector/mokshatest/query/search_stuff/{"filters":{"search":"foobar"}}')
        json = simplejson.loads(resp.body)
        assert json['rows'][0]['name'] == 'foobar'
