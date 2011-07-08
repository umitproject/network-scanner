-- Copyright (C) 2009 Adriano Monteiro Marques.
--
-- Authors: Joao Paulo de Souza Medeiros <ignotus@umitproject.org>
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

-- DROP TABLE software CASCADE;

CREATE TABLE software
(
    pk INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    fk_vendor INTEGER NOT NULL REFERENCES vendor (pk),
    fk_stype INTEGER NOT NULL REFERENCES stype (pk),
    fk_name INTEGER NOT NULL REFERENCES name (pk),
    fk_note INTEGER REFERENCES note (pk),
    description TEXT,
    added DATETIME NOT NULL,
    updated DATETIME NOT NULL
);

-- ALTER TABLE software ADD CONSTRAINT software_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE fingerprint CASCADE;

CREATE TABLE fingerprint
(
    pk INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    fk_sig1 INTEGER NOT NULL REFERENCES s_attractor (pk),
    fk_raw1 INTEGER REFERENCES r_tcpisn (pk),
    added DATETIME NOT NULL,
    updated DATETIME NOT NULL,
    fk_software INTEGER NOT NULL
);

-- ALTER TABLE fingerprint ADD CONSTRAINT fingerprint_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE s_attractor CASCADE;

CREATE TABLE s_attractor
(
    pk INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    samples INTEGER NOT NULL,
    fp BLOB NOT NULL,
    description TEXT
);

-- ALTER TABLE s_attractor ADD CONSTRAINT s_attractor_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE r_tcpisn CASCADE;

CREATE TABLE r_tcpisn
(
    pk INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    samples INTEGER NOT NULL,
    series BLOB NOT NULL,
    description TEXT
);

-- ALTER TABLE r_tcpisn ADD CONSTRAINT r_tcpisn_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE vendor CASCADE;

CREATE TABLE vendor
(
    pk INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
);

-- ALTER TABLE vendor ADD CONSTRAINT vendor_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE stype CASCADE;

CREATE TABLE stype
(
    pk INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
);

-- ALTER TABLE stype ADD CONSTRAINT stype_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE name CASCADE;

CREATE TABLE name
(
    pk INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    description TEXT
);

-- ALTER TABLE name ADD CONSTRAINT name_pk PRIMARY KEY (pk);

--------------------------------------------------------------------------------

-- DROP TABLE note CASCADE;

CREATE TABLE note
(
    pk INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    note TEXT NOT NULL,
    keywords TEXT
);

-- ALTER TABLE note ADD CONSTRAINT note_pk PRIMARY KEY (pk);


--------------------------------------------------------------------------------
-- FOREIGN KEYS                                                               --
--------------------------------------------------------------------------------

-- ALTER TABLE software ADD CONSTRAINT
--     software_vendor_fk FOREIGN KEY(fk_vendor) REFERENCES vendor (pk);

-- ALTER TABLE software ADD CONSTRAINT
--     software_stype_fk FOREIGN KEY(fk_stype) REFERENCES stype (pk);

-- ALTER TABLE software ADD CONSTRAINT
--     software_name_fk FOREIGN KEY(fk_name) REFERENCES name (pk);

-- ALTER TABLE software ADD CONSTRAINT
--     software_note_fk FOREIGN KEY(fk_note) REFERENCES note (pk);

-- ALTER TABLE fingerprint ADD CONSTRAINT
--     fingerprint_sig1_fk FOREIGN KEY(fk_sig1) REFERENCES s_attractor (pk);

-- ALTER TABLE fingerprint ADD CONSTRAINT
--     fingerprint_raw1_fk FOREIGN KEY(fk_raw1) REFERENCES r_tcpisn (pk);
