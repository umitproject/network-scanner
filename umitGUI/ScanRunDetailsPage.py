# Copyright (C) 2005 Insecure.Com LLC.
#
# Author: Adriano Monteiro Marques   <py.adriano@gmail.com>
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
from higwidgets.higboxes import HIGVBox, HIGHBox, hig_box_space_holder
from higwidgets.higtables import HIGTable
from higwidgets.higlabels import HIGEntryLabel

from umitCore.I18N import _


class ScanRunDetailsPage(HIGVBox):
    def __init__(self):
        HIGVBox.__init__(self)
        
        self.__create_widgets()
    
    def __create_widgets(self):
        na = _('Not available')
        self.command_expander = gtk.Expander("<b>"+_("Command Info")+"</b>")
        self.general_expander = gtk.Expander("<b>"+_("General Info")+"</b>")
        
        # Command info
        self.command_label = HIGEntryLabel(_('Command:'))
        self.info_command_label = HIGEntryLabel(na)
        
        self.nmap_version_label = HIGEntryLabel(_('Nmap Version:'))
        self.info_nmap_version_label = HIGEntryLabel(na)
        
        self.verbose_label = HIGEntryLabel(_('Verbosity level:'))
        self.info_verbose_label = HIGEntryLabel(na)
        
        self.debug_label = HIGEntryLabel(_('Debug level:'))
        self.info_debug_label = HIGEntryLabel(na)
        
        self.command_table = HIGTable()
        self.command_hbox = HIGHBox()
        
        # General info:
        self.start_label = HIGEntryLabel(_('Started on:'))
        self.info_start_label = HIGEntryLabel(na)
        
        self.finished_label = HIGEntryLabel(_('Finished on:'))
        self.info_finished_label = HIGEntryLabel(na)
        
        self.host_up_label = HIGEntryLabel(_('Hosts up:'))
        self.info_hosts_up_label = HIGEntryLabel(na)
        
        self.host_down_label = HIGEntryLabel(_('Hosts down:'))
        self.info_hosts_down_label = HIGEntryLabel(na)
        
        self.host_scanned_label = HIGEntryLabel(_('Hosts scanned:'))
        self.info_hosts_scanned_label = HIGEntryLabel(na)
        
        self.open_label = HIGEntryLabel(_('Open ports:'))
        self.info_open_label = HIGEntryLabel(na)
        
        self.filtered_label = HIGEntryLabel(_('Filtered ports:'))
        self.info_filtered_label = HIGEntryLabel(na)
        
        self.closed_label = HIGEntryLabel(_('Closed ports:'))
        self.info_closed_label = HIGEntryLabel(na)
        
        self.general_table = HIGTable()
        self.general_hbox = HIGHBox()
    
    def set_command_info(self, info):
        # Fix aligment!
        self.command_expander.set_use_markup(True)
        self.command_table.set_border_width(5)
        self.command_table.set_row_spacings(6)
        self.command_table.set_col_spacings(6)
        
        try:self.info_command_label.set_text(info['command'])
        except:pass
        
        try:self.info_nmap_version_label.set_text(info['version'])
        except:pass
        
        try:self.info_verbose_label.set_text(info['verbose'])
        except:pass
        
        try:self.info_debug_label.set_text(info['debug'])
        except:pass
        
        self.command_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.command_hbox._pack_noexpand_nofill(self.command_table)
        
        self.command_table.attach(self.command_label,0,1,0,1)
        self.command_table.attach(self.info_command_label,1,2,0,1)
        
        self.command_table.attach(self.nmap_version_label,0,1,1,2)
        self.command_table.attach(self.info_nmap_version_label,1,2,1,2)
        
        self.command_table.attach(self.verbose_label,0,1,2,3)
        self.command_table.attach(self.info_verbose_label,1,2,2,3)
        
        self.command_table.attach(self.debug_label,0,1,3,4)
        self.command_table.attach(self.info_debug_label,1,2,3,4)
        
        self.command_expander.add(self.command_hbox)
        self._pack_noexpand_nofill(self.command_expander)
        self.command_expander.set_expanded(True)
    
    def set_general_info(self, info):
        # Fix aligment!
        self.general_expander.set_use_markup(True)
        self.general_table.set_border_width(5)
        self.general_table.set_row_spacings(6)
        self.general_table.set_col_spacings(6)
        
        try:self.info_start_label.set_text(info['start'])
        except:pass
        
        try:self.info_finished_label.set_text(info['finish'])
        except:pass
        
        try:self.info_hosts_up_label.set_text(info['hosts_up'])
        except:pass
        
        try:self.info_hosts_down_label.set_text(info['hosts_down'])
        except:pass
        
        try:self.info_hosts_scanned_label.set_text(info['hosts_scanned'])
        except:pass
        
        #try:
        self.info_open_label.set_text(info['open_ports'])
        #except:pass
        
        #try:
        self.info_filtered_label.set_text(info['filtered_ports'])
        #except:pass
        
        #try:
        self.info_closed_label.set_text(info['closed_ports'])
        #except:pass
        
        self.general_hbox._pack_noexpand_nofill(hig_box_space_holder())
        self.general_hbox._pack_noexpand_nofill(self.general_table)
        
        self.general_table.attach(self.start_label,0,1,0,1)
        self.general_table.attach(self.info_start_label,1,2,0,1)
        
        self.general_table.attach(self.finished_label,0,1,1,2)
        self.general_table.attach(self.info_finished_label,1,2,1,2)
        
        self.general_table.attach(self.host_up_label,0,1,2,3)
        self.general_table.attach(self.info_hosts_up_label,1,2,2,3)
        
        self.general_table.attach(self.host_down_label,0,1,3,4)
        self.general_table.attach(self.info_hosts_down_label,1,2,3,4)
        
        self.general_table.attach(self.host_scanned_label,0,1,4,5)
        self.general_table.attach(self.info_hosts_scanned_label,1,2,4,5)
        
        self.general_table.attach(self.open_label,0,1,5,6)
        self.general_table.attach(self.info_open_label,1,2,5,6)
        
        self.general_table.attach(self.filtered_label,0,1,6,7)
        self.general_table.attach(self.info_filtered_label,1,2,6,7)
        
        self.general_table.attach(self.closed_label,0,1,7,8)
        self.general_table.attach(self.info_closed_label,1,2,7,8)
        
        self.general_expander.add(self.general_hbox)
        self._pack_noexpand_nofill(self.general_expander)
        self.general_expander.set_expanded(True)

    def set_scan_infos(self, scan_info):
        for scan in scan_info:
            exp = gtk.Expander('<b>%s - %s</b>' % (_('Scan Info'), scan['type'].capitalize()))
            exp.set_use_markup(True)
            hbox = HIGHBox()
            table = HIGTable()
            table.set_border_width(5)
            table.set_row_spacings(6)
            table.set_col_spacings(6)
            
            table.attach(HIGEntryLabel(_('Scan type:')),0,1,0,1)
            table.attach(HIGEntryLabel(scan['type']),1,2,0,1)
            
            table.attach(HIGEntryLabel(_('Protocol:')),0,1,1,2)
            table.attach(HIGEntryLabel(scan['protocol']),1,2,1,2)
            
            table.attach(HIGEntryLabel(_('# scanned ports:')),0,1,2,3)
            table.attach(HIGEntryLabel(scan['numservices']),1,2,2,3)
            
            table.attach(HIGEntryLabel(_('Services:')),0,1,3,4)
            table.attach(self.get_service_view(scan['services'].split(',')),\
                                               1,2,3,4)
            
            hbox._pack_noexpand_nofill(hig_box_space_holder())
            hbox._pack_noexpand_nofill(table)
            
            exp.add (hbox)
            self._pack_noexpand_nofill(exp)
    
    def get_service_view(self, services):
        combo = gtk.combo_box_new_text()
        
        for i in services:
            combo.append_text(i)
        
        return combo
