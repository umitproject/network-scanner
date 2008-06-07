#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
#         Cleber Rodrigues <cleber.gnu@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import gtk
from HIGWidgets import *

def test_entries():
    
    w = HIGWindow()
    w.connect("delete-event", gtk.main_quit)
    
    # vb is the top-most vertical box
    vb = HIGVBox()
    w.add(vb)
    
    # vb
    #  - packed in: w
    #  - packs: * "Section" label
    #               * hb
    vb._pack_noexpand_nofill(HIGSectionLabel("Section"))
    
    # hb
    #  - packed in: vb
    #  - packs: * et
    hb = HIGHBox()
    hb._pack_noexpand_nofill(HIG_box_space_holder())
    
    # let is the Label/Entry Table
    let = HIGTable(2, 2)
    let.attach_label(HIGEntryLabel("Entry 1:"), 0, 1, 0, 1)
    let.attach_entry(gtk.Entry(), 1, 2, 0, 1)
    let.attach_label(HIGEntryLabel("Entry 2:"), 0, 1, 1, 2)
    let.attach_entry(gtk.Entry(), 1, 2, 1, 2)
    hb._pack_expand_fill(let)
	
    vb.pack_line(hb)
    w.show_all()
	
    gtk.main()

if __name__ == '__main__':
    test_entries()
