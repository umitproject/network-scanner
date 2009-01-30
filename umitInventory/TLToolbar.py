# Copyright (C) 2007 Insecure.Com LLC.
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
Timeline toolbar.
"""

import gtk

from higwidgets.higlabels import HIGEntryLabel
from higwidgets.higbuttons import HIGButton

from umitInventory.TLBase import colors_in_file
from umitInventory.TLBase import colors_from_file_gdk
from umitInventory.TLBase import view_mode_descr
from umitInventory.ColoredToggleButton import ColoredToggleButton

class FilterBox(gtk.HBox):
    def __init__(self, *args, **kwargs):
        """
        Expects a filter dict and a TLConnector instance.
        Filter format:
          filter = {0: (Bool, 'CategoryA'), 1: (Bool, 'CategoryB'), .. ,
                    N: (Bool, 'CategoryN')}

            Bool determines wheter we should show content for a category (True),
            or not (False).
        """

        gtk.HBox.__init__(self)

        self.line_filter = { }
        self.categories = [ ]
        self.connector = None
        self.buttons = gtk.HBox()
        self.colors = colors_from_file_gdk()

        for key, value in kwargs.items():
            if key == 'filter':
                self.line_filter = value
            elif key == 'connector':
                self.connector = value

        if self.connector:
            self.connector.connect('filter-update', self.handle_filter_update)

        self.__layout()


    def handle_filter_update(self, obj, lfilter):
        """
        Passes filter to filter property.
        """
        self.line_filter = lfilter


    def get_filter(self):
        """
        Return active filter.
        """
        return self.__filter


    def set_filter(self, lfilter):
        """
        Set a new filter.
        """
        self.__filter = lfilter

        if self.line_filter:
            self.categories = [key for key in self.line_filter.keys()]
            self._setup_top_btns()


    def update_filter(self, widget, filter_key, filter_category):
        """
        Update filter based on filter_key and previous filter status.
        """
        if not self.line_filter:
            return

        self.line_filter[filter_key] = (not self.line_filter[filter_key][0],
            filter_category)

        if self.connector:
            self.connector.emit('filter-update', self.line_filter)


    def _setup_top_btns(self):
        """
        Create and connect filter-buttons.
        """
        # clear self.buttons first
        [self.buttons.remove(w) for w in self.buttons.get_children()]

        for category in self.categories:
            cat_name = self.line_filter[category][1]

            if self.colors:
                color = self.colors[colors_in_file[cat_name]]
            else:
                color = (0, 0, 0)

            b = ColoredToggleButton(cat_name, color)
            b.set_active(self.line_filter[category][0])
            b.connect('toggled', self.update_filter, category, cat_name)

            self.buttons.pack_start(b, False, False, 0)


    def __layout(self):
        """
        Layout widgets.
        """
        self.buttons.show()
        self.pack_start(self.buttons, False, False, 6)
        self.show()

    # Property
    line_filter = property(get_filter, set_filter)


class TimeBox(gtk.HBox):
    """
    GUI Controls for handling Timeline date visualization.
    """

    def __init__(self, connector, tlbase):
        gtk.HBox.__init__(self)

        self.connector = connector
        self.tlbase = tlbase

        self.connector.connect('date-changed', self._update_current_date)

        # viewing by
        cur_mode = view_mode_descr[self.tlbase.graph_mode]
        self.dateselect_lbl = HIGEntryLabel(cur_mode)
        values = self.tlbase.bounds_by_graphmode()
        self.dateselect = gtk.SpinButton(gtk.Adjustment(value=values[2],
            lower=values[0], upper=values[1], step_incr=1), 1)
        self.dateselect_apply = HIGButton(stock=gtk.STOCK_APPLY)
        self.dateselect_apply.connect("clicked", self._date_change)

        self.__layout()


    def _date_change(self, event):
        """
        Sends new date.
        """
        self.connector.emit('date-update', self.dateselect.get_value_as_int())


    def _update_current_date(self, event):
        """
        Update spinbutton and values based on new date.
        """
        cur_mode = view_mode_descr[self.tlbase.graph_mode]
        self.dateselect_lbl.set_label(cur_mode)

        values = self.tlbase.bounds_by_graphmode()
        self.dateselect.set_range(values[0], values[1])
        self.dateselect.set_value(values[2])


    def __layout(self):
        """
        Layout widgets.
        """
        self.pack_start(self.dateselect_lbl, False, False, 0)
        self.pack_start(self.dateselect, False, False, 0)
        self.pack_start(self.dateselect_apply, False, False, 0)


if __name__ == "__main__":
    # filterbox sample
    filterd = {0: (True, 'Nothing'), 1: (False, 'Inventory')}
    lfilter = FilterBox()#filter=filterd)
    w = gtk.Window()
    w.add(lfilter)
    w.show_all()
    w.connect('delete-event', lambda *args:gtk.main_quit())
    filter.filter = filterd

    gtk.main()
