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

import gtk
import gobject

from umit.core.I18N import _

from umit.inventory.TLBase import categories

ALLCHANGES = _("View all changes")
LISTCHANGES = _("Changes listing")

class TLChangesTree(gtk.HBox):
    """
    A treeview that holds Inventory Changes in a timerange by category.
    """

    def __init__(self, connector, datagrabber, db_categories, inventory,
        hostaddr):

        gtk.HBox.__init__(self)

        self.connector = connector
        self.datagrabber = datagrabber
        self.db_categories = db_categories
        self.inventory = inventory
        self.hostaddr = hostaddr

        self.treestore = gtk.TreeStore(str)
        self.treeview = gtk.TreeView(self.treestore)
        self.tcolumn = gtk.TreeViewColumn("%s (0)" % LISTCHANGES)
        cell = gtk.CellRendererText()
        self.tcolumn.pack_start(cell, True)
        self.tcolumn.add_attribute(cell, 'text', 0)
        self.treeview.append_column(self.tcolumn)

        self.fulldata = None # all data for current selection

        self.treeview.connect('row-activated', self._row_activated)
        self.treeview.connect('button-press-event', self._row_clicked)
        self.connector.connect('selection-update', self._update_tree)

        self._append_categories()
        self.__layout()


    def _append_categories(self):
        """
        Append categories to treeview.
        """
        # startup situation
        self.treestore.append(None, [ALLCHANGES])
        for category in self.db_categories:
            self.treestore.append(None, ["%s (0)" % categories[category]])


    def _row_activated(self, tview, path, tvcolumn):
        """
        Some row in treeview was activated.
        """
        if path[len(path) - 1] == 0 and len(path) != 3:
            # clicked on View all changes

            if len(path) == 1:
                # clicked on "main" View all changes
                if self.fulldata is not None:
                    full_load = self.fulldata

                    self.emit('data-update', 'full', full_load)

            elif len(path) == 2:
                # clicked on "View all changes" inside a category
                category_id = path[0]
                category_load = { }
                category_load[category_id] = self.fulldata[category_id]

                self.emit('data-update', 'category', category_load)

        elif len(path) == 3:
            # clicked on some host inside inventory
            category_id = path[0]
            inventory = self.treestore[path[:2]][0].split('(')[0][:-1]
            host_addr = self.treestore[path][0].split('(')[0][:-1]

            especific_load = {category_id: (inventory, host_addr)}

            self.emit('data-update', 'especific', especific_load)

        else:
            # clicked on some other row kind, just expand/collapse
            if self.treeview.row_expanded(path):
                self.treeview.collapse_row(path)
            else:
                self.treeview.expand_row(path, False)

    def _row_clicked(self, tv, event):
        """
        Clicked on treeview, in a row or not.
        """
        if event.button == 1: # left click
            x, y = int(event.x), int(event.y)

            try:
                path, col, xpos, ypos = tv.get_path_at_pos(x, y)
            except TypeError:
                return

            if not path:
                # didn't click in a row.
                return

            text_start = tv.get_cell_area(path, col)[0]

            if path[len(path) - 1] != 0 and len(path) != 3:
                if x >= text_start:
                    # clicked on some other row kind, just expand/collapse
                    if self.treeview.row_expanded(path):
                        self.treeview.collapse_row(path)
                    else:
                        self.treeview.expand_row(path, False)
            else:
                self._row_activated(self.treeview, path, col)


    def _update_tree(self, obj, range_start, range_end):
        """
        Grabs changes from range_start to range_end and then update tree.
        """
        db_categories = self.datagrabber.get_categories()
        self.db_categories = [value[1] for key, value in db_categories.items()]

        data = { }

        # grab changes in timerange
        self.datagrabber.use_dict_cursor()
        for key in db_categories.keys():
            if not range_start or not range_end:
                data[key] = { }
                continue

            chgs = self.datagrabber.timerange_changes_data_generic(range_start,
                range_end, key, self.inventory, self.hostaddr)
            data[key] = chgs
        self.fulldata = data
        self.datagrabber.use_standard_cursor()

        clean_data = { }
        inventories = { }
        addresses = { }

        for category, entries in data.items():
            clean_data[category] = { }

            if not entries:
                # no changes for current category
                continue

            for entry in entries:
                fk_address = entry["fk_address"]
                fk_inventory = entry["fk_inventory"]

                # grab host address
                if not fk_address in addresses.keys():
                    adr = self.datagrabber.get_address_for_address_id_from_db(
                          fk_address)

                    addresses[fk_address] = adr

                # grab inventory name
                if not fk_inventory in inventories.keys():
                    inv_name = self.datagrabber.get_inventory_name_for_id(
                               fk_inventory)

                    inventories[fk_inventory] = inv_name

                # update clean_data
                if inventories[fk_inventory] in clean_data[category]:
                    cdata = clean_data[category][inventories[fk_inventory]]

                    if addresses[fk_address] in cdata:
                        cdata[addresses[fk_address]] += 1
                    else:
                        cdata[addresses[fk_address]] = 1

                    clean_data[category][inventories[fk_inventory]] = cdata

                else:
                    clean_data[category].update(
                        {inventories[fk_inventory]:
                            {addresses[fk_address]: 1}}
                        )

        # write new data into changestree
        changes_sum = 0
        self.treestore.clear()
        self.treestore.append(None, [ALLCHANGES])

        for indx, item in enumerate(self.db_categories):
            data_length = len(data[indx + 1]) # keys starting at 1
            changes_sum += data_length

            root = self.treestore.append(None, ["%s (%d)" % (categories[item],
                data_length)])

            if data_length > 0:
                self.treestore.append(root, [ALLCHANGES])

            for inventory, entries in clean_data[indx + 1].items():

                inv_root = self.treestore.append(root, ["%s (0)" % inventory])
                #self.treestore.append(inv_root, [ALLCHANGES])

                curr_changes_sum = 0
                for address, changes in entries.items():
                    self.treestore.append(inv_root, ["%s (%d)" % (address,
                        changes)])
                    curr_changes_sum += changes

                # set number of changes in inventory title
                self.treestore[inv_root][0] = "%s (%d)" % (inventory,
                    curr_changes_sum)

        self.tcolumn.set_title("%s (%d)" % (LISTCHANGES, changes_sum))


    def __layout(self):
        """
        Layout treeview.
        """
        scrollw = gtk.ScrolledWindow()
        scrollw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrollw.add_with_viewport(self.treeview)
        scrollw.set_size_request(170, -1)

        self.add(scrollw)


gobject.signal_new("data-update", TLChangesTree, gobject.SIGNAL_RUN_LAST,
    gobject.TYPE_NONE, (str, object))

