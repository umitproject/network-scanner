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
higwidgets/higwindows.py

   window related classes
"""

import gtk
from higwidgets import gtk_version_minor

PRIMARY_TEXT_MARKUP = '<span weight="bold" size="larger">%s</span>'

class HIGAlertDialog(gtk.MessageDialog):
    def __init__(self, parent=None, flags=0, type=gtk.MESSAGE_INFO,
                 buttons=gtk.BUTTONS_OK,
                 primary_text=None,
                 secondary_text=None):

        gtk.MessageDialog.__init__(self, parent, flags, type, buttons)

        self.connect('response', self.__destroy)

        self.set_resizable(False)

        self.set_title("Alert")
        self.set_markup(PRIMARY_TEXT_MARKUP % primary_text)

        if secondary_text:

            # GTK up to version 2.4 does not have secondary_text
            if gtk_version_minor > 4:
                self.format_secondary_text(secondary_text)


    def __destroy(self, dialog, id):
        self.destroy()

class HIGWindow(gtk.Window):
    """HIGFied Window"""
    def __init__(self, type=gtk.WINDOW_TOPLEVEL):
        gtk.Window.__init__(self, type)
        self.set_border_width(5)

# The Application main window should have no borders...
# so it should be really a gtk.Window
HIGMainWindow = gtk.Window


