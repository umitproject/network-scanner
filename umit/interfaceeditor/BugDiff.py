#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Adriano Monteiro Marques
#
# Author: Luís A. Bastião Silva <luis.kop@gmail.com>
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
'''
This class help to solve troubles with references and other 
'''

class BugDiff:
    @staticmethod
    def plist(list):
        for i in list:
            BugDiff.pref(i)
    @staticmethod
    def pref(refe):
        tmp = str(refe)
    @staticmethod
    def gref(refe):
        return str(refe)[-11:-1]
    @staticmethod
    def pdic(dic):
        for i in dic:
            print BugDiff.gref(i), dic[i]
            
        
    