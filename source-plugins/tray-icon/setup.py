#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2009 Adriano Monteiro Marques
#
# Author: Francesco Piccinno <stack.box@gmail.com>
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

from umit.plugin.Containers import setup

setup(
    name='Tray Icon',
    version='2.0',
    author=['Francesco Piccinno'],
    url='http://blog.archpwn.org',
    start_file='main',
    provide=['=tray-2.0'],
    description='A simple tray icon for Umit',
    scripts=['sources/main.py'],
    data_files=[('data', ['dist/logo.png', 'dist/preferences.xml'])],
    package_dir={'notification' : 'sources/notification'},
    packages=['notification'],
    license=['GPL'],
    copyright=['(C) 2009 Adrian Monteiro Marques'],
    output='TrayIcon.ump'
)
