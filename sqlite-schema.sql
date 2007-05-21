-- Copyright (C) 2007 Insecure.Com LLC.
--
-- Authors: Joao Paulo de Souza Medeiros <ignotus21@gmail.com>,
--          Guilherme Polo <ggpolo@gmail.com>
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
-- Scan
-------------------

CREATE TABLE scan (
    pk                INTEGER NOT NULL PRIMARY KEY,
    args              TEXT,
    start             TIMESTAMP,
    startstr          TEXT,
    finish            TIMESTAMP,
    finishstr         TEXT,
    xmloutputversion  TEXT,
    xmloutput         TEXT,
    verbose           INTEGER,
    debugging         INTEGER
);


CREATE TABLE scaninfo (
    pk           INTEGER NOT NULL PRIMARY KEY,   
    numservices  INTEGER,
    services     TEXT,
    fk_scanner   INTEGER NOT NULL CONSTRAINT fk_scanner
                    REFERENCES scanner(pk),
    fk_type      INTEGER NOT NULL CONSTRAINT fk_type
                    REFERENCES scan_type(pk),
    fk_protocol  INTEGER NOT NULL CONSTRAINT fk_protocol
                    REFERENCES protocol(pk)
);


CREATE TABLE _scan_scaninfo (
    fk_scan      INTEGER NOT NULL CONSTRAINT fk_scan
                    REFERENCES scan(pk),
    fk_scaninfo  INTEGER NOT NULL CONSTRAINT fk_scaninfo
                    REFERENCES scaninfo(pk)
);

CREATE TABLE _scan_host (
    fk_scan INTEGER NOT NULL CONSTRAINT fk_scan
               REFERENCES scan(pk),
    fk_host INTEGER NOT NULL CONSTRAINT fk_host
               REFERENCES host(pk)
);

CREATE TABLE scan_type (
    pk    INTEGER NOT NULL PRIMARY KEY,
    name  TEXT
);

CREATE TABLE scanner (
    pk       INTEGER NOT NULL PRIMARY KEY,
    name     TEXT,
    version  TEXT
);


-------------------
-- Host
-------------------

CREATE TABLE host (
    pk             INTEGER NOT NULL PRIMARY KEY,
    fk_host_state  INTEGER NOT NULL CONSTRAINT fk_host_state
                      REFERENCES host_state(id)
);

CREATE TABLE address (
    pk         INTEGER NOT NULL PRIMARY KEY,
    address    TEXT,
    type       INTEGER,
    fk_vendor  INTEGER NOT NULL CONSTRAINT fk_vendor
                  REFERENCES vendor(pk)
);

CREATE TABLE vendor (
    pk    INTEGER NOT NULL PRIMARY KEY,
    name  TEXT
);

CREATE TABLE host_state (
    pk     INTEGER NOT NULL PRIMARY KEY,
    state  TEXT
);

CREATE TABLE hostname (
    pk    INTEGER NOT NULL PRIMARY KEY,
    type  INTEGER,
    name  TEXT
);

CREATE TABLE _host_hostname (
    fk_host      INTEGER NOT NULL CONSTRAINT fk_host
                    REFERENCES host(pk),
    fk_hostname  INTEGER NOT NULL CONSTRAINT fk_hostname
                    REFERENCES hostname(pk)
);

CREATE TABLE _host_address (
    fk_host     INTEGER NOT NULL CONSTRAINT fk_host
                   REFERENCES host(pk),
    fk_address  INTEGER NOT NULL CONSTRAINT fk_address
                   REFERENCES address(pk)
);

CREATE TABLE _host_port (
    fk_host     INTEGER NOT NULL CONSTRAINT fk_host
                   REFERENCES host(pk),
    fk_port     INTEGER NOT NULL CONSTRAINT fk_port
                   REFERENCES port(pk)
);


-------------------
-- Ports
-------------------

CREATE TABLE port (
    pk             INTEGER NOT NULL PRIMARY KEY,
    portid         INTEGER,
    conf           INTEGER,
    method         INTEGER,
    fk_service     INTEGER NOT NULL CONSTRAINT fk_service
                      REFERENCES service(pk), 
    fk_protocol    INTEGER NOT NULL CONSTRAINT fk_protocol
                      REFERENCES protocol(pk),
    fk_port_state  INTEGER NOT NULL CONSTRAINT fk_port_state
                      REFERENCES port_state(pk)
);

CREATE TABLE extraports (
    pk             INTEGER NOT NULL PRIMARY KEY,
    count          INTEGER,
    fk_host        INTEGER NOT NULL CONSTRAINT fk_host
                      REFERENCES host(pk),
    fk_port_state  INTEGER NOT NULL CONSTRAINT fk_port_state
                      REFERENCES port_state(pk)
);

-- Protocol could be in a common place maybe
CREATE TABLE protocol (
    pk    INTEGER NOT NULL PRIMARY KEY,
    name  TEXT
);

CREATE TABLE service (
    pk    INTEGER NOT NULL PRIMARY KEY,
    name  TEXT
);

CREATE TABLE port_state (
    pk     INTEGER NOT NULL PRIMARY KEY,
    state  TEXT
);


-------------------
-- Inventory
-------------------

CREATE TABLE inventory (
    pk    INTEGER NOT NULL PRIMARY KEY,
    name  TEXT
);

CREATE TABLE _inventory_scan (
    fk_scan       INTEGER NOT NULL CONSTRAINT fk_scan
                     REFERENCES scan(pk),
    fk_inventory  INTEGER NOT NULL CONSTRAINT fk_inventory
                     REFERENCES inventory(pk)
);
