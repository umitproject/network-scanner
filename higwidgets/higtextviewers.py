#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
#         Cleber Rodrigues <cleber.gnu@gmail.com>
#         João Paulo de Souza Medeiros <ignotus21@gmail.com>
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

"""
higwidgets/higtextviewers.py

   text viewers related classes
"""

__all__ = ['HIGTextView']

import gtk
from higwidgets.higboxes import HIGHBox, HIGScrolledWindow

class HIGTextView(gtk.TextView):
    def __init__(self, text=''):
        gtk.TextView.__init__(self)
        self.set_wrap_mode(gtk.WRAP_WORD)
        self.get_buffer().set_text(text)

#class needed to maintain compatibility of RadialNet with higwidgets 
class HIGTextViewRNet(HIGScrolledWindow):
    def __init__(self):
        HIGScrolledWindow.__init__(self)
        self.__auto_scroll = False
        self.__create_widgets()

    def __create_widgets(self):
        self.__textbuffer = gtk.TextBuffer()
        self.__textview = gtk.TextView(self.__textbuffer)

        self.add_with_viewport(self.__textview)

    def _set_auto_scroll(self, value):
        self.__auto_scroll = value

    def _set_editable(self, editable):
        self.__textview.set_editable(False)

    def _modify_font(self, font):
        self.__textview.modify_font(font)

    def _set_text(self, text):
        self.__textbuffer.set_text(text)

        if self.__auto_scroll:
            self._set_scroll_down()


    def _get_text(self):
        return self.__textbuffer.get_text(self.__textbuffer.get_start_iter(),
                                          self.__textbuffer.get_end_iter())

    def _set_scroll_down(self):
        self.get_vadjustment().set_value(self.get_vadjustment().upper)

    def _get_textbuffer(self):
        return self.__textbuffer


class HIGTextEditor(HIGScrolledWindow):
    def __init__(self):
        HIGScrolledWindow.__init__(self)
        self.connect('expose_event', self.__expose)

        self.__auto_scroll = False

        self.__create_widgets()

    def __create_widgets(self):
        self.__hbox = HIGHBox(spacing=6)

        self.__textbuffer = gtk.TextBuffer()
        self.__textview = gtk.TextView(self.__textbuffer)

        self.__linebuffer = gtk.TextBuffer()
        self.__lineview = gtk.TextView(self.__linebuffer)
        self.__lineview.set_justification(gtk.JUSTIFY_RIGHT)
        self.__lineview.set_editable(False)
        self.__lineview.set_sensitive(False)

        self.__hbox._pack_noexpand_nofill(self.__lineview)
        self.__hbox._pack_expand_fill(self.__textview)

        self.add_with_viewport(self.__hbox)

    def __expose(self, widget, event):
        # code to fix a gtk issue that don't show text correctly
        self.__hbox.check_resize()

    def _set_auto_scroll(self, value):
        self.__auto_scroll = value

    def _set_editable(self, editable):
        self.__textview.set_editable(False)

    def _modify_font(self, font):
        self.__textview.modify_font(font)
        self.__lineview.modify_font(font)

    def _set_text(self, text):
        if text != "":

            count = text.count('\n') + text.count('\r')

            lines = range(1, count + 2)
            lines = [str(i).strip() for i in lines]

            self.__textbuffer.set_text(text)
            self.__linebuffer.set_text('\n'.join(lines))

            if self.__auto_scroll:
                self.bw_set_scroll_down()

        else:

            self.__textbuffer.set_text("")
            self.__linebuffer.set_text("")


    def _get_text(self):
        return self.__textbuffer.get_text(self.__textbuffer.get_start_iter(),
                                          self.__textbuffer.get_end_iter())

    def _set_scroll_down(self):
        self.get_vadjustment().set_value(self.get_vadjustment().upper)

