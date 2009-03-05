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
            elif el.days < 365:
                when = "%d %s ago" % plural(int(el['days'] / 7), 'week', 'weeks')
            else:
                when = "%d %s ago" % plural(int(el['days'] / 365), 'year', 'years')

        return {'time':time, 'date':date , 'when':when, 'should_hide_time':should_hide_time}

