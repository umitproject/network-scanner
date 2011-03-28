# Copyright (C) 2010 Adriano Monteiro Marques.
#
# Author: Diogo Ricardo Marques Pinheiro <diogormpinheiro@gmail.com>
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
from higwidgets.hignotebooks import HIGNotebook
from higwidgets.higtables import HIGTable
from higwidgets.higlabels import HIGSectionLabel, HIGEntryLabel
from higwidgets.higboxes import  hig_box_space_holder
from umit.preferences.FramesHIG import *

from umit.inventory.SettingsWin import NISettingsBox
from umit.core.I18N import _



class InventoryTab(TabBox):

    def __init__(self, name):
        TabBox.__init__(self, name)
        
    def _create_widgets(self):
        self.inv_settings = NISettingsBox(False)
        self.box = self.inv_settings.get_layout()
        self.pack_start(self.box, True, True)
        
    def save(self):
        self.inv_settings._apply_settings(None)