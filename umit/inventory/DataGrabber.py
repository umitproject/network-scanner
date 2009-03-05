# Copyright (C) 2007 Adriano Monteiro Marques
#
# Author:  Guilherme Polo <ggpolo@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

import datetime

from umit.core.Paths import Path

from umit.inventory.Calendar import mdays
from umit.inventory.Calendar import isleap
#from umit.inventory.TLBase import view_kind

from umit.db.Connection import ConnectDB
from umit.db.InventoryChanges import ChangesRetrieve

umitdb = Path.umitdb_ng

DATA_GRAB_MODES = {
    "yearly_sum": "changes_in_year",
    "monthly_sum": "changes_in_month",
    "daily_sum": "changes_in_day",
    "hourly_sum": "changes_in_hour",
    "category": "changes_by_category"
    }

class DataGrabber(ConnectDB, ChangesRetrieve):
    """
    Grab data from Inventories or a single host for an Inventory, for a time
    range and format it to be used in Timeline.
    """

    def __init__(self, calendar, inventory=None, hostaddr=None):
        ConnectDB.__init__(self, umitdb)
        ChangesRetrieve.__init__(self, self.conn, self.cursor)

        self.calendar = calendar
        self.inventory = inventory
        self.hostaddr = hostaddr


    def get_categories(self):
        """
        Get all changes categories in database.
        """
        categories = { }

        self.use_dict_cursor()

        # build categories dict
        for category in self.get_categories_id_name():
            categories[category['pk']] = (True, category['name'])

        self.use_standard_cursor()

        return categories


    def standard_sum_filter(self):
        """
        Standard filter to use when we are grabbing data in Changes Sum kind.
        """
        #return {0: (True, view_kind["sum"])}
        return {0: (True, 'changes_sum')}


    def load_changes_for_timerange(self, start, end):
        """
        Load changes from database for a timerange.
        """


    def count_changes_for_timerange(self, start, end):
        """
        Return number of changes in a timerange.
        """
        count = self.timerange_changes_count(start, end)

        return count


    def changes_by_category(self, *args):
        """
        Generic function for changes_anything_by_category
        """
        start = [ ] # start points
        changes = { } # changes in a range
        categories = self.get_categories()

        # grab data
        for category in categories.keys():
            # unused is a filter that we will discard, it is a filter
            # for Changes Sum, but we will return a filter by category.
            #unused, cmax, cstart, \
            (unused, cstart,
            cevts) = self.changes_for_categoryid(category, *args)

            # add new start point to start list
            start.extend(cstart)

            # if changes is empty, set initial values to it
            if not changes:
                changes = cevts
                continue

            # merge lists
            for key, value in cevts.items():
                cur_list = changes[key]
                [cur_list[indx].extend(i) for indx, i in enumerate(value)]
                changes[key] = cur_list

        # decrement by one each key in categories dict, so it follows filter
        # format used in other places. (0 .. n)
        c_new = { }
        for key, values in categories.items():
            c_new[key - 1] = values

        return c_new, start, changes


    def changes_for_categoryid(self, category, *args):
        """
        Generic function for changes_anything_for_categoryid
        """
        return self.changes_in_range(category, *args)


    def changes_in_range(self, category=None, *args):
        """
        Generic function for changes_anything
        """
        if len(args) == 1: # yearly
            return self.changes_in_year(args[0], category)
        elif len(args) == 2: # monthly
            return self.changes_in_month(args[0], args[1], category)
        elif len(args) == 3: # daily
            return self.changes_in_day(args[0], args[1], args[2], category)
        elif len(args) == 4: # hourly
            return self.changes_in_hour(args[0], args[1], args[2], args[3],
                category)
        else:
            raise Exception("Invalid number of parameters especified")


    """
    Follows changes_in_range especific methods, I plan making them
    generic too.
    """


    def changes_in_year(self, year, category=None):
        """
        Gets changes per "week" in an entire year.
        """
        if isleap(year):
            mdays[2] = 29
        else:
            mdays[2] = 28

        # get last amount of events in past year, or, better:
        # amount of events that occuried in (year - 1) at December, from
        # numberOfDaysInDecember / 2 + (numberOfDaysInDecember / 4) till
        # final of month.

        if year == self.calendar.year_range[0]:
            start_value = 0

        else:
            half = mdays[12] / 2
            quarter = half / 2
            start = datetime.datetime(year - 1, 12, quarter + half)
            end = datetime.datetime(year, 1, 1)

            start_value = self.timerange_changes_count_generic(start, end,
                category, self.inventory, self.hostaddr)

        # get events for year
        year_events = { }

        for m in range(12):
            half = (mdays[m + 1] / 2) + 1
            quarter = (half / 2)

            # months with 31 or 30 days:
            # half = (31/2) + 1 = 16
            # quarter = 8
            # will grab 1 -> 8, 8 -> 16, 16 -> 24, 24 -> end month
            # month with 28 or 29 days:
            # half = (29/2) + 1 = 15
            # quarter = 7
            # will grab 1 -> 7, 7 -> 15, 15 -> 22, 22 -> end month

            days = (1, quarter, half, half + quarter, 1)

            mcount = [ ]

            for i in range(len(days) - 1):
                start = datetime.datetime(year, m + 1, days[i])

                if i == len(days) - 2:
                    dyear = year
                    dmonth = m + 2
                    if m == 11:
                        dyear += 1
                        dmonth = 1

                    end = datetime.datetime(dyear, dmonth, days[i + 1])
                else:
                    end = datetime.datetime(year, m + 1, days[i + 1])

                count = self.timerange_changes_count_generic(start, end,
                    category, self.inventory, self.hostaddr)

                mcount.append([count, ])

            year_events[m] = mcount


        return self.standard_sum_filter(), (start_value, ), year_events


    def changes_in_month(self, year, month, category=None):
        """
        Get changes in a month.
        """
        month_events = { }

        if isleap(year) and month == 2: # month range from 1 to 12
            mdays[2] = 29
        else:
            mdays[2] = 28

        # get last amount of events in past month, or, better:
        # amount of events that occuried in (month - 1) at last day, from
        # 12 PM to 23:59 PM
        self.calendar.dryrun = True
        self.calendar.dec_date(1) # 1 indicates it is a month decrement
        prev_date = self.calendar.temp # what changes were needed to decrement
        self.calendar.dryrun = False

        prev_year = year
        prev_month = month

        for key, value in prev_date.items():
            if key == "year":
                prev_year = value
            elif key == "month":
                prev_month = value

        month_range = self.calendar.get_monthrange(prev_year, prev_month)[1]
        start = datetime.datetime(prev_year, prev_month, month_range, 12)
        end = datetime.datetime(year, month, 1)

        start_value = self.timerange_changes_count_generic(start, end,
            category, self.inventory, self.hostaddr)

        for day in range(mdays[month]):
            day_count = [ ]

            # for each day, grab data for 0 AM .. 11:59 AM, 12 PM .. 23:59 PM
            start = datetime.datetime(year, month, day + 1)
            end = datetime.datetime(year, month, day + 1, 12)

            count1 = self.timerange_changes_count_generic(start, end,
                category, self.inventory, self.hostaddr)

            start = datetime.datetime(year, month, day + 1, 12)

            dyear = year
            dmonth = month
            dday = day

            if day == mdays[month] - 1:
                self.calendar.dryrun = True
                self.calendar.inc_date(1)
                next_date = self.calendar.temp
                self.calendar.dryrun = False

                dday = 1
                for key, value in next_date.items():
                    if key == "year":
                        dyear = value
                    elif key == "month":
                        dmonth = value

            else:
                dday += 2

            end = datetime.datetime(dyear, dmonth, dday)

            count2 = self.timerange_changes_count_generic(start, end,
                category, self.inventory, self.hostaddr)

            day_count.append([count1, ])
            day_count.append([count2, ])
            month_events[day] = day_count


        return self.standard_sum_filter(), (start_value, ), month_events


    def changes_in_day(self, year, month, day, category=None):
        """
        Get changes in a day.
        """
        day_events = { }

        # get last amount of events in past day, or, better:
        # amount of events that occuried in (day - 1) at last hour, from
        # 23:30 to current date 0 hour, 0 minute, 0 second
        self.calendar.dryrun = True
        self.calendar.dec_date(2) # 2 indicates it is a day decrement
        prev_date = self.calendar.temp # what changes were needed to decrement
        self.calendar.dryrun = False

        prev_year = year
        prev_month = month
        prev_day = day - 1

        for key, value in prev_date.items():
            if key == "year":
                prev_year = value
            elif key == "month":
                prev_month = value
            elif key == "day":
                prev_day = value

        start = datetime.datetime(prev_year, prev_month, prev_day, 23, 30)
        end = datetime.datetime(year, month, day)

        start_value = self.timerange_changes_count_generic(start, end,
            category, self.inventory, self.hostaddr)

        # hour by hour
        for hour in range(24):
            hour_count = [ ]

            # first half hour
            start = datetime.datetime(year, month, day, hour)
            end = datetime.datetime(year, month, day, hour, 30)

            count1 = self.timerange_changes_count_generic(start, end,
                category, self.inventory, self.hostaddr)

            # other half
            start = datetime.datetime(year, month, day, hour, 30)

            if hour == 23:
                next_year = year
                next_month = month
                next_day = day

                self.calendar.dryrun = True
                self.calendar.inc_date(2)
                next_date = self.calendar.temp
                self.calendar.dryrun = False

                for key, value in next_date.items():
                    if key == "year":
                        next_year = value
                    elif key == "month":
                        next_month = value
                    elif key == "day":
                        next_day = value

                end = datetime.datetime(next_year, next_month, next_day, 0)

            else:
                end = datetime.datetime(year, month, day, hour + 1)

            count2 = self.timerange_changes_count_generic(start, end,
                category, self.inventory, self.hostaddr)

            hour_count.append([count1])
            hour_count.append([count2])

            day_events[hour] = hour_count


        return self.standard_sum_filter(), (start_value, ), day_events


    def changes_in_hour(self, year, month, day, hour, category=None):
        """
        Get changes in a especific hour.
        """
        hour_events = { }

        # get last amount of events in past hour, or, better:
        # amount of events that occuried in (hour - 1) at last minute
        self.calendar.dryrun = True
        self.calendar.dec_date(3) # 3 indicates it is an hour decrement
        prev_date = self.calendar.temp # what changes were needed to decrement
        self.calendar.dryrun = False

        prev_year = year
        prev_month = month
        prev_day = day
        prev_hour = hour - 1

        for key, value in prev_date.items():
            if key == "year":
                prev_year = value
            elif key == "month":
                prev_month = value
            elif key == "day":
                prev_day = value
                prev_hour = 23

        start = datetime.datetime(prev_year, prev_month, prev_day, prev_hour,
            59)
        end = datetime.datetime(year, month, day, hour, 0)

        start_value = self.timerange_changes_count_generic(start, end,
            category, self.inventory, self.hostaddr)

        # minute by minute
        for minute in range(60):
            start = datetime.datetime(year, month, day, hour, minute)

            if minute == 59:
                next_year = year
                next_month = month
                next_day = day
                next_hour = hour + 1

                self.calendar.dryrun = True
                self.calendar.inc_date(3)
                next_date = self.calendar.temp
                self.calendar.dryrun = False

                for key, value in next_date.items():
                    if key == "year":
                        next_year = value
                    elif key == "month":
                        next_month = value
                    elif key == "day":
                        next_day = value
                        next_hour = 0

                end = datetime.datetime(next_year, next_month, next_day,
                    next_hour)
            else:
                end = datetime.datetime(year, month, day, hour, minute + 1)

            count = self.timerange_changes_count_generic(start, end,
                category, self.inventory, self.hostaddr)

            hour_events[minute] = [[count, ]]


        return self.standard_sum_filter(), (start_value, ), hour_events



if __name__ == "__main__":
    #dg.count_changes_for_timerange(datetime.datetime(2007, 1, 1),
    #                  datetime.datetime(2007, 1, 31, 23, 59, 59, 999))
    #lfilter, max_v, start, evts = dg.changes_in_year(2007)
    #print max_v, start, evts

    # some methods from ChangesRetrieve
    #print dg.get_categories_id_name()
    #print dg.get_categories_name()
    #print dg.get_category_id_by_name('Fingerprint')
    #print dg.get_category_name_by_id(1)

    #max_v, start, evts = dg.changes_for_categoryid(2007, 1)
    #print max_v, start, evts

    from umit.inventory.Calendar import startup_calendar_opts
    from umit.inventory.Calendar import CalendarManager

    start = startup_calendar_opts()
    cal = CalendarManager(**start)

    lfilter, max_v, start, evts = DataGrabber(cal).changes_in_year(2007)
    print lfilter, max_v, start, evts[6]

    #lfilter, max, start, evts = DataGrabber(cal).changes_by_category(2007, 7)
    lfilter, max_v, start, evts = DataGrabber(cal).changes_in_month(2007, 7)

    for key, value in evts.items():
        print key, value
