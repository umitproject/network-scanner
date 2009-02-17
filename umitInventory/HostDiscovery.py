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

import os
import re
import gtk
import socket
import gobject
import commands

from umitCore.NmapCommand import NmapCommand
from umitCore.NmapParser import NmapParser
from umitCore.Paths import Path
from umitCore.I18N import _

from umitInventory.Utils import append_s

from higwidgets.higbuttons import HIGButton
from higwidgets.higlabels import HIGEntryLabel
from higwidgets.higboxes import HIGVBox, HIGHBox, hig_box_space_holder
from higwidgets.higdialogs import HIGAlertDialog
from higwidgets.higframe import HIGFrame

PLATFORM = os.name

alpha = re.compile('[a-zA-Z]')

pixmaps_dir = Path.pixmaps_dir
if pixmaps_dir:
    logo = os.path.join(pixmaps_dir, 'wizard_logo.png')
else:
    logo = None

def tryto_detect_networks(caller=None):
    """
    Working on Linux only for now.
    """

    networks = [ ]
    if PLATFORM == 'nt':
        cmd = 'ipconfig'
    else:
        cmd = 'ifconfig'

    # try to get network interface(s) address(es)
    cmdoutput = commands.getoutput(cmd).split('\n')
    if not cmdoutput:
        print "error here"
        return

    for line in cmdoutput:
        line = line.lstrip()
        if line.startswith('inet addr'):
            line = line.split()[1:]

            if line[0].split(':')[1] == '127.0.0.1': # ignore loopback
                continue

            addr = None
            mask = None
            for l in line: # find ip address and subnet mask

                l = l.split(':')
                if l[0] == 'addr':
                    addr = l[1]
                elif l[0] == 'Mask':
                    mask = l[1]

                if not addr or not mask:
                    continue

                network = netaddress(addr, mask)
                networks.append(network)

    if not networks:
        # "brute force" detection, should work if behind firewall/NAT
        remote = ("umit.sf.net", 80)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = None
        try:
            s.connect(remote)
            ip, localport = s.getsockname()
            s.close()
        except socket.gaierror, e:
            print e
            pass

        if ip:
            ip_last_dot = ip.rfind('.')
            ip = ip[:ip_last_dot+1] + '0/24'
            if ip not in networks:
                networks.append(ip)

    return networks


def netaddress(ipaddr, subnetmask):
    """
    Expects an ip address string, aswell a subnet mask, and returns
    the network address.
    """
    ipaddr = ipaddr.split('.')
    ipaddr = [int(i) for i in ipaddr]
    subnetmask = subnetmask.split('.')
    subnetmask = [int(i) for i in subnetmask]

    # do binary AND between ipaddr and subnetmask to get network address
    netaddr = [ ]
    for indx, i in enumerate(ipaddr):
        netaddr.append(i & subnetmask[indx])

    netaddr = '.'.join([str(i) for i in netaddr]) + '/24'

    return netaddr


class HostDiscovery(gtk.Window):
    """
    GUI for network/host discovery.
    """

    def __init__(self, daddy):
        gtk.Window.__init__(self)

        self.daddy = daddy
        self.rowsel = None
        self.tooltips = gtk.Tooltips()
        self.wtitle = _("Host Discovery")

        # header
        self.title_markup = "<span size='16500' weight='heavy'>%s</span>"
        self.ttitle = HIGEntryLabel("")
        self.ttitle.set_line_wrap(False)
        self.ttitle.set_markup(self.title_markup % self.wtitle)
        self.umit_logo = gtk.Image()
        self.umit_logo.set_from_file(logo)
        # discovery options
        self.netdetect_btn = gtk.Button(_("Detect network(s)"))
        self.netdetect_btn.connect('clicked', self.get_networks)
        self.networks_box = None
        self.addnetworks = gtk.Button(_("Add new entry"))
        self.addnetworks.connect('clicked', self._create_network_entry)
        self.hostdetect_btn = gtk.Button(_("Find hosts"))
        self.hostdetect_btn.connect('clicked', self.get_addresses)
        # target list
        self.target_lbl = HIGEntryLabel(_("Target list"))
        self.target_model = gtk.ListStore(gobject.TYPE_STRING,
            gobject.TYPE_STRING)
        self.tview = gtk.TreeView(self.target_model)
        self.tview.set_size_request(300, int(300/1.6))
        self.tview.columns = [None]*2
        self.tview.columns[0] = gtk.TreeViewColumn(_("Host"))
        self.tview.columns[1] = gtk.TreeViewColumn(_("Network"))
        for n in range(2):
            self.tview.append_column(self.tview.columns[n])
            self.tview.columns[n].cell = gtk.CellRendererText()
            self.tview.columns[n].pack_start(self.tview.columns[n].cell, True)
            self.tview.columns[n].set_attributes(self.tview.columns[n].cell,
                                                 text=n)
        self.tview.get_selection().connect('changed', self._tview_sel_change)
        self.target_remove = gtk.Button(_("Remove from list"))
        self.target_remove.set_sensitive(False)
        self.target_remove.connect('clicked', self._remove_target)
        # bottom buttons
        self.help = HIGButton(stock=gtk.STOCK_HELP)
        self.help.connect('clicked', self._show_help)
        self.cancel = HIGButton(stock=gtk.STOCK_CANCEL)
        self.cancel.connect('clicked', self._exit)
        self.apply = HIGButton(stock=gtk.STOCK_APPLY)
        self.apply.connect('clicked', self._return_list)

        # tooltips
        self.tooltips.set_tip(self.addnetworks,
            _("Add new entry for a network"))
        self.tooltips.set_tip(self.netdetect_btn,
            _("Try to detect network(s)"))
        self.tooltips.set_tip(self.hostdetect_btn,
            _("Find hosts in entered network(s)"))
        self.tooltips.set_tip(self.target_remove,
            _("Remove selection from target list"))


        self.__layout()


    def _create_network_entry(self, event):
        """
        Create a new network entry.
        """
        entry = gtk.Entry()
        entry.set_text('')
        entry.show()
        self.networks_box.add(entry)


    def _tview_sel_change(self, event):
        """
        Row selection changed in treeview.
        """
        model, tv_iter = event.get_selected()
        self.rowsel = tv_iter
        self.target_remove.set_sensitive(True)


    def _remove_target(self, event):
        """
        Remove a host from target list.
        """
        if self.rowsel:
            self.target_model.remove(self.rowsel)
            self.target_remove.set_sensitive(False)
            self.rowsel = None


    def _show_help(self, event):
        """
        Show help.
        """
        pass


    def _exit(self, event):
        """
        Close window.
        """
        self.daddy.discoverywin = None # daddy is NewInventory instance
        self.destroy()


    def _return_list(self, event):
        """
        Return target list.
        """
        hosts = [ ]
        for row in self.target_model:
            hosts.append(row[0])

        self.results = ' '.join([str(h) for h in hosts])

        if self.daddy: # NewInventory instance
            self.daddy.scantarget.set_text(self.results)
            
        self._exit(None)


    def get_networks(self, event):
        """
        Try to detect network(s).
        """
        networks = tryto_detect_networks()

        if not networks:
            dlg = HIGAlertDialog(self,
                message_format=_("No network(s) detected."),
                secondary_text=_("You will need to especify the "
                    "network(s) yourself before detecting hosts."))
            dlg.run()
            dlg.destroy()
            return

        entries = len(self.networks_box.get_children()) - 1

        for amount, nw in enumerate(networks):
            if amount == entries:
                e = gtk.Entry()
                e.set_text('')
                e.show()
                self.networks_box.add(e)
                entries += 1

            entry = self.networks_box.get_children()[amount]
            entry.set_text(nw)


    def get_addresses(self, event):
        """
        Get hosts for network(s).
        """
        networks = []

        for entry in self.networks_box.get_children()[:-1]:
            text_entry = entry.get_text()
            wrong = alpha.search(text_entry)
            if wrong:
                self._error_invalid_network(text_entry)
                return
            elif text_entry:
                networks.append(text_entry)

        if not networks:
            dlg = HIGAlertDialog(self, message_format=_("No network."),
                secondary_text=_("You need to specify at least "
                    "one network to search for hosts."))
            dlg.run()
            dlg.destroy()
            return

        self.scans = { }
        self.scount = 0

        for n in networks:
            discovery = NmapCommand("%s -sP %s" % ('nmap', n))
            discovery.run_scan()

            self.scans[self.scount] = (discovery, n)
            self.scount += 1

        self.target_model.clear()
        self.hostdetect_btn.set_sensitive(False)
        self._adjust_target_label()
        gobject.timeout_add(500, self._check_scans)


    def _adjust_target_label(self):
        """Update target_lbl according to the current scount (assumes that
        scount > 0)."""
        word = append_s(_("scan"), self.scount)
        self.target_lbl.set_label(
                _("Target list") +
                (" (%d " % self.scount) + word +
                _("running"))


    def _check_scans(self):
        """
        Check if some scan finished.
        """
        for item in self.scans.items():
            index = item[0]
            scan = item[1][0]
            network = item[1][1]

            if not scan.scan_state(): # scan finished
                np = NmapParser(scan.get_xml_output_file())
                np.parse()
                for host in np.nmap["hosts"]: # get hosts with 'up' state
                    if host.state == 'up':
                        self.target_model.append((host.ip['addr'], network))

                # remove scan from list
                del self.scans[index]

                self.scount -= 1
                if self.scount:
                    self._adjust_target_label()

                # clean up temp files
                scan.close()

        if self.scount == 0: # all scans finished
            self.hostdetect_btn.set_sensitive(True)
            self.target_lbl.set_label(_("Target list"))
            return False

        return True


    def _error_invalid_network(self, network):
        """
        Show error dialog for invalid network(s).
        """
        dlg = HIGAlertDialog(self, message_format=_('Invalid network(s).'),
            secondary_text=(
                _("There is some invalid character in network") +
                    (" %r" % network) + _("please verify.")))
        dlg.run()
        dlg.destroy()


    def __layout(self):
        """
        Layout widgets
        """
        main_vbox = HIGVBox()
        main_vbox.set_border_width(5)
        main_vbox.set_spacing(12)
        main_hpaned = gtk.HPaned()
        btns_hbox = HIGHBox()
        left_box = HIGVBox()
        right_box = gtk.VBox()

        header_hbox = HIGHBox()
        hostdetect_hbox = HIGHBox()
        targetl_hbox = HIGHBox()
        targetv_hbox = HIGHBox()
        targetr_hbox = HIGHBox()

        # header
        header_hbox._pack_expand_fill(self.ttitle)
        header_hbox._pack_noexpand_nofill(self.umit_logo)
        # network list
        netframe = HIGFrame(_("Network list"))
        settings_align = gtk.Alignment(0.5, 0.5, 1, 1)
        settings_align.set_padding(6, 0, 12, 0)
        nbox = HIGVBox()
        entry = gtk.Entry()
        entry.set_text(_("Sample 192.168.254.0/24"))
        nbox._pack_noexpand_nofill(entry)
        addnw_hbox = HIGHBox()
        addnw_hbox._pack_noexpand_nofill(self.addnetworks)
        nbox.pack_end(addnw_hbox, False, False, 0)
        self.networks_box = nbox
        settings_align.add(nbox)
        netframe.add(settings_align)
        # detection
        hostdetect_hbox._pack_noexpand_nofill(self.netdetect_btn)
        hostdetect_hbox._pack_noexpand_nofill(self.hostdetect_btn)

        # target list
        targetl_hbox._pack_noexpand_nofill(self.target_lbl)
        targetv_hbox._pack_expand_fill(self.tview)
        targetr_hbox.pack_end(self.target_remove, False, False, 0)

        # bottom buttons
        btns_hbox.set_homogeneous(True)
        btns_hbox._pack_expand_fill(self.help)
        btns_hbox._pack_expand_fill(hig_box_space_holder())
        btns_hbox._pack_expand_fill(self.cancel)
        btns_hbox._pack_expand_fill(self.apply)
        # change apply button stock text
        lbl = self.apply.get_children()[0].get_children()[0].get_children()[1]
        lbl.set_text(_("Use target list"))


        left_box._pack_noexpand_nofill(netframe)
        left_box.pack_end(hostdetect_hbox, False, False, 0)
        right_box.pack_start(targetl_hbox, False, False, 0)
        right_box.pack_start(targetv_hbox, True, True, 6)
        right_box.pack_start(targetr_hbox, False, False, 0)

        left_align = gtk.Alignment(0.5, 0.5, 1, 1)
        left_align.set_padding(0, 0, 0, 6)
        left_align.add(left_box)
        right_align = gtk.Alignment(0.5, 0.5, 1, 1)
        right_align.set_padding(0, 0, 6, 0)
        right_align.add(right_box)

        main_hpaned.add1(left_align)
        main_hpaned.add2(right_align)

        main_vbox._pack_noexpand_nofill(header_hbox)
        main_vbox._pack_noexpand_nofill(gtk.HSeparator())
        main_vbox._pack_expand_fill(main_hpaned)
        main_vbox.pack_end(btns_hbox, False, False, 0)

        self.add(main_vbox)


if __name__ == "__main__":
    w = HostDiscovery()
    w.show_all()
    if w.run() == gtk.RESPONSE_APPLY:
        print w.results
        w.destroy()

    gtk.main()
