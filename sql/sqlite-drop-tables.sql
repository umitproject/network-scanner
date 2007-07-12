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
-- Drop Tables
-------------------

-- scan
DROP TABLE scan;
DROP TABLE scaninfo;
DROP TABLE scan_type;
DROP TABLE scanner;
-- host
DROP TABLE host;
DROP TABLE fingerprint_info;
DROP TABLE osmatch;
DROP TABLE osclass;
DROP TABLE osgen;
DROP TABLE osfamily;
DROP TABLE osvendor;
DROP TABLE ostype;
DROP TABLE portused;
DROP TABLE host_state;
DROP TABLE address;
DROP TABLE vendor;
DROP TABLE hostname;
DROP TABLE _host_hostname;
DROP TABLE _host_address;
DROP TABLE _host_port;
-- ports
DROP TABLE port;
DROP TABLE extraports;
DROP TABLE protocol;
DROP TABLE service_info;
DROP TABLE service_name;
DROP TABLE port_state;
-- inventory
DROP TABLE inventory;
DROP TABLE inventory_change_category;
DROP TABLE _inventory_scan;
DROP TABLE _inventory_changes;
-- traceroute
DROP TABLE trace;
DROP TABLE hop;

