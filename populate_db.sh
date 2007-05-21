#!/bin/sh

command=`which sqlite3`
database='testing.db'

# sample data for testing
$command $database "INSERT INTO scanner (name, version) VALUES ('nmap', '4.20')"

$command $database "INSERT INTO scan_type (name) VALUES ('SYN')"
$command $database "INSERT INTO scan_type (name) VALUES ('FIN')"
$command $database "INSERT INTO scan_type (name) VALUES ('XMAS')"

$command $database "INSERT INTO protocol (name) VALUES ('TCP')"
$command $database "INSERT INTO protocol (name) VALUES ('UDP')"

$command $database "INSERT INTO host_state (state) VALUES ('up')"
$command $database "INSERT INTO host_state (state) VALUES ('down')"
$command $database "INSERT INTO host_state (state) VALUES ('unknown')"

$command $database "INSERT INTO port_state (state) VALUES ('closed')"
$command $database "INSERT INTO port_state (state) VALUES ('open')"
$command $database "INSERT INTO port_state (state) VALUES ('filtered')"

$command $database "INSERT INTO service (pk, name) VALUES (21, 'ftp')"
$command $database "INSERT INTO service (pk, name) VALUES (80, 'http')"
$command $database "INSERT INTO service (pk, name) VALUES (3128, 'squid-http')"

$command $database "INSERT INTO vendor (name) VALUES ('Apple')"
$command $database "INSERT INTO vendor (name) VALUES ('Cisco')"
$command $database "INSERT INTO vendor (name) VALUES ('Microsoft')"
$command $database "INSERT INTO vendor (name) VALUES ('Linksys')"
$command $database "INSERT INTO vendor (name) VALUES ('IBM')"
$command $database "INSERT INTO vendor (name) VALUES ('Linux')"
#--

echo "$database populated."
