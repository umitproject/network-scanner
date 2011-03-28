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


## Import Configuration Files from Core

from umit.core.UmitConf import DiffColors
from umit.core.UmitConf import SearchConfig
from umit.core.UmitConf import UmitConf
from umit.core.UmitConf import UmitConf
from umit.core.UmitConf import NmapOutputHighlight


"""
Holds config files: umit.conf, target_list, recents_scans
"""

class TargetList(object):
    def __init__(self):
        pass
    def clean(self):
        pass
    def get_list(self):
        pass


class RecentScans(object):
    def __init__(self):
        pass
    def clean(self):
        pass
    def get_list(self):
        pass



class GeneralSettingsConf(UmitConfigParser, object):
    """
    General Settings defining the settings like enable splash/warnings
    nmap command, remove history (using targets, and recents class), etc
    """
    def __init__(self):
        """ Constructor generalsettings conf"""
        self.parser = Path.config_parser
        self.section_name = "general_settings"
        if not self.parser.has_section(self.section_name):
            self.create_section()
    def create_section(self):
        pass

    def save_changes(self):
        self.parser.save_changes()


if __name__=="__main__":
    gn = GeneralSettingsConf()
