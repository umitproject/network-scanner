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

from umitCore.I18N import _
from umitCore.ServiceList import ServiceList

service_list = ServiceList()

class ServiceCombo(gtk.ComboBoxEntry, object):
    def __init__(self):
        gtk.ComboBoxEntry.__init__(self, gtk.ListStore(str), 0)
        
        self.completion = gtk.EntryCompletion()
        self.child.set_completion(self.completion)
        self.completion.set_model(self.get_model())
        self.completion.set_text_column(0)

        self.update()

    def update(self):
        services = service_list.get_services_list()
        model = self.get_model()
        
        for i in range(len(model)):
                iter = model.get_iter_root()
                del(model[iter])
        
        for s in services:
            model.append([s])

    def get_selected_service(self):
        return self.child.get_text()

    def set_selected_service(self, service):
        self.child.set_text(service)

    selected_service = property(get_selected_service, set_selected_service)

if __name__ == "__main__":
    w = gtk.Window()
    s = ServiceCombo()
    s.update()
    w.add(s)
    w.show_all()

    gtk.main()
