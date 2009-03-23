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
# Copyright 2009, Red Hat, Inc.
# Authors: John (J5) Palmieri <johnp@redhat.com>

from datetime import datetime, timedelta
from UserDict import DictMixin

import bisect

class DateTimeDisplay(object):
    """DateTimeDisplay is an object which takes any number of datetime objects
    and process them for display.
    """
    def __init__(self, *datetime_args):
        # All dates are sorted from latest to earliest
        self._datetime_ordered_list = []
        for dt in datetime_args:
            # convert if not a datetime object
            insert_dt = None
            if isinstance(dt, datetime):
                insert_dt = dt
            elif isinstance(dt, basestring):

                insert_dt = datetime.strptime(dt.rsplit('.', 1)[0],
                                              '%Y-%m-%d %H:%M:%S')

            bisect.insort(self._datetime_ordered_list, insert_dt)

    def __len__(self):
        return len(self._date_time_ordered_list)

    def time_elapsed(self, start_time_index, finish_time_index=None):
        startt = self._datetime_ordered_list[start_time_index]
        finisht = datetime.utcnow()
        if finish_time_index != None:
            finisht = self._datetime_ordered_list[finish_time_index]

        deltat = finisht - startt

        days = deltat.days
        hours = int(deltat.seconds / 3600)
        minutes = int((deltat.seconds - hours * 3600) / 60)
        seconds = deltat.seconds - minutes * 60
        display = ''
        if days:
            display = '%d d %d h %d m' % (days, hours, minutes)
        elif hours:
            display = '%d h %d m' % (hours, minutes)
        elif minutes:
            display = '%d m' % minutes
        else:
            display = '%d s' % seconds


        return ({'days': days, 'minutes': minutes,
                 'seconds': seconds, 'display': display})

    def when(self, index, time_format="%I:%M %p", date_format="%d %b %Y"):
        dt = self._datetime_ordered_list[index]
        time = dt.time().strftime(time_format)
        date = dt.date().strftime(date_format)

        el = self.time_elapsed(index)
        when = None
        should_hide_time = False
        if el['days'] == 0:
            when = 'Today'
        elif el['days'] == 1:
            when = 'Yesterday'
        else:
            should_hide_time = True

            def plural(i, singular, plural):
                word = (i == 1) and singular or plural
                return (i, word)

            if el['days'] < 7:
                when = "%d %s ago" % plural(el['days'], 'day', 'days')
            elif el['days'] < 365:
                when = "%d %s ago" % plural(int(el['days'] / 7), 'week', 'weeks')
            else:
                when = "%d %s ago" % plural(int(el['days'] / 365), 'year', 'years')

        return {'time':time, 'date':date , 'when':when, 'should_hide_time':should_hide_time}

class odict(DictMixin):

    def __init__(self):
        self._keys = []
        self._data = {}

    def index(self, i):
        k = self._keys[i]
        return self._data[k]

    def key_index(self, i):
        return self._keys[i]

    def __setitem__(self, key, value):
        if key not in self._data:
            self._keys.append(key)

        self._data[key] = value

    def __getitem__(self, key):
        return self._data[key]

    def __delitem__(self, key):
        del self._data[key]
        self._keys.remove(key)

    def __iter__(self):
        for key in self._keys:
            yield key

    def keys(self):
        return list(self._keys)

    def copy(self):
        copyDict = odict()
        copyDict._data = self._data.copy()
        copyDict._keys = self._keys[:]
        return copyDict

    def __repr__(self):
        result = []
        for key in self._keys:
            result.append('(%s, %s)' % (repr(key), repr(self._data[key])))
        return ''.join(['OrderedDict', '([', ', '.join(result), '])'])

class QueryCol(dict):
    def __init__(self,
                 column,
                 default_visible,
                 can_sort,
                 can_filter_wildcards):
        super(QueryCol, self).__init__(column = column,
                                       default_visible = default_visible,
                                       can_sort = can_sort,
                                       can_filter_wildcards = can_filter_wildcards)

class QueryPath(dict):
    def __init__(self,
                 path,
                 query_func,
                 primary_key_col,
                 default_sort_col,
                 default_sort_order,
                 can_paginate):
        super(QueryPath, self).__init__(
                         path = path,
                         query_func = query_func,
                         primary_key_col = primary_key_col,
                         default_sort_col = default_sort_col,
                         default_sort_order = default_sort_order,
                         can_paginate = can_paginate,
                         columns=odict())

    def register_column(self,
                        column,
                        default_visible = True,
                        can_sort = False,
                        can_filter_wildcards = False):

        self["columns"][column] = QueryCol(
                column = column,
                default_visible = default_visible,
                can_sort = can_sort,
                can_filter_wildcards = can_filter_wildcards
              )

    def get_query(self):
        return self['query_func']

class ParamFilter(object):
    """Helper class for filtering query arguments"""

    def __init__(self):
        self._translation_table = {}
        self._param_table = {}

    def add_filter(self, param, args=[], cast=None, allow_none=True, filter_func=None):
        pf = {}
        if cast:
            assert(isinstance(cast, type),
                   "cast should be of type <type> not cast %s" % str(type(cast)))

            pf['cast'] = cast

        pf['allow_none'] = allow_none
        pf['filter_func'] = filter_func

        self._param_table[param] = pf
        args.append(param)
        for a in args:
            assert(not(a in self._translation_table),
                   '''The argument %s has been registered for more than
                   one parameter translation''' % (a)
                   )

            self._translation_table[a] = param

    def filter(self, d, conn=None):
        results = {}
        for k, v in d.iteritems():
            if k in self._translation_table:
                param = self._translation_table[k]
                allow_none = True
                assign = True
                if param in self._param_table:
                    pf = self._param_table[param]
                    cast = pf.get('cast')
                    if cast == bool:
                        if isinstance(v, basestring):
                            lv = v.lower()
                            if lv in ('t', 'y', 'true', 'yes'):
                                v = True
                            else:
                                v = False
                        elif not isinstance(v, bool):
                            v = False
                    elif cast:
                        v = cast(v)

                    allow_none = pf['allow_none']

                    ff = pf['filter_func']
                    if ff:
                        ff(conn, results, k, v, allow_none)
                        assign = False

                    if (allow_none or (v != None)) and assign:
                        results[param] = v

        return results

class WeightedSearch(object):
    # FIXME: Need to dial in the weighting algorithm
    CACHE_EXPIRE_TIME = 30 * 60
    LIGHT_WEIGHT = 10
    MEDIUM_WEIGHT = 30
    HEAVY_WEIGHT = 100

    def __init__(self, search_func, cols, cache=None):
            self.search_func = search_func
            self.cache = cache
            self.cols = cols

    def weigh(self, search_term, weighted_hash):
        search_term_len = len(search_term)
        l = len(self.cols)

        # each field gets a decelerating percentage of it's calculated weight
        # e.g. each consecutive field is an order of magnatude less important
        # than the previous field
        factor = 1/sum(xrange(l))

        r = weighted_hash[0]
        for i, result_field in enumerate(self.cols):
            x = l - i
            weight_factor = x * factor

            l_result_field = r[result_field].lower()
            index = l_result_field.find(search_term)

            while(index != -1):
                weighted_hash[1] += self.LIGHT_WEIGHT * weight_factor
                if index == 0:
                    # in front
                    weighted_hash[1] += self.MEDIUM_WEIGHT * weight_factor
                    if search_term_len == len(l_result_field):
                        weighted_hash[1] += self.HEAVY_WEIGHT

                if index + search_term_len == l:
                    # in back
                    weighted_hash[1] += self.MEDIUM_WEIGHT * weight_factor

                index = l_result_field.find(search_term, index + 1)

    def weighted_sort(self, a, b):
        result = 0
        (a_val, a_weight) = a
        (b_val, b_weight) = b

        result = -cmp(a_weight, b_weight)
        if result == 0:
            result = cmp(a_val[self.cols.key_index(0)], b_val[self.cols.key_index(0)])
        return result

    def search(self, search_string):
        if not search_string:
            return []

        search = search_string.lower().replace(',', ' ').split()

        weighted_results = {}
        for s in search:
            results = self.cache.get_value(key = s,
                               createfunc=lambda : self.search_func(s),
                               type="memory",
                               expiretime=self.CACHE_EXPIRE_TIME)

            for r in results:
                rkey = r[self.cols.key_index(0)]

                # if we have already weighted this result get the
                # weighted hash to add weight to
                # else we create a new weighted hash
                if rkey in weighted_results:
                    weighted_hash = weighted_results[rkey]
                else:
                    weighted_hash = [r, 0]


                self.weigh(s, weighted_hash)
                weighted_results[rkey] = weighted_hash

        sorted_list = weighted_results.values()
        sorted_list.sort(self.weighted_sort)

        for i, v in enumerate(sorted_list):
            sorted_list[i] = v[0]

        return sorted_list






