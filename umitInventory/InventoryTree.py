# Copyright (C) 2007 Insecure.Com LLC.
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
Inventory Tree
"""

import gtk
import gobject
import traceback
from ConfigParser import ConfigParser, NoSectionError

from umitDB.XMLStore import XMLStore
from umitCore.Paths import Path
from umitCore.I18N import _
from umitCore.NmapCommand import NmapCommand
from umitGUI.GenericAlertDialogs import GenericAlert
from umitGUI.Icons import get_os_icon

from umitInventory.NewInventory import NewInventory
from umitInventory.InventoryLoad import InventoryLoad
from umitInventory.InventoryCommonDialog import NoScheduleDlg

INVENTORY_INFO = _("Info")
(IPV4, IPV6, MAC, HOSTNAME) = range(4)
SHOW_BY = _("IPv4"), _("IPv6"), _("MAC"), _("Hostname")

class InventoryTree(gtk.Notebook):
    """
    A Notebook that holds a ScrolledWindow that holds a TreeView that holds
    all inventories in database.
    """

    def __init__(self, daddy, title=_("My Inventories")):
        gtk.Notebook.__init__(self)

        self.daddy = daddy
        self.running_scans = { }
        self.scans_timer = -1
        self.invdataload = InventoryLoad()
        self.invdata = None
        self.show_hosts_by = HOSTNAME
        # the following dict will have a format like this when data loads:
        # {inventoryname: {somedisplay:someip_or_info, ...}, ...}
        # it is a way to make a relation between what is been displayed and
        # its correspondent ipv4 in database. This is used to display
        # hostnames instead of ipv4 address for example.
        self.show_related_to = { }

        self.tooltips = gtk.Tooltips()
        self.control_title = gtk.Label(_("%s (0)" % title))
        self.treestore = gtk.TreeStore(gtk.gdk.Pixbuf, str)
        self.treeview = gtk.TreeView(self.treestore)
        self.tcolumn = gtk.TreeViewColumn(_("%s (0)" % title))

        # icon
        render_pixbuf = gtk.CellRendererPixbuf()
        self.tcolumn.pack_start(render_pixbuf, expand=False)
        self.tcolumn.add_attribute(render_pixbuf, 'pixbuf', 0)
        #self.tcolumn.add_attribute(render_pixbuf, 'pixbuf-expander-closed', 0)
        #self.tcolumn.add_attribute(render_pixbuf, 'pixbuf-expander-open', 1)

        # inventory/host/info names
        render_text = gtk.CellRendererText()
        self.tcolumn.pack_start(render_text, expand=True)
        self.tcolumn.add_attribute(render_text, 'text', 1)

        self.treeview.append_column(self.tcolumn)

        self.treeview.connect('row-activated', self._row_activated)
        self.treeview.connect('button-press-event', self._row_clicked)

        self.__set_props()
        self.__do_layout()


    def set_title(self, title):
        """
        Set new title.
        """
        self.tcolumn.set_title(title)
        self.control_title.set_label(title)


    def set_show_hosts_by(self, event, opt):
        """
        Set new way to show hosts.
        """
        if event and not event.get_active():
            return

        self.show_hosts_by = opt
        self.fill_tree()


    def expand_tree(self, event):
        """
        Expand tree.
        """
        self.treeview.expand_all()


    def collapse_tree(self, event):
        """
        Collapse tree.
        """
        self.treeview.collapse_all()


    def fill_tree(self):
        """
        Fill inventory tree list and return the inventories that filled it.
        """
        self.invdata = self.invdataload.load_from_db()

        # need to clean these because tree is refilled several times.
        tr = self.treestore
        tr.clear()
        self.show_related_to = { }

        invs = [ ] # temporary place for inventory names
        for inventory, addrs in self.invdata.items():
            invs.append(inventory)

            root = tr.append(None, [self.render_icon("root_inventory",
                gtk.ICON_SIZE_MENU), '%s' % inventory])

            relations = { }
            if addrs:
                tr.append(root, [self.render_icon(
                    gtk.STOCK_INFO, gtk.ICON_SIZE_MENU), INVENTORY_INFO])
                relations[INVENTORY_INFO] = INVENTORY_INFO

            for addr in addrs: # append hosts to the tree
                # addr[4] holds os short text for current host

                append_now = addr[0] # fallback to ipv4 in case something else
                                     # is selected but not present

                if self.show_hosts_by == HOSTNAME: # default mode
                    if addr[3]: # check for hosts existance
                        append_now = addr[3][0] # show first hostname

                elif self.show_hosts_by == IPV6:
                    if addr[1]: # check for ipv6 existance
                        append_now = addr[1]

                elif self.show_hosts_by == MAC:
                    if addr[2]: # check for ipv6 existance
                        append_now =  addr[2]

                if len(append_now) > 21:
                    append_now = append_now[:20] + '..'

                relations[append_now] = addr[0]
                tr.append(root, [self.render_icon(
                    get_os_icon(addr[4]), gtk.ICON_SIZE_MENU), append_now])

            self.show_related_to[inventory] = relations

        self.set_title(_("My Inventories (%d)" % len(tr)))
        self.treeview.expand_all()

        return invs


    def _edit_inv(self, widget, inv):
        """
        Open Inventory for editing.
        """
        # checking for inventory existance in schemas file.
        schemas = ConfigParser()
        schemas.read(Path.sched_schemas)

        if not schemas.has_section(inv):
            dlg = NoScheduleDlg()
            dlg.run()
            dlg.destroy()
            return

        w = NewInventory(inv, edit_mode=True)
        w.show_all()


    def _get_command_from_schemas(self, inventory):
        """
        Get scan command from schemas profiles.
        """
        schemas = ConfigParser()
        schemas.read(Path.sched_schemas)

        try:
            scan_args = schemas.get(inventory, "command")
            return scan_args

        except NoSectionError, err:
            dlg = GenericAlert(_("Scan will not run!"),
                _("You tried running scan for Inventory '%s',"
                "\nbut it has no data in Scheduler schemas file, neither in "
                "database.\n\nError returned: %s" % (inventory, err)),
                    buttons={1: (gtk.RESPONSE_OK, gtk.STOCK_OK)})
            dlg.run()
            dlg.destroy()


    def _run_inv_scan(self, widget, inv):
        """
        Run Inventory scan.
        """
        if self.daddy:
            inv_id = self.daddy.invdb.get_inventory_id_for_name(inv)
            if not inv_id:

                scan_args = self._get_command_from_schemas(inv)
                if not scan_args:
                    return

            else:
                scan_args = (
                    self.daddy.invdb.get_scan_args_for_inventory_id(inv_id))
                if not scan_args:
                    scan_args = self._get_command_from_schemas(inv)
                    if not scan_args:
                        return


            scan = NmapCommand(scan_args)
            scan.run_scan()

            if not self.running_scans:
                # no scans running, start timer for checking if some scan
                # finished
                self.scans_timer = gobject.timeout_add(4200, self._check_scans)

            self.running_scans[scan] = inv
            running_scans = len(self.running_scans)
            self.daddy._write_statusbar(_("%d scan%s running" % (running_scans,
                running_scans > 1 and 's' or '')))


    def _check_scans(self):
        """
        Check for finished scans.
        """
        todelete = [ ]

        for scan, inventory in self.running_scans.items():
            try:
                scan_state = scan.scan_state()
            except Exception, err:
                # scan failed to run.
                # probably a scan with args that requires root and a
                # normal user tried running.
                dlg = GenericAlert(_("Scan failed to run!"),
                    _("You tried running scan for Inventory '%s',"
                    "\nbut it returned the following:\n\n%s" % (
                        inventory, err)), buttons={1: (gtk.RESPONSE_OK,
                        gtk.STOCK_OK)})
                dlg.run()
                dlg.destroy()
                todelete.append(scan)
                continue

            if not scan_state: # scan finished
                xmlstore = XMLStore(Path.umitdb_ng)
                try:
                    xmlstore.store(scan.get_xml_output_file(),
                            inventory=inventory)
                except Exception:
                    # failed while adding scan to the database
                    dlg = GenericAlert(_("Database couldn't be updated!"),
                            _("The scan for the Inventory %r finished but "
                                "its results couldn't be added to the "
                                "database.\n\n%s" % (inventory,
                                    traceback.format_exc())),
                                buttons={1: (gtk.RESPONSE_OK, gtk.STOCK_OK)})
                    dlg.run()
                    dlg.destroy()
                finally:
                    xmlstore.close() # close connection to the database
                    scan.close()
                    todelete.append(scan)

        for td in todelete: # remove finished scans from running_scans
            del self.running_scans[td]

        running_scans = len(self.running_scans)
        self.daddy._write_statusbar(_("%d scan%s running" % (running_scans,
            running_scans > 1 and 's' or '')))

        if not self.running_scans:
            # all scans completed
            self.daddy._clear_statusbar()
            self.scans_timer = -1
            return False # stop timer

        return True


    def _notebook_controls(self, title):
        """
        Build a "label" for using as notebook title with some controls.
        """
        def where_to_popup(menu, button):
            """
            Calculates position to popup menu.
            """
            winx, winy = self.window.get_position()

            btn_alloc = button.get_allocation()
            btnx, btny = (btn_alloc[0], btn_alloc[1] + btn_alloc[3])

            return (winx + btnx, winy + btny, True)


        def popup_opts_menu(widget):
            """
            Create a popup menu and show it.
            """
            # options menu
            opts_menu = gtk.Menu()

            opt_item = gtk.MenuItem(_("Expand All"))
            opt_item.connect('activate', self.expand_tree)
            opts_menu.add(opt_item)

            opt_item = gtk.MenuItem(_("Collapse All"))
            opt_item.connect('activate', self.collapse_tree)
            opts_menu.add(opt_item)

            opts_menu.add(gtk.SeparatorMenuItem())

            radiogroup = gtk.RadioMenuItem(None, _("View by %s" % SHOW_BY[3]))
            if self.show_hosts_by == 3:
                radiogroup.set_active(True)
            radiogroup.connect('toggled', self.set_show_hosts_by, 3)

            for indx, showby in enumerate(SHOW_BY):
                if indx == 3: # hostnames
                    opts_menu.add(radiogroup)
                else:
                    opt_item = gtk.RadioMenuItem(radiogroup,
                        _("View by %s" % showby))

                    if self.show_hosts_by == indx:
                        opt_item.set_active(True)

                    opt_item.connect('toggled', self.set_show_hosts_by, indx)
                    opts_menu.add(opt_item)

            opts_menu.show_all()
            opts_menu.popup(None, None, where_to_popup, 1, 0, widget)


        self.set_title(title)

        opts_btn = gtk.Button()
        opts_btn.set_relief(gtk.RELIEF_NONE)
        opts_btn.connect('clicked', popup_opts_menu)

        opts_box = gtk.HBox()
        opts_box.pack_start(self.control_title, False, False, 0)
        opts_box.pack_start(gtk.Label("  "), False, False, 0)
        opts_box.pack_start(gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_OUT), False,
            False, 0)
        opts_btn.add(opts_box)
        opts_btn.show_all()

        return opts_btn


    def _make_popup(self, btn, evt_time, inv, host):
        """
        Make a popup menu and.. popup it ;)
        """
        menu = gtk.Menu()
        item = gtk.MenuItem(_("Edit %s") % inv)
        item.connect('activate', self._edit_inv, inv)
        menu.append(item)
        item = gtk.MenuItem(_("Run scan now"))
        item.connect('activate', self._run_inv_scan, inv)
        menu.append(item)
        menu.show_all()
        menu.popup(None, None, None, btn, evt_time)


    def _row_activated(self, tv, path, tvcolumn):
        """
        Some row in tree was activated.
        """
        data = { }
        root = self.treestore[path[0]][1]
        data["root"] = root

        if len(path) > 1:
            # activated a host or inventory_info
            model = self.treeview.get_model()
            tv_iter = model.get_iter(path)
            content = model.get_value(tv_iter, 1)

            data["host_addr"] = (content,
                self.show_related_to[data["root"]][content])

        else:
            # activated an inventory, expand or collapse it
            if self.treeview.row_expanded(path):
                self.treeview.collapse_row(path)
            else:
                self.treeview.expand_row(path, False)

            data["host_addr"] = None

        self.daddy.emit('inventory-activated', data)


    def _row_clicked(self, tv, event):
        """
        Clicked on treeview, in a row or not.
        """
        if event.button in (1, 3): # left/right click
            x = int(event.x)
            y = int(event.y)

            try:
                path, col, xpos, ypos = tv.get_path_at_pos(x, y)
            except TypeError:
                return

            if not path:
                # didn't click in a row.
                return

            tv.grab_focus()
            selection = tv.get_selection()
            if not selection.path_is_selected(path):
                tv.set_cursor(path, col, 0)

            inventory = self.treestore[path[0]][1]
            content = self.treestore[path][1]

            if event.button == 3: # right button, show a popup with options
                self._make_popup(event.button, event.time, inventory, content)
                return

            # left click if we are still here
            data = { }
            data["root"] = inventory

            if len(path) > 1:
                data["host_addr"] = (content,
                    self.show_related_to[data["root"]][content])

            else:
                text_start = tv.get_cell_area(path, col)[0]
                if x >= text_start:
                    # activated an inventory, expand or collapse it
                    if tv.row_expanded(path):
                        tv.collapse_row(path)
                    else:
                        tv.expand_row(path, False)

                data["host_addr"] = None

            self.daddy.emit('inventory-activated', data)


    def __set_props(self):
        """
        InventoryTree widgets properties.
        """
        self.treeview.set_headers_visible(False)


    def __do_layout(self):
        """
        Layout InventoryTree.
        """
        scrollw = gtk.ScrolledWindow()
        scrollw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrollw.add_with_viewport(self.treeview)
        scrollw.set_size_request(200, -1)

        controls = self._notebook_controls(self.tcolumn.get_title())

        self.append_page(scrollw, controls)
        self.show_all()
