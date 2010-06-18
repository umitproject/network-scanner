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
Changes Display for Network Inventory.
"""

import gtk

from umit.core.I18N import _

from umit.gui.DiffCompare import Colors
from umit.gui.DiffCompare import DiffLegendWindow

EMPTY = _("Nothing being shown.")
NA = _("Not Available")

diff_columns = (
    _("Status"), _("Section"), _("Property"),
    _("Previous value"), _("Current value")
    )

class ChangesDiff(gtk.VBox):
    """
    Shows differences between two host ids.
    """

    def __init__(self, invdb):
        gtk.VBox.__init__(self)

        self.invdb = invdb
        self.colors = Colors()

        # header
        self.top_title = gtk.Label()
        self.top_title.set_markup("<b>%s</b>" % EMPTY)
        self.legend_btn = gtk.Button(_("L"))
        self.legend_btn.connect('clicked', self._open_legend_dlg)

        self.diff_tree = gtk.TreeStore(str, str, str, str, str, str)
        self.diff_view = gtk.TreeView(self.diff_tree)

        self._setup_diff_view()
        self.__layout()


    def search_column(self, widget, column_id):
        """
        Change treeview search column.
        """
        self.diff_view.set_search_column(column_id)


    def clear_diff_tree(self):
        """
        Clear treestore.
        """
        self.diff_tree.clear()


    def header_setup(self, title, title2, date, opt):
        """
        Set new header.
        """
        if opt == 0:
            title_text = ("<b>Comparison for %s against last succesful "
                "scan in %s @ %s</b>") # better to break this in two lines ?
        elif opt == 1:
            title_text = "<b>Host %s added in %s @ %s</b>"
        elif opt == 2:
            title_text = "<b>No data for %s in %s @ %s</b>"

        self.top_title.set_markup(title_text % (title, title2, date))


    def header_comparison(self, title, title2, date):
        """
        Set a new comparison header.
        """
        self.header_setup(title, title2, date, 0)


    def header_newhost(self, title, title2, date):
        """
        Set header for new host in inventory.
        """
        self.header_setup(title, title2, date, 1)


    def header_empty(self, title, title2, date):
        """
        Set header for no data.
        """
        self.header_setup(title, title2, date, 2)


    def show_empty_hostid(self):
        """
        Fill DiffTree with nothing at all.
        """
        self.clear_diff_tree()

        status = "Not_present"

        self.diff_tree.append(None, [status[0], _("No data"),
            _("No data available for this host on this date"),
            NA, NA, self.colors.get_hex_color(status[0])])


    def make_diff(self, hostid_new, hostid_old):
        """
        Fill DiffTree showing differences between hostid_new and hostid_old.
        """
        self.clear_diff_tree()

        do_diff = True

        if hostid_old == hostid_new:
            # no diff to show, just show host data for hostid
            do_diff = False

        (ports_n, ep_n, uptime_n, tcp_seq_n,
        tcp_ts_seq_n, ip_id_seq_n,
        osclasses_n, osmatch_n) = self.get_data_for_host_from_db(hostid_new)

        if not do_diff:
            (ports_o, ep_o, uptime_o, tcp_seq_o,
            tcp_ts_seq_o, ip_id_seq_o,
            osclasses_o, osmatch_o) = (ports_n, ep_n, uptime_n, tcp_seq_n,
            tcp_ts_seq_n, ip_id_seq_n, osclasses_n, osmatch_n)
        else:
            (ports_o, ep_o, uptime_o, tcp_seq_o,
            tcp_ts_seq_o, ip_id_seq_o,
            osclasses_o, osmatch_o) = self.get_data_for_host_from_db(hostid_old)
            

        # ports diff
        if self.__verify_if_available([ports_o, ports_n]):
            self.port_diff(ports_o, ports_n, do_diff)

        # Extraports
        if self.__verify_if_available([ep_o, ep_n]):
            self.extraports_diff(ep_o, ep_n, do_diff)

        # Fingerprint
        diff_fingerprint = [uptime_o, uptime_n, tcp_seq_o, tcp_seq_n,
                                  tcp_ts_seq_o, tcp_ts_seq_n, ip_id_seq_o, 
                                  ip_id_seq_n]
        if self.__verify_if_available(diff_fingerprint):
            self.fingerprint_diff(uptime_o, uptime_n, tcp_seq_o, tcp_seq_n,
                                  tcp_ts_seq_o, tcp_ts_seq_n, ip_id_seq_o, 
                                  ip_id_seq_n, do_diff)

        # OS Classes
        if self.__verify_if_available([osclasses_o, osclasses_n]):
            self.osclasses_diff(osclasses_o, osclasses_n, do_diff)

        # OS Match
        if self.__verify_if_available([osmatch_o, osmatch_n]):
            self.osmatch_diff(osmatch_o, osmatch_n, do_diff)


    def port_diff(self, old, new, diff=True):
        """
        Do port diff.
        """
        if not diff:
            status = "Added"
            old = new
        elif old != new:
            status = "Modified"
        else:
            status = "Unchanged"

        r = self.diff_tree.append(None, [status[0], _("Ports"), "", "", "",
            self.colors.get_hex_color(status[0])])

        for key, values in old.items():
            if diff and not key in new:
                closed_now = True
            else:
                closed_now = False

            if closed_now:
                status = "Not_present"
            else:
                if not diff:
                    status = "Added"
                elif new[key] != old[key]:
                    status = "Modified"
                else:
                    status = "Unchanged"

            pr = self.diff_tree.append(r, [status[0],
                _("Port") + (" %d" % key), "",
                "", "", self.colors.get_hex_color(status[0])])

            for k, v in values.items():
                if not closed_now:
                    new_value = new[key][k]

                    if not v and not new_value:
                        continue

                    if not diff:
                        status = "Added"
                        v = ""
                    elif v != new[key][k]:
                        status = "Modified"
                    else:
                        status = "Unchanged"

                    self.diff_tree.append(pr, [status[0], "", k, v, new_value,
                        self.colors.get_hex_color(status[0])])

                else:
                    status = "Not_present"
                    if v:
                        self.diff_tree.append(pr, [status[0], "", k, v, "",
                            self.colors.get_hex_color(status[0])])

        if not diff:
            # Job is complete here if diff=False
            return

        # check for ports only in new data.
        for key, values in new.items():
            if key in old:
                continue

            status = "Added"

            pr = self.diff_tree.append(r, [status[0],
                _("Port") + (" %d" % key), "",
                "", "", self.colors.get_hex_color(status[0])])
            for k, v in values.items():
                if v:
                    self.diff_tree.append(pr, [status[0], "", k, "", v,
                        self.colors.get_hex_color(status[0])])


    def extraports_diff(self, ep_o, ep_n, diff=True):
        """
        Do extraports diff.
        """
        if not diff:
            status = "Added"
            ep_o = ep_n
        elif ep_o != ep_n:
            status = "Modified"
        else:
            status = "Unchanged"

        r = self.diff_tree.append(None, [status[0], _("Extraports"), "", "",
            "", self.colors.get_hex_color(status[0])])

        for key, values in ep_o.items():
            if key in ep_n:
                new_value = ep_n[key]
            else:
                new_value = NA

            d_temp = {_('count'): values}
            dn_temp = {_('count'): new_value}
            self.std_diff(d_temp, dn_temp, key, diff, r)

        if not diff:
            # Job is complete here if diff=False
            return

        for key, values in ep_n.items():
            if key in ep_o:
                continue

            d_temp = {_('count'): values}
            self.std_diff(d_temp, d_temp, key, False, r)


    def fingerprint_diff(self, up_old, up_new, ts_old, ts_new, tts_old,
        tts_new, iis_old, iis_new, diff=True):
        """
        Do fingerprint diff.
        """
        
        if not diff:
            status = "Added"
        elif (up_old != up_new) or (ts_old != ts_new) or (tts_old != tts_new) \
            or (iis_old != iis_new):
            status = "Modified"
        else:
            status = "Unchanged"

        r = self.diff_tree.append(None, [status[0], _("Fingerprint"), "", "",
            "", self.colors.get_hex_color(status[0])])
        # Uptime
        self.std_diff(up_old, up_new, _("Uptime"), diff, r)

        # TCP Sequence
        self.std_diff(ts_old, ts_new, _("TCP Sequence"), diff, r)

        # TCP TS Sequence
        self.std_diff(tts_old, tts_new, _("TCP TS Sequence"), diff, r)

        # IP ID Sequence
        self.std_diff(iis_old, iis_new, _("IP ID Sequence"), diff, r)


    def osclasses_diff(self, osc_o, osc_n, diff=True):
        """
        Do osclasses diff.
        """
        if not diff:
            status = "Added"
            osc_o = osc_n
        elif osc_o != osc_n:
            status = "Modified"
        else:
            status = "Unchanged"

        r = self.diff_tree.append(None, [status[0], _("OS Classes"), "", "",
            "", self.colors.get_hex_color(status[0])])

        roots = { }

        # order keys in descendent order
        o_keys = osc_o.keys()
        o_keys.sort()
        o_keys.reverse()

        for key in o_keys:
            # check if same level of accuracy is present on new data
            if key in osc_n:
                if osc_o[key] != osc_n[key]:
                    status = "Modified"
                elif diff:
                    status = "Unchanged"
            else:
                status = "Not_present"

            oscr = self.diff_tree.append(r, [status[0],
                _("Accuracy") + (" %d%%" % key), "", "", "",
                self.colors.get_hex_color(status[0])])
            roots[key] = oscr

            for indx, item in enumerate(osc_o[key]):
                if status == "Not_present":
                    self.diff_tree.append(oscr, [status[0], "", _("OS Class"),
                        item, NA, self.colors.get_hex_color(status[0])])
                else:
                    try:
                        new_value = osc_n[key][indx]
                        if item != new_value:
                            status = "Modified"
                        else:
                            if diff:
                                status = "Unchanged"
                            else:
                                new_value = item
                                item = ""

                    except IndexError:
                        status = "Not_present"
                        new_value = NA

                    self.diff_tree.append(oscr, [status[0], "", _("OS Class"),
                        item, new_value, self.colors.get_hex_color(status[0])])

        if not diff:
            return

        # check for items only in osc_n
        n_keys = osc_n.keys()
        n_keys.sort()
        n_keys.reverse()

        status = "Added"
        for key in n_keys:
            if key in o_keys and (len(osc_n[key]) > len(osc_o[key])):
                for item in osc_n[key][len(osc_o[key]):]:
                    self.diff_tree.append(roots[key],
                        [status[0], "", _("OS Class"), NA, item,
                        self.colors.get_hex_color(status[0])])

            elif not key in o_keys:
                oscr = self.diff_tree.append(r, [status[0],
                    _("Accuracy") + (" %d%%" % key), "", "", "",
                    self.colors.get_hex_color(status[0])])

                for item in osc_n[key]:
                    self.diff_tree.append(oscr, [status[0], "", _("OS Class"),
                        NA, item, self.colors.get_hex_color(status[0])])


    def osmatch_diff(self, osmatch_o, osmatch_n, diff=True):
        """
        Do OS Match diff.
        """
        if not diff:
            status = "Added"
            osmatch_o = osmatch_n
        elif osmatch_o != osmatch_n:
            status = "Modified"
        else:
            status = "Unchanged"

        r = self.diff_tree.append(None, [status[0], _("OS Match"), "", "", "",
            self.colors.get_hex_color(status[0])])

        if not osmatch_o and not osmatch_n and diff:
            self.diff_tree.append(r, [status[0], "", NA, NA, NA,
                self.colors.get_hex_color(status[0])])
            return

        for key, value in osmatch_o.items():
            if key in osmatch_n:
                new_value = osmatch_n[key]
            else:
                new_value = NA

            # both old value and new value are empty, discard this then
            if not value and not new_value:
                continue

            if diff:
                if value != new_value:
                    status = "Modified"
                else:
                    status = "Unchanged"
            else:
                value = ''

            self.diff_tree.append(r, [status[0], "", key, value, new_value,
                self.colors.get_hex_color(status[0])])

        if not diff or osmatch_o:
            return

        status = "Added"
        for key, value in osmatch_n.items():
            if not value:
                continue

            self.diff_tree.append(r, [status[0], "", key, NA,
                value, self.colors.get_hex_color(status[0])])


    def std_diff(self, old, new, title, diff=True, root=None):
        """
        Append data to tree according to changes between old and new.
        If diff=False, will classify all as 'Added'.
        """
        some_available = self.__verify_if_available([old,new])
        if not some_available:
            return 
        if not diff:
            status = "Added"
            old = new
        elif old != new:
            status = "Modified"
        else:
            status = "Unchanged"

        r = self.diff_tree.append(root, [status[0], title, "", "", "",
            self.colors.get_hex_color(status[0])])

        for key, value in old.items():
            if key in new:
                new_value = new[key]
            else:
                new_value = NA

            if not value and (not new_value or new_value == NA):
                continue

            if not diff:
                status = "Added"
                value = ""
            elif new_value != value:
                status = "Modified"
            else:
                status = "Unchanged"

            self.diff_tree.append(r, [status[0], "", key, value, new_value,
                self.colors.get_hex_color(status[0])])

        if not diff:
            return

        for key, value in new.items():
            if not key in old:
                status = "Added"

                self.diff_tree.append(r, [status[0], "", key, NA, value,
                    self.colors.get_hex_color(status[0])])


    def get_data_for_host_from_db(self, host_id):
        """
        Retrieve and adapt data from database for a host_id.
        """
        # ports
        ports = { }
        port_data = self.invdb.get_portid_and_fks_for_host_from_db(host_id)

        self.invdb.use_dict_cursor()
        for pd in port_data:
            fpd = self.invdb.get_port_data_for_pdata_from_db(pd[2],pd[3],pd[1])
            ports[pd[0]] = fpd

        # extraports
        epdata = self.invdb.get_extraports_data_for_host_from_db(host_id)

        ep_d = { }
        for ep in epdata:
            ep_d[ep['state']] = ep['count']

        # fingerprint data
        fp_data = self.invdb.get_fingerprint_info_for_host_from_db(host_id)

        uptime = { }
        tcp_seq = { }
        ip_id_seq = { }
        tcp_ts_seq = { }

        if fp_data:
            if fp_data['lastboot']:
                uptime['Last Boot'] = fp_data['lastboot']
                uptime['Uptime'] = fp_data['uptime']
            else:
                uptime = {NA: NA}

            tcp_seq[_('TCP Sequence Class')] = fp_data['tcp_sequence_class']
            tcp_seq[_('TCP Sequence Index')] = fp_data['tcp_sequence_index']
            tcp_seq[_('TCP Sequence Difficulty')] = (
                fp_data['tcp_sequence_difficulty'])
            tcp_seq[_('TCP Sequence Value')] = fp_data['tcp_sequence_value']

            ip_id_seq[_('IP ID Sequence Class')] = (
                fp_data['ip_id_sequence_class'])
            ip_id_seq[_('IP ID Sequence Value')] = (
                fp_data['ip_id_sequence_value'])

            tcp_ts_seq[_('TCP TS Sequence Class')] = (
                fp_data['tcp_ts_sequence_class'])
            tcp_ts_seq[_('TCP TS Sequence Value')] = (
                fp_data['tcp_ts_sequence_value'])
        else:
            uptime = {NA: NA}
            tcp_seq = {NA: NA}
            ip_id_seq = {NA: NA}
            tcp_ts_seq = {NA: NA}

        # osclasses
        osclasses = self.invdb.get_osclasses_for_host_from_db(host_id)
        osc_d = { }
        for osc in osclasses:
            key = osc['accuracy']

            cur_osc =  ', '.join(["%s: %s" % (
                k, value) for k, value in osc.items() \
                    if value and k != 'accuracy'])

            if key in osc_d:
                osc_d[key].append(cur_osc)
            else:
                osc_d[key] = [cur_osc]

        # osmatch
        osmatch = self.invdb.get_osmatch_for_host_from_db(host_id)
        if osmatch:
            osmatch['accuracy'] = "%d%%" % osmatch['accuracy']
        else:
            osmatch = { }

        # set standard cursor again
        self.invdb.use_standard_cursor()

        return (ports, ep_d, uptime, tcp_seq, tcp_ts_seq, ip_id_seq, osc_d,
            osmatch)


    def _setup_diff_view(self):
        """
        Setup treeview.
        """
        # create empty columns
        self.diff_view.columns = [None]*len(diff_columns)

        # treeview properties
        self.diff_view.set_enable_search(True)
        self.diff_view.set_search_column(2)
        selection = self.diff_view.get_selection()
        selection.set_mode(gtk.SELECTION_MULTIPLE)

        for n in range(len(diff_columns)):
            self.diff_view.columns[n] = gtk.TreeViewColumn(diff_columns[n])
            cur_column = self.diff_view.columns[n]

            cur_column.set_reorderable(True)
            cur_column.set_resizable(True)
            cur_column.set_sort_column_id(n)
            cur_column.connect('clicked', self.search_column, n)
            cur_column.cell = gtk.CellRendererText()
            cur_column.pack_start(cur_column.cell, True)
            cur_column.set_attributes(cur_column.cell, text=n, background=5)

            self.diff_view.append_column(cur_column)


    def _open_legend_dlg(self, event):
        """
        Open legend dialog.
        """
        dlg = DiffLegendWindow(self.colors)
        dlg.run()
        dlg.destroy()
    
    def __verify_if_available(self, list_values):
        """
        Verify if some fiends are available
        """
        all_not_available = True
        for d in list_values:
            if not all_not_available:
                break
            for k in d.keys():
                if k != "Not Available" or d[k] != "Not Available":
                    all_not_available = False
                    break
        return not all_not_available
        
        
        
    def __layout(self):
        """
        Layout widgets.
        """
        header_hbox = gtk.HBox()

        # sw to hold treeview
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.diff_view)

        # header
        header_hbox.pack_start(self.top_title, False, False, 0)
        header_hbox.pack_end(self.legend_btn, False, False, 0)

        self.pack_start(header_hbox, False, False, 6)
        self.pack_start(sw, True, True, 0)

        self.show_all()
