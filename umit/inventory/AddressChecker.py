# Copyright (C) 2007 Adriano Monteiro Marques
#
# Authors: Guilherme Polo <ggpolo@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA
import re
import struct

def _is_ipv4(addr):
	"""
	I have to add for "/" in ipv4 address. This regex doesnot support for 
	address like "127.0.0.1/22".
	"""
	rex = "^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
	regex = re.compile(rex, re.IGNORECASE)
	if re.match(regex,addr):
		return True
	else:
		return False
		
def _is_ipv6(addr):
	rex = "^(?:(?:(?:[A-F0-9]{1,4}:){6}|(?=(?:[A-F0-9]{0,4}:){0,6}(?:[0-9]{1,3}\.){3}[0-9]{1,3}$)(([0-9A-F]{1,4}:){0,5}|:)((:[0-9A-F]{1,4}){1,5}:|:))(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}|(?=(?:[A-F0-9]{0,4}:){0,7}[A-F0-9]{0,4}$)(([0-9A-F]{1,4}:){1,7}|:)((:[0-9A-F]{1,4}){1,7}|:))$"
	regex = re.compile(rex, re.IGNORECASE)
	if re.match(regex, addr):
		return True
	else:
		return False

def _is_mac(addr):
	rex= "^([a-fA-F0-9]{2}[:|\-]?){5}[a-fA-F0-9]{2}$"
	regex = re.compile(rex, re.IGNORECASE)
	if re.match(regex,addr):
		return True
	else:
		return False
		
def Address_Checker(addr):
	if _is_ipv4(addr):
		return "IPV4"
	elif _is_ipv6(addr):
		return "IPV6"
	elif _is_mac(addr):
		return "MAC"
	else:
		return "NONE"
