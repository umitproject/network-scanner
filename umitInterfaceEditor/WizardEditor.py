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



'''
This is based on Profile.py - Profile Editor Mode
With Wizard My idea it's create a Notebook Editable too, but with First, Second
and others pages. 

It's a connection among profile_editor.xml and wizard.xml. So I'm intend
use the ProfileEdit already done ( not completely but some functions done )
to do a simple Wizard Edit Mode - It's a spread widely to Edit wizard.xml 

So each pages created will have titled as a number. The first one it's the
first page on Wizard and so one, and so one. 


'''

from umitInterfaceEditor.Profile import * 
from umitInterfaceEditor.PageNotebook import * 

from umitCore.Paths import Path

options = Path.options
wizard = Path.wizard

class WizardEdit(ProfileEdit):
    def __init__(self, optionlist):
        ProfileEdit.__init__(self, optionlist, wizard)
        #self.notebook.set_tab_pos(gtk.POS_LEFT)
        
        
    
    
    