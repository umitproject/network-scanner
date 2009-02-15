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
import gobject

from umitInventory.TLBase import colors_from_file

PI = 3.1415926535897931

colors = colors_from_file()

(VERTICAL, HORIZONTAL) = range(2)
(LINEGRAPH, AREAGRAPH) = range(2)

class InteractiveGraph(gtk.Widget):
    """
    Timeline Graph.
    """

    def __init__(self, data, start_points, line_filter, connector=None,
                 y_label='', x_label='', graph_label='', descr_label='',
                 vdiv_labels=None, graph_type=LINEGRAPH,
                 hdivs=5, balloons=True, startup_animation=True,
                 progressive_selection_effect=True,
                 draw_dashed_vert=False, draw_solid_vert=False,
                 draw_arcs_always=False, draw_every_arc=True,
                 gradient_fill=False, gradient_direction=VERTICAL,
                 gradient_on_selection=False):
        """
        -> data is expected to be a dict wit the following format:

            { key0: [ (line1_firstpoint, line2_firstpoint, ..,
                       lineN_firstpoint),
                      (line1_secondpoint, line2_secondpoint, ..,
                       lineN_secondpoint), .., (line1_nthpoint, ..,
                      lineN_nthpoint) ],
              key1: [ .. same as above .. ],
               .
               .
              keyN: [ .. same as above .. ] }

            Number of keys in dict determines number of vertical divisors.


            Examples:
                Graph with one line, three points break, one vertical divisor:
                
                  sample_data = { 0: [(1, ), (2, ), (3, )] }
                  
                  Note: Keys needs to be from 0 .. n (0, 1, 2, .., n)

                Graph with two lines, two points breaks, two vertical divisors:

                  sample_data = { 0: [(1, 2), (4, 5)],
                                  1: [(10, 9), (3, 8)] }

            Bad example:
                  sample_data = { 0: [(1, 2, 3), (1, 2)] }

                Every line needs to contain same amount of points.


        -> start_points is a list of values that defines where each line
            should start, it could be the last points from last date
            before first date in this graph (for example).

            Example for graph with two lines:
               start_values = (5, 0)

            Example for graph with one line:
               start_values = (5, )

            If you especify more start points than needed, they will be
            discarded.

        -> line_filter is used to set what lines should be shown, it has the
            following format:

              Example: line_filter = { 0: (True, "Item A"),
                                       1: (False, "Item B") }

        -> connector is required to update line_filter, graph data and
            possibly other things or to send updates. (this is used in
            conjunction with other umitInventory modules)

        -> y_label defines a label for y axis.

        -> x_label defines a label for x axis.

        -> graph_label defines a title for the graph.

        -> descr_label defines a label that shows a brief description of graph
            meaning or something like that.

        -> vdiv_labels defines labels to be used at each vertical mark.

        -> hdivs determines the number of horizontal divisors.

        -> balloons determines if we should draw balloons pointing to
            higlighted points on selection.

        -> draw_dashed_vert determines if we should draw vertical dashed lines
            on graph.

        -> draw_solid_vert determines if we should draw vertical solid lines
           on graph.

        -> draw_arcs_always determines if arcs should always be drawn, if this
            is set to False arcs will be drawn only when a selection is done.

        -> draw_every_arc determines if every arc will be drawn or just
            drawn at boundary points.
                 
        -> startup_anitmation determines if there will be an effect in graph
            startup.

        -> gradient_fill determines if selection will be painted with a
            gradient or solid color.

        -> gradient_direction determines the direction of gradient used when
            painting selection (if gradient_fill == True).

        -> gradient_on_selection, fill selection with solid color or gradient
            color.

        -> progressive_selection_effect determines if there will be an effect
            after selecting something or not.
        """

        gtk.Widget.__init__(self)

        self.dontdraw = False

        # connector
        self.connector = connector

        # effects
        self.startup_animation = startup_animation
        self.anim_timer = -1
        self.draw_dashed_vert = draw_dashed_vert
        self.draw_solid_vert = draw_solid_vert
        self.selection_effect = progressive_selection_effect
        self.selection_gradient = gradient_on_selection
        self.gradient_direction = gradient_direction
        self.gradient_fill = gradient_fill
        # points highlight (arcs)
        self.draw_arcs_always = draw_arcs_always
        self.draw_every_arc = draw_every_arc
        self.show_balloons = balloons
        # balloons
        self.balloons = [ ]

        # borders
        self.border_width = 2
        self.border_fix = self.border_width / 2.0
        self.top_reserved = 1 # will be calculated when realized.
        self.left_reserved = 1 # will be calculated when realized.
        self.bottom_reserved = 1 # will be calculated when realized.

        # divisors
        self.hdivisors = hdivs # number of horizontal divisors (min 2)
        self.vdivisors = -1 # number of vertical divisors (min 2)
        self.hmarks_pos = { } # holds position for each horizontal mark
        self.vmarks_pos = { } # holds position for each vertical mark
        self.mark_size = 10 # | or - size

        # selection
        self.keep_selection = False # if this is True, this widget wont emit
                                    # selection changed signal.
        self.selection = -1 # nothing selected
        self.alpha_ts = 0 # alpha threshold for selection painting
        self.selection_timer = -1 # timer for doing selection painting
        self.selection_painting = False # control for selection painting

        # graph
        self.hover = -1 # nothing being hovered
        self.graph_type = graph_type
        self.graph_alpha = 0.0 # used for AREAGRAPH alpha during animation
        self.max_value = -1
        self.ylabel = y_label
        self.xlabel = x_label
        self.graph_label = graph_label
        self.descr_label = descr_label
        self.vdiv_labels = vdiv_labels
        self.start_pts_data = start_points
        self.start_pts = [ ]
        self.pts_per_div = -1
        self.graph_data = data
        self.line_filter = line_filter
        self.num_graph_lines = -1
        self.graphpoints = { }
        self.graph = { } # holds all data necessary for drawing the graph.
        self.graph["fg_color"] = (0, 0, 0, 0.5)
        self.graph["bg_gradient"] = ((0.729, 0.851, 1, 0.8), (1, 1, 1, 0.6))
        self.graph["gradient_sel"] = ((0, 0.4, 1), (1, 1, 1))
        self.graph["bg_solid"] = (0.816, 0.906, 1)
        self.graph["bg_selection"] = (0, 0.4, 1)
        self.graph["selection_alpha_max"] = 0.25

        # graph drawing animation
        self.divisors = 2 # number of divisions in each line segment, increasing
                          # this causes animation to be smoother.
        self.ccount = 0
        self.cur_point_indx = 0
        self.painting_piece = 0


    def speedup_performance(self, *args):
        """
        Change settings to speed up drawing performance.
        """
        self.graph["fg_color"] = (0, 0, 0, 1)
        self.hdivisors = 3
        self.gradient_fill = False
        self.selection_gradient = False
        self.selection_effect = False
        self.draw_dashed_vert = False
        self.draw_solid_vert = False
        self.draw_arcs_always = False
        self.draw_every_arc = False
        self.show_balloons = True
        self.anim_timer = 0 # disabling animation

        self.setup_new_graph()


    def best_visual(self, *args):
        """
        Change settings to draw with best visual.
        """
        self.graph["fg_color"] = (0, 0, 0, 0.5)
        self.hdivisors = 5
        self.gradient_fill = True
        self.selection_gradient = True
        self.selection_effect = True
        self.draw_dashed_vert = True
        self.draw_solid_vert = False
        self.draw_arcs_always = False
        self.draw_every_arc = True
        self.show_balloons = True

        self.setup_new_graph()


    def standard_mode(self, *args):
        """
        Set standard settings.
        """
        self.graph["fg_color"] = (0, 0, 0, 0.5)
        self.hdivisors = 5
        self.gradient_fill = False
        self.selection_gradient = False
        self.selection_effect = True
        self.draw_dashed_vert = False
        self.draw_solid_vert = False
        self.draw_arcs_always = False
        self.draw_every_arc = True
        self.show_balloons = True

        self.setup_new_graph()


    def do_animation(self):
        """
        Restart animation.
        """
        self.startup_animation = True
        self.anim_timer = -1
        self.ccount = 0
        self.cur_point_indx = 0
        self.painting_piece = 0

        self.setup_new_graph()


    def setup_new_graph(self):
        """
        Do everything necessary after changing graph.
        """
        if self.max_value == -1:
            # graph has no data
            return

        if not (self.flags() & gtk.REALIZED):
            # timeline isn't realized yet
            return

        self.hmarks_pos = { }
        self.graphpoints = { }
        self.vmarks_pos = { }
        self.balloons = [ ]
        self.keep_selection = True
        self.selection = -1
        self.keep_selection = False

        self._calculate_border_reserved()
        self._calculate_graph_alloc()
        self._calculate_graph_points()

        self.queue_draw()


    def get_graphdata(self):
        """
        Get current graph data.
        """
        return self.__gdata


    def set_graphdata(self, data):
        """
        Set new graph data and setup new pts_per_div and vidivisors.
        """
        self.__gdata = data
        if data:
            self.pts_per_div = len(data[0])
            self.vdivisors = len(data)


    def get_maxvalue(self):
        """
        Returns current max value for graph.
        """
        return self.__maxv


    def set_maxvalue(self, maxvalue):
        """
        Sets new max value for graph.
        """
        if maxvalue < self.hdivisors:
            maxvalue = self.hdivisors

        self.__maxv = maxvalue


    def get_graph_type(self):
        """
        Get current graph type.
        """
        return self.__grapht


    def set_graph_type(self, graph_type):
        """
        Set new graph type.
        """
        self.__grapht = graph_type
        
        if self.flags() & gtk.REALIZED:
            self.queue_draw()


    def get_start_effect(self):
        """
        Retruns True if widget should do an effect on graph startup.
        """
        return self.__seffect


    def set_start_effect(self, effect):
        """
        Set new value for startup_animation.
        """
        self.__seffect = effect


    def find_max_value(self):
        """
        Find and return current max value based on graph data, graph start
        data and active filter.
        """
        newmax = -1

        # start points values
        for indx, value in enumerate(self.start_pts_data):
            if not self.line_filter[indx][0]:
                # line disabled
                continue

            if value > newmax:
                newmax = value

        # graph points values
        for value in self.graph_data.values():
            for v in value:
                for indx, i in enumerate(v):
                    if not self.line_filter[indx][0]:
                        # line disabled
                        continue

                    if i > newmax:
                        newmax = i

        self.max_value = newmax


    def get_active_filter(self):
        """
        Returns current filter being used to draw lines.
        """
        return self.__filter


    def set_active_filter(self, lfilter):
        """
        Set filter to be used when drawing lines.
        """
        self.__filter = lfilter


    def get_alpha_threshold(self):
        """
        Get alpha to be used in selection painting.
        """
        return self.__alphats


    def set_alpha_threshold(self, threshold):
        """
        Set alpha to be used in selection painting.
        """
        self.__alphats = threshold


    def get_divisors(self):
        """
        Get number of divisions per line segment.
        """
        return self.__divisors


    def set_divisors(self, divisors):
        """
        Set number of divisions per line segment.
        """
        if divisors < 1:
            divisors = 1

        self.__divisors = int(divisors)


    def get_hdivisors(self):
        """
        Get number of horizontal divisors
        """
        return self.__hdiv


    def set_hdivisors(self, hdiv):
        """
        Set number of horizontal divisors.
        """
        if hdiv < 2: # min is two
            hdiv = 2

        self.__hdiv = hdiv - 1


    def get_selection(self):
        """
        Return current selectioned piece.
        """
        return self.__selection


    def set_selection(self, selection):
        """
        Set selection and send update to connector.
        """
        self.__selection = selection

        if self.connector and not self.keep_selection:
            # if keep_selection is True, we shouldn't tell other widgets
            # that selection changed.
            self.connector.emit('selection-changed', self.selection)


    def get_cairo_context(self):
        """
        Try to return a cairo context.
        """
        try:
            cr = self.window.cairo_create()
            return cr

        except cairo.Error:
            # widget is being destroyed (probably)
            self.dontdraw = True


    def _calculate_border_reserved(self):
        """
        Calculate space needed to write labels.
        """
        #cr = self.window.cairo_create()
        cr = self.get_cairo_context()

        if not cr:
            return

        if self.graph_label or self.descr_label:
            t = True and self.graph_label or self.descr_label

            _, _, _, height, _, _ = cr.text_extents(t)
            self.top_reserved = height + 6

        _, _, width, height, _, _ = cr.text_extents("%d" % self.max_value)
        self.left_reserved = width + 4 + self.mark_size

        if height / 2.0 > self.top_reserved:
            self.top_reserved = (height / 2.0) + 2

        if self.ylabel:
            _, _, _, height, _, _ = cr.text_extents(self.ylabel)
            self.left_reserved += height + 6

        self.graph["x_start"] = self.left_reserved
        self.graph["y_start"] = self.top_reserved

        # likely to not works always!
        self.bottom_reserved = height + 6 + self.mark_size


    def _calculate_graph_alloc(self):
        """
        Calculates x space, y space, distance between horizontal and
        vertical divisors for graph for current allocated space.
        """
        self.graph["x_space"] = self.allocation[2] - self.left_reserved - \
                                self.border_width
        self.graph["y_space"] = self.allocation[3] - (self.top_reserved + \
                                                      self.bottom_reserved + \
                                                      self.border_fix)

        self.graph["hdiv"] = (self.graph["y_space"] - self.border_width) / \
                             float(self.hdivisors)
        self.graph["vdiv"] = (self.graph["x_space"] - self.border_width) / \
                             float(self.vdivisors)


    def _calculate_point_ypos(self, value):
        """
        Caluate y position for a value.
        """
        if value == 0:
            return self.graph["y_space"] + self.top_reserved
        else:
            return self.graph["y_space"] + self.top_reserved \
                   - (self.graph["y_space"] / (self.max_value / float(value)))


    def _calculate_graph_points(self):
        """
        Calculates (x, y) points for data in self.graph_data.
        """
        x_pts_dist = self.graph["vdiv"] / self.pts_per_div
        x_pts_dx = self.left_reserved + self.border_fix + x_pts_dist

        # Calculate data points position
        for key, item in self.graph_data.items():
            k_pts = [ ]
            for piece in item:
                # calculate y position
                pt = [ ]
                for pv in piece:
                    pt.append(self._calculate_point_ypos(pv))

                # add x position to the point
                pt = [(x_pts_dx, p) for p in pt]

                k_pts.append(pt)
                x_pts_dx += x_pts_dist

            self.graphpoints[key] = k_pts

        if not self.graphpoints:
            return

        self.num_graph_lines = len(self.graphpoints[0][0])

        # Calculate start_point(s) position
        start_x = self.left_reserved
        start_y = [ ]
        for pv in self.start_pts_data:
            start_y.append(self._calculate_point_ypos(pv))
        
        self.start_pts = [(start_x, y) for y in start_y]

        # set startup points for graph animation
        self.cur_point = { }
        for i in range(self.num_graph_lines):
            self.cur_point[i] = self.start_pts[i]


    def _gradient_fill(self, cr, gradient=True):
        """
        Fill graph with gradient or solid color.
        """
        cr.save()

        cr.rectangle(self.graph["x_start"] + self.border_fix,
                     self.graph["y_start"] + self.border_fix,
                     self.graph["x_space"] - self.border_fix,
                     self.graph["y_space"] - self.border_fix)

        if gradient: # gradient fill
            if self.gradient_direction == VERTICAL:
                end_x = self.graph["x_start"] - self.border_width
                end_y = self.graph["y_space"] - self.border_width
            else:
                end_x = self.graph["x_space"] - self.border_width
                end_y = self.graph["y_start"] - self.border_width

            pat = cairo.LinearGradient(self.graph["x_start"] + self.border_fix,
                                       self.graph["y_start"] + self.border_fix,
                                       end_x, end_y)
            pat.add_color_stop_rgba(0, *self.graph["bg_gradient"][0])
            pat.add_color_stop_rgba(1, *self.graph["bg_gradient"][1])
            cr.set_source(pat)

        else: # solid fill
            cr.set_source_rgb(*self.graph["bg_solid"])

        cr.fill()

        cr.restore()


    def _solid_fill(self, cr):
        """
        Fill graph with solid coloring.
        """
        self._gradient_fill(cr, False)


    def _draw_graph_base(self, cr):
        """
        Draw base of graph.
        """
        # draw x, y axis and store marker positions
        #  |
        # _|______
        #  |
        cr.save()

        cr.move_to(self.graph["x_start"], self.graph["y_start"])
        cr.rel_line_to(0, self.graph["y_space"] + self.mark_size)

        self.vmarks_pos[0] = cr.get_current_point()

        cr.rel_line_to(0, - self.mark_size)
        cr.rel_line_to(- self.mark_size, 0)

        self.hmarks_pos[0] = cr.get_current_point()

        cr.rel_line_to(self.graph["x_space"] + self.mark_size, 0)

        cr.set_source_rgba(*self.graph["fg_color"])
        cr.stroke()

        cr.restore()

        # horizontal divisors (first is draw when x axis was drawn)
        hdiv_y = self.top_reserved

        cr.save()

        for hdiv in range(self.hdivisors):
            # + 0.5 is used below to draw a sharp line
            cr.move_to(self.graph["x_start"] - self.mark_size - \
                       self.border_fix, int(hdiv_y) + 0.5)

            cpoint = list(cr.get_current_point())
            cpoint[0] += self.border_fix
            self.hmarks_pos[self.hdivisors - hdiv] = cpoint

            cr.rel_line_to(self.graph["x_space"] + self.mark_size, 0)

            hdiv_y += self.graph["hdiv"]

        cr.set_source_rgba(*self.graph["fg_color"])
        cr.set_line_width(0.5)
        cr.stroke()

        cr.restore()

        # draw vertical marks at bottom (first is draw when y axis was drawn)
        vdiv_x = self.graph["x_space"] + self.left_reserved - \
                 self.border_fix - self.graph["vdiv"]

        cr.save()

        cr.set_line_width(0.5)
        cr.set_source_rgba(*self.graph["fg_color"])

        for vdiv in range(1, self.vdivisors):
            # dashed or solid vertical line
            if self.draw_dashed_vert or self.draw_solid_vert:
                cr.move_to(vdiv_x, self.top_reserved + self.border_fix)
                if self.draw_dashed_vert:
                    cr.set_dash([1, 2], 0)
                cr.rel_line_to(0, self.graph["y_space"])
                cr.stroke()
                cr.set_dash([])

            # bottom vertical mark
            cr.move_to(vdiv_x, self.top_reserved + self.border_fix + \
                               self.graph["y_space"])
            cr.rel_line_to(0, self.mark_size)
            cpoint = list(cr.get_current_point())

            if self.draw_dashed_vert or self.draw_solid_vert:
                cr.stroke()

            cpoint[1] -= self.border_fix
            self.vmarks_pos[self.vdivisors - vdiv] = cpoint

            vdiv_x -= self.graph["vdiv"]

        if not self.draw_dashed_vert or not self.draw_solid_vert:
            cr.stroke()

        cr.restore()


    def _write_hmarks_values(self, cr):
        """
        Write horizontal marks values based on self.max_value
        """
        hm_value = self.max_value / float(self.hdivisors)
        hm_cur = hm_value

        cr.save()
        cr.set_source_rgba(*self.graph["fg_color"])

        for key, pos in self.hmarks_pos.items():
            if key == 0:
                # first value is 0
                text = "0"
            elif key == self.hdivisors:
                # last value is max
                text = "%d" % self.max_value
            else:
                text = "%d" % hm_cur
                hm_cur += hm_value

            # move to correct position
            _, _, width, height, _, _ = cr.text_extents(text)
            cr.move_to(pos[0] - width - 4, pos[1] + height / 2.0)

            # write text
            cr.show_text(text)

        cr.restore()


    def _write_vmarks_values(self, cr):
        """
        Write vertical marks labels.
        """
        if not self.vdiv_labels:
            # nothing to do here
            return

        if self.graph["x_space"] < 890 and len(self.vdiv_labels) > 31:
            modulus = 5
        else:
            modulus = 1

        cr.save()

        cr.set_source_rgba(*self.graph["fg_color"])

        for key, pos in self.vmarks_pos.items():
            if key % modulus != 0:
                continue

            try:
                text = self.vdiv_labels[key]
            except IndexError:
                text = "NA" # "Not Available"

            _, _, width, height, _, _ = cr.text_extents(text)

            cr.move_to(pos[0] - (width / 2.0) - self.border_fix,
                       pos[1] + height + 2)

            cr.show_text(text)

        cr.restore()


    def _write_labels(self, cr):
        """
        Write x, y, bottom, upper labels.
        """
        cr.save()

        cr.set_source_rgba(*self.graph["fg_color"])

        if self.ylabel:
            cr.save()
            _, _, width, height, _, _ = cr.text_extents(self.ylabel)
            cr.move_to(height + 2, self.graph["y_space"] + self.top_reserved + \
                                   self.border_width)
            cr.rotate(- PI/2.0)

            cr.set_source_rgba(*self.graph["fg_color"])
            cr.show_text(self.ylabel)
            cr.restore()

        if self.xlabel:
            cr.save()
            _, _, width, height, _, _ = cr.text_extents(self.xlabel)
            cr.move_to(self.allocation[2] - width - 6, 
                       self.graph["y_space"] + self.top_reserved - \
                       (2 * self.border_width))

            cr.set_source_rgb(*self.graph["fg_color"][:3])
            cr.show_text(self.xlabel)
            cr.restore()

        if self.graph_label or self.descr_label: # graph title/description
            height_label = True and self.descr_label or self.graph_label
            _, _, _, height, _, _ = cr.text_extents(height_label)

            if self.graph_label: # graph title
                cr.save()

                cr.move_to(self.left_reserved + self.border_width, height + 2)
                cr.show_text(self.graph_label)

                cr.restore()

            if self.descr_label: # description
                _, _, width, _, _, _ = cr.text_extents(self.descr_label)

                cr.save()

                cr.move_to(self.allocation[2] - width - 6, height + 2)
                cr.show_text(self.descr_label)

                cr.restore()

        cr.restore()


    def _paint_hover_area(self, cr):
        """
        Paint area being hovered.
        """
        start_x = self.left_reserved + (self.hover * self.graph["vdiv"])
        start_y = self.top_reserved + self.graph["y_space"]
        width = self.graph["vdiv"] + self.border_width
        height = self.mark_size / 2.0 #self.bottom_reserved / 4.0

        cr.save()

        cr.rectangle(start_x, start_y, width, height)
        cr.set_source_rgba(*self.graph["fg_color"])
        cr.fill()

        cr.restore()


    def _paint_selection(self, cr, alpha_threshold=None):
        """
        Paint selected area.
        """
        if self.selection == -1:
            # nothing to paint
            return

        start_x = self.left_reserved + \
                  (self.selection * self.graph["vdiv"]) + self.border_fix
        start_y = self.top_reserved
        height = self.graph["y_space"]
        width = self.graph["vdiv"]

        cr.save()

        cr.rectangle(start_x, start_y, width, height)

        if self.selection_gradient: # use gradient
            pat = cairo.LinearGradient(start_x, start_y, start_x, height)

            bottom_color = self.graph["gradient_sel"][0][:3]
            upper_color = self.graph["gradient_sel"][1][:3]

            if not alpha_threshold:
                alpha_threshold = self.graph["selection_alpha_max"]

            pat.add_color_stop_rgba(0, bottom_color[0], bottom_color[1],
                bottom_color[2], alpha_threshold)
            pat.add_color_stop_rgba(1, upper_color[0], upper_color[1],
                upper_color[2], alpha_threshold)
            cr.set_source(pat)

        else: # use solid color
            color = list(self.graph["bg_selection"])
            if not alpha_threshold:
                alpha_threshold = self.graph["selection_alpha_max"]

            color.extend([alpha_threshold, ])

            cr.set_source_rgba(*color)

        cr.fill()

        cr.restore()


    def _progressive_draw_timer(self):
        """
        This method handles graph animation effect.
        """
        if self.dontdraw:
            # entered here but it was configured to not draw anything,
            # stop timer then
            return False

        # check if we completed a line segment
        if self.painting_piece == self.divisors:
            self.painting_piece = 0

            # start to draw a new line segment then =)
            self.cur_point_indx += 1

            # check if we drawn all points in a vertical divisor
            if self.cur_point_indx == len(self.graphpoints[0]):

                # start to draw at new vertical divisor
                self.ccount += 1
                # at it's first point
                self.cur_point_indx = 0

        cr = self.get_cairo_context()
        if self.graph_type == AREAGRAPH:
            cr.set_line_width(1)

        if not cr:
            # stop timer, widget is being destroyed (probably)
            return False

        ret = self._draw_by_piece(cr)

        # check if we are done
        if not ret:
            if self.graph_type == AREAGRAPH: # still has to paint the background
                gobject.timeout_add(20, self._progressive_graph_fill)
            else:
                self.startup_animation = False
            return False

        return True


    def _progressive_graph_fill(self):
        """
        Fills graph progressively. Called after _progressive_draw_timer
        finishes and this is a AREAGRAPH.
        """
        if self.dontdraw:
            # entered here but it was configured to not draw anything,
            # stop timer then
            return False

        stop = False
        if self.graph_alpha > 0.3:
            self.graph_alpha = 0.3
            stop = True
        else:
            self.graph_alpha += 0.05

        #self._draw_area_graph(cr, self.graph_alpha)
        self.queue_draw()

        if stop:
            # now we are done!
            self.graph_alpha = 0.0
            self.startup_animation = False
            return False

        return True


    def lines_to_draw(self):
        """
        Returns number of "kind" of lines that will be drawn.
        """
        if self.line_filter:
            return sum(1 for k, v in self.line_filter.items() if v[0] == True)
        else:
            return self.num_graph_lines


    def _draw_by_piece(self, cr):
        """
        Draw graph by pieces to create a nice visual effect for startup or
        when data changes.
        """
        cr.set_line_join(cairo.LINE_JOIN_ROUND)

        for k in range(self.num_graph_lines):
            
            # check for final point
            if self.ccount == len(self.graph_data):
                return False

            # check if we should draw this line.
            if self.line_filter and not self.line_filter[k][0]:
                continue

            # get previous point
            if self.ccount == 0 and self.cur_point_indx == 0:
                p = self.start_pts[k]
            elif self.ccount != 0 and self.cur_point_indx == 0:
                p = self.graphpoints[self.ccount - 1]\
                                    [len(self.graphpoints[0])-1][k]
            else:
                p = self.graphpoints[self.ccount][self.cur_point_indx - 1][k]

            # get current point
            cp = self.graphpoints[self.ccount][self.cur_point_indx][k]

            cr.save()
            cr.set_source_rgb(*colors[self.line_filter[k][1]])

            cr.move_to(*self.cur_point[k])

            # draw a piece of line segment
            cr.rel_line_to((cp[0] - p[0]) / float(self.divisors),
                           (cp[1] - p[1]) / float(self.divisors))

            # store current point
            self.cur_point[k] = cr.get_current_point()

            # check if we should draw a circle
            if self.draw_arcs_always:
                if self.draw_every_arc:
                    if self.painting_piece == (self.divisors - 2):
                        cr.arc(cp[0], cp[1], 2, 0, 2 * PI)
                        cr.fill_preserve()
                        
                elif self.cur_point_indx == self.pts_per_div - 1 and \
                    self.painting_piece == (self.divisors - 2):

                    cr.arc(cp[0], cp[1], 2, 0, 2 * PI)
                    cr.fill_preserve()

            # especial check for arc at startup point
            if self.ccount == 0 and self.draw_arcs_always and \
                self.cur_point_indx == 0 and self.painting_piece == 0:

                cr.move_to(*self.start_pts[k])
                cr.arc(self.start_pts[k][0], self.start_pts[k][1], 2, 0, 2 * PI)
                cr.fill_preserve()

            cr.stroke()
            cr.restore()

            """
            cr.save()
            curr_x_pos = cp[0]
            cr.arc(curr_x_pos, 50, 5, 0, 2 * PI)
            cr.fill()
            cr.restore()
            
            cr.save()
            prev_x_pos = p[0]
            cr.set_operator(cairo.OPERATOR_CLEAR)
            cr.arc(prev_x_pos, 50, 5, 0, 2 * PI)
            cr.fill()
            cr.restore()
            """

        self.painting_piece += 1

        return True


    def _draw_graph(self, cr):
        """
        Draw graph, connecting points using rel_line_to.
        """
        # get startup points
        cur_points = { }

        for i in range(self.num_graph_lines):
            cur_points[i] = self.start_pts[i]

        cr.set_line_join(cairo.LINE_JOIN_ROUND)

        for indx in range(self.num_graph_lines):
            # check if we should draw this line
            if self.line_filter and not self.line_filter[indx][0]:
                continue

            for key, pts in self.graphpoints.items():
                for pind, pt in enumerate(pts):

                    # get previous point
                    if key == 0 and pind == 0:
                        p = cur_points[indx]
                    elif key != 0 and pind == 0:
                        p = self.graphpoints[key - 1] \
                                            [len(self.graphpoints[0]) - 1] \
                                            [indx]
                    else:
                        p = self.graphpoints[key][pind - 1][indx]

                    # get current point
                    cp = self.graphpoints[key][pind][indx]

                    cr.save()
                    cr.set_source_rgb(*colors[self.line_filter[indx][1]])

                    cr.move_to(*cur_points[indx])

                    # draw line
                    cr.rel_line_to(cp[0] - p[0], cp[1] - p[1])

                    # get new "startup" point
                    cur_points[indx] = cr.get_current_point()

                    # check if we should draw a circle now.
                    if self.draw_arcs_always: # draw arcs even without selection
                        if self.draw_every_arc:
                            cr.arc(cp[0], cp[1], 2, 0, 2 * PI)
                            cr.fill_preserve()
                        elif pind == self.pts_per_div - 1:
                            cr.arc(cp[0], cp[1], 2, 0, 2 * PI)
                            cr.fill_preserve()
                            
                    else: # draw arcs only when selection happens
                        if self.draw_every_arc:
                            if self.selection == key or \
                                (self.selection == key + 1 and pind == \
                                 self.pts_per_div - 1):
                                cr.arc(cp[0], cp[1], 2, 0, 2 * PI)
                                cr.fill_preserve()

                        elif pind == self.pts_per_div - 1 and \
                            (self.selection == key or \
                             (self.selection == key + 1)):

                            cr.arc(cp[0], cp[1], 2, 0, 2 * PI)
                            cr.fill_preserve()

                    # especial check for arc at startup point
                    if key == 0 and pind == 0 and (self.selection == 0 or \
                                                   self.draw_arcs_always):

                        cr.move_to(*self.start_pts[indx])
                        cr.arc(self.start_pts[indx][0],
                            self.start_pts[indx][1], 2, 0, 2 * PI)
                        cr.fill_preserve()


                    cr.stroke()
                    cr.restore()


    def _draw_area_graph(self, cr, alpha=0.3):
        """
        Draw graph, connecting points and filling the area.
        """
        cr.save()
        cr.set_line_width(1)
        cr.set_line_join(cairo.LINE_JOIN_ROUND)

        # connect the points, go! =)
        for indx, ini_p in enumerate(self.start_pts):
            if self.line_filter and not self.line_filter[indx][0]:
                continue

            cr.new_path()
            cr.move_to(*ini_p)

            for pts in self.graphpoints.values():
                for p in pts:
                    cr.line_to(*p[indx])

            x = cr.get_current_point()[0]

            # stroke every line.
            color = colors[self.line_filter[indx][1]]
            cr.set_source_rgb(*color)
            cr.stroke_preserve()

            # connect end with start point.
            cr.line_to(x, self.graph["y_space"] + self.top_reserved)
            cr.line_to(self.left_reserved + self.border_fix,
                self.graph["y_space"] + self.top_reserved)
            cr.close_path()

            # then set color, and fill.
            cr.set_source_rgba(color[0], color[1], color[2], alpha)
            cr.fill()

        cr.restore()


    def _draw_balloon(self, cr, text, color, pointing_pt):
        """
        Draws a balloon with some text and a color, pointing to pointing_pt.
        """
        # calculates balloon size
        _, _, width, height, _, _ = cr.text_extents(text)
        bwidth = width + 8
        bheight = height + 6

        dir_x = 5
        dir_y = 8
        w = bwidth
        h = bheight

        # this dict determines how balloon will be drawn.
        control = {
            (True, True): (dir_x, dir_y, w, h, -2, 5, 8, 8 + height),
            (True, False): (dir_x, -dir_y, w, -h, 2, 5, 8, -height),
            (False, True): (-dir_x, dir_y, -w, h, -2, -5,
                -width - 10, height + 8),
            (False, False): (-dir_x, -dir_y, -w, -h, 2, -5, -width -10, -8)
            }

        coords = control[(pointing_pt[0] < width,
            pointing_pt[1] - (bheight + 4) < 0)]

        # draw balloon
        cr.save()
        cr.new_path()
        cr.move_to(*pointing_pt)
        cr.rel_line_to(coords[0], coords[1])
        cr.rel_line_to(0, coords[3] + coords[4])
        cr.rel_line_to(coords[2], 0)
        cr.rel_line_to(0, - coords[3] + coords[4])
        cr.rel_line_to(- coords[2] + coords[5], 0)
        cr.close_path()

        # stroke and fill balloon
        if self.graph_type == AREAGRAPH:
            cr.set_line_width(0.7)
            cr.stroke_preserve()

        cr.set_source_rgba(color[0], color[1], color[2], 0.6)
        cr.fill()
        cr.restore()

        # write text
        cr.move_to(pointing_pt[0] + coords[6], pointing_pt[1] + coords[7])
        cr.show_text(text)


    def _update_alpha_ts(self):
        """
        Update alpha to be used in selection painting.
        """
        self.alpha_ts += 0.05

        if self.alpha_ts > self.graph["selection_alpha_max"]:
            self.selection_painting = False
            self.alpha_ts = 0
            self.queue_draw()

            return False

        self.queue_draw()

        return True


    def _setup_balloons(self):
        """
        Get boundary points or every point for current selection.
        """
        self.balloons = [ ]

        if not self.show_balloons:
            # Nothing to do here, balloons disabled.
            return

        if self.selection != -1:
            count = 0
            for pts in self.graphpoints[self.selection]:

                for indx, pt in enumerate(pts):
                    if self.line_filter and not self.line_filter[indx][0]:
                        continue

                    # discard middle points if we are looking only for
                    # boundary points
                    if not self.draw_every_arc and \
                        count != self.pts_per_div - 1:
                        continue

                    color = colors[self.line_filter[indx][1]]
                    value = "%d" % self.graph_data[self.selection][count][indx]
                    self.balloons.append((value, color, pt))

                count += 1

            # get left boundary points
            lines = len(self.graphpoints[self.selection][0])
            points_per_div = len(self.graphpoints[self.selection])
            for indx in range(lines):
                if self.line_filter and not self.line_filter[indx][0]:
                    continue

                color = colors[self.line_filter[indx][1]]

                if self.selection == 0: # startup point
                    pt = self.start_pts[indx]
                    value = "%d" % self.start_pts_data[indx]
                else: # somewhere else in the graph
                    pt = self.graphpoints[self.selection - 1] \
                                         [points_per_div - 1][indx]
                    value = "%d" % self.graph_data[self.selection - 1] \
                                         [points_per_div - 1][indx]

                self.balloons.append((value, color, pt))


    def do_realize(self):
        """
        Setup widget and calls methods for calculating everything needed
        to draw graph.
        """
        self.set_flags(self.flags() | gtk.REALIZED | gtk.CAN_FOCUS)

        self.window = gtk.gdk.Window(self.get_parent_window(),
                                     width=self.allocation.width,
                                     height=self.allocation.height,
                                     window_type=gtk.gdk.WINDOW_CHILD,
                                     wclass=gtk.gdk.INPUT_OUTPUT,
                                     event_mask=self.get_events() |
                                            gtk.gdk.EXPOSURE_MASK |
                                            gtk.gdk.BUTTON_PRESS_MASK |
                                            gtk.gdk.BUTTON_RELEASE_MASK |
                                            gtk.gdk.POINTER_MOTION_MASK |
                                            gtk.gdk.ENTER_NOTIFY_MASK |
                                            gtk.gdk.LEAVE_NOTIFY_MASK)

        self.window.set_user_data(self)
        self.style.attach(self.window)
        self.style.set_background(self.window, gtk.STATE_NORMAL)
        self.window.move_resize(*self.allocation)

        self.find_max_value() # find startup max value
        
        # calculate positions for current allocation.
        self._calculate_border_reserved()
        self._calculate_graph_alloc()
        self._calculate_graph_points()


    def do_unrealize(self):
        self.window.set_user_data(None)


    def do_size_request(self, requisition):
        """
        Sets an acceptable minimal size.
        """
        # minimal size
        #requisition.width = 70 * 3.2
        #requisition.height = 70

        # optimal size
        #width, _ = gtk.gdk.get_default_root_window().get_size()
        #requisition.width = (width * 3) / 4
        requisition.width = 400
        requisition.height = 140


    def do_size_allocate(self, allocation):
        """
        Handles size allocation, calculate new points positions and
        graph dimensions.
        """
        self.allocation = allocation

        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*allocation)

        # lets recalculate positions for new allocation.
        self._calculate_graph_alloc()
        self._calculate_graph_points()
        self._setup_balloons()


    def do_motion_notify_event(self, event):
        """
        Handles mouse motion.
        """
        if self.startup_animation:
            # animation effect still not finished.
            return

        prev_hover = self.hover

        # check if we are inside graph area
        if self.top_reserved <= event.y <= self.graph["y_space"] + \
        self.top_reserved and self.left_reserved <= event.x <= \
        self.graph["x_space"] + self.left_reserved:

            new_hover = int((event.x - self.left_reserved) / \
                         self.graph["vdiv"])

            if new_hover < len(self.graph_data):
                self.hover = new_hover

        else:
            self.hover = -1

        if prev_hover != self.hover:
            self.queue_draw()


    def do_button_release_event(self, event):
        """
        Handles mouse button release.
        """
        if event.button == 1: # left click
            self.balloons = [ ]
            prev_sel = self.selection

            if self.hover != -1:
                if self.selection == self.hover:
                    # clicked on previous selection
                    self.selection = -1 # unselect it

                else:
                    # new selection
                    self.selection = self.hover

            if prev_sel != self.selection:
                self.selection_timer = -1
                gobject.source_remove(self.selection_timer)
                self.queue_draw()


    def do_expose_event(self, event):
        """
        Draws graph.
        """
        if self.dontdraw:
            return

        cr = self.get_cairo_context()
        cr.rectangle(*event.area)
        cr.clip()

        # white background
        cr.save()
        cr.rectangle(*event.area)
        cr.set_source_rgb(1, 1, 1)
        cr.fill()
        cr.restore()

        # graph background
        if self.gradient_fill:
            self._gradient_fill(cr)
        else:
            self._solid_fill(cr)

        # graph base, axis
        self._draw_graph_base(cr)

        # write horizontal marks labels
        self._write_hmarks_values(cr)

        # write vertical marks labels
        self._write_vmarks_values(cr)

        # write x, y, bottom, upper labels
        self._write_labels(cr)

        # paint selection
        if self.selection_painting:
            self._paint_selection(cr, self.alpha_ts)
        else:
            if self.selection != -1:
                if self.selection_timer == -1 and self.selection_effect:
                    self.selection_timer = gobject.timeout_add(20,
                        self._update_alpha_ts)
                    self.selection_painting = True
                else:
                    self._setup_balloons()
                    self._paint_selection(cr)

        # paint area being hovered
        if -1 < self.hover < len(self.graph_data):
            self._paint_hover_area(cr)

        # check if graph is totally empty
        if not self.line_filter:
            return

        # draw graph
        if self.startup_animation and self.anim_timer == -1:
            # start animation
            self.anim_timer = gobject.timeout_add(20,
                self._progressive_draw_timer)
        elif self.startup_animation and self.graph_type == AREAGRAPH:
            self._draw_area_graph(cr, self.graph_alpha)

        elif not self.startup_animation:
            if self.graph_type == AREAGRAPH:
                self._draw_area_graph(cr)
            else:
                self._draw_graph(cr)

        # draw balloons
        for balloon in self.balloons:
            self._draw_balloon(cr, *balloon)


    # Properties
    graph_type = property(get_graph_type, set_graph_type)
    startup_animation = property(get_start_effect, set_start_effect)
    line_filter = property(get_active_filter, set_active_filter)
    alpha_ts = property(get_alpha_threshold, set_alpha_threshold)
    hdivisors = property(get_hdivisors, set_hdivisors)
    divisors = property(get_divisors, set_divisors)
    selection = property(get_selection, set_selection)
    graph_data = property(get_graphdata, set_graphdata)
    max_value = property(get_maxvalue, set_maxvalue)


gobject.type_register(InteractiveGraph)
