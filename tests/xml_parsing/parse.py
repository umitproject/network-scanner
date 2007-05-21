import os
import sys
from umitCore.NmapParser import NmapParser

def print_parsed(npsax):
    print npsax.nmap["scaninfo"]
    return

    print "SCAN"
    print "Args:", npsax.nmap["nmaprun"]["args"]
    print "Start time:", npsax.nmap["nmaprun"]["start"]
    print "Finish time:", npsax.nmap["runstats"]["finished_time"]
    print "XML output version:", npsax.nmap["nmaprun"]["xmloutputversion"]
    print "NMAP version:", npsax.nmap["nmaprun"]["version"]
    print "Verbose:", npsax.nmap["verbose"]
    print "Debugging:", npsax.nmap["debugging"]
    print "Scanner:", npsax.nmap["nmaprun"]["scanner"]

    print "\n\nHOSTS"
    for host in npsax.nmap["hosts"]:
        print "-"*35
        print "Comment:", host.comment
        print "TCP Sequence:", host.tcpsequence
        print "TCP TS Sequence:", host.tcptssequence
        print "IP ID Sequence:", host.ipidsequence
        print "Uptime:", host.uptime
        print "OS Match:", host.osmatch
        print "Ports:", host.ports
        print "Ports used:", host.ports_used
        print "OS Class:", host.osclasses
        print "Hostname:", host.hostnames
        print "IP:", host.ip
        print "IPv6:", host.ipv6
        print "MAC:", host.mac
        print "State:", host.state


if __name__ == "__main__":
    files = sys.argv[1:]
    if not files:
        print "Especify some xml to parse"
        sys.exit(0)

    for file in files:
        try:
            os.stat(file)
        except OSError, e:
            print "OSError:", e
            continue

        np = NmapParser(file)
        np.parse()

        print_parsed(np)
