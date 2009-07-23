#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
#         Cleber Rodrigues <cleber.gnu@gmail.com>
#         Francesco Piccinno <stack.box@gmail.com>
#
# This library is free software; you can redistribute it and/or modify 
# it under the terms of the GNU Lesser General Public License as published 
# by the Free Software Foundation; either version 2.1 of the License, or 
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public 
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License 
# along with this library; if not, write to the Free Software Foundation, 
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA 

import gtk
import gobject

from higwidgets.higspinner import HIGSpinner
from higwidgets.higboxes import HIGHBox
from higwidgets.higbuttons import HIGButton

class HIGEditableLabel(gtk.EventBox):
    # called when label is changed .. if returns True new_value is setted
    __gsignals__ = {'title-edited' : (gobject.SIGNAL_RUN_LAST,
                                      gobject.TYPE_BOOLEAN,
                                      (gobject.TYPE_STRING,
                                       gobject.TYPE_STRING))}

    def __init__(self, label=''):
        gobject.GObject.__init__(self)

        self.label = gtk.Label(label)
        self.entry = gtk.Entry()

        self.lock = False
        
        box = gtk.HBox()
        self.add(box)
        
        box.pack_start(self.label, False, False, 0)
        box.pack_start(self.entry, False, False, 0)
        
        self.set_visible_window(False)
        self.show_all()
        
        self.entry.connect('activate', self.on_entry_activated)
        self.entry.connect('focus-out-event', self.on_lost_focus)
        self.connect('realize', self.on_realize_event)
        self.connect('button-press-event', self.on_button_press_event)

    def on_lost_focus(self, widget, event):
        self.on_entry_activated(widget)

    def on_entry_activated(self, widget):
        # Muttex for focus
        if self.lock:
            return False

        self.lock = True

        old_text = self.label.get_text()
        new_text = self.entry.get_text()

        self.switch_mode(False)

        # If returns True we can change the label
        if self.emit('title-edited', old_text, new_text):
            self.label.set_text(new_text)

        self.lock = False

        return False

    def on_realize_event(self, widget):
        self.entry.hide()

    def on_button_press_event(self, widget, event):
        if event.type == gtk.gdk._2BUTTON_PRESS:
            self.switch_mode(True)

    def switch_mode(self, editing):
        """Switches from editing (True) to label mode (False).
        """
        if editing:
            self.entry.set_text(self.label.get_text())
            self.entry.grab_focus()

            self.label.hide()
            self.entry.show()
        else:
            self.entry.set_text('')

            self.label.show()
            self.entry.hide()

        # Reallocate widget
        self.set_size_request(-1, -1)

    # Getters/setters for compatibility

    def get_text(self):
        return self.label.get_text()

    def set_text(self, label):
        self.label.set_text(label)

    def get_label(self):
        return self.label.get_label()

    def set_label(self, label):
        self.label.set_text(label)

gobject.type_register(HIGEditableLabel)
HIGAnimatedLabel = HIGEditableLabel

gtk.rc_parse_string(""" 
    style "thinWidget" { 
        xthickness = 0 
        ythickness = 0 
    } 
    widget "*.tabNotebookButton" style "thinWidget" 
""") 
 	
class HIGNotebook(gtk.Notebook):
    def __init__(self, popup=True):
        gtk.Notebook.__init__(self)
        if popup:
            self.popup_enable()

class HIGClosableTabLabel(HIGHBox):
    __gsignals__ = { 'close-clicked' : (gobject.SIGNAL_RUN_LAST,
                                        gobject.TYPE_NONE, ()) }

    def __init__(self, label_text=""):
        gobject.GObject.__init__(self)
        #HIGHBox.__init__(self, spacing=4)

        self.label_text = label_text
        self.__create_widgets()

        #self.propery_map = {"label_text" : self.label.get_label}

    def __create_widgets(self):
        self.label = HIGAnimatedLabel(self.label_text)
        
        self.editing = False
        self.image = gtk.image_new_from_stock(gtk.STOCK_CLOSE,
                                              gtk.ICON_SIZE_MENU)
        self.button = HIGButton()
        self.button.set_relief(gtk.RELIEF_NONE)
        self.button.set_focus_on_click(False)
        self.button.add(self.image)
        self.button.set_name('tabNotebookButton')

        self.button.connect('clicked', self.__on_button_clicked)
        self.button.connect('style-set', self.__on_button_style_set)
        self.label.connect('button-press-event', self.on_button_press_event)
        self.label.entry.connect('focus-out-event', self.on_entry_focus_out)
        
        self.pack_start(self.label, False, False, 0)
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

        self.editing = mode
        parent = self.get_parent()

        if parent:
            parent.queue_draw()

    def __on_button_clicked(self, widget):
        if self.editing:
            self.label.on_entry_activated(self.label.entry)
            self.switch_button_mode(False)
        else:
            self.emit('close-clicked')

    def __on_button_style_set(self, widget, prev_style):
        w, h = gtk.icon_size_lookup_for_settings(self.image.get_settings(),
                                                 gtk.ICON_SIZE_MENU)
        self.image.set_size_request(w, h)

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

gobject.type_register(HIGClosableTabLabel)

HIGAnimatedTabLabel = HIGClosableTabLabel
