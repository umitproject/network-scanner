#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import gtk
import gobject

from umitCore.Version import VERSION

class Splash(gtk.Window):
    def __init__(self, image, time=1700):
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        self.set_position(gtk.WIN_POS_CENTER)

        splash_img = gtk.gdk.pixbuf_new_from_file(image)
        pixmap, mask = splash_img.render_pixmap_and_mask()
        width, height = pixmap.get_size()
        del splash_img

        self.set_app_paintable(True)
        self.set_size_request(width, height)
        self.set_resizable(False)
        self.realize()

        self.verbox = gtk.VBox()
        self.version = gtk.Label("%s" % VERSION)

        self.version.set_use_markup(True)
        self.version.set_markup("<span size='22000' weight='heavy'>\
%s</span>" % VERSION)

        # These constants are derived from the dimensions of the open space in
        # the splash graphic. We attempt to center the version number.
        self.verbox.set_size_request(152, 56)
        self.verbox.pack_start(self.version, True, False)

        fixed = gtk.Fixed()
        fixed.put(self.verbox, width - 152, height - 56)
        self.add(fixed)

        self.hid = self.connect("expose-event", self.set_bg, mask, pixmap)
        self.set_bg(self, None, mask, pixmap)
        self.show_all()

        while gtk.events_pending():
            gtk.main_iteration()
        gobject.timeout_add(time, self.destroy)

    def destroy(self):
        gtk.Window.destroy(self)
        return False

    def set_bg(self, widget, event, mask, pixmap):
        if self.window != None:
            self.window.set_back_pixmap(pixmap, False)
        else:
            gobject.idle_add(self.set_bg, widget, event, mask, pixmap)

if __name__ == "__main__":
    from os.path import join
    s = Splash(join(".", "share", "pixmaps", "splash.png"))
    gtk.main()
