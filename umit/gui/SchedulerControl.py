# Copyright (C) 2007 Adriano Monteiro Marques
#
# Authors: Guilherme Polo <ggpolo@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

"""
GUI for controlling Scheduler starting/stopping.
"""

import os
import sys
import gtk
import gobject

from umit.core.I18N import _
from umit.core.Paths import Path
from umit.core.Utils import amiroot, open_url_as
from umit.core.Scheduler import SchedulerControl

from umit.gui.GenericAlertDialogs import GenericAlert
from umit.gui.Help import show_help

if os.name == 'nt':
    run_path = Path.get_running_path()
    if run_path not in sys.path:
        sys.path.append(run_path)

    umit_scheduler = __import__("umit_scheduler")
    class SchedulerControl(object):
        def __getattr__(self, name):
            return lambda *args, **kwargs: umit_scheduler.main([name], False)

START_TEXT = _("Start Scheduler")
STOP_TEXT = _("Stop Scheduler")

class SchedControl(object):
    """
    GUI for controlling Scheduler starting/stopping.
    """

    def __init__(self, daddy):
        self.ui_action = None
        self.daddy = daddy
        self.schedcontrol = SchedulerControl()

        self.stock_icon, self.status_text = self._sched_status()

        gobject.timeout_add(1000, self._update_sched_status)


    def start_scheduler(self):
        """
        Do necessary checks before starting Scheduler.
        """
        err = None
        if not amiroot(): # running as normal user
            alertdlg = GenericAlert(_("Scheduler Controller"),
                  _("You are requesting to start Scheduler as a normal \
user.\n\nIn case some scheduled scan contains any \noptions that requires \
root previlegies they will end \nup not running.\n\nIf you don't want to \
start the Scheduler now, \nselect Cancel, if you want to run it as a normal \
user \nanyway, select OK, otherwise, select Help to learn \nhow you can \
start it as root."), buttons={1: (gtk.RESPONSE_HELP, gtk.STOCK_HELP),
                              2: (gtk.RESPONSE_CANCEL, gtk.STOCK_CANCEL),
                              3: (gtk.RESPONSE_OK, gtk.STOCK_OK)})

            resp = alertdlg.run()

            if resp == gtk.RESPONSE_OK:
                err = self.schedcontrol.start(from_gui=True)
            elif resp == gtk.RESPONSE_HELP:
                show_help(self,"scheduler.html#starting-scheduler-as-root")

            alertdlg.destroy()
        else: # running as root
            err = self.schedcontrol.start(from_gui=True)

        if err:
            alertdlg = GenericAlert(_("Scheduler Controller"),
                    _("The Scheduler couldn't be started, reason:\n\n") +
                    str(err),
                  buttons={1: (gtk.RESPONSE_HELP, gtk.STOCK_HELP),
                           2: (gtk.RESPONSE_OK, gtk.STOCK_OK)})
            resp = alertdlg.run()
            if resp == gtk.RESPONSE_HELP:
                show_help(self,"scheduler.html#starting-scheduler")
            alertdlg.destroy()


    def stop_scheduler(self):
        """
        Stop scheduler if possible.
        """
        err = self.schedcontrol.stop()

        if err: # user not allowed to stop scheduler
            alertdlg = GenericAlert(_("Scheduler Controller"),
                    _("The Scheduler couldn't be stopped, reason:\n\n") +
                    str(err),
                  buttons={1: (gtk.RESPONSE_HELP, gtk.STOCK_HELP),
                           2: (gtk.RESPONSE_OK, gtk.STOCK_OK)})

            resp = alertdlg.run()

            if resp == gtk.RESPONSE_HELP:
                show_help(self,"scheduler.html#stopping-scheduler")

            alertdlg.destroy()


    def _sched_status(self):
        """
        Return stock icon and text based on scheduler status.
        """
        running = self.schedcontrol.running()
        if running:
            status = (gtk.STOCK_YES, STOP_TEXT)
        else:
            status = (gtk.STOCK_NO, START_TEXT)

        return status


    def _scheduler_control(self, event):
        """
        Stop/Start scheduler.
        """
        if self._sched_status()[0] == gtk.STOCK_NO:
            self.start_scheduler()

            if self.daddy:
                self.daddy._clear_tip_statusbar()

        else:
            self.stop_scheduler()


    def _update_sched_status(self):
        """
        Update ui_action for current Scheduler Status.
        """
        prev_icon = self.stock_icon

        new_icon, new_text = self._sched_status()

        self.stock_icon = new_icon
        self.status_text = new_text

        if self.ui_action:
            self.ui_action.set_property('stock-id', self.stock_icon)
            self.ui_action.set_property('tooltip', self.status_text)
            self.ui_action.set_property('label', self.status_text)

        if self.daddy and self.stock_icon:
            if prev_icon == gtk.STOCK_NO and new_icon == gtk.STOCK_YES:
                # scheduler is running now
                self.daddy._clear_tip_statusbar()

            if new_icon == gtk.STOCK_NO:
                self.daddy._write_statusbar_tip(_("Scheduler is not running!"),
                                                False)

        if not self.stock_icon: # widget deleted
            return False

        return True
