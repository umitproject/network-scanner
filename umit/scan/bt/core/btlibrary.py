#!/usr/bin/env python
# Copyright (C) 2008 Adriano Monteiro Marques.
#
# Author: Gaurav Ranjan <g.ranjan143@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA


import os


def bluetooth_library_check():
	"""
	Library Needed to run Bluetooth scan are :
	- python-bluez

	"""
	#is_installed = os.system('pkg-config --exists python-bluez')
	try:
	    import bluetooth
	    return True 
	except ImportError: 
	    return False
