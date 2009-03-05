# Copyright (C) 2007 Adriano Monteiro Marques
#
# Authors: Guilherme Polo <ggpolo@gmail.com>
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
"""
Calendar, this control manages date for Timeline and is also being used
in other pieces of umit.inventory.
"""

import datetime

from umit.core.I18N import _

(INC_YEAR, INC_MONTH, INC_DAY, INC_HOUR) = (
    (DEC_YEAR, DEC_MONTH, DEC_DAY, DEC_HOUR)) = range(4)

months = [
    _("January"), _("February"), _("March"), _("April"), _("May"),
    _("June"), _("July"), _("August"), _("September"),
    _("October"), _("November"), _("December")]

weekdays = [
    _("Monday"), _("Tuesday"), _("Wednesday"), _("Thursday"),
    _("Friday"), _("Saturday"), _("Sunday")]

# Number of days per month (except for February in leap years)
mdays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def monthname(month, first=-1):
    return months[month+first]

def isleap(year):
    """
    Returns True for leap years.
    """
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def startup_calendar_opts():
    """
    Returns a dict to be used as a standard startup dict for CalendarManager.
    """
    methods = ( "year", "month", "day", "hour" )
    datenow = datetime.datetime.now()
    date = { }

    for m in methods:
        date[m] = getattr(datenow, m)

    date["year_range"] = (1970, 3000)

    return date

class Error(Exception):
    pass

class OutOfRangeError(Error):
    pass

class YearOutOfRangeError(OutOfRangeError):
    pass

class YearRangeOutOfRangeError(OutOfRangeError):
    pass

class MonthOutOfRangeError(OutOfRangeError):
    pass

class DayOutOfRangeError(OutOfRangeError):
    pass

class HourOutOfRangeError(OutOfRangeError):
    pass

class FirstWeekdayOutOfRangeError(OutOfRangeError):
    pass

class CalendarManager(object):
    """
    This class control everything related to dates for TimeLine.
    """

    def __init__(self, year, month, day, hour, year_range, first_weekday=0):
        """
        Parameters:

        year                 = initial year (1970-3000)
        month                = initial month (1-12)
        day                  = initial day (1..monthrange)
        hour                 = initial hour (0-23)
        year_range           = year range (n, n) (min 1970, max 3000)
        first_weekday        = first weekday (0 Mon 6 Sun)
        """
        # setting dryrun to True will cause to dates not be modified,
        # setters will just return the new that would be set.
        self.dryrun = False
        self.temp = { } # stores dryrun "changes"

        self.__month_range = (1, 12)
        self.year_range = year_range
        self.year = year
        self.month = month
        self.day = day
        self.fwday = first_weekday
        self.hour = hour


    def get_dryrun(self):
        """
        Get current dryrun status.
        """
        return self.__dryrun


    def set_dryrun(self, enable):
        """
        Enables/Disable dryrun.
        """
        self.__dryrun = enable

        if not self.dryrun:
            # Clean temp dict used to store changes that would be made if
            # dryrun was set to False.
            self.temp = { }


    def validate_date(self, year, month, day, hour):
        pass


    def get_current_firstlast_firstwday(self):
        return self.get_firstlast_firstwday(self.year, self.month)


    def get_firstlast_firstwday(self, year, month):
        """
        Returns the month range (1..n), first month day no. and name, and
        first weekdays in the specified date.
        """
        range_fmday = self.get_monthrange(year, month)
        fwday = self.get_first_weekday()

        fwdays = [ ]
        for day in xrange(1, range_fmday[1]+1):
            weekday = self.get_weekday(year, month, day)[0]
            if weekday == fwday:
                fwdays.append(day)
        fwdays = tuple(fwdays)

        return ((1, range_fmday[1]), (range_fmday[0],
            weekdays[range_fmday[0]]), fwdays)


    def get_date(self, model=None):
        """
        Returns current date set based on a model or using the
        default. Default returns year, month, day, hour, in this order.
        """
        if model:
            try:
                meths = [ ]
                for i in model:
                    meths.append(getattr(self, "get_"+i)())
                return tuple(meths)
            except:
                return self.year, self.month, self.day
        else:
            return self.year, self.month, self.day, self.hour


    def get_current_weekday_name(self):
        """
        Convenience function for get_current_weekday, returns just name
        """
        return self.get_current_weekday()[1]


    def get_current_weekday_no(self):
        """
        Convenience function for get_current_weekday, return just number
        """
        return self.get_current_weekday()[0]


    def get_current_weekday(self):
        """
        Returns weekday day and name for current date.
        """
        self.fix_date()
        return self.get_weekday(self.year, self.month,  self.day)


    def get_weekday(self, year, month, day):
        """
        Returns weekday (0-6 -> Mon-Sun) day and name for a date.
        Year should be at least 1970, month is in range 1..12, and day
        is 1..n.
        """
        if day == 0:
            # silently correct day
            day = 1

        wday = datetime.date(year, month, day).weekday()
        wname = weekdays[wday]
        return wday, wname


    def get_year_range(self):
        """
        Returns current year range.
        """
        return self.__year_range


    def set_year_range(self, yrange):
        """
        Sets new year range
        """
        if yrange[0] < 1970 or yrange[1] > 3000 or yrange[0] >= yrange[1] - 1:
            raise YearRangeOutOfRangeError(yrange)

        if self.dryrun:
            self.temp["year_range"] = yrange
            return

        self.__year_range = yrange


    def get_year(self):
        """
        Returns current year.
        """
        return self.__year


    def set_year(self, year):
        """
        Sets a year.
        """
        if not self.year_range[0] <= year <= self.year_range[1]:
            raise YearOutOfRangeError(year)

        if self.dryrun:
            self.temp["year"] = year
            return

        self.__year = year


    def get_month(self):
        """
        Returns current month.
        """
        return self.__month


    def set_month(self, month):
        """
        Sets a month.
        """
        if not 1 <= month <= 12:
            raise MonthOutOfRangeError(month)

        if self.dryrun:
            self.temp["month"] = month
            return

        self.__month = month

    def get_current_monthrange(self):
        """
        Returns days range for current date.
        """
        month = self.month
        year = self.month
        # When running in dryrun mode use the values that would be changed
        # if not running in this mode.
        if self.dryrun:
            month = self.temp.get('month', year)
            year = self.temp.get('year', year)
        return self.get_monthrange(year, month)


    def get_monthrange(self, year, month):
        """
        Returns days range and first weekday for specified date.
        """
        day1 = self.get_weekday(year, month, 1)[0]
        ndays = mdays[month] + (month == 2 and isleap(year))

        return day1, ndays


    def get_day(self):
        """
        Returns current day.
        """
        return self.__day


    def set_day(self, day):
        """
        Sets a day.
        """
        if not 1 <= day <= self.get_current_monthrange()[1]:
            raise DayOutOfRangeError(day)

        if self.dryrun:
            self.temp["day"] = day
            return

        self.__day = day


    def get_first_weekday(self):
        """
        Returns first weekday.
        """
        return self.__fwday


    def set_first_weekday(self, fwday):
        """
        Sets the first weekday.
        """
        if fwday not in (0, 6):
            raise FirstWeekdayOutOfRangeError(fwday)

        if self.dryrun:
            self.temp["fwday"] = fwday
            return

        self.__fwday = fwday


    def get_hour(self):
        """
        Returns current hour.
        """
        return self.__hour


    def set_hour(self, hour):
        """
        Sets an hour.
        """
        if not 0 <= hour <= 23:
            raise HourOutOfRangeError(hour)

        if self.dryrun:
            self.temp["hour"] = hour
            return

        self.__hour = hour


    def fix_date(self):
        """
        This should be called after setting a date by hand or after
        incrementing/decrementing an year.
        """
        try:
            self.day = self.day
        except DayOutOfRangeError: # changed from leap year to non leap year
            self.day = self.get_current_monthrange()[1]


    def inc_date(self, param, inc=1):
        """
        Increments or decrements a date.
        """
        if inc not in (-1, 1):
            raise Error, "Increment should be -1 or 1"

        if param == INC_YEAR:
            self.__inc_year(inc)

        elif param == INC_MONTH:
            self.__inc_month(inc)

        elif param == INC_DAY:
            self.__inc_day(inc)

        elif param == INC_HOUR:
            self.__inc_hour(inc)


    def dec_date(self, param, inc=-1):
        """
        Just for convenience.
        """
        self.inc_date(param, inc)

    ## Private methods follows.

    def __inc_year(self, inc=1):
        """
        Increments or decrements year.
        """
        try:
            self.year = self.year + inc
        except YearOutOfRangeError:
            self.year = self.year_range[(inc == -1) and 1 or 0]

        self.fix_date()


    def __inc_month(self, inc=1):
        """
        Increments or decrements month.
        """
        try:
            self.month = self.month + inc
        except MonthOutOfRangeError:
            self.__inc_year(inc)
            self.month = self.__month_range[(inc == -1) and 1 or 0]


    def __inc_day(self, inc=1):
        """
        Increments or decrements day.
        """
        try:
            self.day = self.day + inc
        except DayOutOfRangeError:
            self.__inc_month(inc)
            self.day = (inc == -1) and self.get_current_monthrange()[1] or 1

    def __inc_hour(self, inc=1):
        """
        Increments or decrements hour.
        """
        try:
            self.hour = self.hour + inc
        except HourOutOfRangeError:
            self.__inc_day(inc)
            self.hour = (inc == -1) and 23 or 0


    # Properties
    dryrun = property(get_dryrun, set_dryrun)
    year = property(get_year, set_year)
    month = property(get_month, set_month)
    day = property(get_day, set_day)
    fwday = property(get_first_weekday, set_first_weekday)
    hour = property(get_hour, set_hour)
    year_range = property(get_year_range, set_year_range)
