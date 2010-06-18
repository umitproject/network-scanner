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
from umit.core.UmitLogging import log
from umit.core.I18N import _


#Voidplace
from Voidplace import background_xpm
import gc # Garbage collector

'''
Special widgets 
with a wrapper 

The trick is have some gdk.Window
each node have one 


'''


NODE_SIZE = 6 


class SpecialWrapperEntry(object):
    '''
    It's a SpecialWrapper of any widget
    using with inheritance
    '''
    def __init__(self, widget):
        self._entry = widget
        self._ctr = False
        
        
    def unconstruct(self):
        self._left_down_win.set_user_data(None)
        self._left_down_win.destroy()

        self._left_up_win.set_user_data(None) 
        self._left_up_win.destroy()

        self._right_down_win.set_user_data(None)
        self._right_down_win.destroy()
        
        self._right_up_win.set_user_data(None)
        self._right_up_win.destroy()
        
        self._ctr  = True
    
    

        
    def construct(self):
        entry = self._entry
        
        #Left up window 
        win = gtk.gdk.Window(entry.window,
                             6 ,
                             6,
                             gtk.gdk.WINDOW_CHILD,
                             (gtk.gdk.ENTER_NOTIFY_MASK |
                              gtk.gdk.LEAVE_NOTIFY_MASK),
                             gtk.gdk.INPUT_OUTPUT,
                             'left up window',
                             0, 0,
                             entry.get_visual(),
                             entry.get_colormap(),
                             gtk.gdk.Cursor(entry.get_display(), gdk.LEFT_PTR),
                             '', '', True)
        self._left_up_win = win
        win.set_user_data(entry)
        c = win.get_colormap()
        color = c.alloc_color(0,0,0)  
        win.set_background(color)
        
        #Right up window
        win2 = gtk.gdk.Window(entry.window,
                             6, 
                             6,
                             gtk.gdk.WINDOW_CHILD,
                             (gtk.gdk.ENTER_NOTIFY_MASK |
                              gtk.gdk.LEAVE_NOTIFY_MASK),
                             gtk.gdk.INPUT_OUTPUT,
                             'right up window',
                             self._entry.allocation.width-6, 
                             0,
                             entry.get_visual(),
                             entry.get_colormap(),
                             gtk.gdk.Cursor(entry.get_display(), gdk.LEFT_PTR),
                             '', '', True)
        self._right_up_win = win2
        win2.set_user_data(entry)
        #win2.set_background(entry.style.base[entry.state])
        win2.set_background(color)
        #Right Down window
        win3 = gtk.gdk.Window(entry.window,
                             6, 
                             6,
                             gtk.gdk.WINDOW_CHILD,
                             (gtk.gdk.ENTER_NOTIFY_MASK |
                              gtk.gdk.LEAVE_NOTIFY_MASK),
                             gtk.gdk.INPUT_OUTPUT,
                             'right down window',
                             self._entry.allocation.width-6, 
                             self._entry.allocation.height-6,
                             entry.get_visual(),
                             entry.get_colormap(),
                             gtk.gdk.Cursor(entry.get_display(), gdk.LEFT_PTR),
                             '', '', True)
        self._right_down_win = win3
        win3.set_user_data(entry)
        win3.set_background(color)
        #Left down window 
        win4 = gtk.gdk.Window(entry.window,
                             6 ,
                             6,
                             gtk.gdk.WINDOW_CHILD,
                             (gtk.gdk.ENTER_NOTIFY_MASK |
                              gtk.gdk.LEAVE_NOTIFY_MASK),
                             gtk.gdk.INPUT_OUTPUT,
                             'left down window',
                             0, self._entry.allocation.height-6,
                             entry.get_visual(),
                             entry.get_colormap(),
                             gtk.gdk.Cursor(entry.get_display(), gdk.LEFT_PTR),
                             '', '', True)
        self._left_down_win = win4
        win4.set_user_data(entry)  
        win4.set_background(color)

        self._ctr = False
    def need_construct(self):
        '''
        @return : if need or not constuct 
        @rtype: bool
        
        '''
        return self._ctr
        
    def resize(self):
        self._right_up_win.move(0,0)  
        self._right_up_win.move(self._entry.allocation.width-6,0)  
        self._right_down_win.move(self._entry.allocation.width-6,
                                  self._entry.allocation.height-6)       
        self._left_down_win.move(0,self._entry.allocation.height-6)  
    def draw(self):
        self.resize()

        x,y,w,h = self._entry.allocation
        
        win = self._left_up_win
        c = win.get_colormap()
        color = c.alloc_color(0,0,0)   
        color = gtk.gdk.GC(win, 
                                   line_width=6, 
                                   foreground = color )
        win.draw_rectangle(color, True, 0, 0, 6, 6)
        win.show()

        win2 = self._right_up_win
        c = win2.get_colormap()
        color = c.alloc_color(0,0,0)   
        color = gtk.gdk.GC(win2, line_width=6, foreground = color )
        win2.draw_rectangle(color, True, 0, 0, 
                            6, 6)
        win2.show() 
        

        win3 = self._right_down_win
        c = win3.get_colormap()
        color = c.alloc_color(0,0,0)   
        color = gtk.gdk.GC(win3, line_width=6, foreground = color )
        win3.draw_rectangle(color, True, 0, 0, 
                            6, 6)
        win3.show() 
        
        win4 = self._left_down_win
        c = win4.get_colormap()
        color = c.alloc_color(0,0,0)   
        color = gtk.gdk.GC(win4, line_width=6, foreground = color )
        win4.draw_rectangle(color, True, 0, 0, 
                            6, 6)
        win4.show() 
        

class SpecialWrapperGeneric(object):
    ''' 
    This wrapper is for box and contaires 
    '''
    def __init__(self, widget):
        self._entry = widget
        self._vp = False
        self._ctr = False
        self._voidplace = None 

        
    def set_entry(self, entry):
        self._entry = entry

    def unconstruct(self):
        #FIXME: Warning GdkWindow (null) type

        self._left_down_win.set_user_data(None)
        self._left_down_win.destroy()

        self._left_up_win.set_user_data(None) 
        self._left_up_win.destroy()
        
        self._right_down_win.set_user_data(None)
        self._right_down_win.destroy()
        
        self._right_up_win.set_user_data(None)
        self._right_up_win.destroy()

        self._ctr  = False
        

    def unload_voidplace(self):
        log.debug('<<< Unload voidplace happen')
        self._voidplace.set_user_data(None)
        self._voidplace.destroy()
        self._voidplace = None
        self._vp = False

    def hide_voidplace(self):
        assert self._vp

        self._voidplace.hide()    
    def show_voidplace(self):
        assert self._vp 

        self._voidplace.show()

    def voidplace(self):
        '''
        Construct a voidplace 
        '''


        #print self._entry.allocation.width 
        self._xmp = background_xpm
        win_tmp = self._entry.window
        self._voidplace = gtk.gdk.Window(win_tmp,
                             self._entry.allocation.width ,
                             20,
                             gtk.gdk.WINDOW_CHILD,
                             (gtk.gdk.ENTER_NOTIFY_MASK |
                              gtk.gdk.EXPOSURE_MASK |
                              gtk.gdk.BUTTON_PRESS_MASK |
                              gtk.gdk.LEAVE_NOTIFY_MASK),
                             gtk.gdk.INPUT_OUTPUT,
                             'voidplace',
                             self._entry.allocation.x,self._entry.allocation.y,
                             self._entry.get_visual(),
                             self._entry.get_colormap(),
                             gtk.gdk.Cursor(self._entry.get_display(), gdk.LEFT_PTR),
                             '', '', True)
        self._voidplace.set_user_data(self._entry)
        temp_map = gdk.pixmap_colormap_create_from_xpm_d(self._voidplace,
                                                         self._entry.get_colormap(),
                                                         None,
                                                         self._xmp)
        self._voidplace.set_back_pixmap(temp_map[0], False)
        c= self._voidplace.get_colormap()
        color = c.alloc_color(0,65555,0)
        self._voidplace.show()
        self._vp = True 
    def is_voidplace(self):
        return self._voidplace!= None 
    
    def construct(self):
        #TROUBLE:  Warning: g_object_unref: assertion `G_IS_OBJECT (object)' failed
        #Problems like happen because a windows is over other window,
        #so the solution is destroy the over window

        entry = self._entry
        x,y,w,h = self._entry.allocation
        #Left up
        win = gtk.gdk.Window(entry.window,
                             6,
                             6,
                             gtk.gdk.WINDOW_CHILD,
                             (gtk.gdk.ENTER_NOTIFY_MASK |
                              gtk.gdk.LEAVE_NOTIFY_MASK),
                             gtk.gdk.INPUT_OUTPUT,
                             'icon window',
                             x, y,
                             entry.get_visual(),
                             entry.get_colormap(),
                             gtk.gdk.Cursor(entry.get_display(), gdk.LEFT_PTR),
                             '', '', True)
        
        self._left_up_win = win
        win.set_user_data(entry)  
        c = win.get_colormap()
        color = c.alloc_color(0,0,0)   
        win.set_background(color)

        #Left down 
        
        win2 = gtk.gdk.Window(entry.window,
                             6, 
                             6,
                             gtk.gdk.WINDOW_CHILD,
                             (gtk.gdk.ENTER_NOTIFY_MASK |
                              gtk.gdk.LEAVE_NOTIFY_MASK),
                             gtk.gdk.INPUT_OUTPUT,
                             'icon window',
                              x, 
                               y+h-6,
                             entry.get_visual(),
                             entry.get_colormap(),
                             gtk.gdk.Cursor(entry.get_display(), gdk.LEFT_PTR),
                             '', '', True)
        self._left_down_win = win2
        win2.set_user_data(entry)
        win2.set_background(color)

        #Right up
        win3 = gtk.gdk.Window(entry.window,
                             6, 
                             6,
                             gtk.gdk.WINDOW_CHILD,
                             (gtk.gdk.ENTER_NOTIFY_MASK |
                              gtk.gdk.LEAVE_NOTIFY_MASK),
                             gtk.gdk.INPUT_OUTPUT,
                             'icon window',
                              x+w-6, 
                               y,
                             entry.get_visual(),
                             entry.get_colormap(),
                             gtk.gdk.Cursor(entry.get_display(), gdk.LEFT_PTR),
                             '', '', True)
        self._right_up_win = win3
        win3.set_user_data(entry)
        win3.set_background(color)

        #Right down
        win4 = gtk.gdk.Window(entry.window,
                             6, 
                             6,
                             gtk.gdk.WINDOW_CHILD,
                             (gtk.gdk.ENTER_NOTIFY_MASK |
                              gtk.gdk.LEAVE_NOTIFY_MASK),
                             gtk.gdk.INPUT_OUTPUT,
                             'icon window',
                              x+w-6, 
                               y+h-6,
                             entry.get_visual(),
                             entry.get_colormap(),
                             gtk.gdk.Cursor(entry.get_display(), gdk.LEFT_PTR),
                             '', '', True)
        self._right_down_win = win4
        win4.set_user_data(entry)
        
        win4.set_background(color)        
        
        
        self._ctr  = True
    def get_draw(self):
        return self._ctr
    def resize_voidplace(self):

        x,y,w,h = self._entry.allocation
        #self._voidplace.show()
        self._voidplace.move(x,y)
        self._voidplace.resize(w, h)
        
        
    def resize(self):

        x,y,w,h = self._entry.allocation
        self._left_down_win.move(x, y+h-6)
        self._left_up_win.move(x, y)
        self._right_down_win.move(x+w-6, y)
        self._right_up_win.move(x+w-6, y+h-6)
        
        
    def draw(self):

        self.resize()
        x,y,w,h = self._entry.allocation
        win = self._left_down_win
        c = win.get_colormap()
        color = c.alloc_color(0,0,0)   
        color = gtk.gdk.GC(win, 
                                   line_width=6, 
                                   foreground = color )
        win.draw_rectangle(color, True, 0, 0, 6, 6)
        win.show()

        win2 = self._left_up_win
        c = win2.get_colormap()
        color = c.alloc_color(0,0,0)   
        color = gtk.gdk.GC(win2, line_width=6, foreground = color )
        win2.draw_rectangle(color, True, 0, 0, 6, 6)
        win2.show() 

        win2 = self._right_down_win
        c = win2.get_colormap()
        color = c.alloc_color(0,0,0)   
        color = gtk.gdk.GC(win2, line_width=6, foreground = color )
        win2.draw_rectangle(color, True, 0, 0, 6, 6)
        win2.show() 
        
        win2 = self._right_up_win
        c = win2.get_colormap()
        color = c.alloc_color(0,0,0)   
        color = gtk.gdk.GC(win2, line_width=6, foreground = color )
        win2.draw_rectangle(color, True, 0, 0, 6, 6)
        win2.show() 
        #...
        
class SpecialEntry(gtk.Entry):
    def __init__(self):
        gtk.Entry.__init__(self)
        self._icon = SpecialWrapperEntry(self)
    def do_realize(self):
        gtk.Entry.do_realize(self)
        self._icon.construct() 
    def do_expose_event(self,event):
        gtk.Entry.do_expose_event(self, event)
        self._icon.draw()
        
gobject.type_register(SpecialEntry)

from Voidplace import Voidplace

class SpecialVoidplace(Voidplace):
    def __init__(self):
        Voidplace.__init__(self)
        self._icon = SpecialWrapperEntry(self)
    def do_realize(self):
        Voidplace.do_realize(self)
        self._icon.construct() 
    def do_expose_event(self,event):
        Voidplace.do_expose_event(self, event)
        self._icon.draw()
        
gobject.type_register(SpecialVoidplace)

class SpecialHBox(gtk.HBox):
    def __init__(self, name= None):
        gtk.HBox.__init__(self)
        self._icon = None
        self._icon_exists = False 
        self.selected = False
        self._hide  = False
        self._vp = False 
        self._profileoption = None 
        self._name = name
        self.connect('show', self._show_items)
        self.connect('hide', self._hide_items)
    #Private API 
    def _button_press(self, widget, event, other):
        if not self._icon_exists:
            
            self._icon.construct()
            self._icon_exists=True
        
        #self._icon.draw()
        self.emit('button-press-event', event)
    def _hide_items(self, event):
        #log.debug('Hide event <<<')
        for i in self.get_children():
            i.hide()
    def _show_items(self, event):
        #log.debug('Show event <<<' )

        if self._hide :
            self._hide_items(None)
            return 
        if self.is_voidplace() :
            self._icon.show_voidplace()
            #log.debug('Show event <<< :: voidplace' )
        else: 
            for i in self.get_children():
                i.show()
                
            #log.debug('Show event <<< :: childrens' )
        if self.selected:
            self._icon.draw()
        self._hide = False
    def set_view(self, value):
        self._hide = not value
    def set_entry(self):
        self._icon.set_entry(self)
    def _key_press(self, widget, event, other):
        self.emit('key-press-event', event)
    
    #Public API
    def set_profileoption(self,profileoption):
        self._profileoption = profileoption
    def get_profileoption(self):
        return self._profileoption
    
    def set_name(self, name):
        self._name = name
        self._profileoption.set_label(name)
    def get_name(self):
        return self._name
    
    def do_realize(self):
        gtk.HBox.do_realize(self)
        self._icon = SpecialWrapperGeneric(self)
        self._icon.construct() 
        self._icon_exists= True 
    def is_voidplace_visible(self):
        return self._vp
    def is_hide(self):
        return self._hide
    def show_voidplace(self):
        if self.is_voidplace():
            self._icon.show_voidplace()
            self._vp = True
    def hide_voidplace(self):
        if self.is_voidplace():
            self._icon.hide_voidplace()   
            self._vp = False
            
        log.debug('hide voidplace')
   
    def do_voidplace(self):
        if self._icon == None : 
            return 
        self._icon.voidplace()
        self._vp = True
        
    def do_resize_voidplace(self):
        if self.is_voidplace():
            self._icon.resize_voidplace()
            
    def do_draw(self):
        if not self._icon_exists:
            self._icon.construct()
        if self._icon!= None :
            self._icon.draw()
    def do_drag_data_received(self, w, context, x, y, data, info):
        pass

    def do_expose_event(self,event):
        gtk.HBox.do_expose_event(self, event)

        self.do_resize_voidplace()

        self._icon.resize()


    def is_voidplace(self):
        
        if self._icon == None : 
            return False
        return self._icon.is_voidplace()
    
    def do_button_press_event(self, event):
        if self._icon!= None and self._icon_exists:
            self._icon.draw()

    def unload_voidplace(self):
        self._icon.unload_voidplace()
        self._vp = False 
        log.debug('unload voidplace')
    def set_select(self, value):
        self.selected = value 
        if not value and self._icon.get_draw():
            self._icon.unconstruct()
            self._icon_exists = False
    def pack_start(self, child, expand=True, fill=True):
        gtk.HBox.pack_start(self, child, expand, fill)
        child.connect('button-press-event', self._button_press, None)
        child.connect('key-press-event', self._key_press, None)
        
gobject.type_register(SpecialHBox)

class NotebookLabel(gtk.EventBox):
    '''
    Label to Notebook with nodes and borders when selectable
    '''
    def __init__(self, title = ''):
        gtk.EventBox.__init__(self)
        self.label = gtk.Label(title)
        self.add(self.label)
        self._icon = SpecialWrapperEntry(self)
        self._selected = None
        self._vp = False 
        self._name = None
    def set_name(self, name):
        self._name = name
    def get_name(self):
        return self._name
    def set_text(self, text):
        self.label.set_label(text)
    def get_text(self):
        return self.label.get_text()
    
    def set_select(self, value):
        self._selected = value 
    
    def do_realize(self):

        
        gtk.EventBox.do_realize(self)
        self.set_flags(self.flags() | gtk.REALIZED)
        self._icon.construct()
    def voidplace(self):
        '''
        Construct a voidplace 
        '''
        #if (self.window == None):
        #    return
        self._xmp = background_xpm
        win_tmp = self.get_parent_window()
        self._voidplace = gtk.gdk.Window(win_tmp,
                             self.allocation.width ,
                             self.allocation.height,
                             gtk.gdk.WINDOW_CHILD,
                             (gtk.gdk.ENTER_NOTIFY_MASK |
                              gtk.gdk.BUTTON_PRESS_MASK |
                              gtk.gdk.LEAVE_NOTIFY_MASK),
                             gtk.gdk.INPUT_OUTPUT,
                             'voidplace',
                             self.allocation.x,self.allocation.y,
                             self.get_visual(),
                             self.get_colormap(),
                             gtk.gdk.Cursor(self.get_display(), gdk.LEFT_PTR),
                             '', '', True)
        self._voidplace.set_user_data(self)
        self.style.attach(self.window)
        temp_map = gdk.pixmap_colormap_create_from_xpm_d(self._voidplace,
                                                         self.get_colormap(),
                                                         None,
                                                         self._xmp)
        self._voidplace.set_back_pixmap(temp_map[0], False)
        c= self._voidplace.get_colormap()
        color = c.alloc_color(0,65555,0)
        self._draw_gc = gtk.gdk.GC(self._voidplace, 
                                   line_width=6, 
                                   foreground = color )
        self._voidplace.draw_rectangle(self._draw_gc, True, self.allocation.x, 
                                   self.allocation.y, self.allocation.width,
                                   self.allocation.height)
        self._voidplace.show()
        self._vp = True     
    
    def unload(self):
        if not self._icon.need_construct():
            self._icon.unconstruct()
        if self._vp:
            #self._voidplace.set_background(self.style.base[gtk.STATE_NORMAL])
            self._voidplace.set_user_data(None)
            self._voidplace.destroy()
            self._voidplace = None
    def hide_voidplace(self):
        '''
        Hide voidplace
        '''
        self._voidplace.hide()
    def show_voidplace(self):
        ''' 
        Show Voidplace 
        '''
        self._voidplace.show()
    
    def unload_voidplace(self):
        self._voidplace.set_user_data(None)
        self._voidplace.destroy()
        self._voidplace = None
        self._vp=False
        self._selected=True

    def is_voidplace(self):
        return self._vp
    def resize_voidplace(self):
        if self.is_voidplace():
            self._voidplace.show()
            x,y,w,h = self.allocation
            self._voidplace.move(x,y)
            self._voidplace.resize(w, h)
    def do_draw(self):
        if self._selected and not self._vp:
            self._icon.construct()
            self._icon.draw()
    def do_expose_event(self, event):
        
        gtk.EventBox.do_expose_event(self,event)
        if self._selected and not self._vp:
            if self._icon.need_construct():
                self._icon.construct()
            #self._icon.draw()
        else:          
            if not self._icon.need_construct():
                self._icon.unconstruct()
        self.resize_voidplace()


gobject.type_register(NotebookLabel)