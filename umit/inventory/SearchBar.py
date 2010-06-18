# Copyright (C) 2007 Adriano Monteiro Marques
#
# Authors: Guilherme Polo <ggpolo@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

import re
import gtk

from umit.core.I18N import _

from higwidgets.higdialogs import HIGAlertDialog

ip_pattern = re.compile(r"""^(([1]?[0-9]{1,2}|2([0-4][0-9]|5[0-5]))\.){3}
                         ([1]?[0-9]{1,2}|2([0-4][0-9]|5[0-5]))$""", re.VERBOSE)

class SearchBar(gtk.Toolbar):
    """
    Builds a Search toolbar for Network Inventory.
    """

    def __init__(self, daddy=None, invdb=None):
        gtk.Toolbar.__init__(self)

        self.daddy = daddy
        self.invdb = invdb

        self.inventory_list = []
        index = (i for i in xrange(5))
        self.tooltips = gtk.Tooltips()

        self.insert(self.searchcombo(), index.next())
        self.insert(self.invcombo(), index.next())


    def searchcombo(self):
        """
        Create and return a ToolItem with an entry combobox.
        """
        cbentry = gtk.combo_box_entry_new_text()
        cbentry.append_text(_("Search term"))
        cbentry.set_active(0)
        cbentry.remove_text(0) # remove "Search Term" from searchcombo
        cbentry.child.connect('key-press-event', self.comboentry_press)
        cbentry.show()

        btn_search = gtk.Button(stock=gtk.STOCK_FIND)
        btn_search.connect('clicked', self.perform_search, cbentry.child)
        btn_search.show()
        lbl = btn_search.get_children()[0].get_children()[0].get_children()[1]
        lbl.set_label("")
        self.tooltips.set_tip(btn_search, _("Find devices"))

        box = gtk.HBox()
        box.pack_start(cbentry, True, True, 0)
        box.pack_end(btn_search, False, False, 0)

        item = gtk.ToolItem()
        item.add(box)
        item.set_expand(True)

        return item


    def invcombo(self):
        """
        Creates and return a ToolItem with a combobox with a full listing
        of Inventories.
        """
        align = gtk.Alignment(0, 0.5, 0, 1)
        align.set_padding(0, 0, 6, 0)
        cbinv = gtk.combo_box_new_text()
        align.add(cbinv)

        cbinv.append_text(_("Search in"))
        cbinv.append_text(_("All Inventories"))
        cbinv.set_active(1)
        cbinv.connect('changed', self._change_inventory)
        self.inventory_list.append(_("Search in"))
        self.inventory_list.append(_("All Inventories"))

        self.inventory = cbinv.get_active_text()

        item = gtk.ToolItem()
        item.add(align)

        if not self.invdb:
            return item

        for invid, invname in self.invdb.get_inventories_ids_names():
            cbinv.append_text('%s' % invname)
            self.inventory_list.append(invname)

        return item


    def comboentry_press(self, widget, event):
        """
        Handles keypress in combobox.
        """
        kname = gtk.gdk.keyval_name(event.keyval)
        kname = kname.lower()

        if kname == 'return' or kname == 'kp_enter':
            self.perform_search(None, widget)

        return False


    def perform_search(self, event, widget):
        """
        Perform search based on text, inventory and selected category.
        """
        # verify database connection
        if not self.invdb:
            dlg = HIGAlertDialog(None,
                message_format=_("Impossible to perform search."),
                secondary_text=_("Connection to the database isn't "
                    "established. There are some possible reasons: your "
                    "UMIT database could be corrupted, missing, or "
                    "something more strange, or, you aren't running this "
                    "inside UMIT.\n\nIf you suspect this is a bug, please "
                    "report it."))
            dlg.run()
            dlg.destroy()

            #return

        # verify inventory selection
        if not self.inventory_list.index(self.inventory):
            dlg = HIGAlertDialog(None,
                message_format=_("Specify an Inventory."),
                secondary_text=_("You need to select one or All Inventories "
                    "in order to perform a search."))
            dlg.run()
            dlg.destroy()

            return

        # get Inventory(ies) id(s)
        if self.inventory_list.index(self.inventory) == 1: # all Inventories
            invids = (inv[0] for inv in self.invdb.get_inventories_ids())

        else: # single Inventory
            invids = (self.invdb.get_inventory_id_for_name(self.inventory), )

        # build hosts dict based on selected inventory
        hosts = { }
        for invid in invids:
            for scan in self.invdb.get_scans_id_for_inventory(invid):
                # retrieve scan finish timestamp
                fts = self.invdb.get_finish_timestamp_for_scan_from_db(scan[0])

                # retrieve hosts id for each scan
                for host in self.invdb.get_hosts_id_for_scan_from_db(scan[0]):

                    # retrieve ipv4 address for host
                    addr = self.invdb.get_ipv4_for_host_from_db(host[0])

                    hosts[host[0]] = (invid, addr, fts)

        # prepend search term in combobox
        combobox = widget.get_parent()
        combobox.prepend_text(widget.get_text())
        combobox.set_active(0)

        search_text = widget.get_text().strip()

        # Empty string
        if not search_text:
            dlg = HIGAlertDialog(None,
                message_format=_("Empty string not allow"),
                secondary_text=_("Suggestions: port 80, change text, etc."))
            dlg.run()
            dlg.destroy()
            return

        # check if search_text looks like an ip, if it looks like, then verify
        # for devices in hosts dict.
        if not ip_pattern.match(search_text):
            # didnt search by ip, will take "longer" to find the device.
            if self.daddy:
                self.daddy._build_results_view(search_text, hosts)

            return

        host_matches = { }

        # nice, it is a ip or you fooled me :)
        for host in hosts.values():

            if search_text == host[1]: # found IP
                # one device may be related to several scans, but it will
                # be returned just once for an inventory.

                curr_result = (host[0], host[1], "IP") # inv id, addr, category

                if not curr_result in host_matches:
                    date = host[2]
                    host_matches[curr_result] = date


        if self.daddy:
            self.daddy._build_results_view(search_text, host_matches, True)


    def _change_inventory(self, event):
        """
        Changed Inventory selection.
        """
        self.inventory = self.inventory_list[event.get_active()]


    def get_inventory(self):
        """
        Returns current selected Inventory.
        """
        return self.__inventory


    def set_inventory(self, inventory):
        """
        Sets active Inventory.
        """
        self.__inventory = inventory


    # Properties
    inventory = property(get_inventory, set_inventory)
