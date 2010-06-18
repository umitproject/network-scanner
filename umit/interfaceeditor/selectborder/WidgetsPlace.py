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

import gobject
import gtk
from gtk import gdk


class ContainerPlaceGeneric(object):
    '''
    A generic place to put widgets
    '''
    def __init__(self):
        self.unset_flags(gtk.NO_WINDOW)
        self.set_redraw_on_allocate(True)
        self.set_border_width(6)
        self.set_spacing(6)
        self._draw_gc = None
        self.last_added = None 
        self.widget_list = []
    
    def pack_start(self, child,  expand=True, fill=True, padding = 0):
        super(ContainerPlaceGeneric, self).pack_start(child,
                                                      expand=expand,
                                                      fill = fill, 
                                                      padding = padding)
        self._child_add(child)
        self.last_added = child
    
    def _child_add(self, child):
        self.widget_list.append(child)

    def do_realize(self):
        assert not (self.flags() & gtk.NO_WINDOW)
        self.set_flags(self.flags() | gtk.REALIZED)
        
        events = ( gtk.gdk.EXPOSURE_MASK |
                   gtk.gdk.BUTTON_PRESS_MASK |
                   gtk.gdk.BUTTON_RELEASE_MASK)

        self.window = gtk.gdk.Window(self.get_parent_window(),
                                     x=self.allocation.x,
                                     y=self.allocation.y, 
                                     width = self.allocation.width,
                                     height = self.allocation.height,
                                     window_type = gdk.WINDOW_CHILD,
                                     event_mask = (self.get_events() | events ),
                                     wclass = gdk.INPUT_OUTPUT, 
                                     visual=self.get_visual(),
                                     colormap = self.get_colormap())
        self.window.set_user_data(self)
        self.style.attach(self.window)
        c= self.get_colormap()
        color = c.alloc_color(45000,45000,45000)
        self.style.set_background(self.window, gtk.STATE_NORMAL)
                                
        self._draw_gc = gtk.gdk.GC(self.window, 
                                   line_width=6, 
                                   foreground = color )

    def do_expose_event(self, event):
        pass

        
    def do_button_press_event(self, event):
        pass

class ContainerPlace(ContainerPlaceGeneric, gtk.VBox):
    '''
    Place to put widgets 
    '''
    __gtype_name__ = 'ContainerPlace'
    def __init__(self):
        gtk.VBox.__init__(self)
        ContainerPlaceGeneric.__init__(self)

    do_realize = ContainerPlaceGeneric.do_realize
    do_button_press_event=ContainerPlaceGeneric.do_button_press_event
    
    def do_size_allocate(self, allocation):
        gtk.VBox.do_size_allocate(self, allocation)
        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*allocation)
    def do_expose_event(self, event):
        gtk.VBox.do_expose_event(self, event)
        ContainerPlaceGeneric.do_expose_event(self,event)
     
gobject.type_register(ContainerPlace)


from Voidplace import Voidplace
from WrapperWidgets import SpecialHBox, SpecialVoidplace

class EditArea(ContainerPlace):
    def __init__(self, size = 7):
        ContainerPlace.__init__(self)
        self.widgets = [] 
        self.size = size
        for i in range(size):
            self.add_voidplace()
    def add_voidplace(self):
        vp = Voidplace()
        sh = SpecialHBox()
        sh.pack_start(vp, True, True)
        self.widgets.append(sh)
        self.pack_start(sh, True, True)
    def do_expose_event(self, event):
        ContainerPlace.do_expose_event(self, event)
        for i in self.widgets:
            i.do_draw()
    
        
gobject.type_register(EditArea)


def main():
    w = gtk.Window()
    w.set_size_request(200,300)
    ea = EditArea(size=8)
    w.add(ea)
    w.show_all()
    gtk.main()
if __name__=="__main__":
    main()

