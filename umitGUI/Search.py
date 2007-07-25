#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2005 Insecure.Com LLC.
#
# Author: Adriano Monteiro Marques <py.adriano@gmail.com>
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

from higwidgets.higwindows import HIGWindow
from higwidgets.higboxes import HIGVBox
from higwidgets.higbuttons import HIGButton
from higwidgets.higlabels import HIGEntryLabel

from umitCore.I18N import _


class SearchWindow(HIGWindow, object):
    """Search Window. Shows informations about the search while it's running
    """
    def __init__(self):
        HIGWindow.__init__(self)

        self.__create_widgets()
        self.__pack_widgets()
        self.__set_widgets()

    def __create_widgets(self):
        self.vbox = HIGVBox()
        self.cancel_button = HIGButton(stock=gtk.STOCK_CANCEL)
        self.button_box = gtk.HButtonBox()
        self.search_file_label = HIGEntryLabel()
        self.progress = gtk.ProgressBar()

    def __pack_widgets(self):
        self.add(self.vbox)
        self.vbox.pack_start(self.search_file_label)
        self.vbox.pack_start(self.progress)
        self.vbox.pack_start(self.button_box)
        self.button_box.pack_start(self.cancel_button)

    def __set_widgets(self):
        self.button_box.set_layout(gtk.BUTTONBOX_END)
        self.set_title('Searching...')
        self.set_size_request(350, -1)
        self.set_position(gtk.WIN_POS_CENTER)

    def set_filename(self, filename):
        self.__filename = filename
        self.search_file_label.set_text(_("File: %s") % filename)

    def get_filename(self):
        return self.__filename

    def set_path(self, path):
        self.__path = path
        self.forward_progress_status()
        self.progress.set_text(_("Searching inside '%s'") % path)

    def get_path(self):
        return self.__path

    def set_fraction(self, fraction):
        self.__fraction = fraction

    def get_fraction(self):
        return self.__fraction

    def forward_progress_status(self):
        try:
            self.fraction
        except:
            self.fraction = 0.2        
        self.progress.set_fraction(self.fraction + self.progress.get_fraction())


    filename = property(get_filename, set_filename, doc=_("File name been searched"))
    path = property(get_path, set_path, doc=_("Path been scanned"))
    fraction = property(get_fraction, set_fraction, doc=_("Fraction of the progress bar"))

if __name__ == '__main__':
    s = SearchWindow()
    s.filename = 'umit.conf'
    s.path = '/usr/local'

    s.show_all()
    gtk.main()
