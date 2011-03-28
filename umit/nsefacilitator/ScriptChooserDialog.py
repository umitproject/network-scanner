# Copyright (C) 2007 Adriano Monteiro Marques <py.adriano@gmail.com>
#
# Author: Maxim Gavrilov <lovelymax@gmail.com>
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

import os.path

import gobject
import gtk
from higwidgets.higdialogs import HIGDialog
from higwidgets.higtextviewers import HIGTextView
from higwidgets.hignotebooks import HIGNotebook

from umit.core.I18N import _
from umit.core.Paths import Path

from nseBase import ScriptBase
from nseConfig import ScriptConfig
from NmapFetch import NmapFetchScripts
from Utils import *

class ScriptSelection(object):
    def __init__(self, base):
        self.base = base
        self.categories = set()
        self.categories_selected = set()
        self.scripts = set()
        self.scripts_selected = set()
        self.dirs = set()
        self.dirs_selected = set()
        self._process_base(base)

    def _process_base(self, base):
        for item in base.get_script_items():
	    script = item.get_last_installed()
            if script:
                self.categories.update(script.categories)
                self.scripts.add(NmapFetchScripts().nmap_path(script.path))
        self.dirs = set(base.get_config().get_dirs())

    def set_selected(self, selected):
        self.categories_selected = set()
        self.scripts_selected = set()
        self.dirs_selected = set()
        for name in selected.split(","):
            name = name.strip()
            if not name:
                continue
            if name in self.categories:
                self.categories_selected.add(name)
            elif name in self.scripts:
                self.scripts_selected.add(NmapFetchScripts().nmap_path(name))
            elif name in self.dirs:
                self.dirs_selected.add(name)
            else:
                print "Unknown script parameter %s" % name

    def get_selected(self):
        res = []
        if self.categories_selected:
            res.extend(self.categories_selected)
        if self.scripts_selected:
            res.extend(self.scripts_selected)
        if self.dirs_selected:
            res.extend(self.dirs_selected)
        return ",".join(res)

class ScriptChooserDialog(HIGDialog):
    def __init__(self, selected = ''):
        HIGDialog.__init__(self, _("Select Necessory Scripts"), None,
                           gtk.DIALOG_MODAL,
                           (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                            gtk.STOCK_OK, gtk.RESPONSE_OK,
                            gtk.STOCK_HELP, gtk.RESPONSE_HELP))
        self.config = ScriptConfig()
        self.config.load()
        self.base = ScriptBase(self.config)
        self.base.load()
        self.selection = ScriptSelection(self.base)
        self.selection.set_selected(selected)
        self.set_size_request(400, 400)
        self.create_widgets()

    def get_scripts(self):
        return self.selection.get_selected()

    def create_page(self, full_set, selected_set):
        model = gtk.ListStore(bool, str)
        list_view = gtk.TreeView(model)

        model.set_sort_column_id(1, gtk.SORT_ASCENDING)
        list_view.set_headers_visible(False)
        list_view.set_search_column(2)

        cell = gtk.CellRendererToggle()
        cell.connect('toggled', self._toggled_cb, model, selected_set)
        col = gtk.TreeViewColumn(' ', cell, active=0)
        list_view.append_column(col)

        cell = gtk.CellRendererText()
        col = gtk.TreeViewColumn('id', cell, text=1)
        list_view.append_column(col)

        for item in full_set:
            model.append((item in selected_set, item))
            
        #self.list_view.connect('cursor-changed', self.id_select_cb)
        return scroll_wrap(list_view)

    def create_widgets(self):
        notebook = HIGNotebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        notebook.append_page(
            self.create_page(self.selection.categories, self.selection.categories_selected),
            gtk.Label(_("Categories")))
        notebook.append_page(
            self.create_page(self.selection.scripts, self.selection.scripts_selected),
            gtk.Label(_("Scripts")))
        notebook.append_page(
            self.create_page(self.selection.dirs, self.selection.dirs_selected),
            gtk.Label(_("Dirs")))
        self.vbox.add(notebook)
        self.connect("response", self._response_cb)
        self.show_all()

    def _toggled_cb(self, cell, path, model, selected):
        model[path][0] = not model[path][0]
        if model[path][1]:
            selected.add(model[path][1])
        else:
            selected.remove(model[path][1])

    def _response_cb(self, dialog, response_id):
        if response_id != gtk.RESPONSE_HELP:
            return
        import webbrowser
        webbrowser.open("file://%s" %
                        os.path.join(Path.docs_dir, "nse_facilitator.html#chooser"), new=2)
        self.stop_emission("response")

if __name__ == "__main__":
    sd = ScriptChooserDialog("")
    if sd.run() == gtk.RESPONSE_OK:
        print "OK:", sd.get_scripts()
    else:
        print "Cancel"
    sd.destroy()
    
