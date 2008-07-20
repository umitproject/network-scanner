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

from higwidgets.higboxes import HIGVBox

from umitGUI.NmapOutputViewer import NmapOutputViewer
from umitCore.I18N import _

class ScanNmapOutputPage(HIGVBox):
    def __init__(self):
        HIGVBox.__init__(self)
        self.__create_widgets()
        self._pack_expand_fill(self.nmap_output)
    
    def __create_widgets(self):
        self.nmap_output = NmapOutputViewer()

    def get_nmap_output(self):
        buff = self.nmap_output.text_view.get_buffer()
        return buff.get_text(buff.get_start_iter(), buff.get_end_iter())
