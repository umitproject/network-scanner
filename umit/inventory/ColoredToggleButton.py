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
A standard ToggleButton but with an colored eventbox.
"""

import gtk

class ColoredToggleButton(gtk.ToggleButton):

    def __init__(self, label, color):
        gtk.ToggleButton.__init__(self)

        self.lbl = gtk.Label(label)
        self.color_eb = gtk.EventBox()
        self.color_eb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(*color))

        # XXX For some WMs the following two lines are needed in order to
        # obtain the same results elsewhere, it is like eventbox changed
        # its state.
        self.color_eb.modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.Color(*color))
        self.color_eb.modify_bg(gtk.STATE_ACTIVE, gtk.gdk.Color(*color))

        self.__set_props()
        self.__do_layout()
        self.show_all()


    def __set_props(self):
        """
        Set eventbox width, height.
        """
        self.color_eb.set_size_request(12, 6)


    def __do_layout(self):
        """
        Layout colored toggle button.
        """
        color_align = gtk.Alignment(0, 0.6, 1, 0.1)
        color_align.add(self.color_eb)

        button_box = gtk.HBox()
        button_box.pack_start(color_align, False, False, 2)
        button_box.add(self.lbl)

        self.add(button_box)
