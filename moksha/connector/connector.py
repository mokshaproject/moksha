# This file is part of Moksha.
#
# Moksha is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Moksha is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Moksha.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2008, Red Hat, Inc.
# Authors: John (J5) Palmieri <johnp@redhat.com>

from utils import QueryPath, QueryCol, ParamFilter, WeightedSearch
from beaker.cache import Cache

""" Data Connector Interfaces

A Data Connector is an object which translate Moksha data requests to the native
protocol of a data resource such as an XMLRPC or json server and then translates
the results into a format the client is expecting.  They can also implement
caching and other data services.  Think of a connector as an intelligent proxy
to external servers.

All Data Connectors must derive and implement the IConnector interface.  All
other interfaces are optional.  Any feature of an interface which is not
implemented (e.g. sorting in the ITable interface) must
raise NotImplementedError if the value is set to anything but None
"""

class IConnector(object):
    """ Data connector interface

    All connectors must derive from this interface
    """
    _method_paths = {}

    def __init__(self, environ=None, request=None):
        super(IConnector, self).__init__()
        self._environ = environ
        self._request = request

    @classmethod
    def register(self):
        """ This method is called when the connector middleware loads the
        connector class for the first time.  Use this to intitalize any
        class level data.  You are responsible for making sure that data
        is thread safe.
        """
        raise NotImplementedError

    @classmethod
    def register_method(cls, method_path, method):
        cls._method_paths[method_path] = method

    def _dispatch(self, op, resource_path, params, _cookies = None, **kwds):
        """ This method is for dispatching to the correct interface which
        is mostly used by the connector engine

        :op: operation to dispatch to (e.g. request_data or query)
        :resource_path: the path to the resource being requested (e.g.
                        the path information in the URL that comes after
                        the base path)
        :params: a dictionary of name value pairs which are sent as
                   parameters in the request (e.g. the query string in a http
                   get request)
        :cookies: a dictionary of name value pairs which are sent as cookies
                  with the request.  If your resource does not use
                  cookies you may use these values how inline with what the
                  resource expects or ignore them completely.

        :Returns:

            the results of the operation requested
        """
        if op in ('request_data', 'call', 'query', 'query_model'):
            return getattr(self, op)(resource_path, params, _cookies, **kwds)
        elif op in self._method_paths:
            _method_paths[op](params, resource_path, _cookies, **kwds)

        return None

    def request_data(self, resource_path, params, _cookies):
        """ Implement this method to request raw data from a URL resource.
        The URL should be set in register and should never change.  You should
        also consider validating the other arguments instead of just passing
        them blindly in the request

        :resource_path: the path to the resource being requested (e.g.
                            the path information in the URL that comes after
                            the base path)
        :params: a dictionary of name value pairs which are sent as
                     parameters in the request (e.g. the query string in a http
                     get request)
        :cookies: a dictionary of name value pairs which are sent as cookies
                      with the request.  If your resource does not use
                      cookies you may use these values how inline with what the
                      resource expects or ignore them completely.

        :Returns:

            Unparsed data from the resource
        """

        raise NotImplementedError

    def introspect(self):
        """ Implement this method to return all available remote resource paths
        along with documentation for each path broken into this format:

        {
          path: {
                  "doc": general documentation,
                  "return": return documentation,
                  "parameters": {
                                  param name: param documentation
                                },
                }
        }

        You may return None if your resource does not have a way to introspect
        it but you must return something.

        To make sure this is not abused in production introspect can be turned
        off with a configuration option
        """

        raise NotImplementedError

class ICall(object):
    """ Method calling interface for resources that return structured data

    Implement ICall if your resource returns data as a structure (e.g. json and
    XMLRPC resources)
    """

    def call(self, resource_path, params, _cookies):
        """ Implement this method to request structured data from a URL
        resource. The URL should be set in register and should never change.
        You should also consider validating the other arguments instead of just
        passing them blindly in the request.  Using request_data and then
        parsing the results into data structures is one way to implement
        this method and reuse code.

        :resource_path: the path to the resource being requested (e.g.
                        the path information in the URL that comes after
                        the base path)
        :params: a dictionary of name value pairs which are sent as
                 parameters in the request (e.g. the query string in a http
                 get request)
        :cookies: a dictionary of name value pairs which are sent as cookies
                  with the request.  If your resource does not use
                  cookies you may use these values how inline with what the
                  resource expects or ignore them completely.

        :Returns:

            Structured data from the resource
        """

        raise NotImplementedError



class IQuery(object):
    """ Query interface for data destined for a table or data grid

    Implement this interface if you want to provide access to data using
    standard query parameters.  Data grids can use this interface to display
    data in a table and provide controls for sorting, filtering, etc.

    In the register method of the Connector it should call the ITable's
    registration interfaces to register path capabilities. See the register_*
    methods for more information.
    """

    _query_paths = {}

    def query(self, resource_path, params, _cookies,
        start_row = 0,
        rows_per_page = 10,
        sort_col = None,
        sort_order = None,
        filters = {}):

        """ Implement this method if the resource provides a query interface.
        The URL should be set in register and should never change.
        You should also consider validating the other arguments instead of just
        passing them blindly in the request.  TODO: Add a validation helper
        method which validates against the registered paths.

        :resource_path: the path to the resource being requested (e.g.
                        the path information in the URL that comes after
                        the base path)
        :params: a dictionary of name value pairs which are sent as
                 parameters in the request (e.g. the query string in a http
                 get request)
        :cookies: a dictionary of name value pairs which are sent as cookies
                  with the request.  If your resource does not use
                  cookies you may use these values how inline with what the
                  resource expects or ignore them completely.
        :start_row: if pagination is supported this sets the row to start at
        :rows_per_page: if pagination is supported this sets how many rows to
                   return
        :sort_col: Which column we should sort by. None = default
        :sort_order: 1 = ascending, -1 = descending
        :filters: a hash of columns and their filters in this format:
                      {
                        colname: {
                                   "value": value,
                                   "op": operator # "=", "<", ">", etc.
                                 }
                      }

                  - or -

                  {
                    colname: value  # assumes =
                  }

        :Returns:
            A hash with format:
                {
                  "total_rows": total_rows, # number of rows matched by query
                  "rows_per_page": rows_per_page,   # number of rows requested
                                            # due to pagination
                  "visible_rows": len(rows) # num of rows actually returned
                  "start_row": start_row,   # number of first row returned due
                                            # to pagination
                  "rows": rows              # list of rows which were returned
                }
        """

        results = None
        r = {
              "total_rows": 0,
              "rows_per_page": 0,
              "start_row": 0,
              "rows": None
            }

        if not sort_col:
            sort_col = self.get_default_sort_col(resource_path)

        if not sort_order:
            sort_order = self.get_default_sort_order(resource_path)

        if params == None:
            params = {}

        query_func = self.query_model(resource_path).get_query()
        (total_rows, rows) = query_func(self,
                                        start_row = start_row,
                                        rows_per_page = rows_per_page,
                                        order = sort_order,
                                        sort_col = sort_col,
                                        filters = filters,
                                        **params)
        r['total_rows'] = total_rows
        r['rows_per_page'] = rows_per_page
        r['visible_rows'] = len(rows)
        if start_row:
            r['start_row'] = start_row
        r['rows'] = rows

        results = r

        return results

    def query_model(self, resource_path, noparams=None, _cookie=None):
        """ Returns the registered model

            :Returns:
                The path's model
        """
        return self._query_paths[resource_path];

    @classmethod
    def register_query(cls,
                      path,
                      query_func,
                      primary_key_col = None,
                      default_sort_col = None,
                      default_sort_order = None,
                      can_paginate = False):

        qpath = QueryPath(path = path,
                          query_func = query_func,
                          primary_key_col = primary_key_col,
                          default_sort_col = default_sort_col,
                          default_sort_order = default_sort_order,
                          can_paginate = can_paginate)

        cls._query_paths[path] = qpath
        return qpath

    def get_capabilities(self):
        return self._query_paths

    def get_default_sort_order(self, path):
        p = self._query_paths.get(path)
        if p:
            return p['default_sort_order']

        return None

    def get_default_sort_col(self, path):
        p = self._query_paths.get(path)
        if p:
            return p['default_sort_col']

        return None

# TODO: Implement these two interfaces
class IFeed(object):
    def request_feed(self, **params):
        pass

class INotify(object):
    def register_listener(self, listener_cb):
        pass

class ISearch(IQuery):
    filters = ParamFilter()
    filters.add_filter('search', ['s'])

    @classmethod
    def register_search_path(cls,
                             path,
                             search_func,
                             primary_key_col = None,
                             default_sort_col = None,
                             default_sort_order = None,
                             can_paginate = True):

        cls._search_cache = fas_cache = Cache('moksha_search_cache_ ' + path)

        def query_func(conn=None,
                       start_row=0,
                       rows_per_page=10,
                       order=-1,
                       sort_col=None,
                       filters={},
                       **params):

            s = WeightedSearch(lambda search_term: search_func(conn, search_term),
                               cls._query_paths[path]['columns'],
                               cls._search_cache)
            search_string = cls.filters.filter(filters).get('search')
            results = s.search(search_string)


            return (len(results), results[start_row:start_row + rows_per_page])

        qpath = cls.register_query(path = path,
                          query_func = query_func,
                          primary_key_col = primary_key_col,
                          default_sort_col = default_sort_col,
                          default_sort_order = default_sort_order,
                          can_paginate = can_paginate)

        return qpath