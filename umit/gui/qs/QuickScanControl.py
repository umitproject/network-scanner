# Copyright (C) 2010 Adriano Monteiro Marques
#
# Authors: Diogo Pinheiro <diogormpinheiro@gmail.com>
# Original author: Guilherme Polo <ggpolo@gmail.com>
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
# USA

"""
GUI for controlling QuickScan starting.
"""

import os
import sys
import gtk
import gobject

from umit.core.I18N import _
from umit.core.Paths import Path
from umit.core.Utils import amiroot, open_url_as
from umit.core.qs.QuickScan import QuickScanControl

from umit.gui.GenericAlertDialogs import GenericAlert
from umit.gui.Help import show_help

if os.name == 'nt':
    run_path = Path.get_running_path()
    if run_path not in sys.path:
        sys.path.append(run_path)

    qs_launcher = __import__("quickscan_launcher")
    class QuickScanControl(object):
        def __getattr__(self, name):
            return lambda *args, **kwargs: qs_launcher.main([name], False)


class QSControl(object):
    """
    GUI for controlling QuickScan launching.
    """

    def __init__(self, daddy):
        self.qscontrol = QuickScanControl()


    def start_quickscan(self):
        """
        Do necessary checks before starting Scheduler.
        """
        err = self.qscontrol.start(from_gui=True)

        if err:
            alertdlg = GenericAlert(_("QuickScan Launcher"),
                    _("QuickScan couldn't be started, reason:\n\n") +
                    str(err),
                  buttons={1: (gtk.RESPONSE_OK, gtk.STOCK_OK)})
            resp = alertdlg.run()
            alertdlg.destroy()


    def _quickscan_control(self, event):
        """
        Verify if QuickScan is not already started.
        """
        running = self.qscontrol.running()
        if not running:
            self.start_quickscan()
