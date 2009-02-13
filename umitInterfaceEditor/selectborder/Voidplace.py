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
    ". c #FFFFFF",
    # pixels
    " .  .   ",
    ".  .    ",
    "     .. ",
    "     .. ",
    ".    .  ",
    " .  .   ",
    "  . .   ",
    "  ..    ",
    ]


class Voidplace(gtk.Widget):
    '''
    This is a background of edit area 
    it's a void place
    '''
    def __init__(self):
        gtk.Widget.__init__(self)
        self._xmp = background_xpm
    
    def do_realize(self):

        self.set_flags(self.flags() | gtk.REALIZED)
        
        temporary_window = self.get_parent_window()
        events = (gdk.EXPOSURE_MASK | 
                  gdk.BUTTON_PRESS_MASK |
                  gdk.BUTTON_RELEASE_MASK | 
                  gdk.MOTION_NOTIFY )
        self.window = gdk.Window(temporary_window,
                                 width = self.allocation.width,
                                 height = self.allocation.height,
                                 window_type = gdk.WINDOW_CHILD,
                                 event_mask = (self.get_events() | events ),
                                 wclass = gdk.INPUT_OUTPUT,
                                 x = self.allocation.x,
                                 y = self.allocation.y)

        self.window.set_user_data(self)
        self.style.attach(self.window)
        temp_map = gdk.pixmap_colormap_create_from_xpm_d(self.window,
                                                         self.get_colormap(),
                                                         None,
                                                         self._xmp)
        self.window.set_back_pixmap(temp_map[0], False)

    def do_expose_event(self, event):
        pass
        
    def do_size_request(self, requestion):
        pass
    def do_size_allocation(self, allocation):
        self.allocation
        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*allocation)
    def do_button_press_event(self, event):
        x,y,w,h = self.allocation
        c= self.get_colormap()
        color = c.alloc_color(0,0,0)
        self._draw_gc = gtk.gdk.GC(self.window, 
                                   line_width=2, 
                                   foreground = color )
        self.window.draw_rectangle(self._draw_gc,False, 0,0, w, h)
        
    def do_button_release_event(self, event):
        pass
        
    def do_motion_notify_event(self, event):
        pass
    
gobject.type_register(Voidplace)

        