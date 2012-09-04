# This file is part of Moksha.
# Copyright (C) 2008-2010  Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import datetime


def utc_offset(tz):
    """ Return the UTC offset for a given timezone.

        >>> utc_offset('US/Eastern')
        '-4'

    """
    utc_offset = ''
    now = datetime.now(utc)
    now = now.astimezone(timezone(tz))
    offset = now.strftime('%z')
    if offset.startswith('-'):
        offset = offset[1:]
        utc_offset += '-'
    hours = int(offset[:2])
    utc_offset += str(hours)
    # FIXME: account for minutes?
    #minutes = int(offset[2:])
    #if minutes:
    #    utc_offset += '.%d' % ...
    return utc_offset


class DateTimeDisplay(object):
    """
    DateTimeDisplay is an object which takes any number of datetime objects
    and process them for display::

        >>> from datetime import datetime
        >>> now = datetime(2009, 5, 12)
        >>> later = datetime(2009, 5, 13)
        >>> d = DateTimeDisplay(now)
        >>> print d
        2009-05-12 00:00:00
        >>> d.age(later)
        '1 day'
        >>> d.age(datetime(2010, 7, 10, 10, 10), granularity='minute')
        '1 year, 1 month, 29 days, 10 hours and 10 minutes'
        >>> d.age(datetime(2010, 7, 10, 10, 10), tz='Europe/Amsterdam')
        '1 year, 1 month, 29 days and 10 hours'
        >>> d = DateTimeDisplay(datetime(2009, 5, 12, 12, 0, 0))
        >>> d.timestamp
        datetime.datetime(2009, 5, 12, 12, 0)
        >>> d.astimezone('Europe/Amsterdam')
        datetime.datetime(2009, 5, 12, 14, 0, tzinfo=<DstTzInfo 'Europe/Amsterdam' CEST+2:00:00 DST>)

    """
    def __init__(self, timestamp, format='%Y-%m-%d %H:%M:%S'):
        if isinstance(timestamp, basestring) and '.' in timestamp:
            timestamp = timestamp.split('.')[0]
        self.timestamp = timestamp
        if isinstance(timestamp, datetime.datetime):
            self.datetime = timestamp
        elif isinstance(timestamp, time.struct_time):
            self.datetime = datetime.datetime(*timestamp[:-2])
        elif isinstance(timestamp, basestring):
            if hasattr(datetime, 'strptime'): # Python 2.5+
                self.datetime = datetime.datetime.strptime(timestamp, format)
            else: # Python 2.4
                self.datetime = datetime.datetime(*time.strptime(timestamp, format)[:-2])
        else:
            raise Exception("You must provide either a datetime object or a"
                            "string, not %s" % type(timestamp))

    def astimezone(self, tz):
        """ Return `self.datetime` as a different timezone """
        timestamp = self.datetime.replace(tzinfo=utc)
        zone = timezone(tz)
        return zone.normalize(timestamp.astimezone(zone))

    def age(self, end=None, tz=None, granularity='hour', general=False):
        """
        Return the distance of time in words from `self.datetime` to `end`.

            >>> start = datetime(1984, 11, 02)
            >>> now = datetime(2009, 5, 22, 12, 11, 10)
            >>> DateTimeDisplay(start).age(now)
            '2 decades, 4 years, 6 months, 20 days and 12 hours'
            >>> DateTimeDisplay(start).age(now, general=True)
            '2 decades'

        """
        start = self.datetime
        if not end:
            end = datetime.datetime.utcnow()
        else:
            if isinstance(end, DateTimeDisplay):
                end = end.datetime
        if tz:
            zone = timezone(tz)
            end = end.replace(tzinfo=utc)
            end = zone.normalize(end.astimezone(zone))
            start = self.astimezone(tz)

        age = distance_of_time_in_words(start, end, granularity=granularity)

        if general:
            if not age.startswith('less than'):
                age = age.split('and')[0].split(',')[0]

        return age

    def __str__(self):
        return self.datetime.strftime('%Y-%m-%d %H:%M:%S %Z%z')

    def __repr__(self):
        return "<DateTimeDisplay %r>" % self.datetime

# The following functions were all copied *wholesale* from webhelpers.date

def _process_carryover(deltas, carry_over):
    """A helper function to process negative deltas based on the deltas
    and the list of tuples that contain the carry over values"""
    for smaller, larger, amount in carry_over:
        if deltas[smaller] < 0:
            deltas[larger] -= 1
            deltas[smaller] += amount


def _pluralize_granularity(granularity):
    """Pluralize the given granularity"""
    if 'century' == granularity:
        return "centuries"
    return granularity + "s"


def _delta_string(delta, granularity):
    """Return the string to use for the given delta and ordinality"""
    if 1 == delta:
        return "1 " + granularity
    elif delta > 1:
        return str(delta) + " " + _pluralize_granularity(granularity)


def _is_leap_year(year):
    if year % 4 == 0 and year % 400 != 0:
        return True
    return False


def distance_of_time_in_words(from_time, to_time=0, granularity="second",
                              round=False):
    """
    Return the absolute time-distance string for two datetime objects,
    ints or any combination you can dream of.

    If times are integers, they are interpreted as seconds from now.

    ``granularity`` dictates where the string calculation is stopped.
    If set to seconds (default) you will receive the full string. If
    another accuracy is supplied you will receive an approximation.
    Available granularities are:
    'century', 'decade', 'year', 'month', 'day', 'hour', 'minute',
    'second'

    Setting ``round`` to true will increase the result by 1 if the fractional
    value is greater than 50% of the granularity unit.

    Examples:

    >>> distance_of_time_in_words(86399, round=True, granularity='day')
    '1 day'
    >>> distance_of_time_in_words(86399, granularity='day')
    'less than 1 day'
    >>> distance_of_time_in_words(86399)
    '23 hours, 59 minutes and 59 seconds'
    >>> distance_of_time_in_words(datetime(2008,3,21, 16,34),
    ... datetime(2008,2,6,9,45))
    '1 month, 15 days, 6 hours and 49 minutes'
    >>> distance_of_time_in_words(datetime(2008,3,21, 16,34),
    ... datetime(2008,2,6,9,45), granularity='decade')
    'less than 1 decade'
    >>> distance_of_time_in_words(datetime(2008,3,21, 16,34),
    ... datetime(2008,2,6,9,45), granularity='second')
    '1 month, 15 days, 6 hours and 49 minutes'
    """
    granularities = ['century', 'decade', 'year', 'month', 'day', 'hour',
                     'minute', 'second']

    # 15 days in the month is a gross approximation, but this
    # value is only used if rounding to the nearest month
    granularity_size = {'century': 10, 'decade': 10, 'year': 10, 'month': 12,
                        'day': 15, 'hour': 24, 'minute': 60, 'second': 60 }

    if granularity not in granularities:
        raise ValueError("Please provide a valid granularity: %s" %
                        (granularities))

    # Get everything into datetimes
    if isinstance(from_time, int):
        from_time = datetime.datetime.fromtimestamp(time.time()+from_time)

    if isinstance(to_time, int):
        to_time = datetime.datetime.fromtimestamp(time.time()+to_time)

    # Ensure that the to_time is the larger
    if from_time > to_time:
        s = from_time
        from_time = to_time
        to_time = s
    # Stop if the tiems are equal
    elif from_time == to_time:
        return "0 " + _pluralize_granularity(granularity)

    # Collect up all the differences
    deltas = {'century': 0, 'decade': 0, 'year': 0, 'month': 0, 'day': 0,
              'hour': 0, 'minute': 0, 'second' : 0}

    # Collect the easy deltas
    for field in ['month', 'hour', 'day', 'minute', 'second']:
        deltas[field] = getattr(to_time,field) - getattr(from_time,field)

    # deal with year, century and decade
    delta_year = to_time.year - from_time.year
    if delta_year >= 100:
        deltas['century'] = delta_year // 100
    if delta_year % 100 >= 10:
        deltas['decade'] = delta_year // 10 - deltas['century'] * 10
    if delta_year % 10:
        deltas['year'] = delta_year % 10

    # Now we need to deal with the negative deltas, as we move from
    # the smallest granularity to the largest when we encounter a negative
    # we will 'borrow' from the next highest value.  Because to_time is
    # the larger of the two,
    carry_over = [('second', 'minute', granularity_size['second']),
                  ('minute', 'hour', granularity_size['minute']),
                  ('hour', 'day', granularity_size['hour'])]

    _process_carryover(deltas, carry_over)

    # Day is its own special animal.  We need to deal with negative days
    # differently depending on what months we are spanning across.  We need to
    # look up the from_time.month value in order to bring the number of days
    # to the end of the month.
    month_carry = [None, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if deltas['day'] < 0:
        deltas['month'] -= 1
        # Deal with leap years
        if (from_time.month) == 2 and _is_leap_year(from_time.year):
            deltas['day'] += 29
        else:
            deltas['day'] += month_carry[from_time.month]

    carry_over = [('month', 'year', granularity_size['month']),
                  ('year', 'decade', granularity_size['year']),
                  ('decade', 'century', granularity_size['decade'])]

    _process_carryover(deltas, carry_over)

    # Display the differences we care about, at this point we should only have
    # positive deltas
    return_strings = []
    for g in granularities:
        delta = deltas[g]
        # This is the finest granularity we will display
        if g == granularity:
            # We can only use rounding if the granularity is higher than
            # seconds
            if round and g != 'second':
                i = granularities.index(g)
                # Get the next finest granularity and it's delta
                g_p = granularities[i + 1]
                delta_p = deltas[g_p]
                # Determine if we should round up
                if delta_p > granularity_size[g_p] / 2:
                    delta += 1

                if delta != 0:
                    return_strings.append(_delta_string(delta, g))

                if not return_strings:
                    return "less than 1 " + granularity
                break

            else:
                if delta != 0:
                    return_strings.append(_delta_string(delta, g))

                # We're not rounding, check to see if we have encountered
                # any deltas to display, if not our time difference
                # is less than our finest granularity
                if not return_strings:
                    return "less than 1 " + granularity
                break
        # Read the value and continue
        else:
            if delta != 0:
                return_strings.append(_delta_string(delta, g))

    if len(return_strings) == 1:
        return return_strings[0]
    return ", ".join(return_strings[:-1]) + " and " + return_strings[-1]


def time_ago_in_words(from_time, granularity="second", round=False):
    """
    Return approximate-time-distance string for ``from_time`` till now.

    Same as ``distance_of_time_in_words`` but the endpoint is now.
    """
    return distance_of_time_in_words(from_time, datetime.datetime.now(),
        granularity, round)

