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

from umit.plugin.Core import Core
from umit.plugin.Engine import Plugin
from higwidgets.higanimates import HIGAnimatedBar
from umit.gui.ScanNotebook import NmapScanNotebookPage, ScanResult

class MyWidget(HIGAnimatedBar):
    pass

class MenuPlugin(Plugin):
    def start(self, reader):
        self.reader = reader

        self.id = Core().connect('ScanHostsView-created', self.__on_created_hosts)

        for page in Core().get_main_scan_notebook():
            if isinstance(page, NmapScanNotebookPage):
                self.__on_created_hosts( \
                    Core(), page.scan_result.scan_host_view)

    def stop(self):
        Core().disconnect(self.id)

        for page in Core().get_main_scan_notebook():
            if not isinstance(page, NmapScanNotebookPage):
                continue

            for child in page.scan_result.scan_host_view:
                if isinstance(child, MyWidget):
                    page.scan_result.scan_host_view.remove(child)
                    child.hide()
                    child.destroy()

    def __on_created_hosts(self, core, view):
        widget = MyWidget('<tt>I\'m here spying your hosts</tt>')
        widget.show()
        view.pack_start(widget, False, False)

        widget.start_animation(True)

        view.host_view.connect('button-press-event', self.__on_context_menu)

    def __on_context_menu(self, view, evt):
        model, iter = view.get_selection().get_selected_rows()

        if iter and evt.button == 3:
            lbl = "Got from plugin %s" % model.get_value(model.get_iter(iter[0]), 1)
            menu = gtk.Menu()
            menu.append(gtk.MenuItem(lbl))
            menu.show_all()

            menu.popup(None, None, None, evt.button, evt.time)

__plugins__ = [MenuPlugin]
