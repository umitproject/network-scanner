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
-- Scan Triggers
-------------------

-- Triggers for preventing bad insertion on scan
CREATE TRIGGER scan_insert_bad_scanner
    BEFORE INSERT ON scan
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'scan', invalid fk_scanner especified")
        WHERE (SELECT pk FROM scanner WHERE pk = NEW.fk_scanner) IS NULL;
    END;

-- Triggers for preventing bad insertion on scaninfo
CREATE TRIGGER scaninfo_insert_bad_scan
    BEFORE INSERT ON scaninfo
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'scaninfo', invalid fk_scan especified")
        WHERE (SELECT pk FROM scan WHERE pk = NEW.fk_scan) IS NULL;
    END;

CREATE TRIGGER scaninfo_insert_bad_scan_type
    BEFORE INSERT ON scaninfo
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'scaninfo', invalid fk_scan_type especified")
        WHERE (SELECT pk FROM scan_type WHERE pk = NEW.fk_scan_type) IS NULL;
    END;

CREATE TRIGGER scaninfo_insert_bad_protocol
    BEFORE INSERT ON scaninfo
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'scaninfo', invalid fk_protocol especified")
        WHERE (SELECT pk FROM protocol WHERE pk = NEW.fk_protocol) IS NULL;
    END;


-------------------
-- Host Triggers
-------------------

-- Triggers for preventing bad insertion on host
CREATE TRIGGER host_insert_bad_scan
    BEFORE INSERT ON host
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'host', invalid fk_scan especified")
        WHERE (SELECT pk from scan WHERE pk = NEW.fk_scan) IS NULL;
    END;

CREATE TRIGGER host_insert_bad_host_state
    BEFORE INSERT ON host
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'host', invalid fk_host_state especified")
        WHERE (SELECT pk FROM host_state WHERE pk = NEW.fk_host_state) IS NULL;
    END;

-- Trigger for preventing bad insertion on fingerprint_info
CREATE TRIGGER fingerprint_info_insert_bad_host
    BEFORE INSERT ON fingerprint_info
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'fingerprint_info', invalid fk_host especified")
        WHERE (SELECT pk FROM host WHERE pk = NEW.fk_host) IS NULL;
    END;

-- Trigger for preventing bad insertion on address
CREATE TRIGGER address_insert_bad_vendor
    BEFORE INSERT ON address
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'address', invalid fk_vendor especified")
        WHERE (SELECT pk FROM vendor WHERE pk = NEW.fk_vendor) IS NULL;
    END;

-- Triggers for preventing bad insertion on _host_hostname
CREATE TRIGGER _host_hostname_insert_bad_host
    BEFORE INSERT ON _host_hostname
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table '_host_hostname', invalid fk_host especified")
        WHERE (SELECT pk FROM host WHERE pk = NEW.fk_host) IS NULL;
    END;

CREATE TRIGGER _host_hostname_insert_bad_hostname
    BEFORE INSERT ON _host_hostname
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table '_host_hostname', invalid fk_hostname especified")
        WHERE (SELECT pk FROM hostname WHERE pk = NEW.fk_hostname) IS NULL;
    END;

-- Triggers for preventing bad insertion on _host_address
CREATE TRIGGER _host_address_insert_bad_host
    BEFORE INSERT ON _host_address
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table '_host_address', invalid fk_host especified")
        WHERE (SELECT pk FROM host WHERE pk = NEW.fk_host) IS NULL;
    END;

CREATE TRIGGER _host_address_insert_bad_address
    BEFORE INSERT ON _host_address
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table '_host_address', invalid fk_address especified")
        WHERE (SELECT pk FROM address WHERE pk = NEW.fk_address) IS NULL;
    END;

-- Triggers for preventing bad insertion on _host_port
CREATE TRIGGER _host_port_insert_bad_host
    BEFORE INSERT ON _host_port
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table '_host_port', invalid fk_host especified")
        WHERE (SELECT pk FROM host WHERE pk = NEW.fk_host) IS NULL;
    END;
    
CREATE TRIGGER _host_port_insert_bad_port
    BEFORE INSERT ON _host_port
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table '_host_port', invalid fk_port especified")
        WHERE (SELECT pk FROM port WHERE pk = NEW.fk_port) IS NULL;
    END;

-- Trigger for preventing bad insertion on osmatch
CREATE TRIGGER osmatch_insert_bad_host
    BEFORE INSERT ON osmatch
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'osmatch', invalid fk_host especified")
        WHERE (SELECT pk FROM host WHERE pk = NEW.fk_host) IS NULL;
    END;

-- Triggers for preventing bad insertion on osclass
CREATE TRIGGER osclass_insert_bad_osgen
    BEFORE INSERT ON osclass
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'osclass', invalid fk_osgen especified")
        WHERE (SELECT pk FROM osgen WHERE pk = NEW.fk_osgen) IS NULL;
    END;

CREATE TRIGGER osclass_insert_bad_osfamily
    BEFORE INSERT ON osclass
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'osclass', invalid fk_osfamily especified")
        WHERE (SELECT pk FROM osfamily WHERE pk = NEW.fk_osfamily) IS NULL;
    END;

CREATE TRIGGER osclass_insert_bad_osvendor
    BEFORE INSERT ON osclass
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'osclass', invalid fk_osvendor especified")
        WHERE (SELECT pk FROM osvendor WHERE pk = NEW.fk_osvendor) IS NULL;
    END;

CREATE TRIGGER osclass_insert_bad_ostype
    BEFORE INSERT ON osclass
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'osclass', invalid fk_ostype especified")
        WHERE (SELECT pk FROM ostype WHERE pk = NEW.fk_ostype) IS NULL;
    END;

CREATE TRIGGER osclass_insert_bad_host
    BEFORE INSERT ON osclass
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'osclass', invalid fk_host especified")
        WHERE (SELECT pk FROM host WHERE pk = NEW.fk_host) IS NULL;
    END;


-- Triggers for preventing bad insertion on portused
CREATE TRIGGER portused_insert_bad_protocol
    BEFORE INSERT ON portused
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'portused', invalid fk_protocol especified")
        WHERE (SELECT pk FROM protocol WHERE pk = NEW.fk_protocol) IS NULL;
    END;

CREATE TRIGGER portused_insert_bad_port_state
    BEFORE INSERT ON portused
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'portused', invalid fk_port_state especified")
        WHERE (SELECT pk FROM port_state WHERE pk = NEW.fk_port_state) IS NULL;
    END;

CREATE TRIGGER portused_insert_bad_host
    BEFORE INSERT ON portused
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'portused', invalid fk_host especified")
        WHERE (SELECT pk FROM host WHERE pk = NEW.fk_host) IS NULL;
    END;


-------------------
-- Port Triggers
-------------------

-- Triggers for preventing bad insertion on port
CREATE TRIGGER port_insert_bad_service_info
    BEFORE INSERT ON port
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'port', invalid fk_service_info especified")
        WHERE (SELECT pk FROM service_info WHERE pk = NEW.fk_service_info) IS NULL;
    END;
    
CREATE TRIGGER port_insert_bad_protocol
    BEFORE INSERT ON port
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'port', invalid fk_protocol especified")
        WHERE (SELECT pk FROM protocol WHERE pk = NEW.fk_protocol) IS NULL;
    END;

CREATE TRIGGER port_insert_bad_port_state
    BEFORE INSERT ON port
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'port', invalid fk_port_state especified")
        WHERE (SELECT pk FROM port_state WHERE pk = NEW.fk_port_state) IS NULL;
    END;
    
-- Trigger for preventing bad insertion on extraports
CREATE TRIGGER extraports_insert_bad_host
    BEFORE INSERT ON extraports
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'extraports', invalid fk_host especified")
        WHERE (SELECT pk from host WHERE pk = NEW.fk_host) IS NULL;
    END;

CREATE TRIGGER extraports_insert_bad_port_state
    BEFORE INSERT ON extraports
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'extraport', invalid fk_port_state especified")
        WHERE (SELECT pk FROM port_state WHERE pk = NEW.fk_port_state) IS NULL;
    END;

-- Trigger for preventing bad insertion on service_info
CREATE TRIGGER service_info_insert_bad_service_name
    BEFORE INSERT ON service_info
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'service_info', invalid fk_service_name especified")
        WHERE (SELECT pk FROM service_name WHERE pk = NEW.fk_service_name) IS NULL;
    END;

CREATE TRIGGER service_info_insert_bad_ostype
    BEFORE INSERT ON service_info
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'service_info', invalid fk_ostype especified")
        WHERE NEW.fk_ostype IS NOT NULL AND (SELECT pk FROM ostype WHERE pk = NEW.fk_ostype) IS NULL;
    END;


-------------------
-- Inventory Triggers
-------------------

-- Triggers for preventing bad insertion on _inventory_scan
CREATE TRIGGER _inventory_scan_insert_bad_scan
    BEFORE INSERT ON _inventory_scan
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table '_inventory_scan', invalid fk_scan especified")
        WHERE (SELECT pk FROM scan WHERE pk = NEW.fk_scan) IS NULL;
    END;

CREATE TRIGGER _inventory_scan_insert_bad_inventory
    BEFORE INSERT ON _inventory_scan
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table '_inventory_scan', invalid fk_inventory especified")
        WHERE (SELECT pk FROM inventory WHERE pk = NEW.fk_inventory) IS NULL;
    END;

-- Triggers for preventing bad insertion on _inventory_changes
CREATE TRIGGER _inventory_changes_insert_bad_inventory
    BEFORE INSERT ON _inventory_changes
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table '_inventory_changes', invalid fk_inventory especified")
        WHERE (SELECT pk FROM inventory WHERE pk = NEW.fk_inventory) IS NULL;
    END;

CREATE TRIGGER _inventory_changes_insert_bad_category
    BEFORE INSERT ON _inventory_changes
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table '_inventory_changes', invalid fk_category especified")
        WHERE (SELECT pk FROM inventory_change_category WHERE 
               pk = NEW.fk_category) IS NULL;
    END;

CREATE TRIGGER _inventory_changes_insert_bad_address
    BEFORE INSERT ON _inventory_changes
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table '_inventory_changes', invalid fk_address especified")
        WHERE (SELECT pk FROM address WHERE pk = NEW.fk_address) IS NULL;
    END;


-------------------
-- Traceroute Triggers
-------------------

-- Trigger for preventing bad insertion on trace
CREATE TRIGGER trace_insert_bad_protocol
    BEFORE INSERT ON trace
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'trace', invalid fk_protocol especified")
        WHERE (SELECT pk FROM protocol WHERE pk = NEW.fk_protocol) IS NULL;
    END;

-- Trigger for preventing bad insertion on hop
CREATE TRIGGER hop_insert_bad_trace
    BEFORE INSERT ON hop
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'hop', invalid fk_trace especified")
        WHERE (SELECT pk FROM trace WHERE pk = NEW.fk_trace) IS NULL;
    END;

