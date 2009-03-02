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
import gobject
from gtk import gdk
MIN_WIDTH = 200
MIN_HEIGHT = 30
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

SELECTION_NODE_SIZE = 6
BORDER_WIDTH = 3
class Border(object):
    def __init__(self, width=1):
        self._selected = None
        self._draw_gc = None
        self._selection_width = width
        self.unset_flags(gtk.NO_WINDOW)
        self.set_redraw_on_allocate(True)
        self.set_spacing(21)
        self.set_border_width(6)

    # Public API

    def get_selected(self):
        """
        @returns: the currently selected widget
        """

        return self._selected

    def set_selected(self, widget, merda=None):
        """
        @param widget: widget to select, must be a children of self
        """

        #if not widget in self.get_children():
        #    raise ValueError("widget must be a child of %r" % self)

        old_selected = self._selected
        self._selected = widget
        if old_selected != widget:
            self.queue_draw()
            print "queue"


    def pack_start(self, child, expand=True, fill=True, padding=0):
        """
        Identical to gtk.Box.pack_start
        """
        #box = gtk.HBox()
        #box.set_border_width(5)
        #box.pack_start(child,  expand=expand, fill=fill, padding=padding)
        super(Border, self).pack_start(child, expand=expand,
                                              fill=fill, padding=padding)
        self._child_added(child)
    def pack_end(self, child, expand=True, fill=True, padding=0):
        """
        Identical to gtk.Box.pack_end
        """
        super(Border, self).pack_end(child, expand=expand,
                                            fill=fill, padding=padding)
        self._child_added(child)

    def add(self, child):
        """
        Identical to gtk.Container.add
        """
        super(Border, self).add(child)
        self._child_added(child)

    def update_selection(self):
        selected = self._selected
        if not selected:
            return

        border = self._selection_width
        x, y, w, h = selected.allocation
        self.window.draw_rectangle(self._draw_gc, False,
                                   x - (border / 2), y - (border / 2),
                                   w + border, h + border)
        print "print mesmo"
        self.draw_nodes(x,y,w,h)
        
    # GtkWidget
    def draw_nodes(self, x, y, width, height):
        gc = self._draw_gc

        window = self._selected.window

        gc = gdk.GC(window, line_width=self._selection_width)
        if width > SELECTION_NODE_SIZE and height > SELECTION_NODE_SIZE:
            window.draw_rectangle(gc, True, x, y,
                                  SELECTION_NODE_SIZE, SELECTION_NODE_SIZE)
            window.draw_rectangle(gc, True, x, y + height -SELECTION_NODE_SIZE,
                                  SELECTION_NODE_SIZE, SELECTION_NODE_SIZE)
            window.draw_rectangle(gc, True, x + width - SELECTION_NODE_SIZE, y,
                                  SELECTION_NODE_SIZE, SELECTION_NODE_SIZE)
            window.draw_rectangle(gc, True, x + width - SELECTION_NODE_SIZE,
                                  y + height - SELECTION_NODE_SIZE,
                                  SELECTION_NODE_SIZE, SELECTION_NODE_SIZE)
            window.draw_rectangle(gc, False, x, y, width - 1, height - 1)

    def do_realize(self):
        assert not (self.flags() & gtk.NO_WINDOW)
        self.set_flags(self.flags() | gtk.REALIZED)
        self.window = gdk.Window(self.get_parent_window(),
                                 width=self.allocation.width,
                                 height=self.allocation.height,
                                 window_type=gdk.WINDOW_CHILD,
                                 wclass=gdk.INPUT_OUTPUT,
                                 event_mask=(self.get_events() |
                                             gdk.EXPOSURE_MASK |
                                             gdk.BUTTON_PRESS_MASK))
       
        self.window.set_user_data(self)
        self.style.attach(self.window)
        self.style.set_background(self.window, gtk.STATE_NORMAL)
        c = self.get_colormap()
        color = c.alloc_color(1,1,1)
        self._draw_gc = gdk.GC(self.window,
                               line_width=self._selection_width,
                               line_style=gdk.SOLID,
                               #foreground=self.style.bg[gtk.STATE_PRELIGHT])
                               foreground=color)
                 
    def do_button_press_event(self, event):
        selected = self._get_child_at_pos(int(event.x), int(event.y))
        if selected:
            self.set_selected(selected)
        
            

    # Private

    def _get_child_at_pos(self, x, y):
        """
        @param x: x coordinate
        @type x: integer
        @param y: y coordinate
        @type y: integer
        """


        toplevel = self.get_toplevel()
        for child in self.get_children():
            #print child

            coords = toplevel.translate_coordinates(child, x, y)
            if not coords:
                continue

            child_x, child_y = coords
            if (0 <= child_x < child.allocation.width and
                0 <= child_y < child.allocation.height and 
                child.flags() & (gtk.MAPPED | gtk.VISIBLE)):
                
                #print "RETURN"
                return child

    def _child_added(self, child):
        #child.connect('button-press-event',
                      #lambda child, e: self.set_selected(child))
        child.connect('button-press-event',self.set_selected)

class GenericBorder(Border, gtk.VBox):
    __gtype_name__ = 'GenericBorder'

    def __init__(self, width=1):

        gtk.VBox.__init__(self)
        Border.__init__(self, width=width)

    do_realize = Border.do_realize
    do_button_press_event = Border.do_button_press_event

    def do_size_allocate(self, allocation):
        gtk.VBox.do_size_allocate(self, allocation)
        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*allocation)

    def do_expose_event(self, event):
        gtk.VBox.do_expose_event(self, event)
        self.update_selection()
        



class BackgroundWidget(gtk.Widget):
    ''' 
    This is a background for editor 
    
    Use a generic widget and it filled with gdk
    
    '''
    
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
                  gtk.gdk.POINTER_MOTION_MASK |
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

        # These lines make the Placeholder looks like a button
        event.window.draw_line(light_gc, 0, 0, w - 1, 0)
        event.window.draw_line(light_gc, 0, 0, 0, h - 1)
        event.window.draw_line(dark_gc, 0, h -1, w - 1, h - 1)
        event.window.draw_line(dark_gc, w - 1, 0, w - 1, h - 1)
        return False


    def do_motion_notify_event(self, event):
        return False

    def do_button_press_event(self, event):
        light_gc = self.style.light_gc[gtk.STATE_NORMAL]
        dark_gc = self.style.dark_gc[gtk.STATE_NORMAL]
        w, h = event.window.get_size()
        #


        # These lines make the Placeholder looks like a button
        event.window.draw_line(light_gc, 0, 0, w - 1, 0)
        event.window.draw_line(light_gc, 0, 0, 0, h - 1)
        event.window.draw_line(dark_gc, 0, h -1, w - 1, h - 1)
        event.window.draw_line(dark_gc, w - 1, 0, w - 1, h - 1)
        x,y,w, h = self.allocation
        
        x,y,width, height = self.allocation
        border = 5
        gc = gdk.GC(self.window, line_width=3)
        
        window = self.window
        window.draw_rectangle(gc, True, x, y,
                              SELECTION_NODE_SIZE, SELECTION_NODE_SIZE)
        window.draw_rectangle(gc, True, x, y + height -SELECTION_NODE_SIZE,
                              SELECTION_NODE_SIZE, SELECTION_NODE_SIZE)
        window.draw_rectangle(gc, True, x + width - SELECTION_NODE_SIZE, y,
                              SELECTION_NODE_SIZE, SELECTION_NODE_SIZE)
        window.draw_rectangle(gc, True, x + width - SELECTION_NODE_SIZE,
                              y + height - SELECTION_NODE_SIZE,
                              SELECTION_NODE_SIZE, SELECTION_NODE_SIZE)
            
        window.draw_rectangle(gc, False, x, y, width - 1, height - 1)
        #self.draw_nodes( x,y,w, h)
    def get_cenas(self,x,y,w,h):
        #self.queue_draw()
        #self.draw_nodes( x,y,w, h)
        return self.window


gobject.type_register(BackgroundWidget)
def main():
    w = gtk.Window()
    new_widget = BackgroundWidget()
    new_widget2 = BackgroundWidget()
    new_widget3 = BackgroundWidget()
    bb= gtk.Button('sadas')
    #bb.connect('clicked', new_widget.desenha_ponto)

    new_widget.show()
    ev = gtk.EventBox()
    new_widget2.show()
    ev.add(new_widget2)

    label = gtk.Label('ffffff!!!!!!!!!!!!!!!!')
    check = gtk.CheckButton('fsck')
    entr = gtk.Entry()
    #s = gtk.VBox()
    s = GenericBorder()
    a = gtk.EventBox()
    a.add(new_widget3)
    s.pack_start(label, True, True,0)
    s.pack_start(new_widget, True, True,0)
    s.pack_start(bb, True, True,0)
    ev_t = gtk.EventBox()
    ev_t.add(entr)
    s.pack_start(ev, True, True,0)
    s.pack_start(check, True, True,0)
    s.pack_start(ev_t, True, True,0)
    s.pack_start(a, True, True,0)

    w.add(s)
    w.show_all()
    gtk.main()

def main2():
    w = gtk.Window()
    new_widget = BackgroundWidget()
    new_widget2 = BackgroundWidget()
    new_widget3 = BackgroundWidget()
    bb= gtk.Button('sadas')
    #bb.connect('clicked', new_widget.desenha_ponto)

    new_widget.show()
    ev = gtk.EventBox()
    new_widget2.show()
    ev.add(new_widget2)

    label = gtk.Label('ffffff!!!!!!!!!!!!!!!!')
    check = gtk.CheckButton('fsck')
    entr = gtk.Entry()
    s = GenericBorder()
    a = gtk.EventBox()
    a.add(new_widget3)
    s.pack_start(label, True, True,0)
    s.pack_start(new_widget, True, True,0)
    s.pack_start(bb, True, True,0)
    ev_t = gtk.EventBox()
    ev_t.add(entr)
    s.pack_start(ev, True, True,0)
    s.pack_start(check, True, True,0)
    s.pack_start(ev_t, True, True,0)
    s.pack_start(a, True, True,0)

    w.add(s)
    w.show_all()
    gtk.main()
    
if __name__ == "__main__":
    main()
        
        
        
        
