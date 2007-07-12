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

