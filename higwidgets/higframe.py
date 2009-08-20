#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2005 Insecure.Com LLC.
#
# Author: Guilherme Polo <ggpolo@gmail.com>
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
higwidgets/higframe.py

    hig frame
"""

__all__ = ['HIGFrame']

import gtk

class HIGFrame(gtk.Frame):
    """
    Frame without border with bold label.
    """
    def __init__(self, label=None):
        gtk.Frame.__init__(self)
        
        self.set_shadow_type(gtk.SHADOW_NONE)
        self._flabel = gtk.Label()
        self._set_label(label)
        self.set_label_widget(self._flabel)

    def _set_label(self, label):
        self._flabel.set_markup("<b>%s</b>" % label)

#class needed to maintain compatibility of RadialNet with higwidgets
class HIGFrameRNet(gtk.Frame):
    def __init__(self, label=''):
        gtk.Frame.__init__(self)

        self.set_border_width(3)
        self.set_shadow_type(gtk.SHADOW_NONE)

        self.__alignment = gtk.Alignment(0, 0, 1, 1)
        self.__alignment.set_padding(12, 0, 24, 0)

        self.add(self.__alignment)

        self._set_label(label)


    def _set_label(self, label):
        self.set_label("<b>%s</b>" % label)
        self.get_label_widget().set_use_markup(True)


    def _add(self, widget):
        self.__alignment.add(widget)


    def _remove(self, widget):
        self.__alignment.remove(widget)

# Demo
if __name__ == "__main__":
    w = gtk.Window()

    hframe = HIGFrame("Sample HIGFrame")
    aalign = gtk.Alignment(0, 0, 0, 0)
    aalign.set_padding(12, 0, 24, 0)
    abox = gtk.VBox()
    aalign.add(abox)
    hframe.add(aalign)
    w.add(hframe)

    for i in xrange(5):
        abox.pack_start(gtk.Label("Sample %d" % i), False, False, 3)

    w.connect('destroy', lambda d: gtk.main_quit())
    w.show_all()

    gtk.main()
