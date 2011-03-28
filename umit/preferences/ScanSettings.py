# Copyright (C) 2008 Adriano Monteiro Marques.
#
# Author: Luis A. Bastiao Silva <luis.kop@gmail.com>
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

from umit.preferences.FrameHIG import TabBox


class EndScan(TabBox):
    def __init__(self, name):
        """ Create defaults Widget """
        TabBox.__init__(self, name)
        self._pack_widgets()
    def _create_widgets(self):
        """ Create widgets"""







class Factory:
    def create(self, name):
        if name == "End of Scan":
            return self._create_diff()
        elif name == "nmap":
            return self._create_nmap_output()
        elif name == "search":
            return self._create_search()
    def _create_nmap_output(self):
        return NmapResults()


    def _create_diff(self):
        self.colors = Colors()
        return DiffColors(self.colors)
    def _create_search(self):
        return SearchOptions()
