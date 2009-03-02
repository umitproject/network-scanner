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
from higwidgets.higboxes import HIGHBox

class Editor(HIGHBox):

    """
    Create a mainFrame
    """
    def __init__(self):
        HIGHBox.__init__(self)
        
        self.frame = gtk.Frame()
        
        self._pack_expand_fill(self.frame)
        self.__create_draw_area()
        
    def __create_draw_area(self):
        #falta
        #codigo
        msg = "error"
        
    def add_option(self, widget):     
        """
        Add a option to draw area
        """
        assert widget != None
        
        self._pack_expand_fill(widget)
        self.align = gtk.Alignment(0.5,0.5,0,0)
        self.align.set_border_width(5)
        
    
    def remove_option(self, widget):        
        """ 
        Remove option from draw area 
        """
        assert widget != None
        self.remove(widget)


class SelButton(gtk.DrawingArea):
    def __init__(self):
        gtk.DrawingArea.__init__(self)
        self.window = gtk.gdk.Window()



