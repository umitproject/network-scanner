#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
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


from difflib import Differ, restore
from umit.core.I18N import _

class Diff(Differ):
    def __init__(self, result1=[''], result2=[''], junk = "\n"):
        self.result1 = result1
        self.result2 = result2
        self.junk = junk
        
        self.umit_top_banner = ['|'+'-'*70+'|\n',
            '|'+_('Umit - Take the red pill').center (70)+'|\n',
            '|'+_('http://www.umitproject.org').center(70)+'|\n',
            '|'+' '*70+'|\n',
            '|'+_('This diff was generated by Umit').center(70)+'|\n',
            '|'+_("(Changes to this file can make Umit unable to read \
it.)").center(70)+'|\n',
            '|'+'-'*70+'|\n',
            '\n',
            '-'*10+_(' Start of diff ')+'-'*10+'\n']
        
        self.end_diff = ['\n'+'-'*10+_(' End of diff ')+'-'*10+'\n']
        
        Differ.__init__ (self, self.line_junk)
    
    def generate (self):
        diff_result = []
        for line in self.compare(self.result1, self.result2):
            diff_result.append (line)
        
        return self.umit_top_banner + diff_result + self.end_diff

    def generate_without_banner (self):
        diff_result = []
        for line in self.compare(self.result1, self.result2):
            diff_result.append (line)
        return diff_result
    
    def save (self, file):
        open (file, 'w').writelines (self.generate())
    
    def open (self, file):
        diff_file = open (file).readlines()
        
        return self.restore ('\n'.join(diff_file))
    
    def restore (self, string_to_restore):
        diffie = string_to_restore.split('\n')[len(self.umit_top_banner):-(len\
                                                            (self.end_diff)+1)]

        self.restored1 = []
        for i in restore (diffie, 1):
            self.restored1.append (i+'\n')
        
        self.restored2 = []
        for i in restore (diffie, 2):
            self.restored2.append (i+'\n')
        
        return self.restored1, self.restored2

    def line_junk (self, junk):
        if junk == self.junk:
            return True
        else:
            return False
