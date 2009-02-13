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
class PlaceBack(gtk.Widget):
    '''
    This is a background of edit area 
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
    
    
gobject.type_register(PlaceBack)

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
        #for i in self.widget_list:
            #x,y,w,h = self.allocation
            #x,y = i.window.get_position()
            
            #self.window.draw_line(self._draw_gc, x,y, x+w, y)
        
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

# Teste .... 
class kOpSpecialDrawableEntry(gtk.EventBox):
    __gtype_name__ = 'kOpSpecialDrawableEntry'
    def __init__(self):
        gtk.EventBox.__init__(self)
        self.set_border_width(6)
    def do_realize(self):
        self.set_flags(self.flags() | gtk.REALIZED) 
        
        gtk.EventBox.do_realize(self)

        temporary_window = self.get_parent_window()
        events = ( gdk.EXPOSURE_MASK |
                   gdk.BUTTON_PRESS_MASK |
                   gdk.BUTTON_RELEASE_MASK | 
                   gdk.MOTION_NOTIFY )
        self.window = gdk.Window(temporary_window,
                                 width = self.allocation.width,
                                 height = self.allocation.height,
                                 window_type = gdk.WINDOW_CHILD,
                                 event_mask = (self.get_events() |events) ,
                                 wclass = gdk.INPUT_OUTPUT,
                                 visual = self.get_visual(),
                                 x = self.allocation.x,
                                 y = self.allocation.y)
        

        self.window.set_user_data(self)
        self.window.set_background(self.style.base[self.state])        
        #self.style.attach(self.window)
        c= self.get_colormap()
        color = c.alloc_color(65000,0,0)                                                                                                                            
        #self.style.set_background(self.window, gtk.STATE_NORMAL)
        
                                
        self._draw_gc = gtk.gdk.GC(self.window, 
                                   line_width=6, 
                                   foreground = color )
        x,y,w, h = self.allocation 
        self.window.draw_rectangle(self._draw_gc, True, 0, 0, 30, 30)

    def do_button_release_event(self, event):
        pass

    def do_button_press_event(self, event):
        pass
    def do_size_allocate(self, allocation):
        gtk.EventBox.do_size_allocate(self, allocation)
        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*allocation)    
    def do_expose_event(self, event):
        #print "expose"
        gtk.EventBox.do_expose_event(self,event)
        x,y,w, h = self.allocation 
        #print x,y,w,h
        self.window.draw_rectangle(self._draw_gc, True, 0, 0, 90, 30)
        #print "here"

gobject.type_register(kOpSpecialDrawableEntry)

class SpecialWrapperEntry(object):
    def __init__(self, widget):
        self._entry = widget
    def construct(self):
        entry = self._entry
        #        if not entry.flags() & gtk.REALIZED:
        #            entry.realize()
        win = gtk.gdk.Window(entry.window,
                             self._entry.allocation.width/2 ,
                             self._entry.allocation.height,
                             gtk.gdk.WINDOW_CHILD,
                             (gtk.gdk.ENTER_NOTIFY_MASK |
                              gtk.gdk.LEAVE_NOTIFY_MASK),
                             gtk.gdk.INPUT_OUTPUT,
                             'icon window',
                             0, 0,
                             entry.get_visual(),
                             entry.get_colormap(),
                             gtk.gdk.Cursor(entry.get_display(), gdk.LEFT_PTR),
                             '', '', True)
        self._icon_win = win
        win.set_user_data(entry)  
        win.set_background(entry.style.base[entry.state])
        win2 = gtk.gdk.Window(entry.window,
                             self._entry.allocation.width/2, 
                             self._entry.allocation.height,
                             gtk.gdk.WINDOW_CHILD,
                             (gtk.gdk.ENTER_NOTIFY_MASK |
                              gtk.gdk.LEAVE_NOTIFY_MASK),
                             gtk.gdk.INPUT_OUTPUT,
                             'icon window',
                             self._entry.allocation.width/2, 
                             0,
                             entry.get_visual(),
                             entry.get_colormap(),
                             gtk.gdk.Cursor(entry.get_display(), gdk.LEFT_PTR),
                             '', '', True)
        self._icon_win2 = win2
        win2.set_user_data(entry)
        
        win2.set_background(entry.style.base[entry.state])
        
    def resize(self):

        self._icon_win.resize(self._entry.allocation.width/2,
                              self._entry.allocation.height)
        self._icon_win2.resize(self._entry.allocation.width/2,
                              self._entry.allocation.height)
        self._icon_win2.move(self._entry.allocation.width/2,
                              0)        
    def draw(self):
        self.resize()

        x,y,w,h = self._entry.allocation
        win = self._icon_win
        c = win.get_colormap()
        color = c.alloc_color(65000,0,0)   
        color = gtk.gdk.GC(win, 
                                   line_width=6, 
                                   foreground = color )
        win.draw_rectangle(color, True, 0, 0, 20, 20)
        win.show()

        win2 = self._icon_win2
        c = win2.get_colormap()
        color = c.alloc_color(0,65000,0)   
        color = gtk.gdk.GC(win2, line_width=6, foreground = color )
        win2.draw_rectangle(color, True, 0, 0, 
                            30, 30)
        win2.show() 


class SpecialEntry(gtk.Entry):
    def __init__(self):
        gtk.Entry.__init__(self)
        self._icon = SpecialWrapperEntry(self)
    def do_realize(self):
        gtk.Entry.do_realize(self)
        self._icon.construct()
        self.set_flags(self.flags() | gtk.REALIZED) 
        
        temporary_window = self.get_parent_window()
        events = ( gdk.EXPOSURE_MASK |
                   gdk.BUTTON_PRESS_MASK |
                   gdk.BUTTON_RELEASE_MASK | 
                   gdk.MOTION_NOTIFY )       
        #self.window = gdk.Window(temporary_window,
                                 #width = self.allocation.width,
                                 #height = self.allocation.height,
                                 #window_type = gdk.WINDOW_CHILD,
                                 #event_mask = (self.get_events() |events) ,
                                 #wclass = gdk.INPUT_OUTPUT,
                                 #visual = self.get_visual(),
                                 #x = self.allocation.x,
                                 #y = self.allocation.y,
                                 #cursor=gtk.gdk.Cursor(self.get_display(), gdk.LEFT_PTR))
        
        
        #self.window.set_user_data(self)
        #self.window.set_background(self.style.base[self.state])
        #self.style.attach(self.window)
        c= self.get_colormap()
        color = c.alloc_color(65000,0,0)        
        #self.style.set_background(self.window, gtk.STATE_NORMAL)
        self._draw_gc = gtk.gdk.GC(self.window, 
                                   line_width=6, 
                                   foreground = color )
        x,y,w, h = self.allocation 
        #self.window.draw_rectangle(self._draw_gc, True, 0, 0, 30, 30)
    
    def do_expose_event(self,event):
        gtk.Entry.do_expose_event(self, event)
        #x,y,w, h = self.allocation 
        #self.window.draw_rectangle(self._draw_gc, True, 0, 0, 30, 30)
        self._icon.draw()
        #self._icon.resize()

gobject.type_register(SpecialEntry)






def main():
    win = gtk.Window()
    #---BEGIN
    tmp_box = kOpSpecialDrawableEntry()
    box = gtk.HBox()
    pb = PlaceBack()
    
    box.pack_start(pb, True, True)
    tmp_box.add(box)
    #---- BEGIN 
    bg4 = gtk.Entry()
    bg4.set_text('What?')
    bg5 = gtk.CheckButton('Need Root?')
    bg7 = kOpSpecialDrawableEntry()
    bg6 = gtk.HBox()
    bg6.pack_start(bg5, True, True)
    bg6.pack_start(bg4, True, True)
    bg7.add(bg6)
    #----- END
    win.connect("destroy",gtk.main_quit)
    cont1 = ContainerPlace()

    vbox = gtk.VBox()
    vbox.set_border_width(3)
    vbox.set_spacing(30)
    vbox.set_size_request(200,250)
    cont1.pack_start(tmp_box, True, True,0)
    cont1.pack_start(bg7,True, True,0)

    vbox.pack_start(cont1, True, True)
    se = SpecialEntry()
    se.set_text('ss')

    pb_ = PlaceBack()
    vbox.pack_start(se, True, True )
    vbox.pack_start(pb_, True, True )

    win.add(vbox)
    win.show_all()
    wrap= SpecialWrapperEntry(pb_)
    wrap.construct()
    wrap.draw()
    gtk.main()
if __name__ == "__main__":
    main()