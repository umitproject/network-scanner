-- Copyright (C) 2007 Insecure.Com LLC.
--
-- Authors: Guilherme Polo <ggpolo@gmail.com>
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

CREATE TRIGGER scan_insert_bad_scan_type
    BEFORE INSERT ON scan
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'scan', invalid fk_type especified")
        WHERE (SELECT pk FROM scan_type WHERE pk = NEW.fk_type) IS NULL;
    END;

CREATE TRIGGER scan_insert_bad_protocol
    BEFORE INSERT ON scan
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'scan', invalid fk_protocol especified")
        WHERE (SELECT pk FROM protocol WHERE pk = NEW.fk_protocol) IS NULL;
    END;

-- Triggers for preventing bad insertion on _scan_host
CREATE TRIGGER _scan_host_insert_bad_scan
    BEFORE INSERT ON _scan_host
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table '_scan_host', invalid fk_scan especified")
        WHERE (SELECT pk FROM scan WHERE pk = NEW.fk_scan) IS NULL;
    END;
    
CREATE TRIGGER _scan_host_insert_bad_host
    BEFORE INSERT ON _scan_host
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table '_scan_host', invalid fk_host especified")
        WHERE (SELECT pk FROM host WHERE pk = NEW.fk_host) IS NULL;
    END;


-------------------
-- Host Triggers
-------------------

-- Trigger for preventing bad insertion on host
CREATE TRIGGER host_insert_bad_host_state
    BEFORE INSERT ON host
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'host', invalid fk_host_state especified")
        WHERE (SELECT pk FROM host_state WHERE pk = NEW.fk_host_state) IS NULL;
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

-------------------
-- Port Triggers
-------------------

-- Triggers for preventing bad insertion on port
CREATE TRIGGER port_insert_bad_service
    BEFORE INSERT ON port
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'port', invalid fk_service especified")
        WHERE (SELECT pk FROM service WHERE pk = NEW.fk_service) IS NULL;
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
CREATE TRIGGER extraports_insert_bad_port_state
    BEFORE INSERT ON extraports
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad INSERT on table 'extraport', invalid fk_port_state especified")
        WHERE (SELECT pk FROM port_state WHERE pk = NEW.fk_port_state) IS NULL;
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
