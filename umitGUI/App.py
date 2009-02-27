#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Authors: Adriano Monteiro Marques <adriano@umitproject.org>
#          Cleber Rodrigues <cleber.gnu@gmail.com>
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

import os
import os.path
import sys

from umitCore.Paths import Path
from umitCore.UmitOptionParser import option_parser
from umitCore.Utils import is_maemo
from umitCore.I18N import _
from umitCore.UmitLogging import log

from umitPlugin.Engine import PluginEngine

# Script found at http://www.py2exe.org/index.cgi/HowToDetermineIfRunningFromExe
import imp
frozen = (hasattr(sys, "frozen") or # new py2exe
          hasattr(sys, "importers") # old py2exe
          or imp.is_frozen("__main__")) # tools/freeze
del(imp)

def main_is_frozen():
    return frozen


class App:
    def __init__(self, args=sys.argv):
        # Initialite the PluginEngine
        PluginEngine()

    def __parse_cmd_line(self):
        pass

    def __create_show_main_window(self):
        try:
            if option_parser.get_inventory():
                from umitInventory.Viewer import InventoryViewer
                self.main_window = InventoryViewer()
            else:
                from umitGUI.MainWindow import MainWindow
                self.main_window = MainWindow()
        except Exception:
            # If any exception happens at this point we need to stop gtk
            # so Umit doesn't hang.
            import gtk
            gtk.main_quit()
            raise

        if is_maemo():
            import hildon
            self.hildon_app = hildon.Program()
            self.hildon_app.add_window(self.main_window)

        self.main_window.show_all()
    
    def safe_shutdown(self, signum, stack):
        log.debug("\n\n%s\nSAFE SHUTDOWN!\n%s\n" % ("#" * 30, "#" * 30))
        log.debug("SIGNUM: %s" % signum)

        try:
            scans = self.main_window.scan_notebook.get_children()
            for scan in scans:
                log.debug(">>> Killing Scan: %s" % scan.get_tab_label())
                scan.kill_scan()
                scan.close_tab()
                self.main_window.scan_notebook.remove(scan)
                del(scan)
        except NameError:
            pass

        self.main_window._exit_cb()
        sys.exit(signum)

    def run(self):
        # Try to load psyco module, saving this information
        # if we care to use it later (such as in a About Dialog)
        if not os.environ.get('UMIT_DEVELOPMENT', False):
            try:
                import psyco
            except ImportError:
                log.warning(_("RUNNING WITHOUT PSYCO!"))
                log.warning(_("psyco is a module that speeds up the execution "
                    "of Python applications. It is not a requirement, and "
                    "Umit will work normally without it, but you're "
                    "encouraged to install it to have a better speed "
                    "experience. Download psyco at http://psyco.sf.net/"""))
                self.using_psyco = False
            else:
                psyco.profile()
                self.using_psyco = True

        self.diff = option_parser.get_diff()
        if self.diff:
            self.__run_text()
        else:
            self.__run_gui()

    def __run_text(self):
        log.info(">>> Text Mode")

    def __run_gui(self):
        log.info(">>> GUI Mode")
        import warnings
        warnings.filterwarnings("error", module = "gtk")
        try:
            import gtk
        except Warning, e:
            print e.message
            sys.exit(-1)
        warnings.resetwarnings()
        import gobject
        from umitGUI.Splash import Splash
        log.info(">>> Pixmaps path: %s" % Path.pixmaps_dir)
        if not is_maemo():
            pixmap_d = Path.pixmaps_dir
            if pixmap_d:
                pixmap_file = os.path.join(pixmap_d, 'splash.png')
                self.splash = Splash(pixmap_file, 1400)

        if main_is_frozen():
            # This is needed by py2exe
            gtk.gdk.threads_init()
            gtk.gdk.threads_enter()

        # Create and show the main window as soon as possible
        gobject.idle_add(self.__create_show_main_window)

        # Run main loop
        #gobject.threads_init()
        gtk.main()

        if main_is_frozen():
            gtk.gdk.threads_leave()
