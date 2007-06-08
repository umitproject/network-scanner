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
-- Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

--------------------------------------------------------------------------------
-- DATABASE SCHEMA                                                            --
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
-- TABLES                                                                     --
--------------------------------------------------------------------------------

-- DROP TABLE scan CASCADE;

CREATE TABLE scan
(
    pk INTEGER NOT NULL,
    args VARCHAR NOT NULL,
    start TIMESTAMP NOT NULL,
    startstr CHAR(24) NOT NULL,
    finish TIMESTAMP NOT NULL,
    finishstr CHAR(24) NOT NULL,
    xmloutputversion VARCHAR,
    xmloutput TEXT,
    verbose_level INTEGER NOT NULL,
    debugging_level INTEGER NOT NULL,
    hosts_up INTEGER NOT NULL,
    hosts_down INTEGER NOT NULL,
    fk_scanner INTEGER NOT NULL
);

ALTER TABLE scan ADD CONSTRAINT scan_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE scanner CASCADE;

CREATE TABLE scanner
(
    pk INTEGER NOT NULL,
    name VARCHAR NOT NULL,
    version VARCHAR NOT NULL
);

ALTER TABLE scanner ADD CONSTRAINT scanner_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE host CASCADE;

CREATE TABLE host
(
    pk INTEGER NOT NULL,
    distance INTEGER NOT NULL,
    fk_scan INTEGER NOT NULL,
    fk_host_state INTEGER
);

ALTER TABLE host ADD CONSTRAINT host_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE host CASCADE;

CREATE TABLE finger_print_info
(
    pk INTEGER NOT NULL,
    uptime INTEGER,
    lastboot CHAR(24),
    fingerprint TEXT,
    tcp_sequence_class INTEGER,
    tcp_sequence_index INTEGER,
    tcp_sequence_value VARCHAR,
    tcp_sequence_difficulty INTEGER,
    tcp_ts_sequence_class INTEGER,
    tcp_ts_sequence_value VARCHAR,
    ip_id_sequence_class INTEGER,
    ip_id_sequence_value VARCHAR,
    fk_host INTEGER
);

ALTER TABLE finger_print_info
    ADD CONSTRAINT finger_print_info_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE host_state CASCADE;

CREATE TABLE host_state
(
    pk INTEGER NOT NULL,
    state VARCHAR NOT NULL
);

ALTER TABLE host_state ADD CONSTRAINT host_state_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE scan_type CASCADE;

CREATE TABLE scan_type
(
    pk INTEGER NOT NULL,
    name VARCHAR NOT NULL
);

ALTER TABLE scan_type ADD CONSTRAINT scan_type_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE protocol CASCADE;

CREATE TABLE protocol
(
    pk INTEGER NOT NULL,
    name VARCHAR NOT NULL
);

ALTER TABLE protocol ADD CONSTRAINT protocol_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE hostname CASCADE;

CREATE TABLE hostname
(
    pk INTEGER NOT NULL,
    type INTEGER NOT NULL,
    name VARCHAR NOT NULL
);

ALTER TABLE hostname ADD CONSTRAINT hostname_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE _host_hostname CASCADE;

CREATE TABLE _host_hostname
(
    pk INTEGER NOT NULL,
    fk_host INTEGER NOT NULL,
    fk_hostname INTEGER NOT NULL
);

ALTER TABLE _host_hostname ADD CONSTRAINT _host_hostname_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE address CASCADE;

CREATE TABLE address
(
    pk INTEGER NOT NULL,
    address VARCHAR NOT NULL,
    type INTEGER NOT NULL,
    fk_vendor INTEGER
);

ALTER TABLE address ADD CONSTRAINT address_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE vendor CASCADE;

CREATE TABLE vendor
(
    pk INTEGER NOT NULL,
    name VARCHAR NOT NULL
);

ALTER TABLE vendor ADD CONSTRAINT vendor_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE _host_address CASCADE;

CREATE TABLE _host_address
(
    pk INTEGER NOT NULL,
    fk_host INTEGER NOT NULL,
    fk_address INTEGER NOT NULL
);

ALTER TABLE _host_address ADD CONSTRAINT _host_address_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE port CASCADE;

CREATE TABLE port
(
    pk INTEGER NOT NULL,
    portid INTEGER NOT NULL,
    fk_service_info INTEGER,
    fk_protocol INTEGER,
    fk_port_state INTEGER NOT NULL
);

ALTER TABLE port ADD CONSTRAINT port_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE port_state CASCADE;

CREATE TABLE port_state
(
    pk INTEGER NOT NULL,
    state VARCHAR NOT NULL
);

ALTER TABLE port_state ADD CONSTRAINT port_state_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE service_info CASCADE;

CREATE TABLE service_info
(
    pk INTEGER NOT NULL,
    product VARCHAR,
    version VARCHAR,
    extrainfo VARCHAR,
    method INTEGER NOT NULL,
    conf INTEGER NOT NULL,
    fk_ostype INTEGER,
    fk_service INTEGER NOT NULL
);

ALTER TABLE service_info ADD CONSTRAINT service_info_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE _host_port CASCADE;

CREATE TABLE _host_port
(
    pk INTEGER NOT NULL,
    fk_host INTEGER NOT NULL,
    fk_port INTEGER NOT NULL
);

ALTER TABLE _host_port ADD CONSTRAINT _host_port_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE extraports CASCADE;

CREATE TABLE extraports
(
    pk INTEGER NOT NULL,
    count INTEGER NOT NULL,
    fk_host INTEGER NOT NULL,
    fk_port_state INTEGER NOT NULL
);

ALTER TABLE extraports ADD CONSTRAINT extraports_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE inventory CASCADE;

CREATE TABLE inventory
(
    pk INTEGER NOT NULL,
    name VARCHAR NOT NULL
);

ALTER TABLE inventory ADD CONSTRAINT inventory_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE _inventory_scan CASCADE;

CREATE TABLE _inventory_scan
(
    pk INTEGER NOT NULL,
    fk_scan INTEGER NOT NULL,
    fk_inventory INTEGER NOT NULL
);

ALTER TABLE _inventory_scan ADD CONSTRAINT _inventory_scan_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE scaninfo CASCADE;

CREATE TABLE scaninfo
(
    pk INTEGER NOT NULL,
    numservices INTEGER NOT NULL,
    services VARCHAR NOT NULL,
    fk_scan INTEGER NOT NULL,
    fk_scan_type INTEGER NOT NULL,
    fk_protocol INTEGER NOT NULL
);

ALTER TABLE scaninfo ADD CONSTRAINT scaninfo_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE service CASCADE;

CREATE TABLE service
(
    pk INTEGER NOT NULL,
    name VARCHAR NOT NULL
);

ALTER TABLE service ADD CONSTRAINT service_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE portused CASCADE;

CREATE TABLE portused
(
    pk INTEGER NOT NULL,
    portid INTEGER NOT NULL,
    fk_port_state INTEGER NOT NULL,
    fk_protocol INTEGER NOT NULL,
    fk_host INTEGER NOT NULL
);

ALTER TABLE portused ADD CONSTRAINT portused_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE osclass CASCADE;

CREATE TABLE osclass
(
    pk INTEGER NOT NULL,
    accuracy INTEGER NOT NULL,
    fk_osgen INTEGER,
    fk_osfamily INTEGER,
    fk_osvendor INTEGER,
    fk_ostype INTEGER,
    fk_host INTEGER NOT NULL
);

ALTER TABLE osclass ADD CONSTRAINT osclass_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE osmatch CASCADE;

CREATE TABLE osmatch
(
    pk INTEGER NOT NULL,
    name VARCHAR NOT NULL,
    accuracy INTEGER NOT NULL,
    line INTEGER NOT NULL,
    fk_host INTEGER NOT NULL
);

ALTER TABLE osmatch ADD CONSTRAINT osmatch_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE trace CASCADE;

CREATE TABLE trace
(
    pk INTEGER NOT NULL,
    port INTEGER NOT NULL,
    fk_protocol INTEGER NOT NULL
);

ALTER TABLE trace ADD CONSTRAINT trace_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE hop CASCADE;

CREATE TABLE hop
(
    pk INTEGER NOT NULL,
    ttl INTEGER NOT NULL,
    ipaddr VARCHAR NOT NULL,
    host VARCHAR,
    fk_trace INTEGER NOT NULL
);

ALTER TABLE hop ADD CONSTRAINT hop_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE ostype CASCADE;

CREATE TABLE ostype
(
    pk INTEGER NOT NULL,
    type VARCHAR NOT NULL
);

ALTER TABLE ostype ADD CONSTRAINT ostype_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE osvendor CASCADE;

CREATE TABLE osvendor
(
    pk INTEGER NOT NULL,
    vendor VARCHAR NOT NULL
);

ALTER TABLE osvendor ADD CONSTRAINT osvendor_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE osfamily CASCADE;

CREATE TABLE osfamily
(
    pk INTEGER NOT NULL,
    family VARCHAR NOT NULL
);

ALTER TABLE osfamily ADD CONSTRAINT osfamily_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE osgen CASCADE;

CREATE TABLE osgen
(
    pk INTEGER NOT NULL,
    gen VARCHAR NOT NULL
);

ALTER TABLE osgen ADD CONSTRAINT osgen_pk PRIMARY KEY (pk);


--------------------------------------------------------------------------------
-- FOREIGN KEYS                                                               --
--------------------------------------------------------------------------------

ALTER TABLE scan ADD CONSTRAINT scan_scanner_fk
    FOREIGN KEY (fk_scanner) REFERENCES scanner (pk);

--------------------------------------------------------------------------------

ALTER TABLE host ADD CONSTRAINT host_scan_fk
    FOREIGN KEY (fk_scan) REFERENCES scan (pk);

ALTER TABLE host ADD CONSTRAINT host_host_state_fk
    FOREIGN KEY (fk_host_state) REFERENCES host_state (pk);

--------------------------------------------------------------------------------

ALTER TABLE finger_print_info ADD CONSTRAINT finger_print_info_host_fk
    FOREIGN KEY (fk_host) REFERENCES host (pk);

--------------------------------------------------------------------------------

ALTER TABLE _host_hostname ADD CONSTRAINT _host_hostname_host_fk
    FOREIGN KEY (fk_host) REFERENCES host (pk);

ALTER TABLE _host_hostname ADD CONSTRAINT _host_hostname_hostname_fk
    FOREIGN KEY (fk_hostname) REFERENCES hostname (pk);

--------------------------------------------------------------------------------

ALTER TABLE address ADD CONSTRAINT address_vendor_fk
    FOREIGN KEY (fk_vendor) REFERENCES vendor (pk);

--------------------------------------------------------------------------------

ALTER TABLE _host_address ADD CONSTRAINT _host_address_host_fk
    FOREIGN KEY (fk_host) REFERENCES host (pk);

ALTER TABLE _host_address ADD CONSTRAINT _host_address_address_fk
    FOREIGN KEY (fk_address) REFERENCES address (pk);

--------------------------------------------------------------------------------

ALTER TABLE port ADD CONSTRAINT port_service_info_fk
    FOREIGN KEY (fk_service_info) REFERENCES service_info (pk);

ALTER TABLE port ADD CONSTRAINT port_protocol_fk
    FOREIGN KEY (fk_protocol) REFERENCES protocol (pk);

ALTER TABLE port ADD CONSTRAINT port_port_state_fk
    FOREIGN KEY (fk_port_state) REFERENCES port_state (pk);

--------------------------------------------------------------------------------

ALTER TABLE service_info ADD CONSTRAINT service_info_ostype_fk
    FOREIGN KEY (fk_ostype) REFERENCES ostype (pk);

ALTER TABLE service_info ADD CONSTRAINT service_info_service_fk
    FOREIGN KEY (fk_service) REFERENCES service (pk);

--------------------------------------------------------------------------------

ALTER TABLE _host_port ADD CONSTRAINT _host_port_host_fk
    FOREIGN KEY (fk_host) REFERENCES host (pk);

ALTER TABLE _host_port ADD CONSTRAINT _host_port_port_fk
    FOREIGN KEY (fk_port) REFERENCES port (pk);

--------------------------------------------------------------------------------

ALTER TABLE extraports ADD CONSTRAINT extraports_host_fk
    FOREIGN KEY (fk_host) REFERENCES host (pk);

ALTER TABLE extraports ADD CONSTRAINT extraports_port_state_fk
    FOREIGN KEY (fk_port_state) REFERENCES port_state (pk);

--------------------------------------------------------------------------------

ALTER TABLE _inventory_scan ADD CONSTRAINT _inventory_scan_scan_fk
    FOREIGN KEY (fk_scan) REFERENCES scan (pk);

ALTER TABLE _inventory_scan ADD CONSTRAINT _inventory_scan_inventory_fk
    FOREIGN KEY (fk_inventory) REFERENCES inventory (pk);

--------------------------------------------------------------------------------

ALTER TABLE scaninfo ADD CONSTRAINT scaninfo_scan_fk
    FOREIGN KEY (fk_scan) REFERENCES scan (pk);

ALTER TABLE scaninfo ADD CONSTRAINT scaninfo_type_fk
    FOREIGN KEY (fk_scan_type) REFERENCES scan_type (pk);

ALTER TABLE scaninfo ADD CONSTRAINT scaninfo_protocol_fk
    FOREIGN KEY (fk_protocol) REFERENCES protocol (pk);

--------------------------------------------------------------------------------

ALTER TABLE portused ADD CONSTRAINT portused_port_state_fk
    FOREIGN KEY (fk_port_state) REFERENCES port_state (pk);

ALTER TABLE portused ADD CONSTRAINT portused_protocol_fk
    FOREIGN KEY (fk_protocol) REFERENCES protocol (pk);

ALTER TABLE portused ADD CONSTRAINT portused_host_fk
    FOREIGN KEY (fk_host) REFERENCES host (pk);

--------------------------------------------------------------------------------

ALTER TABLE osclass ADD CONSTRAINT osclass_osgen_fk
    FOREIGN KEY (fk_osgen) REFERENCES osgen (pk);

ALTER TABLE osclass ADD CONSTRAINT osclass_osfamily_fk
    FOREIGN KEY (fk_osfamily) REFERENCES osfamily (pk);

ALTER TABLE osclass ADD CONSTRAINT osclass_osvendor_fk
    FOREIGN KEY (fk_osvendor) REFERENCES osvendor (pk);

ALTER TABLE osclass ADD CONSTRAINT osclass_ostype_fk
    FOREIGN KEY (fk_ostype) REFERENCES ostype (pk);

ALTER TABLE osclass ADD CONSTRAINT osclass_host_fk
    FOREIGN KEY (fk_host) REFERENCES host (pk);

--------------------------------------------------------------------------------

ALTER TABLE osmatch ADD CONSTRAINT osmatch_host_fk
    FOREIGN KEY (fk_host) REFERENCES host (pk);

--------------------------------------------------------------------------------

ALTER TABLE trace ADD CONSTRAINT trace_protocol_fk
    FOREIGN KEY (fk_protocol) REFERENCES protocol (pk);

--------------------------------------------------------------------------------

ALTER TABLE hop ADD CONSTRAINT hop_trace_fk
    FOREIGN KEY (fk_trace) REFERENCES trace (pk);

