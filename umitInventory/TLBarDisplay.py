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

import gtk
import cairo
import pango
import gobject

from umitCore.I18N import _

from umitInventory.TLBase import colors_from_file
from umitInventory.TLBase import gradient_colors_from_file
from umitInventory.TLBase import changes_list
from umitInventory.TLBase import changes_in_db

PI = 3.1415926535897931
GOLDENRATIO = 1.618033989
GOLDENRADIUS = GOLDENRATIO ** 4 # my magical number

EMPTY_COLOR =  ((0.3, 0.3, 0.3), (0, 0, 0))
NOSELECTION = _("No Selection")
NOCHANGES = _("No Changes")
STATISTICS = _("Changes Statistics")

class TLSelected(gtk.Widget):
    """
    A widget that shows statistics based on TLGraph selection.
    """

    def __init__(self, connector, datagrabber):
        gtk.Widget.__init__(self)

        self.connector = connector
        self.datagrabber = datagrabber

        self.title = self.create_pango_layout('')
        self.title.set_alignment(pango.ALIGN_CENTER)
        self.second_title = self.create_pango_layout('')
        self.second_title.set_alignment(pango.ALIGN_CENTER)

        # start with empty selection/colors
        self.percent, self.currselection = self.emptygraph()
        not_used, self.newselection = self.emptygraph()
        self.currcolor = (list(EMPTY_COLOR[0]), list(EMPTY_COLOR[1]))
        self.newcolor = EMPTY_COLOR
        self.noselection = True
        self.total = 0 # number of changes in selection
        self.multiplier = { }

        # animation effect control
        self.in_anim = False # bar drawing effect
        self.in_transition = False # color transition effect
        self.piece_cut = 12.0 # how many divisions will be done in each bar
                              # graph to do animation effect.
        self.trans_progress = 0.04 # color transition increments/decrements

        # bar drawing constants
        self.bar_draw = { }

        self.connector.connect('selection-update', self._update_graph)


    def get_selection_data(self):
        """
        Get current selection data.
        """
        return self.__seldata


    def set_selection_data(self, data):
        """
        Sets a dict containing changes for each category for current selection.
        """
        self.__seldata = data

        if self.flags() & gtk.REALIZED:
            self.queue_draw()


    def emptygraph(self):
        """
        Return a dict where each category has 0 changes.
        """
        empty = { }
        percent = { }

        for item in changes_list:
            empty[item] = 0
            percent[item] = 0.0

        return empty, percent


    def colors_diff(self):
        """
        Check if colors are different.
        """
        for indx, color in enumerate(self.currcolor):
            for c_indx, cvalue in enumerate(color):
                nvalue = self.newcolor[indx][c_indx]

                if nvalue != cvalue:
                    return True

        return False


    def _update_graph(self, obj, range_start, range_end):
        """
        New selection, grab changes by category for selection timerange and
        do everything needed to draw new selection.
        """
        if range_start is None and range_end is None: # no selection
            self.noselection = True

            self.total = self._changes_sum_in_selection(self.currselection)
            self.multiplier = { }
            for key, value in self.emptygraph()[0].items():
                self.multiplier[key] = abs(value - self.currselection[key]) / \
                                       self.piece_cut

            self.newcolor = EMPTY_COLOR
            self.percent, self.newselection = self.emptygraph()
            return

        self.noselection = False

        categories = self.datagrabber.get_categories()
        data = { }

        # grab changes by category in current selection
        for key in categories.keys():
            c = self.datagrabber.timerange_changes_count_generic(range_start,
                range_end, key, self.datagrabber.inventory,
                self.datagrabber.hostaddr)
            data[changes_in_db[categories[key][1]]] = c


        data_keys = data.keys()
        for item in changes_list:
            if item not in data_keys:
                data[item] = 0

        # changes sum
        self.total = self._changes_sum_in_selection(data)

        # calculate bars height based on their amount of changes
        bars_height = { }

        for key, value in data.items():
            if self.total == 0:
                bars_height[key] = 0
            else:
                bars_height[key] = ((value * self.bar_draw["bars_y_area"]) / \
                                    float(self.total))

        if not self.total: # range without changes was selected
            self.total = self._changes_sum_in_selection(self.currselection)

        self.percent = { }
        self.multiplier = { }

        for key, value in data.items():
            if not self.total: # present and previous selection have no changes
                self.percent[key] = 0.0
            else:
                self.percent[key] = (float(data[key])/self.total) * 100

            # calculate increment needed to complete this bar animation
            self.multiplier[key] = abs(bars_height[key] - \
                                      self.currselection[key]) / self.piece_cut

        # get new color
        more_changes = self._category_with_more_changes(bars_height)
        if more_changes.values()[0] == 0: # no changes in current selection
            newcolor = EMPTY_COLOR
            color_from = newcolor[0]
            color_to = newcolor[1]
        else:
            color_from = colors_from_file()[more_changes.keys()[0]]
            color_to = gradient_colors_from_file()[more_changes.keys()[0]]

        self.newcolor = (color_from, color_to)
        self.newselection = bars_height # set new selection, this will start
                                        # animation effect.


    def _changes_sum_in_selection(self, datad):
        """
        Returns changes sum in datad.
        """
        return sum(v for v in datad.values())


    def _category_with_more_changes(self, datad):
        """
        Return {category: value} with more changes.
        """
        max_v = -1
        max_d = {"invalid": max_v}

        for key, value in datad.items():
            if key == "nothing": # discarding this category for now
                continue

            if value > max_v:
                max_d = {key: value}
                max_v = value

        if max_v == 0:
            return {"nothing": datad["nothing"]}

        return max_d


    def _write_text(self, cr, text, bold):
        """
        Write centered text on widget.
        """
        cr.save()

        if bold:
            height = 1
            self.title.set_markup("<b>%s</b>" % text)
            cr.update_layout(self.title)
            pango_layout = self.title

        else:
            width, height = self.title.get_size()
            height = (height / pango.SCALE) + 2
            self.second_title.set_text(text)
            cr.update_layout(self.second_title)
            pango_layout = self.second_title

        cr.move_to(1, height + 1)
        cr.set_source_rgb(0, 0, 0)
        cr.show_layout(pango_layout)

        cr.move_to(0, height)
        cr.set_source_rgb(1, 1, 1)
        cr.show_layout(pango_layout)

        cr.restore()


    def _write_title(self, cr):
        """
        Tells _write_text to write widget title.
        """
        if self.noselection:
            self._write_text(cr, NOSELECTION, True)
            self._write_text(cr, NOCHANGES, False)
        else:
            self._write_text(cr, self.datagrabber.title_by_graphmode(True),
                True)
            self._write_text(cr, STATISTICS, False)


    def _draw_base(self, cr):
        """
        Draws __________
        """
        cr.save()

        cr.move_to(self.bar_draw["start_x"], self.bar_draw["start_y"])
        cr.line_to(self.bar_draw["end_x"], self.bar_draw["start_y"])

        cr.set_source_rgba(1, 1, 1, 0.3)
        cr.stroke()

        cr.restore()


    def _paint_background(self, cr):
        """
        Draw and paint widget background with a vertical gradient.
        """
        cr.save()

        cr.new_path()

        # draws a round rectangle, pure Art ;)
        cr.arc(GOLDENRADIUS, self.allocation[3] - GOLDENRADIUS,
               GOLDENRADIUS, PI / 2.0, PI)
        cr.arc(GOLDENRADIUS, GOLDENRADIUS,
               GOLDENRADIUS, PI, - PI / 2.0)
        cr.arc(self.allocation[2] - GOLDENRADIUS, GOLDENRADIUS,
               GOLDENRADIUS, PI + (PI / 2.0), 0)
        cr.arc(self.allocation[2] - GOLDENRADIUS,
               self.allocation[3] - GOLDENRADIUS, GOLDENRADIUS, 0, PI/2.0)

        cr.close_path()

        pat = cairo.LinearGradient(0, 0, 0, self.allocation[3])

        color_from = self.currcolor[0]
        color_to = self.currcolor[1]

        pat.add_color_stop_rgb(0, *color_from)
        pat.add_color_stop_rgb(1, *color_to)

        cr.set_source(pat)
        cr.fill()

        cr.restore()


    def _draw_bar(self, cr, value, color, x_pos):
        """
        Draws a vertical graph bar.
        """
        cr.save()

        cr.rectangle(self.bar_draw["start_x"] + x_pos,
                     self.bar_draw["start_y"], self.bar_draw["bar_width"],
                     - value - 1)

        cr.set_source_rgb(*color)
        cr.fill()

        cr.restore()

        return self.bar_draw["start_y"] - value


    def _write_bar_text(self, cr, text, bar_height, x_pos):
        """
        Write text above or inside bar.
        """
        if self.noselection:
            # nothing to write
            return

        cr.save()
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_BOLD)

        _, _, width, height, _, _ = cr.text_extents(text)
        center = (self.bar_draw["bar_width"] / 2.0) + (height / 2.0)

        if self.bar_draw["start_y"] - bar_height != 0:
            if self.bar_draw["start_y"] - bar_height - width - 3 == 0:
                h_pos = bar_height + width
            elif self.bar_draw["start_y"] - bar_height - width - 3 >= 3:
                h_pos = bar_height + width + 3
            else:
                h_pos = self.bar_draw["start_y"] - 3
        else:
            h_pos = bar_height - 3

        cr.move_to(self.bar_draw["start_x"] + x_pos + center + 1, h_pos)

        cr.rotate(- PI/2)
        cr.set_source_rgb(0, 0, 0)
        cr.show_text(text)
        cr.rotate(PI/2)

        cr.move_to(self.bar_draw["start_x"] + x_pos + center, h_pos - 1)

        cr.rotate(- PI/2)
        cr.set_source_rgb(1, 1, 1)
        cr.show_text(text)
        cr.rotate(PI/2)

        cr.restore()


    def _color_transition(self):
        """
        Color transition.
        """
        continue_trans = False # if this remains False, transition is complete

        # check values to perform color transition
        for indx, color in enumerate(self.currcolor):
            for c_indx, cvalue in enumerate(color):
                nvalue = self.newcolor[indx][c_indx]

                # doing this so in some cases (float point with many digits)
                # we don't stay here forever.
                if abs(nvalue - cvalue) <= self.trans_progress and \
                    nvalue != cvalue:

                    self.currcolor[indx][c_indx] = nvalue
                    continue_trans = True
                    continue

                if cvalue > nvalue:
                    self.currcolor[indx][c_indx] = cvalue - self.trans_progress

                    continue_trans = True

                elif cvalue < nvalue:
                    self.currcolor[indx][c_indx] = cvalue + self.trans_progress

                    continue_trans = True

        if not self.in_anim:
            # This timer starts right after bar drawing starts, so
            # queue_draw is already being called by _update_bars().
            # But, this may end after _update_bars finishes, so it
            # is needed to call queue_draw now.
            self.queue_draw()

        if not continue_trans:
            self.in_transition = False
            return False

        return True


    def _update_bars(self):
        """
        Increment/decrement bar sizes.
        """
        continue_anim = False

        # increment/decrement bars height
        for key, value in self.newselection.items():
            if value > self.currselection[key]:
                self.currselection[key] += self.multiplier[key]
                continue_anim = True

            elif value < self.currselection[key]:
                self.currselection[key] -= self.multiplier[key]
                continue_anim = True

            # doing this so in some cases (float point with many digits)
            # we don't stay here forever.
            if abs(self.currselection[key] - self.newselection[key]) <= 0.5 \
                and self.currselection[key] != self.newselection[key]:

                self.currselection[key] = self.newselection[key]
                continue_anim = True

        if not continue_anim:
            self.in_anim = False
            return False

        self.queue_draw()
        return True


    def _pre_bar_draw(self, cr):
        """
        Calculate where each bar will be draw, and then call _draw_bar to
        draw it.
        """
        for multiplier, item in enumerate(changes_list):
            curr_x_pos = self.bar_draw["bars_distance"] + \
                         (self.bar_draw["bars_distance"] * multiplier) + \
                         (self.bar_draw["bar_width"] * multiplier)

            bar_height = self._draw_bar(cr, self.currselection[item],
                colors_from_file()[item], curr_x_pos)

            self._write_bar_text(cr, "%.1f%%" % self.percent[item], bar_height,
                curr_x_pos)


    def _calculate_bar_sizes(self):
        """
        Calculates everything needed during bars drawing.
        """
        self.bar_draw["start_x"] = 12
        self.bar_draw["end_x"] = self.allocation[2] - 12
        self.bar_draw["start_y"] = self.allocation[3] - 6
        self.bar_draw["bars_distance"] = 5
        self.bar_draw["bars_y_area"] = self.bar_draw["start_y"] - 60

        bars_space = self.allocation[2] - (2 * self.bar_draw["start_x"]) - \
                     self.bar_draw["bars_distance"]
        bar_width = (bars_space / float(len(changes_list))) - \
                    self.bar_draw["bars_distance"]

        self.bar_draw["bar_width"] = bar_width


    def do_realize(self):
        """
        Realizes widget with necessary event_mask and calculate initial
        bar drawing constants.
        """
        self.set_flags(self.flags() | gtk.REALIZED | gtk.CAN_FOCUS)

        self.window = gtk.gdk.Window(self.get_parent_window(),
            width=self.allocation.width, height=self.allocation.height,
            window_type=gtk.gdk.WINDOW_CHILD, wclass=gtk.gdk.INPUT_OUTPUT,
            event_mask=self.get_events() | gtk.gdk.EXPOSURE_MASK)

        self.window.set_user_data(self)
        self.style.attach(self.window)
        self.style.set_background(self.window, gtk.STATE_NORMAL)
        self.window.move_resize(*self.allocation)

        self._calculate_bar_sizes()


    def do_unrealize(self):
        """
        Widget cleanup.
        """
        self.window.set_user_data(None)


    def do_size_request(self, requisition):
        """
        Sets "optimal" minimal size for widget.
        """
        requisition.width = 190
        requisition.height = 130


    def do_size_allocate(self, allocation):
        """
        Handles size allocation and recalculate bar drawing constants.
        """
        self.allocation = allocation

        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*self.allocation)

        self._calculate_bar_sizes()

        self.title.set_width(allocation[2] * pango.SCALE)
        self.second_title.set_width(allocation[2] * pango.SCALE)


    def do_expose_event(self, event):
        """
        Controls widget drawing.
        """
        cr = self.window.cairo_create()
        cr.rectangle(*event.area)
        cr.clip()

        if self.currselection != self.newselection and not self.in_anim:
            self.in_anim = True
            gobject.timeout_add(20, self._update_bars)

        if self.colors_diff() and not self.in_transition:
            self.in_transition = True
            gobject.timeout_add(20, self._color_transition)

        self._paint_background(cr)
        self._write_title(cr)
        self._draw_base(cr)
        self._pre_bar_draw(cr)


    # Properties
    newselection = property(get_selection_data, set_selection_data)


gobject.type_register(TLSelected)
