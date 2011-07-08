#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Authors: Gaurav Ranjan <g.ranjan143@gmail.com?>
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

import struct
import re


def _is_shorthand_ip(ip_str=""):
    """Determine if the address is shortened.

    Args:
        ip_str: A string, the IPv6 address.

    Returns:
        A boolean, True if the address is shortened.

    """
    print(ip_str)
    if ip_str.count('::') == 1:
        return True
    print "False"
    return False


def exapand_ip_arddess(ip_addr=""):
        """
        """
        print(ip_addr)
        if _is_shorthand_ip(ip_addr):
            new_ip = []
            hextet = ip_addr.split('::')

            if len(hextet) > 1:
                sep = len(hextet[0].split(':')) + len(hextet[1].split(':'))
                new_ip = hextet[0].split(':')

                for _ in xrange(8 - sep):
                    new_ip.append('0000')
                new_ip += hextet[1].split(':')

            else:
                new_ip = ip_addr.split(':')
               
            print(new_ip)
            # Now need to make sure every hextet is 4 lower case characters.
            # If a hextet is < 4 characters, we've got missing leading 0's.
            ret_ip = []
            for hextet in new_ip:
                ret_ip.append(('0' * (4 - len(hextet)) + hextet).lower())
            return ':'.join(ret_ip)
        # We've already got a longhand ip_addr.
        return ip_addr
        
def is_ipv6(addr):

	if addr==" ":
		return False
	
	print (addr)
	rex = "^(?:(?:(?:[A-F0-9]{1,4}:){6}|(?=(?:[A-F0-9]{0,4}:){0,6}(?:[0-9]{1,3}\.){3}[0-9]{1,3}$)(([0-9A-F]{1,4}:){0,5}|:)((:[0-9A-F]{1,4}){1,5}:|:))(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}|(?=(?:[A-F0-9]{0,4}:){0,7}[A-F0-9]{0,4}$)(([0-9A-F]{1,4}:){1,7}|:)((:[0-9A-F]{1,4}){1,7}|:))$"
	value = re.compile(rex, re.IGNORECASE)
	if re.match(value, addr):
		#print "It is matched true True"
		return True
	else:
		#print "It is unmatched False"
		return False
