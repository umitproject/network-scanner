-- Copyright (C) 2007 Adriano Monteiro Marques
--
-- Author: Guilherme Polo <ggpolo@gmail.com>
--
-- This program is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 2 of the License, or
-- (at your option) any later version.
--
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

-- Trigger for preventing bad DELETE on scan_type
CREATE TRIGGER scan_type_bad_delete
    BEFORE DELETE ON scan_type
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'scan_type', it still holds references.")
        WHERE (SELECT fk_scan_type FROM scaninfo WHERE fk_scan_type = OLD.pk) IS NOT NULL;
    END;
-- NOTE: table scaninfo is named as scan_info on diagram

-- Trigger for preventing bad DELETE on scanner
CREATE TRIGGER scanner_bad_delete
    BEFORE DELETE ON scanner
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'scanner', it still holds references.")
        WHERE (SELECT fk_scanner FROM scan WHERE fk_scanner = OLD.pk) IS NOT NULL;
    END;

-- Trigger for preventing bad DELETE on scan
CREATE TRIGGER scan_bad_delete
    BEFORE DELETE ON scan
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'scan', it still hold references.")
        WHERE (SELECT fk_scan FROM scaninfo WHERE fk_scan = OLD.pk) IS NOT NULL;
    END;

CREATE TRIGGER scan2_bad_delete
    BEFORE DELETE ON scan
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'scan', it still hold references.")
        WHERE (SELECT fk_scan FROM _inventory_scan WHERE fk_scan = OLD.pk) IS NOT NULL;
    END;

CREATE TRIGGER scan3_bad_delete
    BEFORE DELETE ON scan
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'scan', it still hold references.")
        WHERE (SELECT fk_scan FROM host WHERE fk_scan = OLD.pk) IS NOT NULL;
    END;


-------------------
-- Host Triggers
-------------------

-- Trigger for preventing bad DELETE on vendor
CREATE TRIGGER vendor_bad_delete
    BEFORE DELETE ON vendor
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'vendor', it still holds references.")
        WHERE (SELECT fk_vendor FROM address WHERE fk_vendor = OLD.pk) IS NOT NULL;
    END;

-- Triggers for preventing bad DELETE on address
CREATE TRIGGER address_bad_delete
    BEFORE DELETE ON address
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'address', it still holds references.")
        WHERE (SELECT fk_address FROM _host_address WHERE fk_address=OLD.pk) IS NOT NULL;
    END;

CREATE TRIGGER address2_bad_delete
    BEFORE DELETE ON address
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'address', it still holds references.")
        WHERE (SELECT fk_address FROM _inventory_changes WHERE fk_address=OLD.pk) IS NOT NULL;
    END;

-- Trigger for preventing bad DELETE on hostname
CREATE TRIGGER hostname_bad_delete
    BEFORE DELETE ON hostname
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'hostname', it still holds references.")
        WHERE (SELECT fk_hostname FROM _host_hostname WHERE fk_hostname = OLD.pk) IS NOT NULL;
    END;

-- Trigger for preventing bad DELETE on host_state
CREATE TRIGGER host_state_bad_delete
    BEFORE DELETE ON host_state
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'host_state', it still holds references.")
        WHERE (SELECT fk_host_state FROM host WHERE fk_host_state = OLD.pk) IS NOT NULL;
    END;

-- Trigger for preventing bad DELETE on osgen
CREATE TRIGGER osgen_bad_delete
    BEFORE DELETE ON osgen
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'osgen', it still holds references.")
        WHERE (SELECT fk_osgen FROM osclass WHERE fk_osgen=OLD.pk) IS NOT NULL;
    END;

-- Trigger for preventing bad DELETE on osfamily
CREATE TRIGGER osfamily_bad_delete
    BEFORE DELETE ON osfamily
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'osfamily', it still holds references.")
        WHERE (SELECT fk_osfamily FROM osclass WHERE fk_osfamily = OLD.pk) IS NOT NULL;
    END;

-- Trigger for preventing bad DELETE on osvendor
CREATE TRIGGER osvendor_bad_delete
    BEFORE DELETE ON osvendor
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'osvendor', it still holds references.")
        WHERE (SELECT fk_osvendor FROM oclass WHERE fk_osvendor = OLD.pk) IS NOT NULL;
    END;

-- Triggers for preventing bad DELETE on ostype
CREATE TRIGGER ostype_bad_delete
    BEFORE DELETE ON ostype
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'ostype', it still holds references.")
        WHERE (SELECT fk_ostype FROM osclass WHERE fk_ostype = OLD.pk) IS NOT NULL;
    END;

CREATE TRIGGER ostype2_bad_delete
    BEFORE DELETE ON ostype
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'ostype', it still holds references.")
        WHERE (SELECT fk_ostype FROM service_info WHERE fk_ostype = OLD.pk) IS NOT NULL;
    END;

-- Triggers for preventing bad DELETE on host
CREATE TRIGGER host_bad_delete
    BEFORE DELETE ON host
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'host', it still holds references.")
        WHERE (SELECT fk_host FROM fingerprint_info WHERE fk_host = OLD.pk) IS NOT NULL;
    END;

CREATE TRIGGER host2_bad_delete
    BEFORE DELETE ON host
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'host', it still holds references.")
        WHERE (SELECT fk_host FROM _host_hostname WHERE fk_host = OLD.pk) IS NOT NULL;
    END;

CREATE TRIGGER host3_bad_delete
    BEFORE DELETE ON host
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'host', it still holds references.")
        WHERE (SELECT fk_host FROM _host_address WHERE fk_host = OLD.pk) IS NOT NULL;
    END;

CREATE TRIGGER host4_bad_delete
    BEFORE DELETE ON host
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'host', it still holds references.")
        WHERE (SELECT fk_host FROM osmatch WHERE fk_host = OLD.pk) IS NOT NULL;
    END;

CREATE TRIGGER host5_bad_delete
    BEFORE DELETE ON host
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'host', it still holds references.")
        WHERE (SELECT fk_host FROM osclass WHERE fk_host = OLD.pk) IS NOT NULL;
    END;

CREATE TRIGGER host6_bad_delete
    BEFORE DELETE ON host
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'host', it still holds references.")
        WHERE (SELECT fk_host FROM _host_port WHERE fk_host = OLD.pk) IS NOT NULL;
    END;

CREATE TRIGGER host7_bad_delete
    BEFORE DELETE ON host
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'host', it still holds references.")
        WHERE (SELECT fk_host FROM extraports WHERE fk_host = OLD.pk) IS NOT NULL;
    END;

CREATE TRIGGER host8_bad_delete
    BEFORE DELETE ON host
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'host', it still holds references.")
        WHERE (SELECT fk_host FROM portused WHERE fk_host = OLD.pk) IS NOT NULL;
    END;


-------------------
-- Port Triggers
-------------------

-- Trigger for preventing bad DELETE on service_name
CREATE TRIGGER service_name_bad_delete
    BEFORE DELETE ON service_name
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'service_name', it still holds references.")
        WHERE (SELECT fk_service_name FROM service_info WHERE fk_service_name = OLD.pk) IS NOT NULL;
    END;

-- Triggers for preventing bad DELETE on port_state
CREATE TRIGGER port_state_bad_delete
    BEFORE DELETE ON port_state
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'port_state', it still holds references.")
        WHERE (SELECT fk_port_state FROM portused WHERE fk_port_state = OLD.pk) IS NOT NULL;
    END;

CREATE TRIGGER port_state2_bad_delete
    BEFORE DELETE ON port_state
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'port_state', it still holds references.")
        WHERE (SELECT fk_port_state FROM extraports WHERE fk_port_state = OLD.pk) IS NOT NULL;
    END;

CREATE TRIGGER port_state3_bad_delete
    BEFORE DELETE ON port_state
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'port_state', it still holds references.")
        WHERE (SELECT fk_port_state FROM port WHERE fk_port_state = OLD.pk) IS NOT NULL;
    END;

-- Triggers for preventing bad DELETE on protocol
CREATE TRIGGER protocol_bad_delete
    BEFORE DELETE ON protocol
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'protocol', it still holds references.")
        WHERE (SELECT fk_protocol FROM scan_info WHERE fk_protocol = OLD.pk) IS NOT NULL;
    END;

CREATE TRIGGER protocol2_bad_delete
    BEFORE DELETE ON protocol
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'protocol', it still holds references.")
        WHERE (SELECT fk_protocol FROM port WHERE fk_protocol = OLD.pk) IS NOT NULL;
    END;

CREATE TRIGGER protocol3_bad_delete
    BEFORE DELETE ON protocol
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'protocol', it still holds references.")
        WHERE (SELECT fk_protocol FROM trace WHERE fk_protocol = OLD.pk) IS NOT NULL;
    END;

CREATE TRIGGER protocol4_bad_delete
    BEFORE DELETE ON protocol
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'protocol', it still holds references.")
        WHERE (SELECT fk_protocol FROM portused WHERE fk_protocol = OLD.pk) IS NOT NULL;
    END;

-- Trigger for preventing bad DELETE on service_info
CREATE TRIGGER service_info_bad_delete
    BEFORE DELETE ON service_info
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'service_info', it still holds references.")
        WHERE (SELECT fk_service_info FROM port WHERE fk_service_info = OLD.pk) IS NOT NULL;
    END;

-- Trigger for preventing bad DELETE on port
CREATE TRIGGER port_bad_delete
    BEFORE DELETE ON port
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'port', it still holds references.")
        WHERE (SELECT fk_port FROM _host_port WHERE fk_port = OLD.pk) IS NOT NULL;
    END;


-------------------
-- Inventory Triggers
-------------------

-- Trigger for preventing bad DELETE on inventory
CREATE TRIGGER inventory_bad_delete
    BEFORE DELETE ON inventory
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'inventory', it still holds references.")
        WHERE (SELECT fk_inventory FROM _inventory_scan WHERE fk_inventory=OLD.pk) IS NOT NULL;
    END;

CREATE TRIGGER inventory2_bad_delete
    BEFORE DELETE ON inventory
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'inventory', it still holds references.")
        WHERE (SELECT fk_inventory FROM _inventory_changes WHERE fk_inventory=OLD.pk) IS NOT NULL;
    END;

-- Trigger for preventing bad DELETE on inventory_change_category
CREATE TRIGGER inventory_change_category_bad_delete
    BEFORE DELETE ON inventory_change_category
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'inventory_change_category', it still holds references.")
        WHERE (SELECT fk_category FROM _inventory_changes WHERE fk_category=OLD.pk) IS NOT NULL;
    END;


-------------------
-- Traceroute Triggers
-------------------

-- Trigger for preventing bad DELETE on trace
CREATE TRIGGER trace_bad_delete
    BEFORE DELETE ON trace
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad DELETE on table 'trace', it still holds references.")
        WHERE (SELECT fk_trace FROM hop WHERE fk_trace=OLD.pk) IS NOT NULL;
    END;

