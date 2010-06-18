#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Adriano Monteiro Marques
#
# Author: Luís A. Bastião Silva <luis.kop@gmail.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA


import gtk

from umit.interfaceeditor.RestructFiles import RestructFiles
from higwidgets.higwindows import HIGWindow
from higwidgets.higdialogs import HIGDialog
from higwidgets.higscrollers import HIGScrolledWindow 
from higwidgets.higboxes import HIGVBox

from umit.core.UmitLogging import log
from umit.core.I18N import _
import gobject


'''
DependecesOption is a Windows that shows the options in use
when remove button is pressed at Option Edit Mode

'''



class DependenceOption(HIGDialog):
    def __init__(self, option, restructfiles, profile, wizard):
        HIGDialog.__init__(self, _('Dependence of Option ') + option )
        self.set_size_request(-1,300)
        self.restructfiles = restructfiles
        self._profile = profile
        self._wizard = wizard
        self._draw_widgets()
        self.show_all()
    def _draw_widgets(self):
        self._label = gtk.Label(_('There is a problem deleting this option. This options have dependences.  '))
        self._label_q = gtk.Label(_('Are you sure that can remove this option? Dependences should be removed too'))
        self._label.show()
        self._label_q.show()
        self.vbox.pack_start(self._label, False, False)
        self.vbox.pack_start(self._label_q, False, False)
        self._treeview_compare()
        self.add_button(gtk.STOCK_YES, gtk.RESPONSE_YES)
        self.add_button(gtk.STOCK_NO, gtk.RESPONSE_NO)
        self.action_area.show_all()
    def _treeview_compare(self):
        self._model = gtk.TreeStore(gobject.TYPE_STRING)
        profile = self._model.append( None, ['Profile'])
        wizard = self._model.append( None, ['Wizard'])

        for i in self._profile:

            parent = self._model.append( profile, [i[0]])
            inside = self._model.append( parent, [i[1]] )
            if len(i) == 3:
                self._model.append(inside, [i[2]])

        for i in self._wizard:

            parent = self._model.append( wizard, [i[0]])
            inside = self._model.append( parent, [i[1]] )
            if len(i) == 3:
                self._model.append(inside, [i[2]])	
        self._treeview = gtk.TreeView(self._model)
        column = gtk.TreeViewColumn()
        column.set_title('Name')
        render_text = gtk.CellRendererText()
        column.pack_start(render_text, expand=True)
        column.add_attribute(render_text, 'text', 0)
        self._treeview.append_column(column)
        self.__scrolledwindow = HIGScrolledWindow()
        self.__scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC,
                                         gtk.POLICY_AUTOMATIC)
        self.__scrolledwindow.add(self._treeview)
        self.vbox.pack_start(self.__scrolledwindow, True, True)
        self.__scrolledwindow.show_all()
        self._treeview.show_all()
        self.vbox.show_all()



