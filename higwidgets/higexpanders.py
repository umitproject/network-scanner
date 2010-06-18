#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
#         Cleber Rodrigues <cleber.gnu@gmail.com>
#         João Paulo de Souza Medeiros <ignotus21@gmail.com>
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

"""
higwidgets/higexpanders.py

   expanders related classes
"""

__all__ = ['HIGExpander', 'HIGExpanderRNet']

import gtk

from higwidgets.higboxes import HIGHBox, hig_box_space_holder
from higwidgets.higlabels import HIGSectionLabel

class HIGExpander(gtk.Expander):
    def __init__(self, label):
        gtk.Expander.__init__(self)
		
        self.set_use_markup(True)
        self.set_label(label)
		
        self.hbox = HIGHBox()
        self.hbox.set_border_width(5)
        self.hbox._pack_noexpand_nofill(hig_box_space_holder())
		
        self.add(self.hbox)
	
    def get_container(self):
        return self.hbox

#class needed to maintain compatibility of RadialNet with higwidgets
class HIGExpanderRNet(gtk.Expander):
    def __init__(self, label=''):
        gtk.Expander.__init__(self)

        self.__label = HIGSectionLabel(label)
        self.set_label_widget(self.__label)

        self.__alignment = gtk.Alignment(0, 0, 1, 1)
        self.__alignment.set_padding(12, 0, 24, 0)

        self.add(self.__alignment)


    def _set_label_text(self, text):
        self.__label._set_text(text)


    def _add(self, widget):
        if len(self.__alignment.get_children()) > 0:
            self.__alignment.remove(self.__alignment.get_children()[0])

        self.__alignment.add(widget)


    def _no_padding(self):
        self.__alignment.set_padding(0, 0, 0, 0)
