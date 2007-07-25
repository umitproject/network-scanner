#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2005 Insecure.Com LLC.
#
# Author: Adriano Monteiro Marques <py.adriano@gmail.com>
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

from umitCore.Paths import Path

target_list = Path.target_list

class TargetCombo(gtk.ComboBoxEntry):
    def __init__(self):
        gtk.ComboBoxEntry.__init__(self, gtk.ListStore(str), 0)

        self.completion = gtk.EntryCompletion()
        self.child.set_completion(self.completion)
        self.completion.set_model(self.get_model())
        self.completion.set_text_column(0)

        self.update()

    def update(self):
        t_list = ''
        try:
            t_list_file = open(target_list)
            t_list = t_list_file.readlines()

            t_list_file.close()
        except:
            return None
        else:
            t_model = self.get_model()
            for i in range(len(t_model)):
                iter = t_model.get_iter_root()
                del(t_model[iter])
            
            for i in t_list[:15]:
                t_model.append([i.replace('\n','')])
    
    def add_new_target(self, target):
        t_list = ''
        try:
            t_list_file = open(target_list)
            t_list = t_list_file.readlines()

            t_list_file.close()
        except:
            return None
        else:
            target += '\n'
            if target not in t_list:
                t_list.insert(0,target)

                t_list_file = open(target_list,'w')
                t_list_file.writelines(t_list)
                
                t_list_file.close()
                
                self.update()

    def get_selected_target(self):
        return self.child.get_text()

    def set_selected_target(self, target):
        self.child.set_text(target)

    selected_target = property(get_selected_target, set_selected_target)
    
if __name__ == "__main__":
    w = gtk.Window()
    t = TargetCombo()
    w.add(t)
    w.show_all()

    gtk.main()
