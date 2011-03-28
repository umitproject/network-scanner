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

from umit.nsefacilitator.ScriptManager import NSEPreferencesCatalog, NSEPreferencesColumns
from umit.nsefacilitator.ScriptManager import NSEPreferencesEditor, NSEPreferencesNetwork
from umit.preferences.conf.NSEConf import nse_conf
from umit.nsefacilitator.nseConfig import ScriptConfig
from umit.core.I18N import _



class NSEGeneral(HIGNotebook):
    
    def __init__(self):
        pass


class NSESources(TabBox):

    def __init__(self):
        TabBox.__init__(self, _('Script Sources'))
        
    def _create_widgets(self):
        self.box = NSEPreferencesCatalog(config, False)
        self.pack_start(self.box, True, True)

    
class NSEEditor(TabBox):
    
    def __init__(self):
        TabBox.__init__(self, _('Text Editor'))
        
    def _create_widgets(self):
        self.box = NSEPreferencesEditor(preferences, False)
        self.pack_start(self.box, True, True)        

    
class NSEColumns(TabBox):
    
    def __init__(self):
        TabBox.__init__(self, _('Columns'))
        
    def _create_widgets(self):
        self.box = NSEPreferencesColumns(preferences, False)
        self.pack_start(self.box, True, True)


class NSENetwork(TabBox):
    
    def __init__(self):
        TabBox.__init__(self, _('Proxy Server'))
        
    def _create_widgets(self):
        self.box = NSEPreferencesNetwork(preferences, config, False)
        self.pack_start(self.box, True, True)

        
preferences = nse_conf
config = ScriptConfig()
config.load()
    
class Factory:
    
    def create(self, name):
        if name == "sources":
            return NSESources()
        elif name == "editor":
            return NSEEditor()
        elif name == "columns":
            return NSEColumns()
        elif name == "network":
            return NSENetwork()
