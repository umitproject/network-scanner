#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Adriano Monteiro Marques
#
# Author: Luís A. Bastião Silva <luis.kop@gmail.com>
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
from gtk import gdk
import gobject


background_xpm = [
    # columns rows colors chars-per-pixel
    "8 8 2 1",
    "  c #bbbbbb",
    ". c #0000FF",
    # pixels
    " .  .   ",
    ".    .  ",
    "      ..",
    "      ..",
    ".    .  ",
    " .  .   ",
    "  ..    ",
    "  ..    ",
    ]
MIN_WIDTH = MIN_HEIGHT= 100
class BackgroundWidget(gtk.Widget):  
    def __init__(self):
        gtk.Widget.__init__(self)
        #Attributes
        self._pixmap = None
        self._xmp = background_xpm
        #self.unset_flags(gtk.VISIBLE)
        #self.set_flags(self.flags() | gtk.COMPOSITE_CHILD)
        
        self.show()
    def do_realize(self):
        self.set_flags(self.flags() | gtk.REALIZED)
        
        events = (gtk.gdk.EXPOSURE_MASK |
                  gtk.gdk.BUTTON_PRESS_MASK |
                  gtk.gdk.POINTER_MOTION_MASK|
                  gtk.gdk.BUTTON_RELEASE_MASK)
        self.window = gtk.gdk.Window(self.get_parent_window(), 
                                     x=self.allocation.x,
                                     y=self.allocation.y,
                                     width = self.allocation.width,
                                     height = self.allocation.height,
                                     window_type = gtk.gdk.WINDOW_CHILD, 
                                     wclass = gtk.gdk.INPUT_OUTPUT, 
                                     visual=self.get_visual(),
                                     colormap = self.get_colormap(),
                                     event_mask = self.get_events() | events)
        self.window.set_user_data(self)
        self.style.attach(self.window)
        c = self.get_colormap()
        color = c.alloc_color(65000,6500,655)
        self.style.set_background(self.window,3)

        if not self._pixmap:
            temp = gtk.gdk.pixmap_colormap_create_from_xpm_d(None, 
                                                           self.get_colormap(), 
                                                           None,
                                                           self._xmp)
            self._pixmap = temp[0]
        
        self.window.set_back_pixmap(self._pixmap, False)
        
    def do_size_allocate(self, allocation):

        self.allocation = allocation
        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*allocation)

    def do_size_request(self, requisition):
        requisition.width = MIN_WIDTH
        requisition.height = MIN_HEIGHT

    def do_expose_event(self, event):
        light_gc = self.style.light_gc[gtk.STATE_NORMAL]
        dark_gc = self.style.dark_gc[gtk.STATE_NORMAL]
        w, h = event.window.get_size()
        self.do_size_allocate(gtk.gdk.Rectangle(self.allocation.x, self.allocation.y, w, h))

        # These lines make the Placeholder looks like a button
        event.window.draw_line(light_gc, 0, 0, w - 1, 0)
        event.window.draw_line(light_gc, 0, 0, 0, h - 1)
        event.window.draw_line(dark_gc, 0, h -1, w - 1, h - 1)
        event.window.draw_line(dark_gc, w - 1, 0, w - 1, h - 1)
        return False


    def do_motion_notify_event(self, event):

        return False
    def do_button_release_event(self,event):
        x,y,h,w = self.allocation
        self.window.clear_area(x,y,w,h)
    def do_button_press_event(self, event):
        gc = gdk.GC(self.window, line_width=5, line_style = gtk.gdk.SOLID,
                    foreground=self.style.bg[gtk.STATE_SELECTED])
        x,y,h,w = self.allocation
        self.window.draw_rectangle(gc, True, x,y, w, h)

gobject.type_register(BackgroundWidget)



















def main():
    win = gtk.Window()
    new_widget = BackgroundWidget()
    new_widget2 = BackgroundWidget()
    bb= gtk.Button('sadas')
    ev = gtk.HBox()
    ev.pack_start(new_widget2, True, True, 0)

    label = gtk.Label('ffffff!!!!!!!!!!!!!!!!')
   
    check = gtk.CheckButton('fsck')
    entr = gtk.Entry()
    s = gtk.VBox()
    #s.pack_start(label, False, False,0)
    s.pack_start(new_widget, True, True,0)
    #s.pack_start(bb, False, False,0)
    #ev_t = gtk.EventBox()
    #ev_t.add(entr)
    s.pack_start(ev, True, True,0)
    #s.pack_start(check, False, False,0)
    #s.pack_start(ev_t, False, False,0)
    win.add(s)
    win.show_all()
    gtk.main()   
if __name__ == "__main__":
    main()
            