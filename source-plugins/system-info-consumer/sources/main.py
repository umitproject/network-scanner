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

from umitPlugin.Core import Core
from umitPlugin.Engine import Plugin
from higwidgets.higdialogs import HIGAlertDialog

# This is the consumer Plugin
class SystemInfo(Plugin):
    def start(self, reader):
        self.reader = reader

        self.sysinfo = Core().get_need(self.reader, 'SystemInfo')

        if not self.sysinfo:
            msg = "Cannot use SystemInfo"
        else:
            msg = "Info for %s\n\nRoutes:\n%s\nIfaces:\n%s\n" % (
                self.sysinfo.get_name(),
                self.sysinfo.get_routes(),
                self.sysinfo.get_ifaces()
            )

        dialog = HIGAlertDialog(
            None,
            gtk.DIALOG_MODAL,
            gtk.MESSAGE_INFO,
            message_format="SystemInfo-Consumer",
            secondary_text=msg
        )
        dialog.run()
        dialog.destroy()


    def stop(self):
        pass

__plugins__ = [SystemInfo]
