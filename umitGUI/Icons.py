#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2005 Insecure.Com LLC.
#
# Author: Adriano Monteiro Marques <py.adriano@gmail.com>
#         Cleber Rodrigues <cleber.gnu@gmail.com>
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

import gtk
import re
import sys
import os.path

from umitCore.Paths import Path
from umitCore.UmitConf import is_maemo
from umitCore.UmitLogging import log

######################
# Platform recognition
PLATFORM = sys.platform
if is_maemo():
    PLATFORM = "maemo"

icons = []

icon_names = (\
    # Operating Systems
    'default',
    'freebsd',
    'irix',
    'linux',
    'macosx',
    'openbsd',
    'redhat',
    'shadow_man',
    'solaris',
    'ubuntu',
    'unknown',
    'win',
    
    # Vulnerability Levels
    'vl_1',
    'vl_2',
    'vl_3',
    'vl_4',
    'vl_5')



pixmap_path = Path.pixmaps_dir
if pixmap_path:
    if PLATFORM == 'linux2':
        # FIXME: This naming scheme should be more consistent
        # All icon or all logo, and not mixed up
        for icon_name in icon_names[0:12]:
            file_path = os.path.join(pixmap_path, '%s.svg' % icon_name)
            (key, val) = ('%s_icon' % icon_name, file_path)
            if os.path.exists(file_path):
                log.debug('Register %s icon name for file %s' % (key, val))
                icons.append(('%s_icon' % icon_name, file_path))
            else:
                log.warn('Could not find %s file for icon name %s' % (val, key))

        for icon_name in icon_names[12:]:
            file_path = os.path.join(pixmap_path, '%s.svg' % icon_name)
            (key, val) = ('%s_logo' % icon_name, file_path)
            if os.path.exists(file_path):
                log.debug('Register %s icon name for file %s' % (key, val))
                icons.append(('%s_logo' % icon_name, file_path))
            else:
                log.warning('Could not find %s file for icon name %s' % (val, key))        
    else:
        for icon_name in icon_names:
            for variant in (('icon', '32'), ('logo', '75')):
                #log.debug('Pixmap Path: %s' % pixmap_path)
                file_path = os.path.join(pixmap_path, '%s_%s.png' % (icon_name, variant[1]))
                (key, val) = ('%s_%s' % (icon_name, variant[0]), file_path)
                if os.path.exists(file_path):
                    #log.debug('Register %s icon name for file %s' % (key, val))
                    icons.append((key, val))
                else:
                    log.warn('Could not find %s file for icon name %s' % (val, key))


iconfactory = gtk.IconFactory()

for stock_id, file in icons:
    # only load image files when our stock_id is not present
    pixbuf = gtk.gdk.pixbuf_new_from_file(file)
    iconset = gtk.IconSet(pixbuf)
    iconfactory.add(stock_id, iconset)
    iconfactory.add_default()

def get_os_icon(os_match):
    return get_os(os_match, 'icon')

def get_os_logo(os_match):
    if PLATFORM != 'linux2':
        return get_os(os_match, 'logo')
    return get_os(os_match, 'icon')

def get_os(os_match, type):
    if os_match:
        if re.findall('[rR][eE][dD][ ]+[hH][aA][tT]', os_match):
            # Linux icon
            return 'redhat_%s'%type
        elif re.findall('[uU][bB][uU][nN][tT][uU]', os_match):
            # Linux icon
            return 'ubuntu_%s'%type
        elif re.findall('[lL][iI][nN][uU][xX]', os_match):
            # Linux icon
            return 'linux_%s'%type
        elif re.findall('[wW][iI][nN][dD][oO][wW][sS]', os_match):
            #print '>>> Match windows!'
            # Windows icon
            return 'win_%s'%type
        elif re.findall('[oO][pP][eE][nN][bB][sS][dD]', os_match):
            # OpenBSD icon
            return 'openbsd_%s'%type
        elif re.findall('[fF][rR][eE][eE][bB][sS][dD]', os_match):
            # FreeBSD icon
            return 'freebsd_%s'%type
        elif re.findall('[nN][eE][tT][bB][sS][dD]', os_match):
            # NetBSD icon
            return 'default_%s'%type
        elif re.findall('[sS][oO][lL][aA][rR][iI][sS]',os_match):
            # Solaris icon
            return 'solaris_%s'%type
        elif re.findall('[oO][pP][eE][nN].*[sS][oO][lL][aA][rR][iI][sS]',\
                        os_match):
            # OpenSolaris icon
            return 'solaris_%s'%type
        elif re.findall('[iI][rR][iI][xX]',os_match):
            # Irix icon
            return 'irix_%s'%type
        elif re.findall('[mM][aA][cC].*[oO][sS].*[xX]',os_match):
            # Mac OS X icon
            return 'macosx_%s'%type
        elif re.findall('[mM][aA][cC].*[oO][sS]',os_match):
            # Mac OS icon
            return 'macosx_%s'%type
        else:
            # Default OS icon
            return 'default_%s'%type
    else:
        # This is the icon for unkown OS
        # Can't be a scary icon, like stop, cancel, etc.
        return 'unknown_%s'%type

def get_vulnerability_logo(open_ports):
    open_ports = int(open_ports)
    if open_ports < 3:
        return 'vl_1_logo'
    elif open_ports < 5:
        return 'vl_2_logo'
    elif open_ports < 7:
        return 'vl_3_logo'
    elif open_ports < 9:
        return 'vl_4_logo'
    else:
        return 'vl_5_logo'
