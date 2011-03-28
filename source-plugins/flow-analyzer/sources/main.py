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
from umit.gui.ScanNotebook import NmapScanNotebookPage

class FlowContainer(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        
        paned = gtk.VPaned()
        
        self.text1 = gtk.TextView()
        self.text2 = gtk.TextView()
        
        def scroll(widget):
            sw = gtk.ScrolledWindow()
            sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
            sw.add(widget)
            return sw
    
        paned.pack1(scroll(self.text1))
        paned.pack2(scroll(self.text2))

        message = "Not yet available. Try to start a scan!"

        self.text1.get_buffer().set_text(message)
        self.text2.get_buffer().set_text(message)
        
        self.pack_start(paned)
        self.show_all()
        
    def update(self, page):
        # Simple set the xml and normal output to textviews

        if hasattr(page, 'command_execution') and page.command_execution:
            f = open(page.command_execution.get_xml_output_file(), "r")
            txt = "".join(f.readlines())
            
            self.text1.get_buffer().set_text(txt)
            
            f = open(page.command_execution.get_output_file(), "r")
            txt = "".join(f.readlines())
            
            self.text2.get_buffer().set_text(txt)

class FlowPlugin(Plugin):
    def start(self, reader):
        self.id = Core().connect('NmapScanNotebookPage-created', self.__on_created)

        for page in Core().get_main_scan_notebook():
            if isinstance(page, NmapScanNotebookPage):
                self.__on_created(Core(), page)
                page.emit('scan-finished')

    def stop(self):
        Core().disconnect(self.id)

        for page in Core().get_main_scan_notebook():
            if not isinstance(page, NmapScanNotebookPage):
                continue

            for child in page.scan_result.scan_result_notebook:
                if not isinstance(child, FlowContainer):
                    continue

                idx = page.scan_result.scan_result_notebook.page_num(child)
                page.scan_result.scan_result_notebook.remove_page(idx)

                child.hide()
                child.destroy()

    def __on_created(self, core, page):
        container = FlowContainer()
        
        page.connect('scan-finished', container.update)
        page.scan_result.scan_result_notebook.append_page(container, gtk.Label("Flow Analyzer"))


__plugins__ = [FlowPlugin]
