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

"""
Inventories Viewer main window.
"""

import os
import gtk
import gobject

from higwidgets.higwindows import HIGMainWindow
from higwidgets.hignotebooks import HIGNotebook, HIGAnimatedTabLabel
from higwidgets.higscrollers import HIGScrolledWindow
from higwidgets.higboxes import HIGHBox

from umit.core.I18N import _
from umit.core.Paths import Path
from umit.core.DataDecay import get_decays
from umit.core.Utils import open_url_as

from umit.db.Retrieve import ConnectInventoryDB
from umit.db.Search import SearchDB

from umit.gui.BugReport import BugReport
from umit.gui.SchedulerControl import SchedControl
from umit.gui.Help import show_help

from umit.inventory.StartupSettings import startup_options
from umit.inventory.NewInventory import NewInventory
from umit.inventory.SearchBar import SearchBar
from umit.inventory.ChangesList import ChangesList
from umit.inventory.ChangesDiff import ChangesDiff
from umit.inventory.InventoryTree import InventoryTree
from umit.inventory.Timeline import TLHolder
from umit.inventory.DataRemoval import ConfigureDataRemoval, RemoveOldData
from umit.inventory.SchedulerLog import SchedLog
from umit.inventory.SettingsWin import NISettings
from umit.inventory.About import About
from umit.inventory.InventoryException import NoInventory
from umit.inventory.Utils import append_s


umitdb = Path.umitdb_ng
inventory_info = _("Info")

class InventoryNB(gtk.Notebook):
    """
    Inventory Notebook for each Inventory.
    """

    def __init__(self, daddy):
        gtk.Notebook.__init__(self)
        self.set_scrollable(True)
        self.popup_enable()

        self.daddy = daddy
        self.pages = [ ]

        self.__layout()


    def append_inv(self, title="Info", box=None):
        """
        Add info page.
        """
        if self.page_exists(title):
            return

        custom_title = self.__create_custom_title(title, box)
        box.show()
        custom_title.show()
        self.append_page(box, custom_title)
        self.pages.append(title)

        self.__layout()


    def append_host(self, host_addr, box):
        """
        Add host page.
        """
        if self.page_exists(host_addr):
            return

        custom_title = self.__create_custom_title(host_addr, box)
        box.show()
        custom_title.show()
        self.append_page(box, custom_title)
        self.pages.append(host_addr)

        self.__layout()


    def page_exists(self, pagetitle):
        """
        Check if there is a page with pagetitle in this notebook.
        """
        if pagetitle in self.pages:
            return True

        return False


    def remove_page(self, button, page, text):
        """
        Remove a page from notebook and from self.pages
        """
        del self.pages[self.pages.index(text)]
        self.remove(page)

        if not len(self.pages): # last page in this inventory was just removed
            self.daddy._delete_inventory_page() # delete notebook


    def __add_close_icon_to_button(self, button):
        """
        Adds a close image to the page title close button.
        """
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        image.show()

        gtk.Button.set_relief(button, gtk.RELIEF_NONE)
        settings = gtk.Widget.get_settings(button)

        (w,h) = gtk.icon_size_lookup_for_settings(settings, gtk.ICON_SIZE_MENU)

        gtk.Widget.set_size_request(button, w + 4, h + 4)

        icon_hbox = gtk.HBox(False, 0)
        icon_hbox.pack_start(image, True, False, 0)
        icon_hbox.show()

        button.add(icon_hbox)


    def __create_custom_title(self, title, widget):
        """
        Creates a title with close button.
        """
        title_eb = gtk.EventBox()

        label = gtk.Label(title)
        label.show()

        title_hbox = gtk.HBox(False)
        title_hbox.pack_start(label, False, False, 0)

        title_eb.add(title_hbox)

        if self.daddy.invnb_close_btn:
            button = gtk.Button()
            button.connect('clicked', self.remove_page, widget, title)
            button.show()

            self.__add_close_icon_to_button(button)
            title_hbox.pack_end(button, False, False, 0)

        title_hbox.show()

        return title_eb


    def __layout(self):
        """
        Update notebook.
        """
        self.show()


class InventoryViewer(HIGMainWindow):
    """
    UMIT Network Inventory, Main Window.
    """

    def __init__(self, daddy=None):
        HIGMainWindow.__init__(self)

        self.daddy = daddy

        self.tip_timer = -1
        self.main_accel_group = gtk.AccelGroup()
        self.add_accel_group(self.main_accel_group)

        self.viewernb = HIGNotebook()

        self.invsearch = SearchDB(umitdb)
        self.invdb = ConnectInventoryDB(umitdb)
        self.invtree = InventoryTree(self)
        self.invnb = HIGNotebook()
        self.invnb_close_btn = startup_options()["tabs_close_btn"]
        self.invnbpages_titles = [ ]
        self.invnbpages_objects = [ ]

        # timeline tab
        self.timeline = TLHolder()

        # statusbars
        self.std_statusbar = gtk.Statusbar()
        self.std_sb = self.std_statusbar.get_context_id("stdbar")
        self._write_statusbar("                              ")

        self.tip_statusbar = gtk.Statusbar()
        self.tip_statusbar.set_has_resize_grip(False)
        self.tip_sb = self.tip_statusbar.get_context_id("tipbar")
        self.write_tips = startup_options()["tips"]

        # timer for checking updates
        self.db_stat = os.stat(umitdb).st_mtime
        self.schema_stat = os.stat(Path.sched_schemas).st_mtime
        self.timer_updater = gobject.timeout_add(4200, # nice number
            self.__check_for_updates)

        # gui scheduler controller
        self.schedctrl = SchedControl(self)


        self.inventories = self.invtree.fill_tree()
        self._create_ui_manager()
        self.__set_props()
        self.__do_layout()

        self.connect('inventory-activated', self._inventory_activated)
        self.connect('delete-event', self._exit_ni)
        self.connect('realize', self.on_realize)


    def on_realize(self, event):
        """
        After realizing, change to first page in main notebook (Historic page).
        """
        self.viewernb.set_current_page(0)


    def _close_current_hosttab(self, event):
        """
        Closes current active Host tab.
        """
        holder = self.invnb.get_nth_page(self.invnb.get_current_page())
        if holder:
            title = self.invnb.get_tab_label_text(holder)
            p = self.invnbpages_objects[self.invnbpages_titles.index(title)]

            if len(p.pages):
                tab_label = p.pages[p.get_current_page()]
                content = p.get_nth_page(p.get_current_page())
                p.remove_page(None, content, tab_label)


    def _close_current_invtab(self, event):
        """
        Closes current active inventory notebook.
        """
        holder = self.invnb.get_nth_page(self.invnb.get_current_page())
        if holder:
            label = self.invnb.get_tab_label_text(holder)
            del_index = self.invnbpages_titles.index(label)

            page = self.invnbpages_objects[del_index]
            for p in xrange(page.get_n_pages()-1):
                tab_label = page.pages[p]
                content = page.get_nth_page(p)
                page.remove_page(None, content, tab_label)
            self._delete_inventory_page()


    def _delete_inventory_page(self):
        """
        Removed last page from an Inventory notebook, now remove the Inventory
        notebook.
        """
        cur_page = self.invnb.get_current_page()
        page = self.invnb.get_nth_page(cur_page)
        page_label = self.invnb.get_tab_label_text(page)
        del_index = self.invnbpages_titles.index(page_label)
        del self.invnbpages_titles[del_index]
        del self.invnbpages_objects[del_index]

        self.invnb.remove_page(cur_page)


    def _inventory_activated(self, event, data):
        """
        Activated some item on Inventory tree.
        """
        if not data['host_addr']: # empty inventory was selected
            # clicked on Inventory title, dont do nothing
            return

        title = data["root"] # inventory name

        # check if activated inventory isnt open already
        if not title in self.invnbpages_titles:
            # create new notebook to hold this Inventory
            newinvnb = InventoryNB(self)
            self.invnb.append_page(newinvnb, gtk.Label(title))

            self.invnbpages_titles.append(title)
            self.invnbpages_objects.append(newinvnb)

            # check if a host was activated
            if data["host_addr"][0] != inventory_info:
                box = self._load_inventory_host_data(title,
                    data["host_addr"][1])
                newinvnb.append_host(data["host_addr"][0], box)
            else:
                # inventory info
                box = self._load_inventory_data(title)
                if box:
                    newinvnb.append_inv(box=box)

        else:
            # get Inventory notebook
            p = self.invnbpages_objects[self.invnbpages_titles.index(title)]

            # check if a host was activated
            if data["host_addr"][0] != inventory_info and \
                not p.page_exists(data["host_addr"]):
                box = self._load_inventory_host_data(title,
                    data["host_addr"][1])
                p.append_host(data["host_addr"][0], box)

            # if it is not a host, it was inventory info
            elif data["host_addr"][0] == inventory_info:
                box = self._load_inventory_data(title)
                if box:
                    p.append_inv(box=box)


    def _load_inventory_data(self, inventory_name):
        """
        Load data for activated Inventory.
        """
        fk_inventory = self.invdb.get_inventory_id_for_name(inventory_name)
        scans = self.invdb.get_scans_id_for_inventory(fk_inventory)
        last_scan_id = scans[len(scans)-1][0]
        hosts = self.invtree.invdata[inventory_name]

        box = gtk.VBox()

        # scan info
        hb = gtk.HBox()
        hb.pack_start(gtk.Label(_("Scan count:") + (" %d" % len(scans))),
                False, False, 0)
        box.pack_start(hb, False, False, 0)

        hb = gtk.HBox()
        last_scan_date = self.invdb.get_finish_timestamp_for_scan_from_db(
                last_scan_id)
        hb.pack_start(
                gtk.Label(_("Last scan date:") + (" %s" % last_scan_date)),
                False, False, 0)
        box.pack_start(hb, False, False, 0)

        details = self.invdb.get_scan_details_for_scan_from_db(scans[0][0])
        detc = [
            _("Scan args"), _("XML output version"), _("Verbose"),
            _("Debugging"), _("Scanner name"), _("Scanner version")
            ]
        for indx, item in enumerate(details):
            hb = gtk.HBox()
            hb.pack_start(gtk.Label("%s: %s" % (detc[indx], item)), False,
                False, 0)
            box.pack_start(hb, False, False, 0)

        # "separator"
        box.pack_start(gtk.HSeparator(), False, False, 6)

        # hosts info
        hb = gtk.HBox()
        hb.pack_start(gtk.Label(
            _("Hosts: ") +
            ', '.join([host[0] for host in hosts])), False, False, 0)
        box.pack_start(hb, False, False, 0)

        hb = gtk.HBox()
        hb.pack_start(gtk.Label(_("Host count:") + (" %s" % len(hosts))),
                False, False, 0)
        box.pack_start(hb, False, False, 0)

        sw = gtk.ScrolledWindow()
        sw.add_with_viewport(box)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.show_all()

        return sw


    def _load_inventory_host_data(self, inventory_name, host_addr):
        """
        Load data for a host in an inventory.
        """
        changesd = ChangesDiff(self.invdb)
        changesl = ChangesList(self, self.invdb, changesd,
            data={-1: (inventory_name, host_addr)})

        paned = gtk.VPaned()
        paned.add1(changesl)
        paned.add2(changesd)

        return paned


    def _write_statusbar(self, msg):
        """
        Write some message at standard statusbar.
        """
        self.std_statusbar.pop(self.std_sb)
        self.std_statusbar.push(self.std_sb, msg)


    def _clear_statusbar(self):
        """
        Clear standard statusbar.
        """
        self.std_statusbar.pop(self.std_sb)


    def _write_statusbar_tip(self, tipmsg, timeout=True):
        """
        Write a tip at statusbar.
        """
        if not self.write_tips:
            # tips disabled
            return

        if not self.window: # widget being destroyed
            gobject.source_remove(self.tip_timer)
            return

        self.tip_statusbar.pop(self.tip_sb)
        self.tip_statusbar.push(self.tip_sb, tipmsg)

        if self.tip_timer != -1:
            gobject.source_remove(self.tip_timer)

        if timeout:
            # remove tip after 15 seconds
            self.tip_timer = gobject.timeout_add(15000,
                self._clear_tip_statusbar)


    def _clear_tip_statusbar(self):
        """
        Clear statusbar.
        """
        self.tip_statusbar.pop(self.tip_sb)
        gobject.source_remove(self.tip_timer)
        self.tip_timer = -1

        return False


    def _update_viewer(self):
        """
        Call this when needed to update Network Inventory Viewer.
        """
        inventories = self.invtree.fill_tree()

        # update Edit Inventories menu
        new_inventories = set(inventories).difference(set(self.inventories))
        self.inventories = inventories

        for inv in new_inventories:
            self.main_action_group.add_actions([("_" + inv, None, inv,
                None, inv, self._edit_inventory)])

            self.ui_manager.add_ui(self.ui_manager.new_merge_id(),
                "/menubar/Edit/Inventory", inv, "_" + inv, "menuitem", False)


    def _build_results_view(self, query, returned, buildnow=False):
        """
        Build a TreeView with returned results from search or perform search
        and then Build TreeView.
        """
        def close_page(widget, data):
            """
            Close search page.
            """
            page_num = self.viewernb.page_num(data)
            self.viewernb.remove_page(page_num)


        def row_activated(tv, path, tvcolumn):
            """
            Activated some row in results treeview.
            """
            # create page at "Inventory"
            model = tv.get_model()
            tv_iter = model.get_iter(path)
            host_addr = model.get_value(tv_iter, 1)

            data = { }
            root = model[path[0]][0]
            data["root"] = root
            data["host_addr"] = (host_addr, host_addr) # new format

            self.emit('inventory-activated', data)

            # write tip to statusbar
            self._write_statusbar_tip(_("A page was open at Historic tab!"))


        def buildtv(*args):
            """
            Build treeview and append results.
            """
            lsmodel = gtk.ListStore(str, str, str, str)
            tview = gtk.TreeView(lsmodel)
            columns = 4
            columns_text = (
                _("Inventory"), _("Host"),
                _("First Matched Category"), _("Entry Date")
                )
            tview.columns = [None]*columns

            for n in range(columns):
                tview.columns[n] = gtk.TreeViewColumn(columns_text[n])
                tview.columns[n].cell = gtk.CellRendererText()
                tview.columns[n].pack_start(tview.columns[n].cell, True)
                tview.columns[n].set_attributes(tview.columns[n].cell, text=n)

                tview.append_column(tview.columns[n])

            tview.connect('row-activated', row_activated)

            # layout
            matches = len(args[1])
            word = append_s(_("result"), matches)
            upper_title = gtk.Label()
            upper_title.set_markup(
                    ("<b>%d " % matches) + word + _(" found.") +
                    "</b>")
            hutbox = HIGHBox()
            hutbox._pack_noexpand_nofill(upper_title)
            sw = HIGScrolledWindow()
            sw.add(tview)
            vbox = gtk.VBox()
            vbox.pack_start(hutbox, False, False, 3)
            vbox.pack_start(sw, True, True, 0)

            vbox.show_all()

            # append results to treeview
            results = args[1]

            for res, date in results.items():
                invname = self.invdb.get_inventory_name_for_id(res[0])
                lsmodel.append((invname, res[1], res[2], str(date)))

            title = _("Search: %s") % args[0]
            tab_label = HIGAnimatedTabLabel(title)
            tab_label.connect("close-clicked", close_page, vbox)
            self.viewernb.append_page(vbox, tab_label)


        if buildnow:
            # uhm.. nice, we already have the results.
            buildtv(query, returned)

        else:
            # no results yet, will get them now!
            host_matches = { }

            for key, values in returned.items():
                host_id = key
                inv_id = values[0]
                host_addr = values[1]
                date = values[2]
                res = self.invsearch.search(host_id, query)
                if res: # res = category returned
                    host_matches[(inv_id, host_addr, res)] = date

            # build treeview now
            buildtv(query, host_matches)


    def _create_ui_manager(self):
        """
        Set up user interface.
        """
        self.ui_manager = gtk.UIManager()
        self.main_action_group = gtk.ActionGroup("MainActionGroup")

        about_icon = None
        try: about_icon = gtk.STOCK_ABOUT
        except: pass

        main_actions = [ \
            ("File", None, _("_File"), None),
            ("Edit", None, _("_Edit"), None),
            ("Scheduler", None, _("_Scheduler"), None),
            ("Help", None, _("_Help"), None),

            ("ToolbarOpt", None, _("Tool_bar"), None),
            ("InvTabs", None, _("Devices _tab"), None),
            ("Inventory", None, _("_Inventories"), None),

            # File
            ("New",
             gtk.STOCK_NEW, _("_New Inventory"),
             None, _("Create new Inventory"),
             self._create_new),

            ("CloseHostTab",
             None, _("Close Device tab"),
             "<Control>W", _("Close current host tab"),
             self._close_current_hosttab),

            ("CloseInvTab",
             None, _("Close Inventory tab"),
             "<Shift><Control>W", _("Close current Inventory tab"),
             self._close_current_invtab),

            ("Quit",
             gtk.STOCK_QUIT, _("_Quit"),
             None, _("Close Network Inventory"),
             self._exit_ni),

            # Edit
            ('Control Data Removal',
             None, _("Data Removal"),
             None, _("Data Removal"),
             self._edit_data_removal),

            ('Startup',
             None, _("Startup settings"),
             None, _("Startup settings"),
             self._edit_startup),

            # Scheduler
            # Scheduler log
            ('Sched Log',
             None, _("Scheduler log"),
             None, _("View Scheduler log"),
             self._open_sched_log),

            # Scheduler status
            ('Sched Control',
             self.schedctrl.stock_icon, self.schedctrl.status_text,
             None, self.schedctrl.status_text,
             self.schedctrl._scheduler_control),

            # Help
            ('Show Help',
             gtk.STOCK_HELP, _('_Help'),
             None, _('Shows the application help'),
             self._show_help),

            ('Report a bug',
             gtk.STOCK_DIALOG_INFO, _('_Report a bug'),
             '<Control>b', _("Report a bug"),
             self._show_bug_report),

            ('About',
             about_icon, _("_About"),
             '<Control>a', _("About UMIT Network Inventory"),
             self._show_about)

        ]

        toggle_actions = [
            # Edit
            ("ShowTips",
             None, _("Show ti_ps"),
             None, _("Enable disable tip showing"),
             lambda c: self.set_write_tips(not self.write_tips),
             self.write_tips),

            # Edit/Notebooks
            ("TabCloseBtn",
             None, _("Place close button"),
             None, _("Place a close button upon tab creation"),
             lambda c: self.set_invnb_cbtn(not self.invnb_close_btn),
             self.invnb_close_btn)
        ]

        default_ui = """
            <menubar>
                <menu action='File'>
                    <menuitem action='New' />
                    <separator />
                    <menuitem action='CloseHostTab' />
                    <menuitem action='CloseInvTab' />
                    <menuitem action='Quit' />
                </menu>
                <menu action='Edit'>
                    <menu action='InvTabs'>
                         <menuitem action='TabCloseBtn' />
                    </menu>
                    <menu action='Inventory'>
                    </menu>
                    <menuitem action='ShowTips' />
                    <menuitem action='Control Data Removal' />
                    <menuitem action='Startup' />
                </menu>
                <menu action='Scheduler'>
                    <menuitem action='Sched Log' />
                    <menuitem action='Sched Control' />
                </menu>
                <menu action='Help'>
                    <menuitem action='Show Help' />
                    <menuitem action='Report a bug' />
                    <menuitem action='About' />
                </menu>
            </menubar>
            <toolbar>
                <toolitem action='Sched Control' />
                <separator />
            </toolbar>
            """

        self.main_action_group.add_actions(main_actions)
        self.main_action_group.add_toggle_actions(toggle_actions)

        for action in self.main_action_group.list_actions():
            action.set_accel_group(self.main_accel_group)
            action.connect_accelerator()

        self.ui_manager.insert_action_group(self.main_action_group, 0)
        self.ui_manager.add_ui_from_string(default_ui)

        self.schedctrl.ui_action = self.main_action_group.get_action(
            'Sched Control')

        # add Inventories to edit menu
        for inv in self.inventories:
            self.main_action_group.add_actions([("_" + inv, None, inv,
                None, inv, self._edit_inventory)])

            self.ui_manager.add_ui(self.ui_manager.new_merge_id(),
                "/menubar/Edit/Inventory", inv, "_" + inv, "menuitem", False)


    def _edit_data_removal(self, event):
        """
        Open window for editing data removal for Inventories.
        """
        w = ConfigureDataRemoval()
        w.show_all()


    def _edit_inventory(self, event):
        """
        Open inventory for editing.
        """
        try:
            w = NewInventory(event.get_name()[1:], edit_mode=True)
        except NoInventory:
            return
        w.show_all()


    def _create_new(self, event):
        """
        Open dialog for creating New Inventory.
        """
        w = NewInventory()
        w.show_all()


    def _open_sched_log(self, event):
        """
        Open scheduler log.
        """
        winlog = SchedLog()
        winlog.show_all()


    def _edit_startup(self, event):
        """
        Open window for editing startup settings.
        """
        settwin = NISettings()
        settwin.show_all()


    def _show_help(self, event):
        """
        Open help manual.
        """
        show_help(self,"index.html")


    def _show_bug_report(self, event):
        """
        Open bug report window.
        """
        bug = BugReport()
        bug.show_all()


    def _show_about(self, event):
        """
        Open about window.
        """
        awin = About()
        awin.show_all()


    def _exit_ni(self, *args):
        """
        Do necessary cleanup before destroying window.
        """
        # remove tip timer if still running
        if self.tip_timer != -1:
            gobject.source_remove(self.tip_timer)
            self._clear_tip_statusbar()

        # stop updater timer
        gobject.source_remove(self.timer_updater)

        self.hide()

        # remove old data
        if get_decays()[1]:
            win = RemoveOldData()
            win.show_all()
            win.connect('destroy', self.__leave_ni)
        else:
            self.__leave_ni()


    def __leave_ni(self, *args):
        """
        If you are here, Network Inventory has been cleanedup succesfully.
        """
        if self.daddy:
            self.daddy.running_ni = False
            self.destroy()
        else:
            gtk.main_quit()


    def __check_for_updates(self):
        """
        Check for some possible visual update needed to be done.
        """
        do_update = False

        # check for database changes
        prev_stat = self.db_stat
        try:
            possibly_new = os.stat(umitdb).st_mtime
        except OSError:
            return True

        if prev_stat != possibly_new:
            do_update = True
            self.db_stat = possibly_new

        # check for changes in schemas
        prev_state = self.schema_stat
        try:
            possibly_new = os.stat(Path.sched_schemas).st_mtime
        except OSError:
            return True

        if prev_state != possibly_new:
            do_update = True
            self.schema_stat = possibly_new


        if do_update:
            self._update_viewer()

        return True


    def __set_props(self):
        """
        Set window properties.
        """
        self.set_title(_("UMIT Network Inventory"))
        self.invnb.set_scrollable(True)
        self.viewernb.set_scrollable(True)
        # a size for testing
        self.set_position(gtk.WIN_POS_CENTER)
        width, height = gtk.gdk.get_default_root_window().get_size()
        self.set_default_size((width * 3) / 4, (height * 3) / 4)


    def __do_layout(self):
        """
        Layout window widgets.
        """
        main_vbox = gtk.VBox()
        main_hpaned = gtk.HPaned()
        nb_tl_hpaned = gtk.HPaned()

        menubar = self.ui_manager.get_widget('/menubar')
        main_vbox.pack_start(menubar, False, False, 0)

        schedbar = self.ui_manager.get_widget('/toolbar')
        schedbar.set_show_arrow(False)
        schedbar.set_style(gtk.TOOLBAR_ICONS)
        toolbar = SearchBar(self, self.invdb)

        toolbar_box = gtk.HBox()
        toolbar_box.pack_start(schedbar, False, False, 0)
        toolbar_box.pack_start(toolbar, True, True, 0)
        main_vbox.pack_start(toolbar_box, False, False, 0)

        left_pane_box = gtk.VBox()
        left_pane_box.pack_start(self.invtree, True, True, 0)

        main_hpaned.add1(left_pane_box)
        main_hpaned.add2(nb_tl_hpaned)

        # inventories notebook
        nb_tl_hpaned.pack1(self.invnb, True, False)

        self.viewernb.append_page(main_hpaned, gtk.Label(_(" Historic ")))
        self.viewernb.append_page(self.timeline, gtk.Label(_(" Timeline ")))

        self.timeline.show_all()

        main_vbox.pack_start(self.viewernb, True, True, 0)

        sbs_box = gtk.HBox()
        sbs_box.add(self.tip_statusbar)
        sbs_box.add(self.std_statusbar)
        main_vbox.pack_end(sbs_box, False, False, 0)

        self.add(main_vbox)


    def get_write_tips(self):
        """
        Returns True if tips should be written at statusbar, otherwise, False.
        """
        return self.__wtips


    def set_write_tips(self, write):
        """
        Sets to write tips or not at statusbar.
        """
        self.__wtips = write
        if not self.write_tips:
            self.tip_statusbar.pop(self.tip_sb)


    def get_invnb_cbtn(self):
        """
        Returns True if Inventory tabs have a close button placed on them.
        """
        return self.__invcbtn


    def set_invnb_cbtn(self, enable):
        """
        Sets to show or not close button in each Inventory tab.
        """
        self.__invcbtn = enable


    # Properties
    write_tips = property(get_write_tips, set_write_tips)
    invnb_close_btn = property(get_invnb_cbtn, set_invnb_cbtn)


gobject.signal_new("inventory-activated", InventoryViewer,
                   gobject.SIGNAL_RUN_LAST,
                   gobject.TYPE_NONE,
                   (gobject.TYPE_PYOBJECT,))
