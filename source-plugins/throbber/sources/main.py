#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2008 Francesco Piccinno
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

import sys

from umit.plugin.Core import Core
from umit.plugin.Engine import Plugin

from umit.gui import ScanNotebook
from umit.core.UmitLogging import log

from higwidgets.higboxes import HIGHBox
from higwidgets.hignotebooks import HIGClosableTabLabel, HIGAnimatedLabel


global_animation = None
gtk.rc_parse_string("""
    style "thinWidget" {
        xthickness = 0
        ythickness = 0
    }
    widget "*.tabNotebookButton" style "thinWidget"
    """)

class MyHIGClosableTabLabel(HIGHBox):
    __gsignals__ = { 'close-clicked' : (gobject.SIGNAL_RUN_LAST,
                                        gobject.TYPE_NONE, ()) }

    def __init__(self, label_text=""):
        gobject.GObject.__init__(self)
        #HIGHBox.__init__(self, spacing=4)

        self.label_text = label_text

        self.set_spacing(4)
        self.set_border_width(0)

        self.__create_widgets()

        #self.propery_map = {"label_text" : self.label.get_label}

    def __create_widgets(self):
        self.label = HIGAnimatedLabel(self.label_text)

        self.label.label.set_alignment(0, 0.5)
        self.label.label.set_padding(0, 0)
        self.label.label.set_single_line_mode(True)

        self.anim_image = gtk.Image()
        self.image = gtk.image_new_from_stock(gtk.STOCK_CLOSE,
                                              gtk.ICON_SIZE_MENU)

        self.button = gtk.Button()
        self.button.set_focus_on_click(False)
        self.button.set_relief(gtk.RELIEF_NONE)
        self.button.set_name('tabNotebookButton')
        self.button.add(self.image)

        self.button.connect('clicked', self.__close_button_clicked)
        self.button.connect('style-set', self.__button_style_set)
        self.label.connect('button-press-event', self.on_button_press_event)
        self.label.entry.connect('focus-out-event', self.on_entry_focus_out)

        self.pack_start(self.anim_image, False, False, 0)
        self.pack_start(self.label)
        self.pack_end(self.button, False, False, 0)

        self.show_all()
        self.switch_button_mode(False)

    def on_entry_focus_out(self, widget, event):
        self.switch_button_mode(False)

    def on_button_press_event(self, widget, event):
        if event.type == gtk.gdk._2BUTTON_PRESS:
            self.switch_button_mode(True)

    def switch_button_mode(self, mode):
        """Switch button from editing mode (True) to label mode (False)
        """
        if mode:
            self.image.set_from_stock(gtk.STOCK_APPLY, gtk.ICON_SIZE_MENU)
        else:
            self.image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)

        parent = self.get_parent()

        if parent:
            parent.queue_draw()

    def do_realize(self):
        global global_animation
        
        HIGHBox.do_realize(self)
        
        self.anim_image.set_from_animation(global_animation)
        self.anim_image.hide()

    def __button_style_set(self, widget, prev_style):
        w, h = gtk.icon_size_lookup_for_settings(widget.get_settings(),
                                                 gtk.ICON_SIZE_MENU)
        widget.set_size_request(w + 2, h + 2)

    def __close_button_clicked(self, widget):
        self.emit('close-clicked')

    def set_throbber_pixbuf(self, animated):
        self.anim_image.set_from_animation(animated)

    def get_text(self):
        return self.label.get_text()

    def set_text(self, text):
        self.label.set_text(text)

    def get_label(self):
        return self.label.get_label()

    def set_label(self, label):
        self.label.set_text(label)

    def get_animated_label(self):
        return self.label

    def get_animated_image(self):
        return self.anim_image

    def start_animation(self):
        self.anim_image.show()

    def stop_animation(self):
        self.anim_image.hide()

# OMG! I can hook the world!

class Throbber(Plugin):
    def start(self, reader):
        global global_animation

        log.info('We\'re going to hook a class man. Pay attention.')

        Core().connect('NmapScanNotebookPage-created', self.__on_new_nb_page)

        path = reader.extract_file('data/throbber-16.gif')

        global_animation = gtk.gdk.PixbufAnimation(path)

        ScanNotebook.HIGAnimatedTabLabel = MyHIGClosableTabLabel
        sys.modules['higwidgets.hignotebooks'].HIGClosableTabLabel = \
                                           MyHIGClosableTabLabel
        sys.modules['higwidgets.hignotebooks'].HIGAnimatedTabLabel = \
                                           MyHIGClosableTabLabel

        self.update_existing_tab_labels(MyHIGClosableTabLabel)

    def __on_new_nb_page(self, core, page):
        page.toolbar.scan_button.connect('clicked', self.__start_scan, page)
        page.connect('scan-finished', self.__stop_scan)

    def __start_scan(self, widget, page):
        if page.status.get_scanning():
            lbl = Core().get_main_scan_notebook().get_tab_label(page)

            if isinstance(lbl, MyHIGClosableTabLabel):
                lbl.start_animation()

    def __stop_scan(self, page):
        lbl = Core().get_main_scan_notebook().get_tab_label(page)

        if isinstance(lbl, MyHIGClosableTabLabel):
            lbl.stop_animation()

    def stop(self):
        log.info('Reverting changes.')

        ScanNotebook.HIGAnimatedTabLabel = HIGClosableTabLabel
        sys.modules['higwidgets.hignotebooks'].HIGClosableTabLabel = \
                                           HIGClosableTabLabel
        sys.modules['higwidgets.hignotebooks'].HIGAnimatedTabLabel = \
                                           HIGClosableTabLabel

        self.update_existing_tab_labels(HIGClosableTabLabel)

    def update_existing_tab_labels(self, klass):
        # We're going to do a foreach on every notebook page and change the tab
        # label of every child.
        
        log.debug('Applying %s to every page in notebook.' % str(klass))

        notebook = Core().get_main_scan_notebook()

        for page in notebook:
            # Just create a new tab label widget.
            old_label = notebook.get_tab_label(page)

            tab_label = klass(old_label.get_text())
            tab_label.get_animated_label().connect('title-edited', \
                                                   notebook.title_edited_cb, \
                                                   page)
            tab_label.connect('close-clicked', notebook.close_scan_cb)

            # Setting up
            notebook.set_tab_label(page, tab_label)

            log.debug('New tab-label class applied to page %s' % str(page))

__plugins__ = [Throbber]
