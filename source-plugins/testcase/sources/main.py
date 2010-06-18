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

import gtk
import sys

from test.autogen import TestAutoGen

from umit.plugin.Core import Core
from umit.plugin.Engine import Plugin
from higwidgets.higdialogs import HIGAlertDialog

class Test(Plugin):
    def start(self, reader):
        testcase = TestAutoGen()
        passed, msg = testcase.run(reader)

        if passed:
            type = gtk.MESSAGE_INFO
        else:
            type = gtk.MESSAGE_ERROR

        if passed:
            title = "Test passed"
        else:
            title = "Test not passed"

        dialog = HIGAlertDialog(
            Core().mainwindow,
            gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_MODAL,
            type, message_format=title,
            secondary_text=msg
        )
        dialog.run()
        dialog.destroy()

    def stop(self):
        return

__plugins__ = [Test]
