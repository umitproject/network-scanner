#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
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
import os.path

from higwidgets.higwindows import HIGWindow
from higwidgets.higboxes import HIGVBox
from higwidgets.higbuttons import HIGButton
from higwidgets.higboxes import HIGVBox, HIGHBox
from higwidgets.higboxes import HIGSpacer, hig_box_space_holder
from higwidgets.higlabels import HIGSectionLabel, HIGEntryLabel
from higwidgets.higtables import HIGTable
from higwidgets.higdialogs import HIGAlertDialog

from time import localtime
from types import StringTypes

from umitCore.I18N import _
from umitCore.UmitLogging import log
from umitCore.NmapParser import months
from umitCore.SearchResult import SearchDir, SearchDB, SearchTabs
from umitCore.UmitConf import SearchConfig

from umitGUI.FileChoosers import DirectoryChooserDialog
from umitGUI.ProfileCombo import ProfileCombo
from umitGUI.TargetCombo import TargetCombo
from umitGUI.OptionCombo import OptionCombo
from umitGUI.ServiceCombo import ServiceCombo
from umitGUI.OSCombo import OSClassCombo, OSMatchCombo

search_config = SearchConfig()

class SearchGUI(gtk.HPaned, object):
    def __init__(self, notebook):
        gtk.HPaned.__init__(self)

        self._create_widgets()
        self._pack_widgets()
        self._connect_events()

        self.any_profile = _("Any profile")
        self.any_option = _("Any option")
        self.any_target = _("Any target")
        self.any_service = _("Any service")
        self.any_product = _("Any product")
        self.any_osclass = _("Any os class")
        self.any_osmatch = _("Any os match")
        self.any = _("Any")

        # Setting default values
        self.port_open = True
        self.port_filtered = True
        self.port_closed = True
        self.profile = self.any_profile
        self.option = self.any_option
        self.target = self.any_target
        self.service = self.any_service
        self.product = self.any_product
        self.osclass = self.any_osclass
        self.osmatch = self.any_osmatch

        # Search options
        self.directory = search_config.directory
        self.file_extension = search_config.file_extension
        self.save_time = search_config.save_time
        self.save = search_config.store_results
        self.search_db = search_config.search_db

        self.parsed_results = {}
        self._set_result_view()
        self.scan_num = 1
        self.id = 0
        self.notebook = notebook

    def _create_widgets(self):
        # Main widgets
        self.hpaned = gtk.HPaned()
        self.main_vbox = HIGVBox()

        # Results section
        self.result_section = HIGSectionLabel(_("Results"))
        self.result_vbox = HIGVBox()
        self.result_hbox = HIGHBox()
        self.result_list = gtk.ListStore(str, str, int) # title, date, id
        self.result_view = gtk.TreeView(self.result_list)
        self.result_scrolled = gtk.ScrolledWindow()
        self.result_title_column = gtk.TreeViewColumn(_("Scan"))
        self.result_date_column = gtk.TreeViewColumn(_("Date"))

        # Search notebook
        self.search_vbox = HIGVBox()
        self.search_notebook = gtk.Notebook()
        self.search_button = HIGButton(stock=gtk.STOCK_FIND)

        # General page
        self.general_vbox = HIGVBox()
        self.general_hbox = HIGHBox()
        #self.general_start_hbox = HIGHBox()
        #self.general_finish_hbox = HIGHBox()
        
        self.general_section = HIGSectionLabel(_("General search parameters"))
        
        self.general_table = HIGTable()

        self.general_option_label = HIGEntryLabel(_("Option"))
        self.general_profile_label = HIGEntryLabel(_("Profile"))
        #self.general_finished_label = HIGEntryLabel(_("Finished"))
        #self.general_started_label = HIGEntryLabel(_("Started"))
        self.general_keyword_label = HIGEntryLabel(_("Keyword"))

        self.general_keyword_entry = gtk.Entry()
        self.general_option_combo = OptionCombo()
        self.general_profile_combo = ProfileCombo()
        #self.general_started_range = DateRange()
        #self.general_finished_range = DateRange()

        # Host page
        self.host_vbox = HIGVBox()
        self.host_hbox = HIGHBox()
        #self.host_uptime_hbox = HIGHBox()
        #self.host_lastboot_hbox = HIGHBox()
        
        self.host_section = HIGSectionLabel(_("Host search parameters"))
        
        self.host_table = HIGTable()

        self.host_target_label = HIGEntryLabel(_("Target"))
        self.host_mac_label = HIGEntryLabel(_("MAC"))
        self.host_ipv4_label = HIGEntryLabel(_("IPv4"))
        self.host_ipv6_label = HIGEntryLabel(_("IPv6"))
        #self.host_uptime_label = HIGEntryLabel(_("Uptime"))
        #self.host_lastboot_label = HIGEntryLabel(_("Last boot"))

        self.host_target_combo = TargetCombo()
        self.host_mac_entry = gtk.Entry()
        self.host_ipv4_entry = gtk.Entry()
        self.host_ipv6_entry = gtk.Entry()
        #self.host_uptime_range = DateRange()
        #self.host_lastboot_range = DateRange()


        # Service
        self.serv_vbox = HIGVBox()
        self.serv_hbox = HIGHBox()
        self.serv_section = HIGSectionLabel(_("Service search parameters"))
        self.serv_table = HIGTable()

        self.serv_port_label = HIGEntryLabel(_("Port number"))
        self.serv_service_label = HIGEntryLabel(_("Service"))
        self.serv_product_label = HIGEntryLabel(_("Product"))
        self.serv_portstate_label = HIGEntryLabel(_("Port state"))
        
        self.serv_port_entry = gtk.Entry()
        self.serv_service_combo = ServiceCombo()
        self.serv_product_entry = gtk.Entry()
        self.serv_portstate_check = PortState()


        # OS
        self.os_vbox = HIGVBox()
        self.os_hbox = HIGHBox()
        self.os_section = HIGSectionLabel(_("Operating System search \
parameters"))
        self.os_table = HIGTable()
        
        self.os_osclass_label = HIGEntryLabel(_("OS class"))
        self.os_osmatch_label = HIGEntryLabel(_("OS match"))
        
        self.os_osclass_combo = OSClassCombo()
        self.os_osmatch_combo = OSMatchCombo()


        # Search options page
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
        # Packing result section
        self.result_vbox.set_border_width(12)
        self.result_vbox._pack_noexpand_nofill(self.result_section)
        self.result_vbox._pack_expand_fill(self.result_hbox)

        self.result_scrolled.set_size_request(185, -1)
        #self.result_scrolled.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.result_scrolled.add(self.result_view)
        self.result_scrolled.set_policy(gtk.POLICY_AUTOMATIC,
                                        gtk.POLICY_AUTOMATIC)
        self.result_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.result_hbox._pack_expand_fill(self.result_scrolled)

        ## Search Notebook
        self.search_vbox._pack_expand_fill(self.search_notebook)
        self.search_vbox._pack_expand_fill(self.search_button)

        self.search_notebook.set_border_width(1)
        self.search_vbox.set_border_width(12)
        
        # General page
        self.general_vbox.set_border_width(12)
        self.general_vbox._pack_noexpand_nofill(self.general_section)
        self.general_vbox._pack_noexpand_nofill(self.general_hbox)
        
        #self.general_vbox._pack_noexpand_nofill(self.general_start_section)
        #self.general_vbox._pack_noexpand_nofill(self.general_start_hbox)
        
        #self.general_vbox._pack_noexpand_nofill(self.general_finish_section)
        #self.general_vbox._pack_noexpand_nofill(self.general_finish_hbox)
        
        self.general_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.general_hbox._pack_expand_fill(self.general_table)

        #self.general_start_hbox._pack_noexpand_nofill(hig_box_space_holder())
        #self.general_start_hbox._pack_noexpand_nofill(self.general_started_range)

        #self.general_finish_hbox._pack_noexpand_nofill(hig_box_space_holder())
        #self.general_finish_hbox._pack_expand_fill(self.general_finished_range)
        

        self.general_table.attach_label(self.general_keyword_label, 0, 1, 0, 1)
        self.general_table.attach_label(self.general_profile_label, 0, 1, 1, 2)
        self.general_table.attach_label(self.general_option_label, 0, 1, 2, 3)

        self.general_table.attach_entry(self.general_keyword_entry, 1, 2, 0, 1)
        self.general_table.attach_entry(self.general_profile_combo, 1, 2, 1, 2)
        self.general_table.attach_entry(self.general_option_combo, 1, 2, 2, 3)
        
        self.search_notebook.append_page(self.general_vbox,
                                         gtk.Label(_("General")))

        # Host page
        self.host_vbox.set_border_width(12)
        self.host_vbox._pack_noexpand_nofill(self.host_section)
        self.host_vbox._pack_noexpand_nofill(self.host_hbox)
        
        #self.host_vbox._pack_noexpand_nofill(self.host_uptime_section)
        #self.host_vbox._pack_noexpand_nofill(self.host_uptime_hbox)

        #self.host_vbox._pack_noexpand_nofill(self.host_lastboot_section)
        #self.host_vbox._pack_noexpand_nofill(self.host_lastboot_hbox)
        
        self.host_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.host_hbox._pack_expand_fill(self.host_table)

        #self.host_uptime_hbox._pack_noexpand_nofill(hig_box_space_holder())
        #self.host_uptime_hbox._pack_noexpand_nofill(self.host_uptime_range)

        #self.host_lastboot_hbox._pack_noexpand_nofill(hig_box_space_holder())
        #self.host_lastboot_hbox._pack_expand_fill(self.host_lastboot_range)

        self.host_table.attach_label(self.host_target_label, 0, 1, 0, 1)
        self.host_table.attach_label(self.host_mac_label, 0, 1, 1, 2)
        self.host_table.attach_label(self.host_ipv4_label, 0, 1, 2, 3)
        self.host_table.attach_label(self.host_ipv6_label, 0, 1, 3, 4)

        self.host_table.attach_entry(self.host_target_combo, 1, 2, 0, 1)
        self.host_table.attach_entry(self.host_mac_entry, 1, 2, 1, 2)
        self.host_table.attach_entry(self.host_ipv4_entry, 1, 2, 2, 3)
        self.host_table.attach_entry(self.host_ipv6_entry, 1, 2, 3, 4)
        
        self.search_notebook.append_page(self.host_vbox, gtk.Label(_("Host")))

        # Service page
        self.serv_vbox.set_border_width(12)
        self.serv_vbox._pack_noexpand_nofill(self.serv_section)
        self.serv_vbox._pack_noexpand_nofill(self.serv_hbox)
        
        self.serv_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.serv_hbox._pack_expand_fill(self.serv_table)

        self.serv_table.attach_label(self.serv_port_label, 0, 1, 0, 1)
        self.serv_table.attach_label(self.serv_portstate_label, 0, 1, 1, 2)
        self.serv_table.attach_label(self.serv_product_label, 0, 1, 2, 3)
        self.serv_table.attach_label(self.serv_service_label, 0, 1, 3, 4)

        self.serv_table.attach_entry(self.serv_port_entry, 1, 2, 0, 1)
        self.serv_table.attach_entry(self.serv_portstate_check, 1, 2, 1, 2)
        self.serv_table.attach_entry(self.serv_product_entry, 1, 2, 2, 3)
        self.serv_table.attach_entry(self.serv_service_combo, 1, 2, 3, 4)
        
        self.search_notebook.append_page(self.serv_vbox,
                                         gtk.Label(_("Service")))

        # OS page
        self.os_vbox.set_border_width(12)
        self.os_vbox._pack_noexpand_nofill(self.os_section)
        self.os_vbox._pack_noexpand_nofill(self.os_hbox)

        self.os_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.os_hbox._pack_expand_fill(self.os_table)

        self.os_table.attach_label(self.os_osclass_label, 0, 1, 0, 1)
        self.os_table.attach_label(self.os_osmatch_label, 0, 1, 1, 2)

        self.os_table.attach_entry(self.os_osclass_combo, 1, 2, 0, 1)
        self.os_table.attach_entry(self.os_osmatch_combo, 1, 2, 1, 2)

        self.search_notebook.append_page(self.os_vbox, gtk.Label(_("OS")))

        # Search options page
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


        self.search_notebook.append_page(self.opt_vbox,
                                         gtk.Label(_("Search options")))

        self.pack1(self.search_vbox, True, False)
        self.pack2(self.result_vbox, True, False)

    def _connect_events(self):
        self.os_osclass_combo.connect("changed", self.update_osmatch)
        self.search_button.connect("clicked", self.start_search)

        self.opt_extension_entry.connect("focus-out-event",
                                         self.update_extension_entry)
        self.opt_save_check.connect("toggled", self.update_save_check)
        self.opt_search_check.connect("toggled", self.update_search_check)
        self.opt_path_entry.connect_entry_change(self.update_path_entry)
        self.opt_savetime_entry.connect_entry_change(self.update_savetime_entry)
        

    def update_path_entry(self, widget, extra=None):
        search_config.directory = widget.get_text()

    def update_savetime_entry(self, widget, extra=None):
        search_config.save_time = self.opt_savetime_entry.time

    def update_extension_entry(self, widget, extra=None):
        search_config.file_extension = widget.get_text()

    def update_save_check(self, widget):
        search_config.store_results = widget.get_active()

    def update_search_check(self, widget):
        search_config.search_db = widget.get_active()

    def start_search(self, widget):
        if not self.search_db and \
           not self.directory:
            self.search_notebook.set_current_page(-1)
            d = HIGAlertDialog(message_format=_("No search method selected!"),
                               secondary_text=_("Umit can search results on \
directories or inside it's own database. Please, select a method by choosing \
a directory or by checking the search data base option at the 'Search options' \
tab before start the search"))
            d.run()
            d.destroy()
            return
        
        search_dict = dict(keyword=self.keyword,
                           profile=self.profile,
                           option=self.option,
                           target=self.target,
                           mac=self.mac,
                           ipv4=self.ipv4,
                           ipv6=self.ipv6,
                           port=self.port,
                           port_open=self.port_open,
                           port_filtered=self.port_filtered,
                           port_closed=self.port_closed,
                           service=self.service,
                           osclass=self.osclass,
                           osmatch=self.osmatch,
                           product=self.product)

        self.clear_result_list()
        
        if self.search_db:
            search_db = SearchDB()

            for result in search_db.search(**search_dict):
                self.append_result(result)

        if self.directory:
            search_dir = SearchDir(self.directory, self.file_extension)

            for result in search_dir.search(**search_dict):
                self.append_result(result)

        search_tabs = SearchTabs(self.notebook)
        for result in search_tabs.search(**search_dict):
            self.append_result(result)  

    def clear_result_list(self):
        for i in range(len(self.result_list)):
            iter = self.result_list.get_iter_root()
            del(self.result_list[iter])

    def append_result(self, parsed_result):
        title = ""
        if parsed_result.scan_name:
            title = parsed_result.scan_name
        elif parsed_result.nmap_xml_file:
            title = os.path.split(parsed_result.nmap_xml_file)[-1]
        elif parsed_result.profile_name and parsed_result.target:
            title = "%s on %s" % (parsed_result.profile_name,
                                  parsed_result.target)
        else:
            title = "Scan %s" % (self.scan_num)
            self.scan_num += 1

        try:
            date = localtime(float(parsed_result.start))
            date_field = "%02d %s %04d" % (date[2],
                                           months[date[1]][:3],
                                           date[0])
        except ValueError:
            date_field = _("Unknown")


        self.parsed_results[self.id] = [title, parsed_result]
        self.result_list.append([title, date_field, self.id])
        self.id += 1

    def update_osmatch(self, widegt):
        self.os_osmatch_combo.update(self.os_osclass_combo.selected_osclass)

    def get_keyword(self):
        return self.general_keyword_entry.get_text()

    def set_keyword(self, keyword):
        self.general_keyword_entry.set_text(keyword)

    def get_profile(self):
        if self.general_profile_combo.selected_profile == self.any_profile or \
           self.general_profile_combo.selected_profile == self.any:
            return "*"
        return self.general_profile_combo.selected_profile

    def set_profile(self, profile):
        self.general_profile_combo.selected_profile = profile

    def get_option(self):
        if self.general_option_combo.selected_option == self.any_option or \
           self.general_option_combo.selected_option == self.any:
            return "*"
        return self.general_option_combo.selected_option

    def set_option(self, option):
        self.general_option_combo.selected_option = option

    def get_target(self):
        if self.host_target_combo.selected_target == self.any_target or \
           self.host_target_combo.selected_target == self.any:
            return "*"
        return self.host_target_combo.selected_target

    def set_target(self, target):
        self.host_target_combo.selected_target = target

    def get_mac(self):
        return self.host_mac_entry.get_text()

    def set_mac(self, mac):
        self.host_mac_entry.set_text(mac)

    def get_ipv4(self):
        return self.host_ipv4_entry.get_text()

    def set_ipv4(self, ipv4):
        self.host_ipv4_entry.set_text(ipv4)

    def get_ipv6(self):
        return self.host_ipv6_entry.get_text()

    def set_ipv6(self, ipv6):
        self.host_ipv6_entry.set_text(ipv6)

    def get_port(self):
        return self.serv_port_entry.get_text().split(";")

    def set_port(self, port):
        if type(port) in StringTypes:
            self.serv_port_entry.set_text(port)
        elif type(port) == type([]):
            self.serv_port_entry.set_text(";".join(port))

    def get_port_open(self):
        return self.serv_portstate_check.open

    def set_port_open(self, open):
        self.serv_portstate_check.open = open

    def get_port_filtered(self):
        return self.serv_portstate_check.filtered

    def set_port_filtered(self, filtered):
        self.serv_portstate_check.filtered = filtered

    def get_port_closed(self):
        return self.serv_portstate_check.closed

    def set_port_closed(self, closed):
        self.serv_portstate_check.closed = closed

    def get_service(self):
        if self.serv_service_combo.selected_service == self.any_service or \
           self.serv_service_combo.selected_service == self.any:
            return "*"
        return self.serv_service_combo.selected_service

    def set_service(self, service):
        self.serv_service_combo.selected_service = service

    def get_osclass(self):
        if self.os_osclass_combo.selected_osclass == self.any_osclass or \
           self.os_osclass_combo.selected_osclass == self.any:
            return "*"
        return self.os_osclass_combo.selected_osclass

    def set_osclass(self, osclass):
        self.os_osclass_combo.selected_osclass = osclass

    def get_osmatch(self):
        if self.os_osmatch_combo.selected_osmatch == self.any_osmatch or \
           self.os_osmatch_combo.selected_osmatch == self.any:
            return "*"
        return self.os_osmatch_combo.selected_osmatch

    def set_osmatch(self, osmatch):
        self.os_osmatch_combo.selected_osmatch = osmatch

    def get_product(self):
        if self.serv_product_entry.get_text() == self.any_product or \
           self.serv_product_entry.get_text() == self.any:
            return "*"
        return self.serv_product_entry.get_text()

    def set_product(self, product):
        self.serv_product_entry.set_text(product)

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
        self.opt_savetime_entry.time = save_time

    def get_save(self):
        return self.opt_save_check.get_active()

    def set_save(self, save):
        self.opt_save_check.set_active(save)

    def get_search_db(self):
        return self.opt_search_check.get_active()

    def set_search_db(self, search_db):
        self.opt_search_check.set_active(search_db)

    def get_selected_results(self):
        selection = self.result_view.get_selection()
        rows = selection.get_selected_rows()
        list_store = rows[0]

        results = {}
        for row in rows[1]:
            r = row[0]
            results[list_store[r][2]] = self.parsed_results[list_store[r][2]]

        return results

    def _set_result_view(self):
        self.result_view.set_enable_search(True)
        self.result_view.set_search_column(0)
        
        selection = self.result_view.get_selection()
        selection.set_mode(gtk.SELECTION_MULTIPLE)

        self.result_view.append_column(self.result_title_column)
        self.result_view.append_column(self.result_date_column)
        
        self.result_title_column.set_resizable(True)
        self.result_date_column.set_resizable(True)
        
        self.result_title_column.set_sort_column_id(0)
        self.result_date_column.set_sort_column_id(1)
        
        self.result_title_column.set_reorderable(True)
        self.result_date_column.set_reorderable(True)

        cell = gtk.CellRendererText()
        
        self.result_title_column.pack_start(cell, True)
        self.result_date_column.pack_start(cell, True)
        
        self.result_title_column.set_attributes(cell, text=0)
        self.result_date_column.set_attributes(cell, text=1)
        

    keyword = property(get_keyword, set_keyword)
    profile = property(get_profile, set_profile)
    option = property(get_option, set_option)
    target = property(get_target, set_target)
    mac = property(get_mac, set_mac)
    ipv4 = property(get_ipv4, set_ipv4)
    ipv6 = property(get_ipv6, set_ipv6)
    port = property(get_port, set_port)
    port_open = property(get_port_open, set_port_open)
    port_filtered = property(get_port_filtered, set_port_filtered)
    port_closed = property(get_port_closed, set_port_closed)
    service = property(get_service, set_service)
    product = property(get_product, set_product)
    osclass = property(get_osclass, set_osclass)
    osmatch = property(get_osmatch, set_osmatch)
    directory = property(get_directory, set_directory)
    file_extension = property(get_file_extension, set_file_extension)
    save_time = property(get_save_time, set_save_time)
    save = property(get_save, set_save)
    search_db = property(get_search_db, set_search_db)
    selected_results = property(get_selected_results)

class Date(gtk.HBox, object):
    def __init__(self):
        gtk.HBox.__init__(self)
        self._create_widgets()
        self._connect_widgets()
        self._pack_widgets()

        self.date = localtime()[:3]

    def _create_widgets(self):
        t = localtime()
        self.date_button = HIGButton()
        self.date_sep = gtk.Label(", ")
        self.hour = gtk.SpinButton(gtk.Adjustment(value=t[3],
                                                  lower=0,
                                                  upper=23,
                                                  step_incr=1), 1)
        self.hour_sep = gtk.Label(":")
        self.minute = gtk.SpinButton(gtk.Adjustment(value=t[4],
                                                  lower=0,
                                                  upper=59,
                                                  step_incr=1), 1)

    def _connect_widgets(self):
        self.date_button.connect("clicked", self.show_calendar)

    def _pack_widgets(self):
        self.hour.set_width_chars(2)
        self.minute.set_width_chars(2)
        
        self.pack_start(self.date_button, False, False)
        self.pack_start(self.date_sep, False, False)
        self.pack_start(self.hour, False, False)
        self.pack_start(self.hour_sep, False, False)
        self.pack_start(self.minute, False, False)

    def show_calendar(self, widget):
        calendar = DateCalendar()
        calendar.connect_calendar(self.update_button)
        calendar.show_all()

    def update_button(self, widget):
        date = list(widget.get_date())
        date[1] += 1 # Add 1 to month, because calendar date is zero-based
        self.date = tuple(date)

    def set_date(self, date):
        # Localtime Format: (year, month, day)
        self.date_button.set_label("%02d %s %04d" % (date[2],
                                                     months[date[1]][:3],
                                                     date[0]))
        self._date = date

    def get_date(self):
        return self._date

    def get_time(self):
        return (self.hour.get_value_as_int(), self.minute.get_value_as_int())

    def set_time(self, time):
        print time
        if type(time) == type([]):
            self.hour.set_value(time[0])
            self.minute.set_value(time[1])
        elif type(time) in StringTypes:
            time = time.split(";")
            self.hour.set_value(time[0])
            self.minute.set_value(time[1])

    date = property(get_date, set_date)
    time = property(get_time, set_time)
    _date = localtime()[:3]

class DateCalendar(gtk.Window, object):
    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_POPUP)
        self.set_position(gtk.WIN_POS_MOUSE)
        
        self.calendar = gtk.Calendar()
        self.add(self.calendar)

    def connect_calendar(self, method):
        self.calendar.connect("day-selected-double-click",
                              self.kill_calendar,
                              method)

    def kill_calendar(self, widget, method):
        method(widget)
        self.destroy()

class DateRange(gtk.HBox, object):
    def __init__(self):
        gtk.HBox.__init__(self)

        self._create_widgets()
        self._pack_widgets()

    def _create_widgets(self):
        self.label2 = gtk.Label("<b> %s </b>" % _("/"))
        
        self.entry1 = Date()
        self.entry2 = Date()

    def _pack_widgets(self):
        self.label2.set_use_markup(True)

        self.pack_start(self.entry1, False, False)
        self.pack_start(self.label2, False, False)
        self.pack_start(self.entry2, False, False)
        
    def get_start(self):
        return self.entry1.date + self.entry1.time

    def set_start(self, start):
        self.entry1.date = start[:3]
        self.entry1.time = start[3:]

    def get_end(self):
        return self.entry2.date +self.entry2.time

    def set_end(self, end):
        self.entry2.date = end[:3]
        self.entry2.time = end[3:]

    start = property(get_start, set_start)
    end = property(get_end, set_end)

class PortState(gtk.VBox, object):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.open_check = gtk.CheckButton(_("Open"))
        self.filtered_check = gtk.CheckButton(_("Filtered"))
        self.closed_check = gtk.CheckButton(_("Closed"))

        self.pack_start(self.open_check, False, False)
        self.pack_start(self.filtered_check, False, False)
        self.pack_start(self.closed_check, False, False)

    def get_open(self):
        return self.open_check.get_active()

    def set_open(self, open):
        self.open_check.set_active(open)

    def get_filtered(self):
        return self.filtered_check.get_active()

    def set_filtered(self, filtered):
        self.filtered_check.set_active(filtered)

    def get_closed(self):
        return self.closed_check.get_active()

    def set_closed(self, closed):
        self.closed_check.set_active(closed)


    open = property(get_open, set_open)
    filtered = property(get_filtered, set_filtered)
    closed = property(get_closed, set_closed)

class PathEntry(HIGHBox, object):
    def __init__(self):
        HIGHBox.__init__(self)
        self.entry = gtk.Entry()
        self.button = HIGButton(stock=gtk.STOCK_OPEN)

        self.entry.set_width_chars(20)
        self.button.connect("clicked", self.open_dialog)
        
        self._pack_expand_fill(self.entry)
        self._pack_noexpand_nofill(self.button)

    def connect_entry_change(self, method):
        self.entry.connect("focus-out-event", method)

    def open_dialog(self, widget):
        dialog = DirectoryChooserDialog(title=_("Choose the path to search in"))
        dialog.run()
        self.path = dialog.get_filename()
        self.entry.grab_focus()
        dialog.destroy()

    def get_path(self):
        return self.entry.get_text()

    def set_path(self, path):
        self.entry.set_text(path)

    path = property(get_path, set_path)

class SaveTime(HIGHBox, object):
    def __init__(self):
        HIGHBox.__init__(self)
        self.entry = gtk.SpinButton(gtk.Adjustment(value=30,
                                                   lower=0,
                                                   upper=9999,
                                                   step_incr=1), 1)
        self.time_list = gtk.ListStore(str)
        self.time_combo = gtk.ComboBoxEntry(self.time_list, 0)

        self.entry.set_width_chars(4)

        for i in SearchConfig().time_list.keys():
            self.time_list.append([i])

        self._pack_noexpand_nofill(self.entry)
        self._pack_expand_fill(self.time_combo)

    def get_time(self):
        # Format: [self.entry.get_text(), self.time_combo.child.get_text()]
        # Format: ["10", "days"]
        return [self.entry.get_text(), self.time_combo.child.get_text()]

    def connect_entry_change(self, method):
        self.entry.connect("focus-out-event", method)
        self.time_combo.connect("changed", method)

    def set_time(self, time):
        self.entry.set_value(int(time[0]))
        self.time_combo.child.set_text(time[1])

    time = property(get_time, set_time)

if __name__ == "__main__":
    def quit(x, y):
        print "keyword", s.keyword
        print "profile", s.profile
        print "option", s.option
        print "target", s.target
        print "mac", s.mac
        print "ipv4", s.ipv4
        print "ipv6", s.ipv6
        print "port", s.port
        print "port_open", s.port_open
        print "port_filtered", s.port_filtered
        print "port_closed", s.port_closed
        print "service", s.service
        print "product", s.product
        print "osclass", s.osclass
        print "osmatch", s.osmatch
        print "directory", s.directory
        print "file_extension", s.file_extension
        print "save_time", s.save_time
        print "save", s.save
        print "search_db", s.search_db
        print "selected_results", s.selected_results
            
        gtk.main_quit()


    s = SearchGUI()
    s.keyword = "Testing Keyword"
    s.profile = "Testing Profile"
    s.option = "Testing Option"
    s.target = "www.microsoft.com"
    s.mac = "MAC Address"
    s.ipv4 = "IPv4 Address"
    s.ipv6 = "IPv6 Address"
    s.port = "20"
    s.port_open = True
    s.port_filtered = True
    s.port_closed = True
    s.service = "ssh"
    s.osclass = "Any class"
    s.osmatch = "Any match"
    s.product = "OpenSSH"
    s.directory = "/home/adriano"
    s.file_extension = "usr;txt;nmap"
    s.save_time = ["30", "Years"]
    s.save = True
    s.search_db = True
    
    w = gtk.Window()
    w.set_size_request(700, 420)
    w.connect("delete-event", quit)
    w.add(s)
    
    w.show_all()

    gtk.main()
