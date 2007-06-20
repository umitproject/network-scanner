# Copyright (C) 2005 Insecure.Com LLC.
#
# Authors: Adriano Monteiro Marques <py.adriano@gmail.com>
#          Cleber Rodrigues <cleber.gnu@gmail.com>
#                           <cleber@globalred.com.br>
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
import os.path
import sys
import optparse

import gtk
import gobject

from umitGUI.Splash import Splash
from umitGUI.MainWindow import MainWindow

from umitCore.Paths import Path
from umitCore.UmitConf import is_maemo
from umitCore.I18N import _
from umitCore.Logging import log


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
        self.__create_option_parser()

    def __create_option_parser(self):
        self.option_parser = optparse.OptionParser()
        self.options, self.args = self.option_parser.parse_args()

    def __parse_cmd_line(self):
        pass

    def __create_show_main_window(self):
        self.main_window = MainWindow()
        
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
        try:
            import psyco
            psyco.profile()
            self.using_psyco = True
        except:
            log.warning(_("RUNNING WITHOUT PSYCO!"))
            log.warning(_("""Psyco is a module that speeds up the execution of this \
application. It is not a requirement, and Umit runs perfectly well with or without it, \
but you're encourajed to install it to have a better speed experience. Download it \
at http://psyco.sf.net/"""))
            self.using_psyco = False

        if not is_maemo():
            pixmap_d = Path.pixmaps_dir
            if pixmap_d:
                pixmap_file = os.path.join(pixmap_d, 'splash.png')
                self.splash = Splash(pixmap_file, 1400)

        if main_is_frozen():
            # This is needed by py2exe
            gtk.threads_init()
            gtk.threads_enter()

        # Create and show the main window as soon as possible
        gobject.idle_add(self.__create_show_main_window)

        # Run main loop
        #gobject.threads_init()
        gtk.main()

        if main_is_frozen():
            gtk.threads_leave()
