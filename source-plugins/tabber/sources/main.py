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

# yeah we can do it :)
import tabber.paned as paned
import tabber.views as views

from umitPlugin.Core import Core
from umitPlugin.Engine import Plugin

class TabberPlugin(Plugin):
    def start(self, reader):
        self.reader = reader

        self._paned = paned.UmitPaned()

        main = Core().mainwindow
        main.vbox.remove(main.scan_notebook)
        main.vbox.pack_start(self._paned)

        self._paned.add_view(paned.PANE_CENTER, main.scan_notebook)
        self._paned.show_all()

    def stop(self):
        main = Core().mainwindow
        self._paned.hide()
        self._paned.remove_child()
        main.vbox.remove(self._paned)
        main.vbox.pack_start(main.scan_notebook)

    def get_paned(self):
        return self._paned

    # Public APIs
    paned = property(get_paned)

__plugins__ = [TabberPlugin]
