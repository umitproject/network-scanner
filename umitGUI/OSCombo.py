#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
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

from umitCore.I18N import _
from umitCore.OSList import OSList

os_list = OSList()

class OSClassCombo(gtk.ComboBoxEntry, object):
    def __init__(self):
        gtk.ComboBoxEntry.__init__(self, gtk.ListStore(str), 0)
        
        self.completion = gtk.EntryCompletion()
        self.child.set_completion(self.completion)
        self.completion.set_model(self.get_model())
        self.completion.set_text_column(0)

        self.update()

    def update(self):
        osclass = os_list.get_class_list()
        model = self.get_model()
        
        for i in range(len(model)):
                iter = model.get_iter_root()
                del(model[iter])
        
        for oc in osclass:
            model.append([oc])

    def get_selected_osclass(self):
        return self.child.get_text()

    def set_selected_osclass(self, osclass):
        self.child.set_text(osclass)

    selected_osclass = property(get_selected_osclass, set_selected_osclass)

class OSMatchCombo(gtk.ComboBoxEntry, object):
    def __init__(self):
        gtk.ComboBoxEntry.__init__(self, gtk.ListStore(str), 0)
        
        self.completion = gtk.EntryCompletion()
        self.child.set_completion(self.completion)
        self.completion.set_model(self.get_model())
        self.completion.set_text_column(0)

    def update(self, osclass):
        osmatch = os_list.get_match_list(osclass)
        if osmatch:
            model = self.get_model()
        
            for i in range(len(model)):
                iter = model.get_iter_root()
                del(model[iter])

            for om in osmatch:
                model.append([om])

    def get_selected_osmatch(self):
        return self.child.get_text()

    def set_selected_osmatch(self, osmatch):
        self.child.set_text(osmatch)

    selected_osmatch = property(get_selected_osmatch, set_selected_osmatch)


if __name__ == "__main__":
    w = gtk.Window()
    s = OSClassCombo()
    s.update()
    w.add(s)
    w.show_all()

    gtk.main()
