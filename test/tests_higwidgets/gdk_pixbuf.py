#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2005 Insecure.Com LLC.
#
# Author: Adriano Monteiro Marques <py.adriano@gmail.com>
#         Cleber Rodrigues <cleber.gnu@gmail.com>
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

w = gtk.Window()

vb = gtk.VBox()
hb = gtk.HBox()

w_e = gtk.Entry()
h_e = gtk.Entry()
r_b = gtk.Button("resize")

i = gtk.Image()
i.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file("gnome-green-rest.png"))

def cb_do_resize(widget, image, width_entry, height_entry):

    width = int(width_entry.get_text())
    height = int(height_entry.get_text())
    
    pixbuf = image.get_pixbuf()
    pixbuf.scale_simple(width, height, gtk.gdk.INTERP_BILINEAR)

    image.set_from_pixbuf(pixbuf)
    image.hide()
    image.show()
    image.queue_draw()


w.connect('delete-event', gtk.main_quit)
r_b.connect('clicked', cb_do_resize, i, w_e, h_e)

vb.pack_start(i)
vb.pack_start(hb)

for widget in (w_e, h_e, r_b):
    hb.pack_start(widget)

w.add(vb)
w.show_all()
gtk.main()
