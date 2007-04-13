##
## UmitConf.py
## Login : <py.adriano@gmail.com>
## Started on  Wed Apr  5 09:43:03 2006 Adriano Monteiro Marques
## $Id$
## 
## Copyright (C) 2006 Adriano Monteiro Marques
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##

from ConfigParser import ConfigParser, DEFAULTSECT

class UmitConfigParser(ConfigParser):
    filenames = None
    fp = None
    
    def __init__(self, *args):
        ConfigParser.__init__(self, *args)

    def set(self, section, option, value):
        if not self.has_section(section):
            self.add_section(section)
        
        ConfigParser.set(self, section, option, value)
        self.save_changes()

    def read(self, filenames):
        self.filenames = ConfigParser.read(self, filenames)    

    def readfp(self, fp, filename=None):
        ConfigParser.readfp(self, fp, filename)
        self.fp = fp
        self.filenames = filename

    def save_changes(self):
        if self.filenames:
            filename = None
            if type(self.filenames) == type(""):
                filename = self.filenames
            elif type(self.filenames) == type([]) and len(self.filenames) == 1:
                filename = self.filenames[0]
            else:
                raise Exception("Wrong filename")
            self.write(open(filename, 'w'))
        elif self.fp:
            self.write(self.fp)

    def write(self, fp):
        '''Write alphabetically sorted config files'''
        if self._defaults:
            fp.write("[%s]\n" % DEFAULTSECT)
            
            items = self._defaults.items()
            items.sort()
            
            for (key, value) in items:
                fp.write("%s = %s\n" % (key, str(value).replace('\n', '\n\t')))
            fp.write("\n")

        sects = self._sections.keys()
        sects.sort()
        
        for section in sects:
            fp.write("[%s]\n" % section)
            for (key, value) in self._sections[section].items():
                if key != "__name__":
                    fp.write("%s = %s\n" %
                             (key, str(value).replace('\n', '\n\t')))
            fp.write("\n")
