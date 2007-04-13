# Copyright (C) 2005 Insecure.Com LLC.
#
# Author: Adriano Monteiro Marques <py.adriano@gmail.com>
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

import cPickle

from umitCore.Paths import Path

os_dump = Path.os_dump

def load_dumped_os():
    of = open(os_dump)
    osd = cPickle.load(of)
    of.close()
    return osd


class OSList(object):
    def __init__(self):
        self.os = load_dumped_os()

    def get_match_list(self, osclass):
        if osclass in self.os.keys():
            return self.os[osclass]
        return None

    def get_class_list(self):
        return self.os.keys()
    
if __name__ == "__main__":
    o = OSList()

    from pprint import pprint
    pprint (o.os)
