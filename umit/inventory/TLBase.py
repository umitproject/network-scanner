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

import datetime

from umit.core.I18N import _
from umit.core.Paths import Path
#from umit.core.UmitConfigParser import UmitConfigParser # stopped working here
from ConfigParser import ConfigParser

from umit.inventory.Calendar import CalendarManager
from umit.inventory.Calendar import months
from umit.inventory.Calendar import monthname
from umit.inventory.Calendar import startup_calendar_opts
from umit.inventory.DataGrabber import DataGrabber
from umit.inventory.DataGrabber import DATA_GRAB_MODES

settings_file = Path.tl_conf
#configparser = UmitConfigParser()
configparser = ConfigParser()
configparser.read(settings_file)

changes_in_db = {
        'nothing': _("Nothing"),
        'inventory': _("Inventory"),
        'availability': _("Availability"),
        'several': _("Several"),
        'fingerprint': _("Fingerprint"),
        'ports': _("Ports")
        }

categories = dict(changes_in_db)
categories['changes_sum'] = _("Changes Sum")

changes_list = changes_in_db.keys()

view_mode = {
    "yearly": _("Yearly View"),
    "monthly": _("Monthly View"),
    "daily": _("Daily View"),
    "hourly": _("Hourly View")
    }

view_mode_order = ["yearly", "monthly", "daily", "hourly"]

view_mode_descr = {
    "yearly": _("Year"),
    "monthly": _("Month"),
    "daily": _("Day"),
    "hourly": _("Hour")
    }

view_kind = {
    "sum": _("Changes Sum"),
    "category": _("By Category")
    }

view_kind_order = ["sum", "category"]

xlabels = {
    "yearly": _("Months"),
    "monthly": _("Days"),
    "daily": _("Hours"),
    "hourly": _("Minutes")
    }

def tl_startup_options():
    """
    Returns Timeline startup options dict.
    """
    section = "Startup"

    if not configparser.has_section(section):
        return # would be better to raise some Exception

    startup = { }
    for opt, value in configparser.items(section):
        startup[opt] = value

    return startup


def gradient_colors_from_file():
    """
    Retrieve gradient from timeline settings file.
    """
    section = "Gradient"

    if not configparser.has_section(section):
        return

    gradient = { }
    for category, color in configparser.items(section):
        ccolor = color.split(',')
        ccolor = [float(colr) for colr in ccolor]
        gradient[category] = ccolor

    return gradient


def colors_from_file():
    """
    Retrieve colors from timeline settings file.
    """
    section = "Colors"

    if not configparser.has_section(section):
        return # would be better to raise some Exception

    colors = { }
    for category, color in configparser.items(section):
        ccolor = color.split(',')
        ccolor = [float(colr) for colr in ccolor]
        colors[category] = ccolor

    return colors


def colors_from_file_gdk():
    """
    Retrieve colors from timeline settings file and convert to gdk format.
    """
    colors = colors_from_file()

    for key, value in colors.items():
        colors[key] = [int(65535 * v) for v in value]

    return colors


class TLBase(CalendarManager, DataGrabber):
    """
    This class does the necessary Timeline management.
    """

    def __init__(self, connector, inventory, hostaddr):
        # using current date at startup
        CalendarManager.__init__(self, **startup_calendar_opts())
        DataGrabber.__init__(self, self, inventory, hostaddr)

        self.connector = connector
        self.grabber_method = None
        self.grabber_params = None
        self.labels = None
        self.xlabel = None

        self.selection = -1
        self.sel_range = (None, None)
        self.graph_mode = tl_startup_options()["mode"]
        self.graph_kind = tl_startup_options()["kind"]
        self.update_grabber()

        self.connector.connect('selection-changed', self._handle_selection)
        self.connector.connect('data-changed', self._update_graph_data)
        self.connector.connect('date-update', self._update_date)


    def grab_data(self):
        """
        Grab data for graph using current settings.
        """
        return getattr(self, self.grabber_method)(*self.grabber_params)


    def update_grabber(self):
        """
        Updates grabber method, params and graph vlabels.
        """
        if self.graph_kind == "sum":
            grab_mode = self.graph_mode + "_" + self.graph_kind
        else:
            grab_mode = "category"

        self.grabber_method = DATA_GRAB_MODES[grab_mode]

        labels = [ ]
        if self.graph_mode == "yearly":
            params = (self.year, )
            for m in months:
                labels.append(m[:3])

        elif self.graph_mode == "monthly":
            params = (self.year, self.month)
            for i in range(self.get_current_monthrange()[1]):
                labels.append("%d" % (i + 1))

        elif self.graph_mode == "daily":
            params = (self.year, self.month, self.day)
            for i in range(24):
                labels.append("%d" % i)

        elif self.graph_mode == "hourly":
            params = (self.year, self.month, self.day, self.hour)
            for i in range(60):
                labels.append("%d" % i)

        self.grabber_params = params
        self.labels = labels
        self.xlabel = xlabels[self.graph_mode]


    def descr_by_graphmode(self):
        """
        Returns a description with graph meaning.
        """
        graph_descr = [
            _("end of a week"), _("end of 12 hours period"),
            _("end of half hour period"), _("end of a minute")
            ]

        return _("Each point break represents ") + \
               graph_descr[view_mode_order.index(self.graph_mode)]


    def title_by_graphmode(self, useselection=False):
        """
        Returns a formatted date based on current graph mode (Yearly,
        Monthly, .. ).
        """
        def adjust(date):
            # prepends a 0 in cases where a date is minor than 10,
            # so (example) hour 2 displays as 02.
            if date < 10:
                date = "0%s" % date

            return date


        if useselection and self.selection != -1:
            fmtddate = [
                  "%s, %s" % (monthname((self.selection + 1) % 12),
                              # % 12 above is used so we don't have
                              # problems in case self.selection > 12,
                              # that is, when someone is viewing in
                              # other mode different than "Yearly".
                              self.year),

                  "%s, %s %s, %s" % (self.get_weekday(self.year,
                                      self.month, (self.selection+1)%\
                                      (self.get_current_monthrange()[1]+1))[1],
                                     monthname(self.month), self.selection+1,
                                     self.year),

                  "%s, %s %s, %s (%s:00)" % (self.get_current_weekday_name(),
                                             monthname(self.month),
                                             self.day, self.year,
                                             adjust(self.selection % 23)),

                  "%s, %s %s, %s (%s:%s)" % (self.get_current_weekday_name(),
                                             monthname(self.month), self.day,
                                             self.year, adjust(self.hour),
                                             adjust(self.selection))
                       ]
        else:
            fmtddate = [

                  _("Year %(year)s") % {'year': self.year},

                  "%s, %s" % (monthname(self.month), self.year),

                  "%s, %s %s, %s" % (self.get_current_weekday_name(),
                                        monthname(self.month), self.day,
                                        self.year),

                  "%s, %s %s, %s (%s:00)" % (self.get_current_weekday_name(),
                                             monthname(self.month),
                                             self.day, self.year, self.hour)
                       ]

        return fmtddate[view_mode_order.index(self.graph_mode)]


    def bounds_by_graphmode(self):
        """
        Return min, max and current value for graph mode.
        """

        values = [
            (self.year_range[0], self.year_range[1], self.year),
            (1, 12, self.month),
            (1, self.get_current_monthrange()[1], self.day),
            (0, 23, self.hour)
            ]

        return values[view_mode_order.index(self.graph_mode)]


    def _handle_selection(self, obj, selection):
        """
        Handles TLGraph selection, so we detect the selected timerange.
        """
        self.selection = selection

        if selection == -1: # deselected
            start = end = None

        elif self.graph_mode == "yearly": # months
            selection += 1 # months starting at 1
            start = datetime.datetime(self.year, selection, 1)
            end = start + datetime.timedelta(days=self.get_monthrange(
                self.year, selection)[1])
        elif self.graph_mode == "monthly": # days
            selection += 1 # days starting at 1
            start = datetime.datetime(self.year, self.month, selection)
            end = start + datetime.timedelta(days=1)

        elif self.graph_mode == "daily": # hours
            start = datetime.datetime(self.year, self.month, self.day,
                selection)
            end = start + datetime.timedelta(seconds=3600)

        elif self.graph_mode == "hourly": # minutes
            start = datetime.datetime(self.year, self.month, self.day,
                self.hour, selection)
            end = start + datetime.timedelta(seconds=60)

        self.sel_range = (start, end)

        self.connector.emit('selection-update', start, end)


    def _update_graph_data(self, obj, *args):
        """
        Received a request to perform graph data update.
        """
        if args[0] and args[1]:
            self.graph_mode = args[0]
            self.graph_kind = args[1]

        self.update_grabber()

        glabel = self.title_by_graphmode() # graph title
        dlabel = self.descr_by_graphmode() # graph description

        line_filter, start, evts = self.grab_data()

        self.connector.emit('data-update', line_filter, start, evts,
            self.labels, self.xlabel, glabel, dlabel)


        self.connector.emit('date-changed')


    def _update_date(self, obj, arg):
        """
        Update date based on current mode.
        """
        modes = {
            "yearly": "year",
            "monthly": "month",
            "daily": "day",
            "hourly": "hour" }

        if self.graph_mode in modes:
            setattr(self, modes[self.graph_mode], arg)

        self.connector.emit('data-changed', None, None)
