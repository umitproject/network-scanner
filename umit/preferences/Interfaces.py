# Copyright (C) 2008 Adriano Monteiro Marques.
#
# Author: Luis A. Bastiao Silva <luis.kop@gmail.com>
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
from higwidgets.hignotebooks import HIGNotebook
from higwidgets.higtables import HIGTable
from higwidgets.higlabels import HIGSectionLabel, HIGEntryLabel
from higwidgets.higboxes import  hig_box_space_holder
from umit.preferences.FramesHIG import *

from umit.gui.NmapOutputProperties import NmapOutputPropertiesBox
# Colors section
from umit.gui.DiffCompare import Colors
#Search section
from umit.gui.SearchGUI import PathEntry, SaveTime

from umit.core.UmitConf import SearchConfig
from umit.core.UmitLogging import log
from umit.core.I18N import _

search_config = SearchConfig()






class InterfaceDetails(HIGNotebook):

    def __init__(self, name):
        HIGNotebook.__init__(self)
        self._create_widgets()


    def _create_widgets(self):
        # Notebook
        self._nb = self
        self._create_nmap_output()
        self._create_diff()
        self._create_search()

        self._nb.append_page(self._diff_box, gtk.Label(_('Diff Colors')))
        self._nb.append_page(self._nmap_box, gtk.Label(_('Nmap Results')))

        self._nb.append_page(self._search_box, gtk.Label(_('Search')))

    # Create Pages
    def _create_nmap_output(self):
        self._nmap_box = HIGScrolledWindow()
        self._nmap_res = NmapOutputPropertiesBox(None)
        self._nmap_box.add_with_viewport(self._nmap_res)

    def _create_diff(self):
        self.colors = Colors()
        self._diff_box = DiffColors(self.colors)
    def _create_search(self):
        self._search_box = SearchOptions()



# Class of Colors

class DiffColors(TabBox, object):
    def __init__(self, colors):
        self.colors = colors
        TabBox.__init__(self, _('Diff Colors'))
        self._pack_widgets()
        self._connect_widgets()



    def _create_widgets(self):
        self.vbox = HIGVBox()
        self.table = HIGTable()

        self.unchanged_button = gtk.ColorButton(self.colors.unchanged)
        self.unchanged_label = gtk.Label(_("Property remained <b>U</b>nchanged"))

        self.added_button = gtk.ColorButton(self.colors.added)
        self.added_label = gtk.Label(_("Property was <b>A</b>dded"))

        self.modified_button = gtk.ColorButton(self.colors.modified)
        self.modified_label = gtk.Label(_("Property was <b>M</b>odified"))

        self.not_present_button = gtk.ColorButton(self.colors.not_present)
        self.not_present_label = gtk.Label(_("Property is <b>N</b>ot present"))

    def _pack_widgets(self):
        self.unchanged_label.set_use_markup(True)
        self.added_label.set_use_markup(True)
        self.modified_label.set_use_markup(True)
        self.not_present_label.set_use_markup(True)

        self.table.attach_label(self.unchanged_button, 0, 1, 0, 1)
        self.table.attach_entry(self.unchanged_label, 1, 2, 0, 1)

        self.table.attach_label(self.added_button, 0, 1, 1, 2)
        self.table.attach_entry(self.added_label, 1, 2, 1, 2)

        self.table.attach_label(self.modified_button, 0, 1, 2, 3)
        self.table.attach_entry(self.modified_label, 1, 2, 2, 3)

        self.table.attach_label(self.not_present_button, 0, 1, 3, 4)
        self.table.attach_entry(self.not_present_label, 1, 2, 3, 4)

        self.vbox.pack_start(self.table)
        self.pack_start(self.vbox, False, False)


    def _connect_widgets(self):
        self.unchanged_button.connect("color-set",
                                      self.set_color,
                                      "unchanged")
        self.added_button.connect("color-set",
                                  self.set_color,
                                  "added")
        self.modified_button.connect("color-set",
                                     self.set_color,
                                     "modified")
        self.not_present_button.connect("color-set",
                                        self.set_color,
                                        "not_present")

    def set_color(self, widget, prop):
        self.colors.__setattr__(prop, widget.get_color())

class SearchOptions(TabBox, object):
    def __init__(self):
        TabBox.__init__(self, _('Search Options'))
        self._pack_widgets()
        self.directory = search_config.directory
        self.file_extension = search_config.file_extension
        self.save_time = search_config.save_time
        self.save = search_config.store_results
        self.search_db = search_config.search_db
        self._connect_events()
    def _create_widgets(self):
        self.opt_vbox = HIGVBox()
        self.opt_local_hbox = HIGHBox()
        self.opt_base_hbox = HIGHBox()
        self.opt_local_section = HIGSectionLabel(_("Local files"))
        self.opt_local_table = HIGTable()
        self.opt_base_section = HIGSectionLabel(_("Database"))
        self.opt_base_table = HIGTable()

        self.opt_path_label = HIGEntryLabel(_("Directory"))
        self.opt_extension_label = HIGEntryLabel(_("File extension"))
        self.opt_savetime_label = HIGEntryLabel(_("Save results for"))

        self.opt_path_entry = PathEntry()
        self.opt_extension_entry = gtk.Entry()
        self.opt_savetime_entry = SaveTime()
        self.opt_save_check = gtk.CheckButton(_("Save scan results in data \
base for latter search"))
        self.opt_search_check = gtk.CheckButton(_("Search saved scan results \
in data base"))

    def _pack_widgets(self):
        self.opt_vbox.set_border_width(12)
        self.opt_vbox._pack_noexpand_nofill(self.opt_local_section)
        self.opt_vbox._pack_noexpand_nofill(self.opt_local_hbox)

        self.opt_vbox._pack_noexpand_nofill(self.opt_base_section)
        self.opt_vbox._pack_noexpand_nofill(self.opt_base_hbox)

        self.opt_local_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.opt_local_hbox._pack_expand_fill(self.opt_local_table)

        self.opt_base_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.opt_base_hbox._pack_expand_fill(self.opt_base_table)

        self.opt_local_table.attach_label(self.opt_path_label, 0, 1, 0, 1)
        self.opt_local_table.attach_label(self.opt_extension_label, 0, 1, 1, 2)

        self.opt_local_table.attach_entry(self.opt_path_entry, 1, 2, 0, 1)
        self.opt_local_table.attach_entry(self.opt_extension_entry, 1, 2, 1, 2)

        self.opt_base_table.attach_label(self.opt_savetime_label, 0, 1, 0, 1)
        self.opt_base_table.attach_label(self.opt_save_check, 0, 2, 1, 2)
        self.opt_base_table.attach_label(self.opt_search_check, 0, 2, 2, 3)

        self.opt_base_table.attach_entry(self.opt_savetime_entry, 1, 2, 0, 1)
        self.pack_start(self.opt_vbox, False, False)
    def _connect_events(self):
        self.opt_extension_entry.connect("focus-out-event",
                                         self.update_extension_entry)
        self.opt_save_check.connect("toggled", self.update_save_check)
        self.opt_search_check.connect("toggled", self.update_search_check)
        self.opt_path_entry.connect_entry_change(self.update_path_entry)
        self.opt_savetime_entry.connect_entry_change(self.update_savetime_entry)
    def update_path_entry(self, widget, extra=None):
        search_config.directory = widget.get_text()

    def update_search_check(self, widget):
        search_config.search_db = widget.get_active()

    def update_savetime_entry(self, widget, extra=None):
        print "save time"
        search_config.save_time = self.opt_savetime_entry.time
        print search_config.save_time

    def update_extension_entry(self, widget, extra=None):
        print "set extension"
        search_config.file_extension = widget.get_text()

    def update_save_check(self, widget):
        search_config.store_results = widget.get_active()
    def get_directory(self):
        return self.opt_path_entry.path

    def set_directory(self, directory):
        self.opt_path_entry.path = directory

    def get_file_extension(self):
        return self.opt_extension_entry.get_text().split(";")

    def set_file_extension(self, file_extension):
        if type(file_extension) == type([]):
            self.opt_extension_entry.set_text(";".join(file_extension))
        elif type(file_extension) in StringTypes:
            self.opt_extension_entry.set_text(file_extension)

    def get_save_time(self):
        return self.opt_savetime_entry.time

    def set_save_time(self, save_time):
        print "set save"
        self.opt_savetime_entry.time = save_time

    def get_save(self):
        return self.opt_save_check.get_active()

    def set_save(self, save):
        self.opt_save_check.set_active(save)

    def get_search_db(self):
        return self.opt_search_check.get_active()

    def set_search_db(self, search_db):
        self.opt_search_check.set_active(search_db)


    directory = property(get_directory, set_directory)
    file_extension = property(get_file_extension, set_file_extension)
    save_time = property(get_save_time, set_save_time)
    save = property(get_save, set_save)
    search_db = property(get_search_db, set_search_db)




class NmapResults(TabBox):
    def __init__(self):
        TabBox.__init__(self, _('Nmap Results'))
    def _create_widgets(self):
        self.box =  NmapOutputPropertiesBox(None)
        self.pack_start(self.box, False, False)

class Factory:
    def create(self, name):
        if name == "diff":
            return self._create_diff()
        elif name == "nmap":
            return self._create_nmap_output()
        elif name == "search":
            return self._create_search()
    def _create_nmap_output(self):
        return NmapResults()


    def _create_diff(self):
        self.colors = Colors()
        return DiffColors(self.colors)
    def _create_search(self):
        return SearchOptions()
