# -*- coding: utf-8 -*-

# Copyright (C) 2009 Adriano Monteiro Marques.
#
# Author: Daniel Mendes Cassiano <dcassiano@umitproject.org>
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

import os
import sys
import gtk

from subprocess import Popen, PIPE

from higwidgets.higwindows import HIGMainWindow
from higwidgets.higboxes import HIGVBox

from umit.core.Paths import Path
from umit.core.Utils import amiroot

from umit.gui.qs.EntryField import EntryField
#from umit.core.qs import Nmap
from umit.libkeybinder import libkeybinder

root = amiroot()

def unhide_callback(data=None):
    """
    Handler called when key pressed to unhide quickscan
    """
    data.deiconify()
    data.show_all()
    data.focus()

class MainWindow(HIGMainWindow):
    """
    
    """
    def __init__(self):
        HIGMainWindow.__init__(self)
        self.vbox = HIGVBox()
        self.main_hbox = gtk.HBox()
        self.set_default_size(500, 30)
        self.set_border_width(0)
        self.connect('delete-event', gtk.main_quit)
       
        
class Main(MainWindow, EntryField):
    """
    Launch the Main Window and pack the Entry Field on it.
    """

#TODO: i18n!
#TODO: Fix the paths of modules issue

    def __init__(self):
        MainWindow.__init__(self)
        EntryField.__init__(self)
        self.set_title("Umit QuickScan")
        self.add(self.main_hbox)
        self.set_position(gtk.WIN_POS_CENTER)
        
        status_icon = gtk.StatusIcon()
        menu = gtk.Menu()
        menu_item = gtk.MenuItem("Umit Network Scanner")
        menu_item.connect('activate', self.launch_umit, status_icon)
        menu.append(menu_item)
        
        menu_separator = gtk.SeparatorMenuItem()
        menu.append(menu_separator)
        
        menu_item2 = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        menu_item2.connect('activate', self.quit_by_icon, status_icon)
        menu.append(menu_item2)
        
        status_icon.set_from_file(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "qs", "umit-menu.xpm"))
        status_icon.set_tooltip("Umit Quick Scan")
        status_icon.connect('popup-menu', self.icon_menu, menu)
        status_icon.connect('activate', self.minimize_to_tray)
        status_icon.set_visible(True)

        
        self.main_hbox.pack_start(self.vbox, True, True, 6)
        self.vbox.pack_start(self.entry, False, True, 6)
        #self.show_all()
		
        libkeybinder.bind(libkeybinder.Modifiers['alt'], 'q', unhide_callback, self)
        
    def minimize_to_tray(self, widget):
        if not self.get_property("visible"):
            self.show_all()
        else:
            self.hide()
        
    def launch_umit(self, widget, data=None):
        """
        Launch the Network Scanner.
        """
        if data:
            self.command_process = Popen("umit", bufsize=1, stdin=PIPE,
                                         stdout=PIPE, stderr=PIPE)
        
    def quit_by_icon(self, widget, data=None):
        """
        Quit of QS by the menu.
        """
        if data:
            data.set_visible(False)
        self._exit_cb()
        
    def icon_menu(self, widget, button, time, data=None):
        """
        The icon menu of the try icon.
        """
        if button == 3:
            if data:
                data.show_all()
                data.popup(None, None, None, 3, time)
                
    def _exit_cb(self, widget=None, extra=None):
        libkeybinder.unbind_all()
        gtk.main_quit()

    def is_root(self):
        """
        Check if is root.
        """
        if not root:
            print "[Warning] You are not root!"


if __name__ == "__main__":
    Path.set_umit_conf(os.path.dirname(sys.argv[0]))
    Path.set_running_path(os.path.abspath(os.path.dirname(sys.argv[0])))
    a = Main()
    gtk.main()

