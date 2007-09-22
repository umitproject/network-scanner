#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2005 Insecure.Com LLC.
#
# Author: Adriano Monteiro Marques <py.adriano@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import gtk
import gobject

from umitCore.Paths import VERSION, REVISION

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

        self.fixed = gtk.Fixed()
        self.verbox = gtk.VBox()
        self.version = gtk.Label("%s" % VERSION)
        self.revision = gtk.Label("Rev. %s" % REVISION)

        self.version.set_use_markup(True)
        self.version.set_markup("<span size='24000' weight='heavy'>\
%s</span>" % VERSION)
        self.revision.set_use_markup(True)
        self.revision.set_markup("<span size='10000' weight='heavy'>\
Rev. %s</span>" % REVISION)

        self.verbox.pack_start(self.version, False, False)
        self.verbox.pack_start(self.revision, False, False)

        self.fixed.put(self.verbox, width - 110, height - 55)
        self.add(self.fixed)

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
            self.input_shape_combine_mask(mask, 0, 0)
            self.window.set_back_pixmap(pixmap, False)
        else:
            gobject.idle_add(self.set_bg, widget, event, mask, pixmap)

if __name__ == "__main__":
    from os.path import join
    s = Splash(join(".", "share", "pixmaps", "splash.png"))
    gtk.main()