# -*- coding: utf-8 -*-

# Copyright (C) 2009 Adriano Monteiro Marques.
#
# Author: Daniel Mendes Cassiano <dcassiano@umitproject.org>
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

import os
import sys

from umit.core.Paths import Path
from umit.core.qs.ImportData import QSData

class DataHandler(QSData):

    def __init__(self):
        QSData.__init__(self)
        Path.set_umit_conf(os.path.dirname(sys.argv[0]))
        Path.set_running_path(os.path.abspath(os.path.dirname(sys.argv[0])))
        data = QSData()
        self.recent_scans = data.get_recent_scans()
        self.profiles = data.get_profiles()
        self.target_list = data.get_target_list
        self.nmap_options = data.get_nmap_options()
        self.nmap_command_option = data.get_nmap_command_option()
        self.db_data = data.get_from_db()
    

    def fix_data(self, data):
        #to fix and normalize data
        new_data = data.strip(" ").strip(".").strip(",").strip(";").strip(":")
        
        return new_data

    def handler(self):
        #to handle data
        pass

    def return_result(self, someObj):
        return someObj


if __name__ == "__main__":
    a = DataHandler()


