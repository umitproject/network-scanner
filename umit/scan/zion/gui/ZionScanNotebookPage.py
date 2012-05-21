#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 Adriano Monteiro Marques
#
# Author: Joao Paulo de Souza Medeiros <ignotus@umitproject.org>
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
import gobject
import netifaces
import thread
import getopt
import re
from multiprocessing import Process, Queue
from ipaddr import IPNetwork

from higwidgets.higframe import HIGFrameRNet
from higwidgets.higboxes import HIGVBox, HIGHBox
from higwidgets.higdialogs import HIGAlertDialog
from higwidgets.higscrollers import HIGScrolledWindow

from umit.core.UmitConf import ProfileNotFound, Profile
from umit.core.Paths import Path
from umit.core.UmitLogging import log
from umit.core.I18N import _
from umit.umpa.sniffing.libpcap import pypcap

from umit.gui.ScanOpenPortsPage import ScanOpenPortsPage

from umit.scan.zion.gui.AttractorWidget import AttractorWidget
from umit.zion.scan import probe
from umit.zion.core import address, options, zion, host
from umit.zion.core.host import PORT_STATE_OPEN


ICON_DIR = 'share/pixmaps/umit/'

PIXBUF_FIREWALL = gtk.gdk.pixbuf_new_from_file(ICON_DIR + 'firewall.png')
PIXBUF_SYNPROXY = gtk.gdk.pixbuf_new_from_file(ICON_DIR + 'shield.png')
PIXBUF_HONEYD = gtk.gdk.pixbuf_new_from_file(ICON_DIR + 'honey.png')
PIXBUF_UNKNOWN = gtk.gdk.pixbuf_new_from_file(ICON_DIR + 'unknown_32.png')

SCANNING = _("Scanning")

class ZionHostsView(gtk.Notebook):
    """
    """
    def __init__(self):
        """
        """
        gtk.Notebook.__init__(self)
        self.set_border_width(6)
        self.set_tab_pos(gtk.POS_TOP)

        self.__create_widgets()

    def __create_widgets(self):
        """
        """
        self.__scans_page = ZionScansPage()
        self.__ports_page = HIGVBox()
        
        self.open_ports = ScanOpenPortsPage()

        self.append_page(self.__scans_page, gtk.Label(_('Scans')))
        self.append_page(self.__ports_page, gtk.Label(_('Ports')))
        
        self.__ports_page.add(self.open_ports)
        
    def port_mode(self):
        self.open_ports.host.port_mode() 
    
    def get_scans_page(self):
        """
        """
        return self.__scans_page

class ZionScansPage(HIGHBox):
    """
    """
    def __init__(self):
        """
        """
        HIGHBox.__init__(self)
        
        # Creating widgets
        self.__create_widgets()
        
        # Setting scrolled window
        self.__set_scrolled_window()
        
        # Setting text view
        self.__set_text_view()
        
        # Getting text buffer
        self.text_buffer = self.text_view.get_buffer()
        
        # Adding widgets
        self.__boxalign = gtk.Alignment()
        self.__boxalign.set_padding(8, 0, 0, 8)
        self.__boxalign.add(self.__hbox)
        self._pack_expand_fill(self.scrolled)
        self._pack_noexpand_nofill(self.__boxalign)
        
    def __create_widgets (self):
        # Creating widgets
        self.scrolled = gtk.ScrolledWindow()
        self.text_view = gtk.TextView()
        
        self.__hbox = HIGVBox()
        self.__attractor = AttractorWidget()
        self.__osinfo = gtk.Label()
        self.__textalign = gtk.Alignment()
        self.__textalign.add(self.__osinfo)
        self.__textalign.set_padding(8, 0, 0, 8)
        self.__frame_attractor = HIGFrameRNet(_('Attractor'))
        self.__frame_attractor._add(self.__attractor)

        self.__hbox._pack_noexpand_nofill(self.__frame_attractor)
        self.__hbox._pack_noexpand_nofill(self.__textalign)
        
    def __set_scrolled_window(self):
        # By default the vertical scroller remains at bottom
        self._scroll_at_bottom = True

        # Seting scrolled window
        self.scrolled.set_border_width(5)
        self.scrolled.add(self.text_view)
        self.scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
    def __set_text_view(self):
        self.text_view.set_wrap_mode(gtk.WRAP_WORD)
        self.text_view.set_editable(False)
        
    def write(self, text):
        """
        Write text to output box.
        """
        self.text_buffer.insert(self.text_buffer.get_end_iter(), text)
        
    def clean(self):
        """
        Clear all text in output box.
        """
        self.text_buffer.set_text('')
        self.clear_os_info()
        self.clear_attractors()
        
    def update_attractors(self,attractors):
        """
        Update the attractors at widget to plot them.
        """
        self.__attractor.update(attractors)
        
    def clear_attractors(self):
        """
        Clean the attractors ploted in widget
        """
        self.__attractor.update([])
        
    def update_os_info(self, info):
        """
        Update information about OS running on host.
        """
        str = 'Information:\nVendor: %s\nOS: %s %s' % (info['vendor_name'], info['os_name'], info['os_version'])
        self.__osinfo.set_text(str)
        
    def clear_os_info(self):
        """
        Clear information about OS scanned
        """
        self.__osinfo.set_text("")
        
    def hide_attractor_box(self):
        """
        Hide the box containing the attractor widget.
        """
        self.remove(self.__boxalign)
        
    def show_attractor_box(self):
        """
        Show the box containing the attractor widget.
        """
        self._pack_noexpand_nofill(self.__boxalign)
        self.show_all()

            
class ZionHostsList(gtk.ScrolledWindow):
    """
    """
    def __init__(self):
        """
        """
        gtk.ScrolledWindow.__init__(self)
        self.set_border_width(6)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.set_shadow_type(gtk.SHADOW_NONE)

        self.__create_widgets()

    def __create_widgets(self):
        """
        """
        self.__cell_text = gtk.CellRendererText()
        self.__cell_pixbuf = gtk.CellRendererPixbuf()

        self.__hosts_store = gtk.ListStore(gtk.gdk.Pixbuf, str)

        self.__hosts_treeview = gtk.TreeView(self.__hosts_store)
        self.__hosts_treeview.connect('cursor-changed', self.__cursor_callback)

        self.__hosts_column = list()

        self.__column_type = gtk.TreeViewColumn(_('Type'),
                                                self.__cell_pixbuf,
                                                pixbuf=0)
        self.__column_host = gtk.TreeViewColumn(_('Host'),
                                                self.__cell_text,
                                                text=1)

        self.__column_type.set_reorderable(True)
        self.__column_type.set_resizable(False)
        self.__column_host.set_reorderable(True)
        self.__column_host.set_resizable(False)

        self.__hosts_treeview.append_column(self.__column_type)
        self.__hosts_treeview.append_column(self.__column_host)

        self.__hosts_store.set_sort_func(0, self.__sort_type)
        self.__hosts_store.set_sort_func(1, self.__sort_host)

        self.add(self.__hosts_treeview)

        self.__hosts_treeview.set_cursor((0,))
        self.__cursor_callback(self.__hosts_treeview)

    def __cursor_callback(self, widget):
        """
        """
        path = widget.get_cursor()[0]
        if len(self.__hosts_store)>0:
            iter = self.__hosts_store.get_iter(path)
            self.__hosts_store.get_value(iter, 0)

    def __sort_type(self, treemodel, iter1, iter2):
        """
        """
        return 0

    def __sort_host(self, treemodel, iter1, iter2):
        """
        """
        return 0
    
    def clear_hosts(self):
        """
        """
        for i in range(len(self.__hosts_store)):
            iter = self.__hosts_store.get_iter_root()
            del(self.__hosts_store[iter])
        
    def add_host(self, name, host_type=None):
        """
        """
        self.__hosts_store.append([host_type,name])
        pass

class ZionResultsPage(gtk.HPaned):
    """
    """
    def __init__(self):
        """
        """
        gtk.HPaned.__init__(self)

        self.__create_widgets()
        self.set_position(200)

    def __create_widgets(self):
        """
        """
        self.__list = ZionHostsList()
        self.__view = ZionHostsView()

        self.add1(self.__list)
        self.add2(self.__view)
        
    def clear_port_list(self):
        """Clear Umit's scan result ports list."""
        self.__view.open_ports.host.clear_port_list()
        
    def set_host_port(self, host):
        """Set host to dipslay in Ports tab."""
        host_page = self.__view.open_ports.host
        host_page.switch_port_to_list_store()
        
        host_page.clear_port_list()
        
        ports = host.get_ports()
        port_ids = ports.keys()
        port_ids.sort()
        
        for port in port_ids:
            host_page.add_port(
                    (self.findout_service_icon(ports[port]), ) +
                    get_port_info(ports[port]))
            
    def update_host_info(self, host):
        """Update host info to show host ports."""
        self.__view.port_mode()
        self.set_host_port(host)        
            
    def findout_service_icon(self, port_info):
        return gtk.STOCK_YES
    
    def get_hosts_view(self):
        """
        """
        return self.__view
    
    def get_hosts_list(self):
        """
        """
        return self.__list

class ZionProfile(HIGVBox):
    """
    """
    def __init__(self, target=None):
        """
        """
        HIGVBox.__init__(self)

        self.target = target
        self.result = ZionResultsPage()

        self.pack_end(self.result)
        self.result.get_hosts_view().set_current_page(0)
        
        # construct communication queues
        self.q1 = Queue()
        self.q2 = Queue()
        fd = self.q2._reader.fileno()
        # observe received messages in queue
        gobject.io_add_watch(fd, gobject.IO_IN, self.update)

    def update_target(self, target):
        """
        """
        self.target = target

    def check_scan(self):
        """
        """
        if self.target:
            return True
        return False
    
    def update_info(self, text):
        """
        Update information page.
        """
        self.result.get_hosts_view().get_scans_page().write(text)
        
    def update_port_info(self, host):
        """
        Update the port scan information of host.
        """
        self.result.update_host_info(host)
        self.update_info('Host scanning finished\n')
        
    def update_attractors(self, attractors):
        """
        Update the scans page with the graph of attractors
        """
        self.result.get_hosts_view().get_scans_page().update_attractors(attractors)
        
    def update_host_information(self, info):
        """
        Update information about OS running on host.
        """
        self.result.get_hosts_view().get_scans_page().update_os_info(info)
        self.update_info('OS detection finished\n')
        
    def honeyd_finished(self, result):
        """
        Write information about honeyd detection result
        """
        if result:
            self.update_info('Target is honeyd\n')
        else:
            self.update_info('Target isnt honeyd\n')
            
    def synproxy_finished(self, result):
        """
        Write information about synproxy detection result
        """
        if result:
            self.update_info('Target is synproxy\n')
        else:
            self.update_info('Target isnt synproxy\n')   
            
    def update(self, fd, cond):
        """
        Update interface with the information received by zion process
        """
        signal, params = self.q2.get()
        
        if signal=='update_status':
            self.update_info(params)
        elif signal=='scan_finished':
            self.update_port_info(params)
        elif signal=='attractors_built':
            self.update_attractors(params)
        elif signal=='matching_finished':
            self.update_host_information(params)
        elif signal=='honeyd_finished':
            self.honeyd_finished(params)
        elif signal=='synproxy_finished':
            self.synproxy_finished(params)
        return True            

class ZionProfileHoneyd(ZionProfile):
    """
    """
    def __init__(self, target=None):
        """
        """
        ZionProfile.__init__(self, target)
        # remove attractor box
        self.result.get_hosts_view().get_scans_page().hide_attractor_box()
    
    def start(self):
        """
        """        
        self.result.get_hosts_list().clear_hosts()
        targets = []
        addr_list = []
        print "self.Target Value is -"
        print(self.target)
        if self.target.find('/') == -1:
            print "It does not contain /"
            if address.recognize(self.target) == address.Unknown:
                if address.is_name(self.target):
                    l = probe.get_addr_from_name(self.target)
                    for i in l:
                        try:
                            targets.append(host.Host(i, self.target))
                            addr_list.append(i)
                            host_str = '%s\n%s' % (i, self.target)
                            self.result.get_hosts_list().add_host(host_str)
                        except:
                            print "Unimplemented support to address: %s." % i
                else:
                    print "Error : Does not recoginise target"
            else:
                targets.append(host.Host(self.target))
                addr_list.append(self.target)
                self.result.get_hosts_list().add_host(self.target)
        else:
            for ip in IPNetwork(self.target):
                ip_str = '%s' % ip
                targets.append(host.Host(ip_str))
                addr_list.append(ip_str)
                self.result.get_hosts_list().add_host(ip_str)

        
        #addr = iter(addr_list)
        destaddr = addr_list[0]
        device = get_default_device(destaddr)
        
        if address.recognize(destaddr) == address.IPv4:
            saddr = get_ip_address(device)
        elif address.recognize(destaddr) == address.IPv6:
            temp_addr = get_ipv6_address(device)
            print(temp_addr)
            if temp_addr.find('%') != -1:
                saddr = temp_addr.split('%')[0]
                
            else:
                saddr = temp_addr
        else:
            print "Unknown address format"
        
            
        #saddr = "2001:0:53aa:64c:2496:d8dd:c44e:b5fd"
        #print "Source address -",
        #print(saddr)
        


        opts = options.Options()
        opts.add("-c",device)
        opts.add("--forge-addr",saddr)
        # honeyd option
        opts.add("-n")
        
        for target in targets:
            z = zion.Zion(opts,  [target])
            p = Process(target=z.run, args=(self.q2,))
            p.start()

class ZionProfileOS(ZionProfile):
    """
    """
    def __init__(self, target=None):
        """
        """
        ZionProfile.__init__(self, target)
        
    def start(self):
        """
        """
        z = zion.Zion(options.Options(), [])

        self.result.get_hosts_view().get_scans_page().clean()
        self.result.clear_port_list()

        # clear previous hosts in the list
        self.result.get_hosts_list().clear_hosts()

        # verify address to scan
        addr_list = []

        if self.target.find('/') == -1:
            if address.recognize(self.target) == address.Unknown:
                if address.is_name(self.target):
                    l = probe.get_addr_from_name(self.target)
                    pp.pprint(l)
                    for i in l:
                        try:
                            z.append_target(host.Host(i, self.target))
                            host_str = '%s\n%s' % (i, self.target)
                            addr_list.append(i)
                            self.result.get_hosts_list().add_host(host_str)
                        except:
                            print "Unimplemented support to address: %s." % i
                else:
                    print "Error : Does not recoginise target"
            else:
                z.append_target(host.Host(self.target))
                addr_list.append(self.target)
                self.result.get_hosts_list().add_host(self.target)
        else:
            for ip in IPNetwork(self.target):
                ip_str = '%s' % ip
                z.append_target(host.Host(ip_str))
                addr_list.append(ip_str)
                self.result.get_hosts_list().add_host(ip_str)
        
        
        #addr = iter(addr_list)
        pp.pprint(addr_list)
        destaddr = addr_list[0]
        # configure zion options
        device = get_default_device(destaddr)
        
        if address.recognize(destaddr) == address.IPv4:
            saddr = get_ip_address(device)
        elif address.recognize(destaddr) == address.IPv6:
            temp_addr = get_ipv6_address(device)
            print(temp_addr)
            if temp_addr.find('%') != -1:
                saddr = temp_addr.split('%')[0]
                #saddr = "2001:0:53aa:64c:389d:9c27:87c7:55a8"
            else:
                saddr = temp_addr
        else:
            print "Unknown address format"
        
        ##saddr = "2001:0:53aa:64c:38d3:b950:c44e:b128"
        #saddr = get_ip_address(device)
        #print "----------------------"
        #print saddr
        #print destaddr
        
        z.get_option_object().add("-c",device)
        z.get_option_object().add("-d")
        z.get_option_object().add("--forge-addr",saddr)

        p = Process(target=z.run, args=(self.q2,))
        p.start()
           

class ZionProfilePrompt(ZionProfile):
    """
    """
    def __init__(self, target=None):
        """
        """
        ZionProfile.__init__(self, target)
        
        # hide attractor box
        self.result.get_hosts_view().get_scans_page().hide_attractor_box()

        self.__command_hbox = HIGHBox()
        self.__command_label = gtk.Label(_('Command:'))
        self.command_entry = gtk.Entry()

        self.__command_hbox._pack_noexpand_nofill(self.__command_label)
        self.__command_hbox._pack_expand_fill(self.command_entry)

        self._pack_noexpand_nofill(self.__command_hbox)

    def check_scan(self):
        """
        """
        if self.command_entry.get_text().strip():
            return True
        return False
    
    def start(self):
        """
        """
        zion_options = options.Options()
        
        # get command options
        command = self.command_entry.get_text().strip()
        try:
            opts, addrs = getopt.gnu_getopt(command.split(),
                    options.OPTIONS_SHORT,
                    options.OPTIONS_LONG)
        except getopt.GetoptError, e:
            print 'Error: %s.' % e
            
        for o in opts:
            opt, value = o
            zion_options.add(opt, value)
            
        # hide attractor box if not needed
        if zion_options.has(options.OPTION_DETECT) or zion_options.has(options.OPTION_SYNPROXY):
            self.result.get_hosts_view().get_scans_page().show_attractor_box()
            
        z = zion.Zion(zion_options, [])
            
        for a in addrs:
            if address.recognize(a) == address.Unknown:
                l = probe.get_addr_from_name(a)
                for i in l:
                    try:
                        z.append_target(host.Host(i, a))
                    except:
                        print "Unimplemented support to address: %s." % i
            else:
                z.append_target(host.Host(a))
        
        # run zion
        p = Process(target=z.run, args=(self.q2,))
        p.start()
        

class ZionProfileSYNProxy(ZionProfile):
    """
    """
    def __init__(self, target=None):
        """
        """
        ZionProfile.__init__(self, target)
        # remove attractor box
        self.result.get_hosts_view().get_scans_page().hide_attractor_box()
        
    def start(self):
        """
        """        
        self.result.get_hosts_list().clear_hosts()
        targets = []
        addr_list = []
        if self.target.find('/') == -1:
            print "It does not contain /"
            if address.recognize(self.target) == address.Unknown:
                if address.is_name(self.target):
                    l = probe.get_addr_from_name(self.target)
                    for i in l:
                        try:
                            targets.append(host.Host(i, self.target))
                            addr_list.append(i)
                            host_str = '%s\n%s' % (i, self.target)
                            self.result.get_hosts_list().add_host(host_str)
                        except:
                            print "Unimplemented support to address: %s." % i
                else:
                    print "Error : Does not recoginise target"
            else:
                targets.append(host.Host(self.target))
                addr_list.append(self.target)
                self.result.get_hosts_list().add_host(self.target)
        else:
            for ip in IPNetwork(self.target):
                ip_str = '%s' % ip
                targets.append(host.Host(ip_str))
                addr_list.append(ip_str)
                self.result.get_hosts_list().add_host(ip_str)

        
        #addr = iter(addr_list)
        destaddr = addr_list[0]
        device = get_default_device(destaddr)
        #print "Destination Address-"
        #print(destaddr)
        if address.recognize(destaddr) == address.IPv4:
            saddr = get_ip_address(device)
        elif address.recognize(destaddr) == address.IPv6:
            temp_addr = get_ipv6_address(device)
            if temp_addr.find('%') != -1:
                saddr = temp_addr.split('%')[0]
                #saddr = "2001:0:53aa:64c:2c70:cf79:c44e:bda4"
            else:
                saddr = temp_addr
        else:
            print "Unknown address format"
        
            
        print "Source address -",
        print(saddr)

        opts = options.Options()
        opts.add("-c",device)
        opts.add("--forge-addr",saddr)
        # synproxy option
        opts.add("-y")
                
        for target in targets:
            z = zion.Zion(opts,  [target])
            p = Process(target=z.run, args=(self.q2,))
            p.start()

PROFILE_CLASS = {'1': ZionProfileHoneyd,
                 '2': ZionProfileOS,
                 '3': ZionProfilePrompt,
                 '4': ZionProfileSYNProxy}

class ZionScanNotebookPage(gtk.Alignment):
    """
    """
    def __init__(self, page):
        """
        """
        gtk.Alignment.__init__(self, 0, 0, 1, 1)

        self.page = page
        self.profile = None

    def profile_changed(self, widget, event=None):
        """
        """
        profile = self.page.toolbar.selected_profile
        target = self.page.toolbar.selected_target.strip()

        if self.profile != profile:
            id = Profile()._get_it(profile, 'zion_id')
            if self.get_child():
                self.remove(self.get_child())

            self.add(PROFILE_CLASS[id](target))

            if type(self.get_child()) == ZionProfilePrompt:
                self.page.toolbar.target_entry.set_sensitive(False)
                self.get_child().command_entry.connect('changed',
                    lambda x: self.page.toolbar.scan_button.set_sensitive(True))
            else:
                self.page.toolbar.target_entry.set_sensitive(True)

            self.show_all()
            self.profile = profile

    def target_changed(self, widget, event=None):
        """
        """
        target = self.page.toolbar.selected_target.strip()
        self.get_child().update_target(target)

        if self.get_child().check_scan():
            self.page.toolbar.scan_button.set_sensitive(True)
        else:
            self.page.toolbar.scan_button.set_sensitive(False)

    def start_scan_cb(self, widget):
        """
        """
        target = self.page.toolbar.selected_target.strip()
        self.page.toolbar.add_new_target(target)
        self.get_child().start()

    def kill_scan(self):
        """
        """
        pass

    def close_tab(self):
        """
        """
        pass

    def create_references(self):
        """
        """
        self.target_handle = self.page.toolbar.target_entry.connect('changed',
                self.target_changed)
        self.page.toolbar.target_entry.changed_handler = self.target_handle

    def delete_references(self):
        """
        """
        id = self.target_handle
        if (self.page.toolbar.target_entry.handler_is_connected(id)):
            self.page.toolbar.target_entry.disconnect(id)
            self.page.toolbar.target_entry.changed_handler = None

def get_port_info(port):
    """Return port info."""
    if (port.status == host.PORT_STATE_OPEN):
        status = 'open'
    elif (port.status == host.PORT_STATE_FILTERED):
        status = 'filtered'
    else:
        status = 'closed'
        
    if (port.protocol == host.PROTOCOL_TCP):
        protocol = 'tcp'
    elif (port.protocol == PROTOCOL_UDP):
        protocol = 'udp'
    elif (port.protocol == PROTOCOL_ICMP):
        procotol = 'icmp'
    else:
        protocol = ''

    return (
            int(port.number),
            protocol,
            status,
            port.service,
            '')

def get_default_device(destaddr):
    """
    If any default device is available in options use that, otherwise,
    Return the first (default) network device, which is usually 'eth0' under
    Linux and Windows and varies under BSD.
    address.recognize(destaddr) == address.IPv4:
    address.recognize(destaddr) == address.IPv6:

    @return: name of the first device.
    """

    # TODO: read device from options
    #device = "eth0"
    devices = pypcap.findalldevs()
    exp = re.compile('usb*', re.IGNORECASE)
    for dev in devices:
        if re.match(exp,dev) or dev == 'any':
            print 
        else:
            if address.recognize(destaddr) == address.IPv4:
                if destaddr == '127.0.0.1':
                    device = 'lo'
                    break
                else:
                    # Iterated interface could be down, so try to get ip first, if an exception
                    # occurs, pass to the next interface.
                    try:
                        saddr = netifaces.ifaddresses(dev)[netifaces.AF_INET][0]['addr']
                    except KeyError, e:
                        continue
                    if saddr == '127.0.0.1':
                        device = dev
                        continue
                    else:
                        device = dev
                        break
            elif address.recognize(destaddr) == address.IPv6:
                if destaddr == '::1' or destaddr == '0000:0000:0000:0000:0000:0000:0000:0001' or destaddr == '0:0:0:0:0:0:0:1':
                    device = 'lo'
                    break
                else:
                    # Iterated interface could be down, so try to get ip first, if an exception
                    # occurs, pass to the next interface.
                    try:
                        saddr = netifaces.ifaddresses(dev)[netifaces.AF_INET6][0]['addr']
                    except KeyError, e:
                        continue    
                    saddr_re = re.compile('fe80*', re.IGNORECASE)
                    if saddr == '::1':
                        continue
                    elif re.match(saddr_re , saddr):
                        device = dev
                        continue
                    else:
                        device = dev
                        break
            else:
                 device = devices[0]
                        
    print devices
    print device
    #device = netifaces.interfaces()[0]
    return device

def get_ip_address(interface):
    """ Return the ip address of the specified interface """
    return netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
    
def get_ipv6_address(interface):
    """ Return the ip address of the specified interface """
    return netifaces.ifaddresses(interface)[netifaces.AF_INET6][0]['addr']
