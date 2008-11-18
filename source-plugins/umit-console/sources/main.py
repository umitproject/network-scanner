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

import console.console as console

# yes we can do it
from tabber import paned
from tabber.views import UmitView

from umitCore.I18N import _
from umitPlugin.Core import Core
from umitPlugin.Engine import Plugin
from umitPlugin.Atoms import Singleton
from higwidgets.higbuttons import HIGButton
from higwidgets.higtooltips import HIGTooltip, HIGTooltipData

help_strings = [
    _("This is the help system of umitConsole.\n"
    "Now i'll show you some umit funcionality\n\n\n" +
    "<i>Press <b>Close</b> or <b>Next</b> to continue</i>\n"),

    _("Ok, let's introduce myself. The window above is a Python prompt.\n"
      "Type a line of Python code, hit <i>Enter</i> and watch it run!\n\n"
      "For example try typing some math. Like <tt>2 + 6</tt>\n"),

    _("It could handle everything that Python supports. But it is also\n"
      "used to interact with <b>UMIT</b> codebase and his <i>UI</i>.\n"
      "For example try typing:\n\n"
      "<tt>from umitPlugin.Core import Core</tt>\n"
      "<tt>Core().get_main_toolbar().hide()</tt>\n")
]


class MiniButton(gtk.Button):
    def __init__(self, stock):
        gtk.Button.__init__(self)

        img = gtk.image_new_from_stock(stock, gtk.ICON_SIZE_MENU)
        img.show()

        self.add(img)
        self.set_relief(gtk.RELIEF_NONE)
        self.connect('size-allocate', self.__size_allocate)

    def __size_allocate(self, widget, alloc):
        alloc.width = alloc.height
        return gtk.Button.do_size_allocate(self, alloc)

class Help(object):
    def __init__(self, console):
        self.index = 0
        self.array = help_strings
        self.console = console
        self.tip = None

    def next(self):
        if self.index < len(self.array) - 1:
            self.index += 1

    def previous(self):
        if self.index > 0:
            self.index -= 1

    def current(self):
        string = self.array[self.index]
        data = HIGTooltipData(string)

        hbb = gtk.HBox(2, False)

        btn = MiniButton(stock=gtk.STOCK_CLOSE)
        btn.connect('clicked', self.__on_close)
        hbb.pack_start(btn, False, False, 0)
        
        btn = MiniButton(stock=gtk.STOCK_GO_BACK)
        btn.connect('clicked', self.__on_back)

        if self.index == 0:
            btn.set_sensitive(False)

        hbb.pack_start(btn, False, False, 0)

        btn = MiniButton(stock=gtk.STOCK_GO_FORWARD)
        btn.connect('clicked', self.__on_forward)

        if self.index == len(self.array) - 1:
            btn.set_sensitive(False)

        hbb.pack_start(btn, False, False, 0)

        hbb.show_all()
        
        align = gtk.Alignment(1.0, 0.5)
        align.add(hbb)

        align.show_all()

        data.append_widget(align)

        return data

    def __on_back(self, widget):
        self.previous()
        self.__on_close(widget)
        self.show_help()

    def __on_forward(self, widget):
        self.next()
        self.__on_close(widget)
        self.show_help()

    def __on_close(self, widget):
        if self.tip:
            self.tip.close_and_destroy()

    def show_help(self):
        self.__on_close(None)
        self.tip = HIGTooltip()
        x, y = self.console.window.get_origin()
        self.tip.show_at(self.console, self.current(), x, y)

class ConsoleView(UmitView):
    label_text = "Umit Shell"

    def create_ui(self):
        self.console = console.Console(globals())
        self.console.connect('eval', self.__on_help)
        self.console.banner()

        self.help = Help(self.console)

        self._main_widget.add(self.console)
        self._main_widget.show_all()

    def __on_help(self, console, cmd):
        cmd = cmd.replace("\n", "")

        if cmd == "help":
            self.help.show_help()
            return True
        
        return False

class ConsolePlugin(Plugin):
    def start(self, reader):
        self.reader = reader
        self.view = ConsoleView()

        tabber = Core().get_need(self.reader, 'Tabber')
        tabber.paned.add_view(paned.PANE_BOTTOM, self.view)

    def stop(self):
        tabber = Core().get_need(self.reader, 'Tabber')
        tabber.paned.remove_view(self.view)

__plugins__ = [ConsolePlugin]
