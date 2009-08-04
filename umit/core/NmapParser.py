# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
#         Guilherme Polo <ggpolo@gmail.com>
#         João Paulo de Souza Medeiros <ignotus21@gmail.com>
#         Luis A. Bastiao Silva <luis.kop@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import re
import time
import calendar

from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl

UNKNOWN = "Unknown"

class AttributesImplDict(dict, AttributesImpl):
    """Use this for displaying AttributesImpl just like a dict."""

class HostInfo(object):
    def __init__(self, host_id):
        self.osclass = []
        self.osmatch = []
        self.osfingerprint = []
        self.portused = []
        self.ports = []
        self.extraports = []
        self.tcpsequence = {}
        self.hostnames = []
        self.tcptssequence = {}
        self.ipidsequence = {}
        self.trace = {'port': '', 'proto': '', 'hop': []}
        self.status = {}
        self.address = []
        self.hostscript = []

        # Umit extension
        self.id = host_id
        self.comment = ''

        # XXX this structure it not being used yet.
        self.nmap_host = {
                'status': {'state': '', 'reason': ''},
                'smurf': {'responses': ''},
                'times': {'to': '', 'srtt': '', 'rttvar': ''},
                'hostscript': [],
                'distance': {'value': ''},
                'trace': {'port': '', 'proto': '', 'hop': []},
                'address': [],
                'hostnames': [],
                'ports': [],
                'uptime': {'seconds': '', 'lastboot': ''},
                'tcpsequence': {'index': '', 'values': '', 'class': ''},
                'tcptssequence': {'values': '', 'class': ''},
                'ipidsequence': {'values': '', 'class': ''},
                'os': {}
                }

    # Host ID
    def get_id(self):
        try:
            return self._id
        except AttributeError:
            raise Exception("Id is not set yet.")

    def set_id(self, host_id):
        try:
            self._id = int(host_id)
        except (TypeError, ValueError):
            raise Exception("Invalid id! It must represent an integer, "
                    "received %r" % host_id)

    # VENDOR
    def get_vendor(self):
        vendor = UNKNOWN
        for address in self.address:
            if address['addrtype'] != 'mac':
                continue
            try:
                vendor = address['vendor']
                break
            except KeyError:
                pass

        return vendor

    # TRACEROUTE
    def get_hop_by_ttl(self, ttl):
        for hop in self.trace['hop']:
            if ttl == int(hop['ttl']):
                return hop
        return None

    def get_number_of_hops(self):
        count = 0
        for hop in self.trace['hop']:
            if int(hop['ttl']) > count:
                count = int(hop['ttl'])
        return count

    # UPTIME
    # FORMAT: {"seconds":"", "lastboot":""}
    def set_uptime(self, uptime):
        self._uptime = uptime

    def get_uptime(self):
        if self._uptime:
            return self._uptime

        # Avoid empty dict return
        return {'seconds': '', 'lastboot': ''}

    # HOSTNAME
    def get_hostname(self):
        hostname = []

        if self.hostnames:
            try:
                hostname.append(self.hostnames[0]['name'])
            except KeyError:
                pass

        for addr in self.address:
            if addr['addrtype'] == 'mac':
                format = '(%s)'
            else:
                format = '%s'
            hostname.append(format % addr['addr'])

        return ' '.join(hostname) or UNKNOWN

    def get_open_ports(self):
        open_count = 0
        for port in self.ports:
            if port['state'] == 'open':
                open_count += 1

        return open_count

    def get_filtered_ports(self):
        filtered_count = 0
        for port in self.ports:
            if port['state'] == 'filtered':
                filtered_count += 1
        for extra in self.extraports:
            if extra['state'] == 'filtered':
                filtered_count += int(extra['count'])

        return filtered_count

    def get_closed_ports(self):
        closed_count = 0
        for port in self.ports:
            if port['state'] == 'closed':
                closed_count += 1
        for extra in self.extraports:
            if extra['state'] == 'closed':
                closed_count += int(extra['count'])

        return closed_count

    def get_scanned_ports(self):
        scanned = len(self.ports)
        for extra in self.extraports:
            scanned += int(extra['count'])

        return scanned

    def get_services(self):
        services = []
        for port in self.ports:
            services.append({
                'service_name': port.get('name', UNKNOWN),
                'portid': port.get('portid', ''),
                'service_version': port.get('version', UNKNOWN),
                'service_product': port.get('product', ''),
                'port_state': port.get('state', UNKNOWN),
                'protocol': port.get('protocol', '')})
        return services

    def _get_status_state(self):
        return self.status.get('state', '')

    def _get_type_address(self, addrtype):
        for addr in self.address:
            if addr['addrtype'] == addrtype:
                return addr

    def _get_ipv4(self):
        return self._get_type_address('ipv4')

    def _get_ipv6(self):
        return self._get_type_address('ipv6')

    def _get_mac(self):
        return self._get_type_address('mac')

    # Properties
    id = property(get_id, set_id)
    uptime = property(get_uptime, set_uptime)
    services = property(get_services)
    state = property(_get_status_state, doc="Get the host status state")
    ip = property(_get_ipv4, doc="Return the first ipv4 address found")
    ipv6 = property(_get_ipv6, doc="Return the first ipv6 address found")
    mac = property(_get_mac, doc="Return the first mac address found")

    _uptime = {}


class ParserBasics(object):
    def __init__ (self):
        self.nmap = {
                'nmaprun': {},
                'runstats': {
                    'finished': {},
                    'hosts': {'up': '', 'down': '', 'total': ''}
                    },
                'verbose': {'level': ''},
                'debugging': {'level': ''},
                'scaninfo': [],
                'taskbegin': [],
                'taskprogress': [],
                'taskend': [],
                #'host': [],
                'hosts': []
                }

    def set_host_comment(self, host_id, comment):
        for host in self.nmap['hosts']:
            if host.id == host_id:
                host.comment = comment
                break
        else:
            raise Exception("Comment could not be saved! Host not "
                    "found at NmapParser!")

    def get_host_comment(self, host_id):
        for host in self.nmap.get('hosts', []):
            if host.id == host_id:
                return host.comment
        else:
            raise Exception("Comment could not be saved! Host not "
                    "found at NmapParser!")

    def get_profile(self):
        return self.nmap['nmaprun'].get('profile', '')

    def set_profile(self, profile):
        self.nmap['nmaprun']['profile'] = profile

    def get_profile_name(self):
        return self.nmap['nmaprun'].get('profile_name', '')

    def set_profile_name(self, name):
        self.nmap['nmaprun']['profile_name'] = name

    def get_profile_description(self):
        return self.nmap['nmaprun'].get('description', '')

    def set_profile_description(self, description):
        self.nmap['nmaprun']['description'] = description

    def get_profile_hint(self):
        return self.nmap['nmaprun'].get('hint', '')

    def set_profile_hint(self, hint):
        self.nmap['nmaprun']['hint'] = hint

    def get_profile_annotation(self):
        return self.nmap['nmaprun'].get('annotation', '')

    def set_profile_annotation(self, annotation):
        self.nmap['nmaprun']['annotation'] = annotation

    def get_profile_options(self):
        options = self.nmap['nmaprun'].get('options', '')
        if isinstance(options, list):
            return ','.join(options)
        elif isinstance(options, basestring):
            return options

    def set_profile_options(self, options):
        if isinstance(options, (list, basestring)):
            self.nmap['nmaprun']['options'] = options
        elif isinstance(options, dict):
            self.nmap['nmaprun']['options'] = options.keys()
        else:
            raise Exception("Profile option error: wrong argument format! "
                    "Need a string, list or dict.")

    def get_target(self):
        return self.nmap['nmaprun'].get('target', '')

    def set_target(self, target):
        self.nmap['nmaprun']['target'] = target

    def get_nmap_output(self):
        return self.nmap['nmaprun'].get('nmap_output', '')

    def set_nmap_output(self, nmap_output):
        self.nmap['nmaprun']['nmap_output'] = nmap_output

    def get_debugging_level (self):
        return self.nmap['debugging'].get('level', '')

    def set_debugging_level(self, level):
        self.nmap['debugging']['level'] = level

    def set_debugging(self, debug):
        self.nmap['debugging'] = debug

    def get_verbose_level (self):
        return self.nmap['verbose'].get('level', '')

    def set_verbose_level(self, level):
        self.nmap['verbose']['level'] = level

    def set_verbose(self, verbose):
        self.nmap['verbose'] = verbose

    def get_scaninfo(self):
        return self.nmap.get('scaninfo', [])

    def set_scaninfo(self, info):
        self.nmap['scaninfo'] = info

    def append_scaninfo(self, info):
        self.nmap['scaninfo'].append(info)

    def get_services_scanned(self):
        services = [scan['services'] for scan in self.nmap.get('scaninfo', [])]
        return ','.join(services)

    def get_nmap_command(self):
        return self._verify_output_options(self.nmap['nmaprun'].get('args', ''))

    def set_nmap_command(self, command):
        self.nmap['nmaprun']['args'] = self._verify_output_options(command)

    def get_scan_type(self):
        return [stype['type'] for stype in self.nmap.get('scaninfo', [])]

    def get_protocol (self):
        return [proto['protocol'] for proto in self.nmap.get('scaninfo', [])]

    def get_num_services(self):
        num = 0
        for sinfo in self.nmap.get('scaninfo', []):
            num += int(sinfo['numservices'])

        return num

    def get_date(self):
        epoch = int(self.nmap['nmaprun'].get('start', '0'))
        return time.localtime(epoch)

    def get_start(self):
        return self.nmap['nmaprun'].get('start', '0')

    def set_start(self, start):
        self.nmap['nmaprun']['start'] = start

    def set_date(self, date):
        if type(date) == type(int):
            self.nmap['nmaprun']['start'] = date
        else:
            raise Exception("Wrong date format. Date should be saved "
                    "in epoch format!")

    def get_open_ports(self):
        open_count = 0
        for host in self.nmap.get('hosts', []):
            open_count += host.get_open_ports()

        return open_count

    def get_filtered_ports(self):
        filtered_count = 0
        for host in self.nmap.get('hosts', []):
            filtered_count += host.get_filtered_ports()

        return filtered_count

    def get_closed_ports(self):
        closed_count = 0
        for host in self.nmap['hosts']:
            closed_count += host.get_closed_ports()

        return closed_count

    def get_formated_date(self):
        date = self.get_date()
        return '%s %s, %s - %s:%s' % (calendar.month_name[date[1]],
                                      str(date[2]),
                                      str(date[0]),
                                      str(date[3]).zfill(2),
                                      str(date[4]).zfill(2))

    def get_scanner(self):
        return self.nmap['nmaprun'].get('scanner', '')

    def set_scanner(self, scanner):
        self.nmap['nmaprun']['scanner'] = scanner

    def get_scanner_version (self):
        return self.nmap['nmaprun'].get('version', '')

    def set_scanner_version(self, version):
        self.nmap['nmaprun']['version'] = version

    ## Addresses
    def get_type_addresses(self, addrtype):
        addresses = []
        for host in self.nmap.get('hosts', []):
            for addr in host.address:
                if addr['addrtype'] == addrtype:
                    addresses.append(addr['addr'])
        return addresses

    # IPv4
    def get_ipv4_addresses(self):
        return self.get_type_addresses('ipv4')

    # MAC
    def get_mac_addresses(self):
        return self.get_type_addresses('mac')

    # IPv6
    def get_ipv6_addresses(self):
        return self.get_type_addresses('ipv6')


    def get_hostnames(self):
        hostnames = []
        for host in self.nmap.get('hosts', []):
            hostnames.extend(host.hostnames)
        return hostnames

    def get_ports(self):
        ports = []
        for host in self.nmap.get('hosts', []):
            ports.append(host.ports)

        return ports

    def get_hosts(self):
        return self.nmap.get('hosts', None)

    def get_runstats(self):
        return self.nmap.get('runstats', None)

    def set_runstats(self, stats):
        self.nmap['runstats'] = stats

    def get_hosts_down(self):
        return self.nmap['runstats']['hosts'].get('down', 0)

    def set_hosts_down(self, down):
        self.nmap['runstats']['hosts']['down'] = int(down)

    def get_hosts_up(self):
        return self.nmap['runstats']['hosts'].get('up', 0)

    def set_hosts_up(self, up):
        self.nmap['runstats']['hosts']['up'] = int(up)

    def get_hosts_total(self):
        return self.nmap['runstats']['hosts'].get('total', 0)

    def set_hosts_total(self, scanned):
        self.nmap['runstats']['hosts']['total'] = int(scanned)

    def get_finish_time(self):
        return self.nmap['runstats']['finished'].get('timestr', '')

    def set_finish_time(self, finish):
        self.nmap['runstats']['finished']['timestr'] = finish

    def get_finish_epoch_time(self):
        return time.localtime(self.nmap['runstats']['finished'].get('time', 0))

    def set_finish_epoch_time(self, epoch_time):
        self.nmap['runstats']['finished']['time'] = float(epoch_time)

    def get_scan_name(self):
        return self.nmap.get('scan_name', '')

    def set_scan_name(self, scan_name):
        self.nmap['scan_name'] = scan_name

    def get_formated_finish_date(self):
        date = self.finish_epoch_time
        return '%s %s, %s - %s:%s' % (calendar.month_name[date[1]],
                                      str(date[2]),
                                      str(date[0]),
                                      str(date[3]).zfill(2),
                                      str(date[4]).zfill(2))

    def _verify_output_options(self, command):
        found = re.findall('(-o[XGASN]{1}) {0,1}', command)
        splited = command.split(' ')

        if found:
            for option in found:
                pos = splited.index(option)
                del splited[pos+1]
                del splited[pos]

        return ' '.join(splited)

    def get_comments(self):
        return [host.comment for host in self.nmap['hosts']]

    profile = property(get_profile, set_profile)
    profile_name = property(get_profile_name, set_profile_name)
    profile_description = property(get_profile_description,
                                   set_profile_description)
    profile_hint = property(get_profile_hint, set_profile_hint)
    profile_annotation = property(get_profile_annotation,
                                  set_profile_annotation)
    profile_options = property(get_profile_options, set_profile_options)
    target = property(get_target, set_target)
    nmap_output = property(get_nmap_output, set_nmap_output)
    debugging_level = property(get_debugging_level, set_debugging_level)
    verbose_level = property(get_verbose_level, set_verbose_level)
    scaninfo = property(get_scaninfo, set_scaninfo)
    services_scanned = property(get_services_scanned)
    nmap_command = property(get_nmap_command, set_nmap_command)
    scan_type = property(get_scan_type)
    protocol = property(get_protocol)
    num_services = property(get_num_services)
    date = property(get_date, set_date)
    open_ports = property(get_open_ports)
    filtered_ports = property(get_filtered_ports)
    closed_ports = property(get_closed_ports)
    formated_date = property(get_formated_date)
    scanner = property(get_scanner, set_scanner)
    scanner_version = property(get_scanner_version, set_scanner_version)
    ipv4 = property(get_ipv4_addresses)
    mac = property(get_mac_addresses)
    ipv6 = property(get_ipv6_addresses)
    hostnames = property(get_hostnames)
    ports = property(get_ports)
    hosts = property(get_hosts)
    runstats = property(get_runstats, set_runstats)
    hosts_down = property(get_hosts_down, set_hosts_down)
    hosts_up = property(get_hosts_up, set_hosts_up)
    hosts_total = property(get_hosts_total, set_hosts_total)
    finish_time = property(get_finish_time, set_finish_time)
    finish_epoch_time = property(get_finish_epoch_time, set_finish_epoch_time)
    formated_finish_date = property(get_formated_finish_date)
    comments = property(get_comments)
    start = property(get_start, set_start)
    scan_name = property(get_scan_name, set_scan_name)


class NmapParserSAX(ParserBasics, ContentHandler):
    def __init__(self):
        ParserBasics.__init__(self)
        self.id_sequence = 0

        self.in_run_stats = False
        self.in_host = False
        self.in_ports = False
        self.in_port = False
        self.in_os = False
        self.in_trace = False

        # _tmp_port is used while parsing a port entity
        self._tmp_port = {}

        self.nmap_xml_file = None
        self.unsaved = False

    def set_parser(self, parser):
        self.parser = parser

    def set_xml_file(self, nmap_xml_file):
        self.nmap_xml_file = nmap_xml_file

    def parse(self):
        if self.nmap_xml_file:
            if isinstance(self.nmap_xml_file, basestring):
                self.parser.parse(self.nmap_xml_file)
            else:
                self.nmap_xml_file.seek(0)
                self.parser.parse(self.nmap_xml_file)
        else:
            raise Exception("There's no file to be parsed!")

    def generate_id(self):
        self.id_sequence += 1
        return self.id_sequence

    def _parse_nmaprun(self, attrs):
        d = self.nmap['nmaprun']

        self.scanner = attrs.get('scanner', '')
        self.scanner_version = attrs.get('version', '')
        self.start = attrs.get('start', '')
        self.nmap_command = attrs.get('args', '')
        d['xmloutputversion'] = attrs.get('xmloutputversion', '')

        # Umit extension
        self.nmap_output = attrs.get('nmap_output', '')
        self.profile = attrs.get('profile', '')
        self.profile_name = attrs.get('profile_name', '')
        self.profile_hint = attrs.get('hint', '')
        self.profile_description = attrs.get('description', '')
        self.profile_annotation = attrs.get('annotation', '')
        self.profile_options = attrs.get('options', '')
        self.target = attrs.get('target', '')
        self.scan_name = attrs.get('scan_name', '')

    def _parse_runstats_finished(self, attrs):
        self.finish_time = attrs.get('timestr', '')
        self.finish_epoch_time = attrs.get('time', 0)

    def _parse_runstats_hosts(self, attrs):
        self.hosts_up = attrs.get('up', 0)
        self.hosts_down = attrs.get('down', 0)
        self.hosts_total = attrs.get('total', 0)

    def _parse_host(self, attrs):
        self.host_info = HostInfo(self.generate_id())
        # Umit extension
        self.host_info.comment = attrs.get('comment', '')


    def startElement(self, name, attrs):
        # AttributesImplDict is used here so utils/xmldisplay.py can display
        # instances of AttributesImpl without any effort.
        attrs = AttributesImplDict(attrs)

        if name == 'nmaprun':
            self._parse_nmaprun(attrs)

        elif name in ('verbose', 'debugging'):
            getattr(self, 'set_%s' % name)(attrs.copy())

        elif name in ('scaninfo', 'taskbegin', 'taskprogress', 'taskend'):
            self.nmap[name].append(attrs.copy())

        # Parse runstats
        elif name == 'runstats':
            self.in_run_stats = True
        elif self.in_run_stats and name == 'finished':
            self._parse_runstats_finished(attrs)
        elif self.in_run_stats and name == 'hosts':
            self._parse_runstats_hosts(attrs)

        # Parse hosts
        elif name == 'host':
            self.in_host = True
            self._parse_host(attrs)
        elif self.in_host and name in ('status', 'times', 'smurf', 'distance',
                'uptime', 'tcpsequence', 'tcptssequence', 'ipidsequence'):
            setattr(self.host_info, name, attrs.copy())
        elif self.in_host and name in ('address', 'hostscript'):
            getattr(self.host_info, name).append(attrs.copy())
        elif self.in_host and name == 'hostnames':
            self.in_hostnames = True
        elif self.in_host and self.in_hostnames and name == 'hostname':
            self.host_info.hostnames.append(attrs.copy())
        # port
        elif self.in_host and name == 'ports':
            self.in_ports = True
        elif self.in_host and self.in_ports and name == 'extraports':
            # XXX extrareasons not supported yet
            self.host_info.extraports.append(attrs.copy())
        elif self.in_host and self.in_ports and name == 'port':
            self.in_port = True
            self._tmp_port.update(attrs)
        elif self.in_host and self.in_ports and \
                self.in_port and name in ('state', 'service'):
            self._tmp_port.update(attrs)
        # os
        elif self.in_host and name == 'os':
            self.in_os = True
        elif self.in_host and self.in_os and name in ('osmatch',
                'osclass', 'portused', 'osfingerprint'):
            getattr(self.host_info, name).append(attrs.copy())
        # trace
        elif self.in_host and name == 'trace':
            self.in_trace = True
            self.host_info.trace.update(attrs.copy())
        elif self.in_trace and name == 'hop':
            self.host_info.trace['hop'].append(attrs.copy())


    def endElement(self, name):
        if name == 'runstats':
            self.in_run_stats = False
        elif name == 'host':
            self.in_host = False
            self.nmap['hosts'].append(self.host_info)
            del self.host_info
        elif self.in_host and name == 'hostnames':
            self.in_hostnames = False
        elif self.in_host and name == 'ports':
            self.in_ports = False
        elif self.in_host and self.in_ports and name == 'port':
            self.in_port = False
            self.host_info.ports.append(self._tmp_port.copy())
            self._tmp_port.clear()
        elif self.in_host and self.in_os and name == 'os':
            self.in_os = False
        elif self.in_host and name == 'trace':
            self.in_trace = False


    def write_xml(self, xml_file):
        xml_file = self._verify_file(xml_file)
        self.write_parser = XMLGenerator(xml_file)

        # First, start the document:
        self.write_parser.startDocument()

        # Nmaprun element:
        self._write_nmaprun()

        # Scaninfo element:
        self._write_scaninfo()

        # Verbose element:
        self._write_verbose()

        # Debugging element:
        self._write_debugging()

        # Hosts elements:
        self._write_hosts()

        # Runstats element:
        self._write_runstats()

        # End of the xml file:
        self.write_parser.endElement('nmaprun')
        self.write_parser.endDocument()

    def _write_runstats(self):
        ##################
        # Runstats element
        self.write_parser.startElement('runstats', AttributesImpl(dict()))

        ## Finished element
        self.write_parser.startElement('finished',
                AttributesImpl({
                    'time': str(time.mktime(self.finish_epoch_time)),
                    'timestr': self.finish_time})
                )
        self.write_parser.endElement('finished')

        ## Hosts element
        self.write_parser.startElement('hosts',
                AttributesImpl({
                    'up': str(self.hosts_up),
                    'down': str(self.hosts_down),
                    'total': str(self.hosts_total)})
                )
        self.write_parser.endElement('hosts')


        self.write_parser.endElement('runstats')
        # End of Runstats element
        #########################

    def _write_hosts(self):
        for host in self.hosts:
            # Start host element
            self.write_parser.startElement('host',
                    AttributesImpl({
                        'comment': host.comment})
                    )

            # Status element
            self.write_parser.startElement('status',
                    AttributesImpl({
                        'state': host.status['state']})
                    )
            self.write_parser.endElement('status')


            ##################
            # Address elements
            for address in host.address:
                self.__remove_none(address)
                self.write_parser.startElement('address',
                        AttributesImpl({
                            'addr': address.get('addr', ''),
                            'vendor': address.get('vendor', ''),
                            'addrtype': address.get('addrtype', '')})
                        )
                self.write_parser.endElement('address')
            # End of Address elements
            #########################


            ###################
            # Hostnames element
            self.write_parser.startElement('hostnames', AttributesImpl({}))

            for hname in host.hostnames:
                if not isinstance(hname, dict):
                    continue
                self.write_parser.startElement('hostname',
                        AttributesImpl({
                            'name': hname.get('name', ''),
                            'type': hname.get('type', '')})
                        )
                self.write_parser.endElement('hostname')

            self.write_parser.endElement('hostnames')
            # End of Hostnames element
            ##########################


            ###############
            # Ports element
            self.write_parser.startElement('ports', AttributesImpl({}))

            ## Extraports elements
            for export in host.extraports:
                self.__remove_none(export)
                self.write_parser.startElement('extraports',
                        AttributesImpl({
                            'count': str(export.get('count', '')),
                            'state': export.get('state', '')})
                        )
                self.write_parser.endElement('extraports')

            ## Port elements
            for port in host.ports:
                self.__remove_none(port)
                self.write_parser.startElement('port',
                    AttributesImpl({
                        'portid': port.get('portid', ''),
                        'protocol': port.get('protocol', '')})
                    )

                ### Port state
                self.write_parser.startElement('state',
                        AttributesImpl({
                            'state': port.get('state', '')})
                        )
                self.write_parser.endElement('state')

                ### Port service info
                self.write_parser.startElement('service',
                        AttributesImpl({
                            'conf': port.get('conf', ''),
                            'method': port.get('method', ''),
                            'name': port.get('name', ''),
                            'product': port.get('product', ''),
                            'version': port.get('version', ''),
                            'extrainfo': port.get('extrainfo', '')})
                        )
                self.write_parser.endElement('service')

                self.write_parser.endElement('port')

            self.write_parser.endElement('ports')
            # End of Ports element
            ######################


            ############
            # OS element
            self.write_parser.startElement('os', AttributesImpl({}))

            ## Ports used elements
            for pu in host.portused:
                if not isinstance(pu, dict):
                    continue

                self.__remove_none(pu)
                self.write_parser.startElement('portused',
                        AttributesImpl({
                            'state': pu.get('state', ''),
                            'proto': pu.get('proto', ''),
                            'portid': pu.get('portid', '')})
                        )
                self.write_parser.endElement('portused')

            ## Osclass elements
            for oc in host.osclass:
                if not isinstance(oc, dict):
                    continue

                self.__remove_none(oc)
                self.write_parser.startElement('osclass',
                        AttributesImpl({
                            'vendor': oc.get('vendor', ''),
                            'osfamily': oc.get('osfamily', ''),
                            'type': oc.get('type', ''),
                            'osgen': oc.get('osgen', ''),
                            'accuracy': oc.get('accuracy', '')})
                        )
                self.write_parser.endElement('osclass')

            ## Osmatch elements
            for om in host.osmatch:
                if not isinstance(om, dict):
                    continue

                self.__remove_none(om)
                self.write_parser.startElement('osmatch',
                        AttributesImpl({
                            'name': om.get('name', ''),
                            'accuracy': om.get('accuracy', '')})
                        )
                self.write_parser.endElement('osmatch')

            ## Osfingerprint element
            if isinstance(host.osfingerprint, dict):
                self.__remove_none(host.osfingerprint)
                self.write_parser.startElement('osfingerprint',
                        AttributesImpl({
                            'fingerprint': host.osfingerprint.get(
                                'fingerprint', '')})
                        )
                self.write_parser.endElement('osfingerprint')


            self.write_parser.endElement('os')
            # End of OS element
            ###################

            # Uptime element
            if isinstance(host.uptime, dict):
                self.write_parser.startElement('uptime',
                        AttributesImpl({
                            'seconds': host.uptime.get('seconds', ''),
                            'lastboot': host.uptime.get('lastboot', '')})
                        )
                self.write_parser.endElement('uptime')

            #####################
            # Sequences elementes
            ## TCP Sequence element
            if isinstance(host.tcpsequence, dict):
                self.write_parser.startElement('tcpsequence',
                        AttributesImpl({
                            'index': host.tcpsequence.get('index', ''),
                            'class': host.tcpsequence.get('class', ''),
                            'difficulty': host.tcpsequence.get('difficulty',
                                ''),
                            'values': host.tcpsequence.get('values', '')})
                        )
                self.write_parser.endElement('tcpsequence')

            ## IP ID Sequence element
            if isinstance(host.ipidsequence, dict):
                self.write_parser.startElement('ipidsequence',
                        AttributesImpl({
                            'class': host.ipidsequence.get('class', ''),
                            'values': host.ipidsequence.get('values', '')})
                        )
                self.write_parser.endElement('ipidsequence')

            ## TCP TS Sequence element
            if isinstance(host.tcptssequence, dict):
                self.write_parser.startElement('tcptssequence',
                        AttributesImpl({
                            'class': host.tcptssequence.get('class', ''),
                            'values': host.tcptssequence.get('values', '')})
                        )
                self.write_parser.endElement('tcptssequence')
            # End of sequences elements
            ###########################
            
            # Trace elements
            
            if isinstance(host.trace, dict):
                self.write_parser.startElement('trace',
                        AttributesImpl({
                            'port': host.trace.get('port', ''),
                            'proto': host.trace.get('proto', '')})
                        )
                
                # Write hops:
                for hop in host.trace['hop']:
                    self.write_parser.startElement('hop',
                        AttributesImpl(hop))
                    self.write_parser.endElement('hop')
                
                self.write_parser.endElement('trace')
            # End trace elements

            # End host element
            self.write_parser.endElement('host')

    def _write_debugging(self):
        self.write_parser.startElement('debugging',
                AttributesImpl({
                    'level': str(self.debugging_level)})
                )
        self.write_parser.endElement('debugging')

    def _write_verbose(self):
        self.write_parser.startElement('verbose',
                AttributesImpl({
                    'level': str(self.verbose_level)})
                )
        self.write_parser.endElement('verbose')

    def _write_scaninfo(self):
        for scan in self.scaninfo:
            if not isinstance(scan, dict):
                continue

            self.write_parser.startElement('scaninfo',
                    AttributesImpl({
                        'type': scan.get('type', ''),
                        'protocol': scan.get('protocol', ''),
                        'numservices': scan.get('numservices', ''),
                        'services': scan.get('services', '')})
                    )
            self.write_parser.endElement('scaninfo')

    def _write_nmaprun(self):
        self.write_parser.startElement('nmaprun',
                AttributesImpl({
                    'annotation': str(self.profile_annotation),
                    'args': str(self.nmap_command),
                    'description': str(self.profile_description),
                    'hint': str(self.profile_hint),
                    'nmap_output': str(self.nmap_output),
                    'options': str(self.profile_options),
                    'profile': str(self.profile),
                    'profile_name': str(self.profile_name),
                    'scanner': str(self.scanner),
                    'start': str(self.start),
                    'startstr': str(self.formated_date),
                    'target': str(self.target),
                    'version': str(self.scanner_version),
                    'scan_name': str(self.scan_name)})
                )

    def _verify_file(self, xml_file):
        # let errors be raised
        if isinstance(xml_file, basestring):
            xml_file = open(xml_file, 'w')
        else:
            mode = xml_file.mode
            if mode in ('r+', 'w', 'w+'):
                xml_file.seek(0)
        return xml_file

    def __remove_none(self, dic):
        # saxutils will have problems if your dic contain any None items
        # (it will try to use the replace method, for example, which a
        # None object doesn't have).
        for k, v in dic.items():
            if k is None or v is None:
                del dic[k]

    def is_unsaved(self):
        return self.unsaved


def nmap_parser_sax(nmap_xml_file=""):
    parser = make_parser()
    nmap_parser = NmapParserSAX()

    parser.setContentHandler(nmap_parser)
    nmap_parser.set_parser(parser)
    nmap_parser.set_xml_file(nmap_xml_file)

    return nmap_parser

NmapParser = nmap_parser_sax
