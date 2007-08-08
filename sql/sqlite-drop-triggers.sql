-- Copyright (C) 2007 Insecure.Com LLC.
--
-- Author: Guilherme Polo <ggpolo@gmail.com>
--
-- This program is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 2 of the License, or
-- (at your option) any later version.
--
-- This program is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with this program; if not, write to the Free Software
-- Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 
-- USA


-------------------
-- Drop Triggers
-------------------

--
-- Triggers for handling INSERT
--

-- scan
DROP TRIGGER scan_insert_bad_scanner;
DROP TRIGGER scaninfo_insert_bad_scan;
DROP TRIGGER scaninfo_insert_bad_scan_type;
DROP TRIGGER scaninfo_insert_bad_protocol;
-- host
DROP TRIGGER host_insert_bad_scan;
DROP TRIGGER host_insert_bad_host_state;
DROP TRIGGER fingerprint_info_insert_bad_host;
DROP TRIGGER address_insert_bad_vendor;
DROP TRIGGER _host_hostname_insert_bad_host;
DROP TRIGGER _host_hostname_insert_bad_hostname;
DROP TRIGGER _host_address_insert_bad_host;
DROP TRIGGER _host_address_insert_bad_address;
DROP TRIGGER _host_port_insert_bad_host;
DROP TRIGGER _host_port_insert_bad_port;
DROP TRIGGER osmatch_insert_bad_host;
DROP TRIGGER osclass_insert_bad_osgen;
DROP TRIGGER osclass_insert_bad_osfamily;
DROP TRIGGER osclass_insert_bad_osvendor;
DROP TRIGGER osclass_insert_bad_ostype;
DROP TRIGGER osclass_insert_bad_host;
DROP TRIGGER portused_insert_bad_protocol;
DROP TRIGGER portused_insert_bad_port_state;
DROP TRIGGER portused_insert_bad_host;
-- ports
DROP TRIGGER port_insert_bad_service_info;
DROP TRIGGER port_insert_bad_protocol;
DROP TRIGGER port_insert_bad_port_state;
DROP TRIGGER extraports_insert_bad_host;
DROP TRIGGER extraports_insert_bad_port_state;
DROP TRIGGER service_info_insert_bad_service_name;
DROP TRIGGER service_info_insert_bad_ostype;
-- inventory
DROP TRIGGER _inventory_scan_insert_bad_scan;
DROP TRIGGER _inventory_scan_insert_bad_inventory;
DROP TRIGGER _inventory_changes_insert_bad_inventory;
DROP TRIGGER _inventory_changes_insert_bad_category;
DROP TRIGGER _inventory_changes_insert_bad_address;
-- traceroute
DROP TRIGGER trace_insert_bad_protocol;
DROP TRIGGER hop_insert_bad_trace;


--
-- Triggers for handling UPDATE
--

-- scan
DROP TRIGGER scan_update_bad_scanner;
DROP TRIGGER scaninfo_update_bad_scan;
DROP TRIGGER scaninfo_update_bad_scan_type;
DROP TRIGGER scaninfo_update_bad_protocol;
-- host
DROP TRIGGER host_update_bad_scan;
DROP TRIGGER host_update_bad_host_state;
DROP TRIGGER fingerprint_info_update_bad_host;
DROP TRIGGER address_update_bad_vendor;
DROP TRIGGER _host_hostname_update_bad_host;
DROP TRIGGER _host_hostname_update_bad_hostname;
DROP TRIGGER _host_address_update_bad_host;
DROP TRIGGER _host_address_update_bad_address;
DROP TRIGGER _host_port_update_bad_host;
DROP TRIGGER _host_port_update_bad_port;
DROP TRIGGER osmatch_update_bad_host;
DROP TRIGGER osclass_update_bad_osgen;
DROP TRIGGER osclass_update_bad_osfamily;
DROP TRIGGER osclass_update_bad_osvendor;
DROP TRIGGER osclass_update_bad_ostype;
DROP TRIGGER osclass_update_bad_host;
DROP TRIGGER portused_update_bad_protocol;
DROP TRIGGER portused_update_bad_port_state;
DROP TRIGGER portused_update_bad_host;
-- ports
DROP TRIGGER port_update_bad_service_info;
DROP TRIGGER port_update_bad_protocol;
DROP TRIGGER port_update_bad_port_state;
DROP TRIGGER extraports_update_bad_host;
DROP TRIGGER extraports_update_bad_port_state;
DROP TRIGGER service_info_update_bad_service_name;
DROP TRIGGER service_info_update_bad_ostype;
-- inventory
DROP TRIGGER _inventory_scan_update_bad_scan;
DROP TRIGGER _inventory_scan_update_bad_inventory;
DROP TRIGGER _inventory_changes_update_bad_inventory;
DROP TRIGGER _inventory_changes_update_bad_category;
DROP TRIGGER _inventory_changes_update_bad_address;
-- traceroute
DROP TRIGGER trace_update_bad_protocol;
DROP TRIGGER hop_update_bad_trace;


--
-- Triggers for handling DELETE
--

-- scan
DROP TRIGGER scan_type_bad_delete;
DROP TRIGGER scanner_bad_delete;
DROP TRIGGER scan_bad_delete;
DROP TRIGGER scan2_bad_delete;
DROP TRIGGER scan3_bad_delete;
-- host
DROP TRIGGER vendor_bad_delete;
DROP TRIGGER address_bad_delete;
DROP TRIGGER address2_bad_delete;
DROP TRIGGER hostname_bad_delete;
DROP TRIGGER host_state_bad_delete;
DROP TRIGGER osgen_bad_delete;
DROP TRIGGER osfamily_bad_delete;
DROP TRIGGER osvendor_bad_delete;
DROP TRIGGER ostype_bad_delete;
DROP TRIGGER ostype2_bad_delete;
DROP TRIGGER host_bad_delete;
DROP TRIGGER host2_bad_delete;
DROP TRIGGER host3_bad_delete;
DROP TRIGGER host4_bad_delete;
DROP TRIGGER host5_bad_delete;
DROP TRIGGER host6_bad_delete;
DROP TRIGGER host7_bad_delete;
DROP TRIGGER host8_bad_delete;
-- ports
DROP TRIGGER service_name_bad_delete;
DROP TRIGGER port_state_bad_delete;
DROP TRIGGER port_state2_bad_delete;
DROP TRIGGER port_state3_bad_delete;
DROP TRIGGER protocol_bad_delete;
DROP TRIGGER protocol2_bad_delete;
DROP TRIGGER protocol3_bad_delete;
DROP TRIGGER protocol4_bad_delete;
DROP TRIGGER service_info_bad_delete;
DROP TRIGGER port_bad_delete;
-- inventory
DROP TRIGGER inventory_bad_delete;
DROP TRIGGER inventory2_bad_delete;
DROP TRIGGER inventory_change_category_bad_delete;
-- traceroute
DROP TRIGGER trace_bad_delete;

