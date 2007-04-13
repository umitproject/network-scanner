##
## UserConf.py
## Login : <adriano@localhost.localdomain>
## Started on  Sat Apr  8 16:20:57 2006 Adriano Monteiro Marques
## $Id$
## 
## Copyright (C) 2006 Adriano Monteiro Marques
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##

import os
import os.path

from umitCore.BasePaths import base_paths
from umitCore.Logging import log


umit_conf_content = '''[diff]
colored_diff = True

[output_highlight]
enable_highlight = True

[diff_colors]
unchanged = [65213, 65535, 38862]
added = [29490, 42662, 54079]
not_present = [58079, 19076, 12703]
modified = [63881, 42182, 13193]
'''

target_list_content = ''' '''

recent_scans_content = ''' '''

scan_profile_content = '''[Quick Scan]
description = 
hint = 
options = Disable reverse DNS resolution,Aggressive,Verbose
command = nmap -T Aggressive -v -n %s
annotation = 

[Intense Scan]
description = 
hint = 
options = Version detection,Operating system detection,Aggressive, Verbose
command = nmap -T Aggressive -sV -O -v %s
annotation = 

[Regular Scan]
description = 
hint = 
options = Verbose
command = nmap -v %s
annotation = 

[Quick and verbose scan]
description = 
hint = 
options = Watch packets,Verbose,Debug,Aggressive,Disable reverse DNS resolution
command = nmap -d -T Aggressive --packet_trace -v -n %s
annotation = 

[Operating System Detection]
description = 
hint = 
options = Operating system detection,Verbose
command = nmap -O -v %s
annotation = 

[Quick Services version detection]
description = 
hint = 
options = Version detection,Aggressive,Verbose
command = nmap -T Aggressive -sV -v %s
annotation = 

[Quick Full version Detection Scan]
description = 
hint = 
options = Aggressive,Version detection,Operating system detection,Disable reverse DNS resolution,Verbose
command = nmap -T Aggressive -sV -n -O -v %s
annotation = 

[Quick Operating System detection]
description = 
hint = 
options = Operating system detection,Aggressive,Verbose
command = nmap -T Aggressive -O -v %s
annotation =  '''

profile_editor_content = '''<?xml version="1.0"?>
<interface>
  <groups>
    <group name="Scan"/>
    <group name="Ping"/>
    <group name="Target"/>
    <group name="Source"/>
    <group name="Other"/>
    <group name="Advanced"/>
  </groups>
  <Scan label="Scan options">
    <option_list label="TCP scan: ">
      <option name="None"/>
      <option name="ACK scan"/>
      <option name="FIN scan"/>
      <option name="Null Scan"/>
      <option name="TCP SYN Scan"/>
      <option name="TCP connect Scan"/>
      <option name="Window Scan"/>
      <option name="Xmas Tree"/>
    </option_list>    
    <option_list label="Special scans: ">
      <option name="None"/>
      <option name="IP protocol Scan"/>
      <option name="List Scan"/>
      <option name="Ping scanning"/>
    </option_list>    
    <option_list label="Timing: ">
      <option name="None"/>
      <option name="Paranoid"/>
      <option name="Sneaky"/>
      <option name="Polite"/>
      <option name="Normal"/>
      <option name="Aggressive"/>
      <option name="Insane"/>
    </option_list>    
    <option_check label="FTP bounce attack" option="FTP bounce attack" arg_type="str"/>
    <option_check label="Idle Scan (Zombie)" option="Idle Scan" arg_type="str"/>
    <option_check label="Services version detection" option="Version detection"/>
    <option_check label="Operating system detection" option="Operating system detection"/>
    <option_check label="Disable reverse DNS resolution" option="Disable reverse DNS resolution"/>
    <option_check label="IPv6 support" option="IPv6 support"/>
    <option_check label="Maximum Retries" option="Max Retries" arg_type="int"/>
  </Scan>
  <Ping label="Ping options">
    <option_check label="Don't ping before scanning" option="Ping after Scan"/>
    <option_check label="ICMP ping" option="ICMP ping"/>
    <option_check label="ICMP timestamp request" option="ICMP timestamp"/>
    <option_check label="ICMP netmask request" option="ICMP netmask"/>
    <option_check label="Default ping type" option="Default ping"/>
    <option_check label="ACK ping" option="TCP ACK" arg_type="str"/>
    <option_check label="SYN ping" option="TCP SYN" arg_type="str"/>
    <option_check label="UDP probes" option="UDP Probe" arg_type="str"/>
  </Ping>
  <Target label="Target options">
    <option_check label="Excluded hosts/networks" option="Excluded hosts/networks" arg_type="str"/>
    <option_check label="Excluded hosts/networks from file" option="Excluded hosts/networks from file" arg_type="path"/>
    <option_check label="Read hosts to be scanned from file" option="Read hosts from file" arg_type="path"/>
    <option_check label="Scan random hosts" option="Scan random hosts" arg_type="int"/>
    <option_check label="Ports to scan" option="Ports to scan" arg_type="str"/>
    <option_check label="Only scan ports listed on services" option="Scan services ports"/>
  </Target>
  <Source label="Source options">
    <option_check label="Use decoys to hide identity" option="Use decoys" arg_type="str"/>
    <option_check label="Set source IP address" option="Set source IP" arg_type="str"/>
    <option_check label="Set source port" option="Set source port" arg_type="str"/>
    <option_check label="Set network interface" option="Set network interface" arg_type="str"/>
  </Source>
  <Other label="Other options">
    <option_check label="Extra options definied by user" option="Extra" arg_type="str"/>
    <option_check label="Set IPv4 time to live (ttl)" option="Set IPv4 ttl" arg_type="str"/>
    <option_check label="Fragment IP packets" option="Fragment IP Packets"/>
    <option_check label="Verbosity level" option="Verbose" arg_type="level"/>
    <option_check label="Debugging level" option="Debug" arg_type="level"/>
    <option_check label="Watch packets" option="Watch packets"/>
    <option_check label="Disable randomizing scanned ports" option="Disable randomizing scanned ports"/>
  </Other>
  <Advanced label="Advanced options">
    <option_check label="Time spent before giving up on an IP" option="Time before give up IP" arg_type="int"/>
    <option_check label="Time spent before retransmitting or timing out" option="Time before retransmitting" arg_type="int"/>
    <option_check label="Minimum timeout time per probe" option="Min timeout per probe" arg_type="int"/>
    <option_check label="Specifies the initial probe timeout" option="Initial probe timeout" arg_type="int"/>
    <option_check label="Maximum number of hosts in parallel" option="Max parallel hosts" arg_type="int"/>
    <option_check label="Minimum number of hosts in parallel" option="Min parallel hosts" arg_type="int"/>
    <option_check label="Maximum number of scans in parallel" option="Max parallel scans" arg_type="int"/>
    <option_check label="Minimum number of scans in parallel" option="Min parallel scans" arg_type="int"/>
    <option_check label="Maximum amount of time between probes" option="Max time between probes" arg_type="int"/>
    <option_check label="Minimum amount of time between probes" option="Min time between probes" arg_type="int"/>
  </Advanced>
</interface>'''

options_content = '''<?xml version="1.0"?>
<nmap_options>
  <option name="FTP bounce attack"
          option="-b %s"
          hint="Try to use a given FTP server as proxy"
          arguments="Host in standard URL notation: username:password@server:port"
          need_root="0"/>
          
  <option name="Max Retries"
          option="--max_retries %s"
          hint="Limit the maximum number of retransmissions the port scan engine should do"
          arguments="The number of retransmissions"
          need_root="0"/>
          
  <option name="ACK scan"
          option="-sA"
          hint="Try to discover firewall rulesets"
          arguments=""
          need_root="1"/>
          
  <option name="FIN scan"
          option="-sF"
          hint="Stealth FIN scan mode"
          arguments=""
          need_root="1"/>
          
  <option name="Idle Scan"
          option="-sI %s"
          hint="Use a zombie host to scan a given target"
          arguments="Zombie host address in the format: host[:probeport]"
          need_root="0"/>
          
  <option name="Null Scan"
          option="-sN"
          hint="Stealth Null Scan"
          arguments=""
          need_root="1"/>
          
  <option name="TCP SYN Scan"
          option="-sS"
          hint="Default TCP Scan for root user"
          arguments=""
          need_root="1"/>
          
  <option name="TCP connect Scan"
          option="-sT"
          hint="Default TCP Scan for non-root users"
          arguments=""
          need_root="0"/>
          
  <option name="Window Scan"
          option="-sW"
          hint="Window Scan"
          arguments=""
          need_root="1"/>
          
  <option name="Xmas Tree"
          option="-sX"
          hint="Stealth Xmas Scan"
          arguments=""
          need_root="1"/>
          
  <option name="IP protocol Scan"
          option="-sO"
          hint="Scan for IP protocols"
          arguments=""
          need_root="1"/>
          
  <option name="IP protocol Scan with number"
          option="-sO -p%"
          hint="Scan for IP protocols"
          arguments=""
          need_root="1"/>
          
  <option name="List Scan"
          option="-sL"
          hint=""
          arguments=""
          need_root="0"/>
          
  <option name="Ping scanning"
          option="-sP"
          hint=""
          arguments=""
          need_root="0"/>
          
  <option name="Paranoid"
          option="-T Paranoid"
          hint="Slowest scan (Avoid IDS detection)"
          arguments=""
          need_root="0"/>
          
  <option name="Sneaky"
          option="-T Sneaky"
          hint="Slower scan"
          arguments=""
          need_root="0"/>
          
  <option name="Polite"
          option="-T Polite"
          hint="Slow scan"
          arguments=""
          need_root="0"/>
          
  <option name="Normal"
          option="-T Normal"
          hint="Default scan"
          arguments=""
          need_root="0"/>
          
  <option name="Aggressive"
          option="-T Aggressive"
          hint="Fast scan"
          arguments=""
          need_root="0"/>
          
  <option name="Insane"
          option="-T Insane"
          hint="Faster scan"
          arguments=""
          need_root="0"/>
          
  <option name="Version detection"
          option="-sV"
          hint="Try to detect version of services on scanned hosts"
          arguments=""
          need_root="0"/>
          
  <option name="Operating system detection"
          option="-O"
          hint="Try to detect running OS on scanned hosts"
          arguments=""
          need_root="1"/>
          
  <option name="Disable reverse DNS resolution"
          option="-n"
          hint=""
          arguments=""
          need_root="1"/>
          
  <option name="Ping after Scan"
          option="-P0"
          hint="Don't ping hosts before scanning"
          arguments=""
          need_root="0"/>
          
  <option name="TCP ACK"
          option="-PA%s"
          hint="TCP ACK ping a host or network"
          arguments="List of tageted ports"
          need_root="0"/>
          
  <option name="TCP SYN"
          option="-PS%s"
          hint="TCP SYN ping a host or network"
          arguments="List of tageted ports"
          need_root="1"/>
          
  <option name="UDP Probe"
          option="-PU%s"
          hint="UDP probes to ping a host or network"
          arguments="List of targeted ports"
          need_root="0"/>
          
  <option name="ICMP ping"
          option="-PE"
          hint="ICMP ping a host or network"
          arguments=""
          need_root="1"/>
          
  <option name="ICMP timestamp"
          option="-PP"
          hint="ICMP timestamp request to ping host or network"
          arguments=""
          need_root="1"/>
          
  <option name="ICMP netmask"
          option="-PM"
          hint="ICMP netmask request to ping host or network"
          arguments=""
          need_root="1"/>
          
  <option name="Default ping"
          option="-PB"
          hint="Default Ping"
          arguments=""
          need_root="0"/>
          
  <option name="IPv6 support"
          option="-6"
          hint="Enable IPv6 support"
          arguments=""
          need_root="1"/>
          
  <option name="Excluded hosts/networks"
          option='--exclude %s'
          hint="Exclude given hosts/networks separated by comma"
          arguments=""
          need_root="0"/>

  <option name="Excluded hosts/networks from file"
          option='--excludefile "%s"'
          hint="Exclude hosts/networks inside given file"
          arguments=""
          need_root="0"/>

  <option name="Read hosts from file"
          option='-iL "%s"'
          hint="Read hosts to be scanned from given file"
          arguments=""
          need_root="0"/>
          
  <option name="Scan random hosts"
          option="-iR %s"
          hint="Nmap will generate a given number of random hosts to be scanned. Use '0' to infinite number of random hosts."
          arguments=""
          need_root="0"/>
          
  <option name="Ports to scan"
          option="-p%s"
          hint="Select ports to be scanned"
          arguments=""
          need_root="0"/>

  <option name="Scan services ports"
          option="-F"
          hint="Only scan ports listed on services file"
          arguments=""
          need_root="0"/>
          
  <option name="Use decoys"
          option="-D %s"
          hint="Use given decoys to hide identity"
          arguments=""
          need_root="1"/>
         
  <option name="Set source IP"
          option="-S %s"
          hint="Set source IP address"
          arguments=""
          need_root="1"/>
          
  <option name="Set source port"
          option="--source_port %s"
          hint="Use given ports as source for scans"
          arguments=""
          need_root="0"/>
          
  <option name="Set network interface"
          option="-e %s"
          hint="Use given network interface to scan"
          arguments=""
          need_root="0"/>
          
  <option name="IP protocol scan"
          option="-sO"
          hint="Scan for IP protocols"
          arguments=""
          need_root="1"/>
          
  <option name="List scan"
          option="-sL"
          hint="Scan for IP protocols"
          arguments=""
          need_root="0"/>
          
  <option name="Ping scanning"
          option="-sP"
          hint="Ping hosts in a given network to figure out which hosts are up"
          arguments=""
          need_root="0"/>
          
  <option name="Fragment IP Packets"
          option="-f"
          hint="Split up TCP headers over several packets."
          arguments=""
          need_root="1"/>
          
  <option name="Set IPv4 ttl"
          option="--ttl %s"
          hint="Set IPv4 time to live (ttl)."
          arguments=""
          need_root="1"/>
          
  <option name="Disable randomizing scanned ports"
          option="-r"
          hint="Avoid random port scan"
          arguments=""
          need_root="0"/>
          
  <option name="Fragment Size"
          option="--mtu %s"
          hint="Specify fragments size"
          arguments="Fragment size"
          need_root="1"/>
          
  <option name="UDP Scan"
          option="-sU"
          hint="Scan for udp services"
          arguments=""
          need_root="1"/>
          
  <option name="Specific Scan"
          option="-p%s"
          hint="Scan for an specific IP Protocol"
          arguments="Number of the protocols to be scaned"
          need_root="1"/>
          
  <option name="Limit OS Detection"
          option="--osscan_limit"
          hint="Only try to discover OS if there is at least one open and one closed TCP port"
          arguments=""
          need_root="1"/>
          
  <option name="Time before give up IP"
          option="--host_timeout %s"
          hint="Time spent before giving up on an IP"
          arguments=""
          need_root="0"/>
          
  <option name="Time before retransmitting"
          option="--max_rtt_timeout %s"
          hint="Time spent before retransmitting or timing out"
          arguments=""
          need_root="0"/>

  <option name="Min timeout per probe"
          option="--min_rtt_timeout %s"
          hint="Minimum amount of timeout time per probe"
          arguments=""
          need_root="0"/>
          
  <option name="Initial probe timeout"
          option="--initial_rtt_timeout %s"
          hint="Initial amount of timeout time per probe"
          arguments=""
          need_root="0"/>
          
  <option name="Max parallel hosts"
          option="--max_hostgroup %s"
          hint="Maximum number of parallel hosts"
          arguments=""
          need_root="0"/>
          
  <option name="Min parallel hosts"
          option="--min_hostgroup %s"
          hint="Minimum number of parallel hosts"
          arguments=""
          need_root="0"/>
          
  <option name="Max parallel scans"
          option="--max_parallelism %s"
          hint="Maximum number of parallel scans"
          arguments=""
          need_root="0"/>
          
  <option name="Min parallel scans"
          option="--min_parallelism %s"
          hint="Minimum number of parallel scans"
          arguments=""
          need_root="0"/>
          
  <option name="Max time between probes"
          option="--scan_delay %s"
          hint="Maximum time between scan probes"
          arguments=""
          need_root="0"/>
          
  <option name="Min time between probes"
          option="--max_scan_delay %s"
          hint="Minimum time between scan probes"
          arguments=""
          need_root="0"/>
          
  <option name="None"
          option=""
          hint=""
          arguments=""
          need_root="0"/>
          
  <option name="Extra"
          option="%s"
          hint=""
          arguments=""
          need_root="0"/>
          
  <option name="Verbose"
          option="-v"
          hint="Raise verbosity level"
          arguments=""
          need_root="0"/>
          
  <option name="Debug"
          option="-d"
          hint="Raise debug level"
          arguments=""
          need_root="0"/>
          
  <option name="Watch packets"
          option="--packet-trace"
          hint="Watch packet while they go through the network"
          arguments=""
          need_root="0"/>
</nmap_options>'''

wizard_content = '''<?xml version="1.0"?>
<interface>
  <groups>
    <group name="Scan"/>
    <group name="Ping"/>
    <group name="Target"/>
    <group name="Source"/>
    <group name="Other"/>
  </groups>
  <Scan label="Choose Scan Type">
    <option_list label="TCP scan">
      <option name="None"/>
      <option name="ACK scan"/>
      <option name="FIN scan"/>
      <option name="Null Scan"/>
      <option name="TCP SYN Scan"/>
      <option name="TCP connect Scan"/>
      <option name="Window Scan"/>
      <option name="Xmas Tree"/>
    </option_list>
    <option_list label="Special scans: ">
      <option name="None"/>
      <option name="IP protocol Scan"/>
      <option name="List Scan"/>
      <option name="Ping scanning"/>
    </option_list>
    <option_list label="Timing: ">
      <option name="None"/>
      <option name="Paranoid"/>
      <option name="Sneaky"/>
      <option name="Polite"/>
      <option name="Normal"/>
      <option name="Aggressive"/>
      <option name="Insane"/>
    </option_list>    
    <option_check label="Services version detection" option="Version detection"/>
    <option_check label="Operating system detection" option="Operating system detection"/>
  </Scan>
  <Ping label="Ping options">
    <option_check label="Don't ping before scanning" option="Ping after Scan"/>
    <option_check label="ICMP ping" option="ICMP ping"/>
    <option_check label="ICMP timestamp request" option="ICMP timestamp"/>
    <option_check label="ICMP netmask request" option="ICMP netmask"/>
    <option_check label="Default ping type" option="Default ping"/>
    <option_check label="ACK ping" option="TCP ACK" arg_type="str"/>
    <option_check label="SYN ping" option="TCP SYN" arg_type="str"/>
    <option_check label="UDP probes" option="UDP Probe" arg_type="str"/>
  </Ping>
  <Target label="Target options">
    <option_check label="Excluded hosts/networks" option="Excluded hosts/networks" arg_type="str"/>
    <option_check label="Ports to scan" option="Ports to scan" arg_type="str"/>
    <option_check label="Only scan ports listed on services" option="Scan services ports"/>
  </Target>
  <Source label="Source options">
    <option_check label="Use decoys to hide identity" option="Use decoys" arg_type="str"/>
    <option_check label="Set source IP address" option="Set source IP" arg_type="str"/>
    <option_check label="Set source port" option="Set source port" arg_type="str"/>
  </Source>
  <Other label="Other options">
    <option_check label="Extra options definied by user" option="Extra" arg_type="str"/>
    <option_check label="Set IPv4 time to live (ttl)" option="Set IPv4 ttl" arg_type="str"/>
    <option_check label="Fragment IP packets" option="Fragment IP Packets"/>
    <option_check label="Verbosity level" option="Verbose" arg_type="level"/>
    <option_check label="Debugging level" option="Debug" arg_type="level"/>
    <option_check label="Watch packets" option="Watch packets"/>
  </Other>
</interface>'''


def create_user_dir(user_home):
    log.debug("Create user dir at given home: %s" % user_home)
    user_dir = os.path.join(user_home, base_paths['config_dir'])
    
    if os.path.exists(user_home) and os.access(user_home, os.R_OK and os.W_OK)\
           and not os.path.exists(user_dir):
        os.mkdir(user_dir)
        log.debug("Umit user dir successfully created! %s" % user_dir)
    else:
        log.warning("No permissions to create user dir!")
        return False

    return dict(user_dir=user_dir,
                config_dir=user_dir,
                config_file=create_umit_conf(user_dir),
                target_list=create_target_list(user_dir),
                recent_scans=create_recent_scans(user_dir),
                scan_profile=create_scan_profile(user_dir),
                profile_editor=create_profile_editor(user_dir),
                options=create_options(user_dir),
                wizard=create_wizard(user_dir))

def create_config_file(user_dir, filename, default_content):
    log.debug("create_config_file %s" % filename)
    
    config_file_path = os.path.join(user_dir, filename)
    if not os.path.exists(config_file_path):
        open(config_file_path, 'w').write(default_content)
    return config_file_path

def create_profile_editor(user_dir):
    return create_config_file(user_dir, base_paths['profile_editor'], profile_editor_content)

def create_recent_scans(user_dir):
    return create_config_file(user_dir, base_paths['recent_scans'], recent_scans_content)

def create_scan_profile(user_dir):
    return create_config_file(user_dir, base_paths['scan_profile'], scan_profile_content)

def create_target_list(user_dir):
    return create_config_file(user_dir, base_paths['target_list'], target_list_content)

def create_umit_conf(user_dir):
    return create_config_file(user_dir, base_paths['config_file'], umit_conf_content)

def create_wizard(user_dir):
    return create_config_file(user_dir, base_paths['wizard'], wizard_content)

def create_options(user_dir):
    return create_config_file(user_dir, base_paths['options'], options_content)


if __name__ == "__main__":
    create_user_dir("/home/adriano")
