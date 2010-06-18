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
import gobject

from umit.plugin.Core import Core
from umit.plugin.Engine import Plugin

from higwidgets.hignotebooks import HIGAnimatedTabLabel
from higwidgets.higtooltips import *

try:
    import vte
except ImportError:
    raise Exception("To use this plugin you need python vte binding.")

class TerminalPage(gtk.Bin):
    def __init__(self):
        super(TerminalPage, self).__init__()
        
        self.term = vte.Terminal()
        self.term.fork_command()

        self.__termbox = gtk.HBox()
        self.__scroll = gtk.VScrollbar(self.term.get_adjustment())
        border = gtk.Frame()
        border.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        border.add(self.term)
        self.__termbox.pack_start(border)
        self.__termbox.pack_start(self.__scroll, False)
        self.add(self.__termbox)

    def do_size_request(self, req):
        (w,h) = self.__termbox.size_request()
        req.width = w
        req.height = h

    def do_size_allocate(self, alloc):
        self.allocation = alloc
        wid_req = self.__termbox.size_allocate(alloc)

gobject.type_register(TerminalPage)

class TerminalPlugin(Plugin):
    def start(self, reader):
        self.reader = reader

        # Create a ToolItem
        self.item = gtk.ToolButton(None, "Terminal")

        image = gtk.image_new_from_stock(gtk.STOCK_ABOUT, \
                                         gtk.ICON_SIZE_LARGE_TOOLBAR)
        image.show()
        self.item.set_icon_widget(image)

        # Append our item
        Core().get_main_toolbar().insert(self.item, -1)
        self.item.connect('clicked', self.__on_create_page)
        self.item.show_all()

    def stop(self):
        Core().get_main_toolbar().remove(self.item)

    def __on_create_page(self, widget):
        nb = Core().get_main_scan_notebook()

        widget = TerminalPage()
        widget.show_all()

        label = HIGAnimatedTabLabel("Terminal")
        label.connect('close-clicked', self.__on_close_page, widget)

        gtk.Notebook.append_page(nb, widget, label)

    def __on_close_page(self, widget, page):
        nb = Core().get_main_scan_notebook()
        idx = gtk.Notebook.page_num(nb, page)

        if idx > 0:
            page.hide()
            gtk.Notebook.remove_page(nb, idx)

__plugins__ = [TerminalPlugin]
