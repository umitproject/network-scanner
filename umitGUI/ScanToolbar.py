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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import gtk

from higwidgets.higboxes import HIGHBox
from higwidgets.higlabels import HIGEntryLabel

from umitCore.I18N import _

from umitGUI.ProfileCombo import ProfileCombo
from umitGUI.TargetCombo import TargetCombo


class ScanCommandToolbar(HIGHBox):
    def __init__(self):
        HIGHBox.__init__(self)

        self.command_label = HIGEntryLabel(_("Command:"))
        self.command_entry = gtk.Entry()
        
        self._pack_noexpand_nofill(self.command_label)
        self._pack_expand_fill(self.command_entry)
        
    def get_command(self):
        return self.command_entry.get_text()

    def set_command(self, command):
        self.command_entry.set_text(command)

    command = property(get_command, set_command)

class ScanToolbar(HIGHBox):
    def __init__(self):
        HIGHBox.__init__(self)

        self._create_target()
        self._create_profile()

        self.scan_button = gtk.Button(_("Scan"))

        self._pack_noexpand_nofill(self.target_label)
        self._pack_expand_fill(self.target_entry)
        
        self._pack_noexpand_nofill(self.profile_label)
        self._pack_expand_fill(self.profile_entry)
        
        self._pack_noexpand_nofill(self.scan_button)

        self.target_entry.set_focus_child(self.target_entry.child)
        self.profile_entry.set_focus_child(self.profile_entry.child)

        self.target_entry.child.grab_focus()

        # Events
        self.target_entry.child.connect('key-press-event',\
                        self.next, self.profile_entry.child)
        self.target_entry.child.connect('activate',
                        lambda x: self.profile_entry.child.grab_focus())
        self.profile_entry.child.connect('activate',
                        lambda x: self.scan_button.clicked())
        
    def _create_target(self):
        self.target_label = HIGEntryLabel(_("Target:"))
        self.target_entry = TargetCombo()
        
        self.update_target_list()

    def _create_profile(self):
        self.profile_label = HIGEntryLabel(_('Profile:'))
        self.profile_entry = ProfileCombo()
        
        self.update()

    def next(self, widget, event, next_widget):
        if event.hardware_keycode == 23:
            next_widget.grab_focus()

    def get_target(self):
        return self.target_entry.get_child().get_text()

    def get_profile_name(self):
        return self.profile_entry.get_child().get_text()

    def update_target_list(self):
        self.target_entry.update()
        
    def add_new_target(self, target):
        self.target_entry.add_new_target(target)

    def get_selected_target(self):
        return self.target_entry.selected_target

    def set_selected_target(self, target):
        self.target_entry.selected_target = target

    def update(self):
        self.profile_entry.update()
    
    def set_profiles(self, profiles):
        self.profile_entry.set_profiles(profiles)

    def get_selected_profile(self):
        return self.profile_entry.selected_profile

    def set_selected_profile(self, profile):
        self.profile_entry.selected_profile = profile

    selected_profile = property(get_selected_profile, set_selected_profile)
    selected_target = property(get_selected_target, set_selected_target)

if __name__ == "__main__":
    w = gtk.Window()
    box = gtk.VBox()
    w.add(box)

    stool = ScanToolbar()
    sctool = ScanCommandToolbar()

    box.pack_start(stool)
    box.pack_start(sctool)

    w.connect("delete-event", lambda x,y: gtk.main_quit())
    w.show_all()
    gtk.main()
