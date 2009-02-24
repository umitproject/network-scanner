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
import pango

from higwidgets.hignotebooks import HIGAnimatedTabLabel

from umitCore.I18N import _
from umitCore.UmitLogging import log
from umitCore.Paths import Path
from umitInventory.Calendar import months
from umitInventory.TLBase import changes_in_db

umitdb = Path.umitdb_ng

class ChangesList(gtk.VBox):
    def __init__(self, daddy, invdb, display, data, data_built=False,
        load_now=True, data_range=(None, None)):
        """
        display expects to receive a ChangesDiff instance.

        data is the data you are passing, format:
           {category: (inventory, host_addr)} if data_built is False.

        data_built defines if you are passing data ready to be shown.

        load_now decides if TreeView will be built on startup or not.

        data_range sets a range to grab changes, (None, None) grabs
        everything.
        """

        gtk.VBox.__init__(self)

        self.invdb = invdb
        self.display = display
        self.daddy = daddy
        self.showing_data = None # full data being displayed is store here

        self.tview = gtk.TreeView()
        self.btns_box = gtk.HBox()
        self.viewing_lbl = gtk.Label()

        if load_now:
            self._set_data(data, data_built, data_range)

        self.tview.get_selection().connect('changed', self.row_changed)
        self.__layout()


    def _set_model(self):
        """
        Set liststore model.
        """
        pre_model = (str, ) * self.tcolumns
        self.model = gtk.ListStore(*pre_model)
        self.modelfilter = self.model.filter_new()

        self.tview.set_model(None)
        self.tview.set_model(self.modelfilter)


    def _set_data(self, data, data_built=False, data_range=(None, None)):
        """
        New data to use in treeview.
        """
        # clear previous data if any
        self.show_states = [ ]
        self.row_data = { }
        self.viewing_rows = { }

        self.showing_data = data
        self.data_built = data_built
        self.drange = data_range

        if data_built:
            columns = 5
            viewing = _("Inventories")
        else:
            viewing = _("Categories")

            if data.keys()[0] == -1:
                columns = 3
            else:
                columns = 2

        self.inventory = None
        self.hostaddr = None
        self.tcolumns = columns
        self._set_model()
        self._create_columns()
        self._setup_columns()

        filter_states = None

        if self.tcolumns == 5:
            filter_states = self._setup_rows_with_prebuilt_data(data)

        elif columns in (2, 3):
            self.category = data.keys()[0]
            self.inventory = data[self.category][0]
            self.hostaddr = data[self.category][1]
            filter_states = self._load_data(self.category, self.inventory,
                self.hostaddr, self.drange)

        if filter_states:
            self.show_states = filter_states
            self.modelfilter.set_visible_func(self.visible_tv)

        self._setup_top_box(self.btns_box, viewing)


    def visible_tv(self, model, tv_iter):
        """
        Set "visible" items on list.
        """
        to_show = [category for category, enabled in self.show_states.items() \
                                if enabled]

        return model.get_value(tv_iter, 0) in to_show


    def check_menu_selection(self, item, menu):
        """
        Do filter based on active items on menu.
        """
        index_states = [ ]
        items = menu.get_children()

        for item in items:
            if item.get_active():
                enabled = True
            else:
                enabled = False

            self.show_states[item.get_children()[0].get_label()] = enabled

        self.modelfilter.refilter()
        self.viewing_rows = self.filter_rows(self.row_data)

        self.update_viewing_lbl()


    def filter_rows(self, full):
        """
        Filter full data to show only partial data based on states.
        """
        count = 0
        partial = { }

        for value in full.values():
            if self.show_states[value[3]]:
                vnew = list(value)
                vnew[2] = count
                partial[count] = tuple(vnew)

                count += 1

        return partial


    def row_changed(self, tview):
        """
        Load data for selected row.
        """
        cdata = self.viewing_rows

        try:
            row = tview.get_selected_rows()[1][0][0]
        except IndexError: # list not filled with data yet
            return

        if self.tcolumns == 5:
            # get from model
            self.inventory = self.model[row][0]
            self.hostaddr = self.model[row][1]

        if cdata[row][0] == -1: # host down
            self.display.header_empty(self.hostaddr, self.inventory,
                self.model[row][self.tcolumns - 1])
            self.display.show_empty_hostid()
            return

        if cdata[row][0] == cdata[row][1]:
            # display complete text for first scan result for this host
            self.display.header_newhost(self.hostaddr, self.inventory,
                self.model[row][self.tcolumns - 1])
        else:
            self.display.header_comparison(self.hostaddr, self.inventory,
                self.model[row][self.tcolumns - 1])

        self.display.make_diff(cdata[row][0], cdata[row][1])

        if self.tcolumns == 5:
            self.inventory = None
            self.hostaddr = None


    def _create_columns(self):
        """
        Create TreeView columns.
        """
        columns = (
            (_("Inventory"), 0), (_("Host address"), 0),
            (_("Category"), 0), (_("Short change description"), 400),
            (_("Change date"), 0)
            )

        self.tview.columns = [None]*self.tcolumns

        start = len(columns) - self.tcolumns

        # remove previous columns if any
        for column in self.tview.get_columns():
            self.tview.remove_column(column)

        for i in range(self.tcolumns):
            column = columns[i + start]

            self.tview.columns[i] = gtk.TreeViewColumn(column[0])

            if column[1]: # minimum size
                self.tview.columns[i].set_min_width(column[1])


    def _setup_columns(self):
        """
        Set TreeView columns properties and etc.
        """
        for n in range(self.tcolumns):
            curr_column = self.tview.columns[n]
            curr_column.set_resizable(True)
            curr_column.cell = gtk.CellRendererText()
            curr_column.pack_start(self.tview.columns[n].cell, True)
            curr_column.set_attributes(self.tview.columns[n].cell, text=n)

            if n == self.tcolumns - 2: # description column
                curr_column.cell.set_property('ellipsize', pango.ELLIPSIZE_END)

            self.tview.append_column(curr_column)

        self.tview.set_search_column(1)


    def _setup_top_box(self, box, title):
        """
        Create and connect top items.
        """
        def create_custom_button(label):
            """
            Returns a button with a label and a down arrow.
            """
            cbtn = gtk.Button()
            cbtn.set_relief(gtk.RELIEF_NONE)

            box = gtk.HBox()
            box.pack_start(label, False, False, 0)
            box.pack_start(gtk.Label("  "), False, False, 0)
            box.pack_start(gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_OUT), False,
                False, 0)

            cbtn.add(box)
            return cbtn


        def where_to_popup(menu, button):
            """
            Calculates position to popup menu.
            """
            winx, winy = self.window.get_position()

            btn_alloc = button.get_allocation()
            btnx, btny = (btn_alloc[0], btn_alloc[1] + btn_alloc[3])

            return (winx + btnx, winy + btny, True)


        def popup_view_menu(widget):
            """
            Popup menu to enable/disable categories/inventories.
            """
            ctg_menu = gtk.Menu()

            for category, enabled in self.show_states.items():
                ctg_item = gtk.CheckMenuItem(category)
                if enabled:
                    ctg_item.set_active(True)

                ctg_item.connect('toggled', self.check_menu_selection, ctg_menu)
                ctg_menu.add(ctg_item)

            ctg_menu.show_all()
            ctg_menu.popup(None, None, where_to_popup, 1, 0, widget)


        def popup_opts_menu(widget):
            """
            Popup menu to view options for current changeslist.
            """
            opt_menu = gtk.Menu()

            if self.tcolumns != 5:
                refresh_opt = gtk.MenuItem(_("Refresh"))
                refresh_opt.connect('activate', self.reload_data)
                opt_menu.add(refresh_opt)

            if title != _("Inventories"):
                tl_opt = gtk.MenuItem(_("Timeline for this host"))
                tl_opt.connect('activate', self.timeline_for_host)
                opt_menu.add(tl_opt)

            opt_menu.show_all()
            opt_menu.popup(None, None, where_to_popup, 1, 0, widget)


        # remove previous widgets
        [box.remove(w) for w in box.get_children()]

        if not self.show_states:
            return

        view_btn = create_custom_button(gtk.Label(title))
        view_btn.connect('clicked', popup_view_menu)
        view_btn.show_all()

        opts_btn = None
        if self.tcolumns != 5 or title != _("Inventories"):
            opts_btn = create_custom_button(gtk.Label(_("Options")))
            opts_btn.connect('clicked', popup_opts_menu)
            opts_btn.show_all()

        box.pack_start(view_btn, False, False, 0)

        if opts_btn:
            box.pack_start(opts_btn, False, False, 3)

        box.pack_end(self.viewing_lbl, False, False, 3)
        box.show_all()

        self.update_viewing_lbl()


    def reload_data(self, event):
        """
        Reload data on this changeslist.
        """
        self._set_data(self.showing_data, self.data_built, self.drange)


    def timeline_for_host(self, event):
        """
        Show timeline for a especific host (Only available in Historic, for
        now at least).
        """
        def close_page(widget, data):
            """
            Close search page.
            """
            page_num = self.daddy.viewernb.page_num(data)
            self.daddy.viewernb.remove_page(page_num)

        from umitInventory.Timeline import TLHolder

        fk_inventory = self.invdb.get_inventory_id_for_name(self.inventory)
        fk_address = (
            self.invdb.get_address_id_for_address_from_db(self.hostaddr))

        tl = TLHolder(fk_inventory, fk_address)
        tl.show_all()

        title = "%s/%s" % (self.inventory, self.hostaddr)
        tab_label = HIGAnimatedTabLabel(title)
        tab_label.show()
        tab_label.connect("close-clicked", close_page, tl)
        self.daddy.viewernb.append_page(tl, tab_label)


    def update_viewing_lbl(self):
        """
        Update viewing_lbl based on viewing_rows.
        """
        vrows = len(self.viewing_rows)
        if vrows:
            self.viewing_lbl.set_label(
                    _("Viewing") + (" 1-%d " % vrows) +
                    _("of") + (" %d" % vrows))
        else:
            self.viewing_lbl.set_label(_("Nothing to view"))


    def format_date(self, date):
        """
        Format date to be displayed in Date column.
        """
        try:
            date.hour
        except AttributeError, e:
            log.critical(">>> Report this as a BUG!, sqlite didn't return "
                "column with timestamp format, errmsg: %s" % e)
            log.debug(">>> date, type(date):", date, type(date))

            return date

        return "%02d:%02d:%02d, %02d %s %s" % (date.hour, date.minute,
            date.second, date.day, months[date.month-1][:3], date.year)


    def _setup_rows_with_prebuilt_data(self, data_dict):
        """
        Use this method in case you are passing built data for ChangesList.
        """
        states = { }

        indx = 0
        for category_id, values in data_dict.items():
            db_category = self.invdb.get_category_name_by_id(category_id)

            for value in values:
                inventory_id = value["fk_inventory"]
                address_id = value["fk_address"]
                text = value["short_description"]
                entry_date = value["entry_date"]

                new_hostid = value["new_hostid"]
                old_hostid = value["old_hostid"]

                inv_name = self.invdb.get_inventory_name_for_id(inventory_id)
                host_addr = self.invdb.get_address_for_address_id_from_db(\
                    address_id)

                if not inv_name in states:
                    # filter by Inventory
                    states[inv_name] = True

                self.model.append([
                    inv_name, host_addr, changes_in_db[db_category], text,
                    self.format_date(entry_date)
                    ])

                self.row_data[indx] = [new_hostid, old_hostid, indx, inv_name]

                indx += 1

        # filter
        self.viewing_rows = self.row_data.copy()

        return states


    def _load_data(self, category, inventory, host_addr, data_range):
        """
        Load data for especified inventory and host address and
        a category possibly in a data_range or not.
        """
        fk_category = category
        fk_inventory = self.invdb.get_inventory_id_for_name(inventory)
        fk_address = self.invdb.get_address_id_for_address_from_db(host_addr)

        # Not done for now: case for only range especified

        if data_range[0] and data_range[1] and fk_category != -1:
            # range and category especified
            changes = self.invdb.get_inventory_changes_for_category_in_range(
                fk_inventory, fk_address, category, data_range[0],
                data_range[1])

        elif not (data_range[0] and data_range[1]) and fk_category != -1:
            # only category especified

            # this is not being used anywhere right now.
            changes = self.invdb.get_inventory_changes_for_category(
                fk_inventory, fk_address, category)

        else:
            # no range and no category especified
            changes = self.invdb.get_inventory_changes(fk_inventory,
                fk_address)

        return self._setup_rows(changes, fk_category)


    def _setup_rows(self, changes, category=-1):
        """
        Create filter and setup liststore rows with changes from _load_data.
        """
        # available categories
        states = { }

        for indx, change in enumerate(changes):
            entry_date = change[2]
            text = change[3]

            if category == -1: # changes for every category
                affected = changes_in_db[change[4]]
                self.model.append([affected, text,
                    self.format_date(entry_date)])

                if not affected in states:
                    states[affected] = True

                # [newid, oldid, index in current list, category]
                self.row_data[indx] = [change[1], change[0], indx, affected]

            else: # changes for a single category
                self.model.append([text, self.format_date(entry_date)])

                # [newid, oldid, index in current list]
                self.row_data[indx] = [change[1], change[0], indx]

        # filter
        self.viewing_rows = self.row_data.copy()

        return states


    def __layout(self):
        """
        Layout widgets.
        """
        sw = gtk.ScrolledWindow()
        sw.add(self.tview)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.set_size_request(-1, 220)

        self.pack_start(self.btns_box, False, False, 0)
        self.pack_start(sw, True, True, 0)

        self.show_all()
