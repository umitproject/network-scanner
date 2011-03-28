#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2008 Adriano Monteiro Marques
#
# Author: Francesco Piccinno <stack.box@gmail.com>
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
import gtk

from higwidgets.higdialogs import HIGAlertDialog

from umit.core.UmitLogging import log

from umit.plugin.Core import Core
from umit.plugin.Engine import Plugin

class Notifier(Plugin):
    def start(self, reader):
        self.reader = reader
        self.tray = Core().get_need(self.reader, 'tray')

        if not self.tray:
            d = HIGAlertDialog(
                Core().mainwindow,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                message_format='Error - Notifier',
                secondary_text='Unable to get the instance of tray module. The plugin cannot operate correctly.')
            d.run()
            d.destroy()
        else:
            self.__connect_signals()

    def stop(self):
        pass

    def __connect_signals(self):
        # Here we're going to connect various signals.
        Core().connect('NmapScanNotebookPage-created',
            lambda core, page, obj: \
                page.connect('scan-finished', obj.__on_scan_finished),
            self
        )
   
    # Signals handlers
    def __on_scan_finished(self, page):
        if not self.tray:
            log.debug('Cannot procede: self.tray == None')
            return

        title = page.get_tab_label()
        if page.status.get_scan_failed():
            msg = 'The scan failed. (%s)' % page.command_execution.get_error()
            icon = gtk.STOCK_DIALOG_ERROR
        else:
            msg = 'Scan finished.'
            icon = gtk.STOCK_DIALOG_INFO

        log.debug('Showing notification (%s, %s)' % (title, msg))
        self.tray.show_notification(msg, title, stock=icon, timeout=2000)

__plugins__ = [Notifier]
