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

-- Triggers for preventing bad update on scaninfo
CREATE TRIGGER scaninfo_update_bad_scanner
    BEFORE UPDATE ON scaninfo
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK,"'Bad UPDATE on table 'scaninfo',  invalid fk_scanner especified")
        WHERE (SELECT pk FROM scanner WHERE pk = NEW.fk_scanner) IS NULL;
    END;

CREATE TRIGGER scaninfo_update_bad_scan_type
    BEFORE UPDATE ON scaninfo
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad UPDATE on table 'scaninfo', invalid fk_type especified")
        WHERE (SELECT pk FROM scan_type WHERE pk = NEW.fk_type) IS NULL;
    END;

CREATE TRIGGER scaninfo_update_bad_protocol
    BEFORE UPDATE ON scaninfo
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad UPDATE on table 'scaninfo', invalid fk_protocol especified")
        WHERE (SELECT pk FROM protocol WHERE pk = NEW.fk_protocol) IS NULL;
    END;

-- Triggers for preventing bad update on _scan_scaninfo
CREATE TRIGGER _scan_scaninfo_update_bad_scan
    BEFORE UPDATE ON _scan_scaninfo
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad UPDATE on table '_scan_scaninfo', invalid fk_scan especified")
        WHERE (SELECT pk FROM scan WHERE pk = NEW.fk_scan) IS NULL;
    END;

CREATE TRIGGER _scan_scaninfo_update_bad_scaninfo
    BEFORE UPDATE ON _scan_scaninfo
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad UPDATE on table '_scan_scaninfo', invalid fk_scaninfo especified")
        WHERE (SELECT pk FROM scaninfo WHERE pk = NEW.fk_scaninfo) IS NULL;
    END;

-- Triggers for preventing bad update on _scan_host
CREATE TRIGGER _scan_host_update_bad_scan
    BEFORE UPDATE ON _scan_host
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad UPDATE on table '_scan_host', invalid fk_scan especified")
        WHERE (SELECT pk FROM scan WHERE pk = NEW.fk_scan) IS NULL;
    END;
    
CREATE TRIGGER _scan_host_update_bad_host
    BEFORE UPDATE ON _scan_host
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad UPDATE on table '_scan_host', invalid fk_host especified")
        WHERE (SELECT pk FROM host WHERE pk = NEW.fk_host) IS NULL;
    END;


-------------------
-- Host Triggers
-------------------

-- Trigger for preventing bad update on host
CREATE TRIGGER host_update_bad_host_state
    BEFORE UPDATE ON host
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad UPDATE on table 'host', invalid fk_host_state especified")
        WHERE (SELECT pk FROM host_state WHERE pk = NEW.fk_host_state) IS NULL;
    END;

-- Trigger for preventing bad update on address
CREATE TRIGGER address_update_bad_vendor
    BEFORE UPDATE ON address
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad UPDATE on table 'address', invalid fk_vendor especified")
        WHERE (SELECT pk FROM vendor WHERE pk = NEW.fk_vendor) IS NULL;
    END;

-- Triggers for preventing bad update on _host_hostname
CREATE TRIGGER _host_hostname_update_bad_host
    BEFORE UPDATE ON _host_hostname
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad UPDATE on table '_host_hostname', invalid fk_host especified")
        WHERE (SELECT pk FROM host WHERE pk = NEW.fk_host) IS NULL;
    END;

CREATE TRIGGER _host_hostname_update_bad_hostname
    BEFORE UPDATE ON _host_hostname
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad UPDATE on table '_host_hostname', invalid fk_hostname especified")
        WHERE (SELECT pk FROM hostname WHERE pk = NEW.fk_hostname) IS NULL;
    END;

-- Triggers for preventing bad update on _host_address
CREATE TRIGGER _host_address_update_bad_host
    BEFORE UPDATE ON _host_address
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad UPDATE on table '_host_address', invalid fk_host especified")
        WHERE (SELECT pk FROM host WHERE pk = NEW.fk_host) IS NULL;
    END;

CREATE TRIGGER _host_address_update_bad_address
    BEFORE UPDATE ON _host_address
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad UPDATE on table '_host_address', invalid fk_address especified")
        WHERE (SELECT pk FROM address WHERE pk = NEW.fk_address) IS NULL;
    END;

-- Triggers for preventing bad update on _host_port
CREATE TRIGGER _host_port_update_bad_host
    BEFORE UPDATE ON _host_port
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad UPDATE on table '_host_port', invalid fk_host especified")
        WHERE (SELECT pk FROM host WHERE pk = NEW.fk_host) IS NULL;
    END;
    
CREATE TRIGGER _host_port_update_bad_port
    BEFORE UPDATE ON _host_port
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad UPDATE on table '_host_port', invalid fk_port especified")
        WHERE (SELECT pk FROM port WHERE pk = NEW.fk_port) IS NULL;
    END;

-------------------
-- Port Triggers
-------------------

-- Triggers for preventing bad update on port
CREATE TRIGGER port_update_bad_service
    BEFORE UPDATE ON port
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad UPDATE on table 'port', invalid fk_service especified")
        WHERE (SELECT pk FROM service WHERE pk = NEW.fk_service) IS NULL;
    END;
    
CREATE TRIGGER port_update_bad_protocol
    BEFORE UPDATE ON port
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad UPDATE on table 'port', invalid fk_protocol especified")
        WHERE (SELECT pk FROM protocol WHERE pk = NEW.fk_protocol) IS NULL;
    END;

CREATE TRIGGER port_update_bad_port_state
    BEFORE UPDATE ON port
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad UPDATE on table 'port', invalid fk_port_state especified")
        WHERE (SELECT pk FROM port_state WHERE pk = NEW.fk_port_state) IS NULL;
    END;
    
-- Trigger for preventing bad update on extraports
CREATE TRIGGER extraports_update_bad_port_state
    BEFORE UPDATE ON extraports
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad UPDATE on table 'extraport', invalid fk_port_state especified")
        WHERE (SELECT pk FROM port_state WHERE pk = NEW.fk_port_state) IS NULL;
    END;


-------------------
-- Inventory Triggers
-------------------

-- Triggers for preventing bad update on _inventory_scan
CREATE TRIGGER _inventory_scan_update_bad_scan
    BEFORE UPDATE ON _inventory_scan
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad UPDATE on table '_inventory_scan', invalid fk_scan especified")
        WHERE (SELECT pk FROM scan WHERE pk = NEW.fk_scan) IS NULL;
    END;

CREATE TRIGGER _inventory_scan_update_bad_inventory
    BEFORE UPDATE ON _inventory_scan
    FOR EACH ROW BEGIN
        SELECT RAISE(ROLLBACK, "Bad UPDATE on table '_inventory_scan', invalid fk_inventory especified")
        WHERE (SELECT pk FROM inventory WHERE pk = NEW.fk_inventory) IS NULL;
    END;

