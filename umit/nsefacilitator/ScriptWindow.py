# Copyright (C) 2007 Adriano Monteiro Marques <py.adriano@gmail.com>
#
# Author: Maxim Gavrilov <lovelymax@gmail.com>
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
from higwidgets.higwindows import HIGMainWindow

class ScriptWindow(HIGMainWindow):
    """HIGMainWindow with Menu, ToolBar and StatusBar.

       One can define actions, toggle_actions and ui for handling interface
       and create_main() method for create center view and than call create_layout().

    """

    def create_ui_manager(self, actions, toggle_actions, ui):
        if not actions and not toggle_actions:
            return
        self.accel_group = gtk.AccelGroup()
        self.add_accel_group(self.accel_group)

        self.action_group = gtk.ActionGroup(str(self.__class__)) #'ScriptManagerActionGroup')
        if actions:
            self.action_group.add_actions(actions)
        if toggle_actions:
            self.action_group.add_toggle_actions(toggle_actions)

        for action in self.action_group.list_actions():
            action.set_accel_group(self.accel_group)
            action.connect_accelerator()
        if ui:
            self.ui_manager = gtk.UIManager()
            self.ui_manager.insert_action_group(self.action_group, 0)
            self.ui_manager.add_ui_from_string(ui)

    def create_menu(self):
        menu_bar = self.ui_manager.get_widget('/menubar')
        return menu_bar

    def create_toolbar(self):
        self.toolbar = self.ui_manager.get_widget('/toolbar')
        return self.toolbar

    def create_statusbar(self):
        self.statusbar = gtk.Statusbar()
        self.statusbar.set_has_resize_grip(True)
        self.statusbar2 = gtk.Statusbar()
        self.statusbar2.set_has_resize_grip(False)
        self.statusbar.pack_end(self.statusbar2)
        return self.statusbar
    
    def create_layout(self, actions, toggle_actions, ui):
        vbox = gtk.VBox()
        self.create_ui_manager(actions, toggle_actions, ui)
        vbox.pack_start(self.create_menu(), False, False)
        vbox.pack_start(self.create_toolbar(), False, False)
        vbox.pack_end(self.create_statusbar(), False, False)

        vbox.pack_start(self.create_main(), True, True)
        self.add(vbox)

