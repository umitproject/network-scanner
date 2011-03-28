#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2008 Adriano Monteiro Marques.
#
# Author: Luis A. Bastiao Silva <luis.kop@gmail.com>
#
# This library is free software; you can redistribute it and/or modify 
# it under the terms of the GNU Lesser General Public License as published 
# by the Free Software Foundation; either version 2.1 of the License, or 
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public 
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License 
# along with this library; if not, write to the Free Software Foundation, 
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA 

from math import pi

"""
This module make some designs in cairo contex
"""


def cr_rectangule_curve( cr, x, y, w, h, radius=10):
    """
    Draw rectangule with curve corner
    @param cr: CairoContext
    @param x: x coord
    @param y: y coord
    @param w: width of rectangle
    @param h: height of rectangle
    @param radius: defautl -> 10
    """
    
    #print "Raio = %d\n x = %d ;; y = %d ;; w = %d ;; h = %d " %(radius,\
                                                                #x,y,w,h)
    ## Left top corner
    #cr.new_path()
    #cr.arc(x+radius,y+radius, radius,pi, (3/2)*pi)
    #cr.fill_preserve()
    ## Right top corner
    #cr.move_to(0,0)
    #cr.arc(w+x-radius,y-radius, radius,(3/2)*pi, 2*pi)
    #cr.fill_preserve()
    ### Left button corner 
    ##cr.arc(x+radius,y+h-radius, radius,0.5*pi, pi)
    
    ### Right button corner
    ##cr.arc(x+w-radius,y+h-radius, radius,0, 0.5*pi)
    #cr.close_path()
    
    # References:
    # http://lists.freedesktop.org/archives/cairo-commit/2007-July/008204.html
    
    context = cr 
    r = radius
    context.move_to(x+r,y)                      # Move to A
    context.line_to(x+w-r,y)                    # Straight line to B
    context.curve_to(x+w,y,x+w,y,x+w,y+r)  # Curve to C, Control points are both at Q
    context.line_to(x+w,y+h-r)                  # Move to D
    context.curve_to(x+w,y+h,x+w,y+h,x+w-r,y+h) # Curve to E
    context.line_to(x+r,y+h)                    # Line to F
    context.curve_to(x,y+h,x,y+h,x,y+h-r)       # Curve to G
    context.line_to(x,y+r)                      # Line to H
    context.curve_to(x,y,x,y,x+r,y)             # Curve to A


    
    

    


# FIXME: complete this - it's manipulater Cairo Window
class CairoManipulateObject(object):
    def __init__(self, cr, x,y, w, h):
        """
        Receive a cairo window that can be manipulated by some implemented 
        functions in this module 
        @param cr: CairoContext
        """
        self.cr = cr 
        self.x = x 
        self.y = y
        self.height = h 
        self.width = w
    
    def cr_rectangule_curve( cr, x, y, w, h, radius=10):
        """
        Draw rectangule with curve corner
        @param cr: CairoContext
        @param x: x coord
        @param y: y coord
        @param w: width of rectangle
        @param h: height of rectangle
        @param radius: defautl -> 10
        """
        # Copy from function 
        pass 
    