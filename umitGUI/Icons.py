#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Authors: Adriano Monteiro Marques <adriano@umitproject.org>
#          Cleber Rodrigues <cleber.gnu@gmail.com>
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

import gtk
import gobject
import re
import sys
import os.path

from umitCore.Paths import Path
from umitCore.UmitConf import is_maemo
from umitCore.UmitLogging import log

icon_names = (
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

plugins_icons = (
    'extension',
    'paths'
)

pixmap_path = Path.pixmaps_dir
if pixmap_path:
    # This is a generator that returns file names for pixmaps in the order they
    # should be tried.
    def get_pixmap_file_names(icon_name, size):
        yield '%s.svg' % icon_name
        yield '%s_%s.png' % (icon_name, size)

    iconfactory = gtk.IconFactory()
    for icon_name in plugins_icons:
        for type, size in (('small', 16), ('normal', 32)):
            key = '%s_%s' % (icon_name, type)
            try:
                pixbuf = gtk.gdk.pixbuf_new_from_file(
                   os.path.join(pixmap_path, "%s-%d.png" % (icon_name, size))
                )
                iconfactory.add(key, gtk.IconSet(pixbuf))
            except gobject.GError:
                continue

    for icon_name in icon_names:
        for type, size in (('icon', '32'), ('logo', '75')):
            key = '%s_%s' % (icon_name, type)
            # Look for a usable image file.
            for file_name in get_pixmap_file_names(icon_name, size):
                file_path = os.path.join(pixmap_path, file_name)
                try:
                    pixbuf = gtk.gdk.pixbuf_new_from_file(file_path)
                    break
                except gobject.GError:
                    # Try again.
                    pass
            else:
                log.warn('Could not find the icon for %s at any of (%s) \
in %s' % (icon_name,
          ', '.join(get_pixmap_file_names(icon_name, size)),
          pixmap_path))
                continue
            iconset = gtk.IconSet(pixbuf)
            iconfactory.add(key, iconset)
            log.debug('Register %s icon name for file %s' % (key, file_path))
    iconfactory.add_default()

def get_os_icon(os_match):
    return get_os(os_match, 'icon')

def get_os_logo(os_match):
    return get_os(os_match, 'logo')

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

def get_pixbuf(stock_id, w=None, h=None):
    "Get the pixbuf for a stock item defined in icons"

    name, size = stock_id.split("_")

    if size == "small":
        size = 16
    elif size == "normal":
        size = 32
    else:
        raise Exception("Could not determine the pixel size")

    fname = os.path.join(pixmap_path, "%s-%d.png" % (name, size))

    if w and h:
        return gtk.gdk.pixbuf_new_from_file_at_size(fname, w, h)
    else:
        return gtk.gdk.pixbuf_new_from_file(fname)
