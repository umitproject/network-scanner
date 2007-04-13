##
## BasePaths.py
## Login : <adriano@localhost.localdomain>
## Started on  Sat Apr  8 17:49:23 2006 Adriano Monteiro Marques
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

import os
import os.path
import sys


######################
# Platform recognition
PLATFORM = sys.platform
HOME = os.path.expanduser("~")
#HOME = os.environ.get('HOME', '')
CURRENT_DIR = os.getcwd()


base_paths = dict(config_file = 'umit.conf',
                  config_dir = '.umit',
                  user_dir = os.path.join(HOME, '.umit'),
                  scan_profile = 'scan_profile.usp',
                  profile_editor = 'profile_editor.xml',
                  recent_scans = 'recent_scans.txt',
                  target_list = 'target_list.txt',
                  wizard = 'wizard.xml',
                  options = 'options.xml',
                  umit_op = 'umit.op',
                  umit_opf = 'umit.opf',
                  umit_opi = 'umit.opi',
                  umit_opt = 'umit.opt',
                  pixmaps_dir = os.path.join('share', 'pixmaps'),
                  i18n_dir = os.path.join('share','locale'),
                  i18n_message_file = 'umit.mo',
                  scan_results_extension = 'usr',  # comes from umit scan result
                  scan_profile_extension = 'usp',  # comes from umit scan profile
                  user_home = HOME,
                  basic_search_sequence = [HOME, CURRENT_DIR],
                  config_search_sequence = [HOME, CURRENT_DIR],
                  pixmaps_search_sequence = [os.path.join(CURRENT_DIR, 'share', 'pixmaps'),
                                             HOME],
                  i18n_search_sequence = [os.path.join(CURRENT_DIR, 'share', 'locale'), HOME],
                  umitdb = "umit.db",
                  services = "nmap-services",
                  services_dump = "services.dmp",
                  os_db = "nmap-os-db",
                  os_dump = "os_db.dmp",
                  os_fingerprints = "nmap-os-fingerprints",
                  umit_version = "umit_version",
                  os_classification = "os_classification.dmp")


if PLATFORM == 'linux2' or PLATFORM == 'linux1':
    base_paths.update(dict(user_home = HOME,
                           basic_search_sequence = [os.path.join(HOME, base_paths['config_dir']),
                                                    '/opt/umit', HOME, CURRENT_DIR],
                           config_search_sequence = [os.path.join(HOME, base_paths['config_dir']),
                                                     CURRENT_DIR, '/etc'],
                           pixmaps_search_sequence = [os.path.join(CURRENT_DIR,
                                                                   'share',
                                                                   'pixmaps'),
                                                      '/usr/share/pixmaps',
                                                      '/opt/umit', HOME],
                           i18n_search_sequence = [os.path.join(CURRENT_DIR, 'share', 'locale'),
                                                   '/usr/share/locale',
                                                   HOME, CURRENT_DIR]))
elif PLATFORM == 'win32':
    PROGRAM_FILES = os.environ.get("PROGRAMFILES", "\\")
    UMIT_DIR = os.path.join(PROGRAM_FILES, "Umit")
    PIXMAPS_DIR = os.path.join(UMIT_DIR, 'share', 'pixmaps')
    
    base_paths.update(dict(\
        basic_search_sequence = [UMIT_DIR, PROGRAM_FILES, HOME, CURRENT_DIR],
        config_search_sequence = [UMIT_DIR, PROGRAM_FILES, HOME, CURRENT_DIR],
        pixmaps_search_sequence = [PIXMAPS_DIR, PROGRAM_FILES,
                                   os.path.join(CURRENT_DIR, 'share', 'pixmaps'),
                                   HOME],
        i18n_search_sequence = [UMIT_DIR, PROGRAM_FILES,
                                os.path.join(CURRENT_DIR, 'share', 'locale'), HOME],))

elif PLATFORM == 'darwin':
    base_paths.update(dict(user_home = HOME,
                           basic_search_sequence = [os.path.join(HOME, 'Applications'),
                                                    '/Local', '/Network',
                                                    '/System/Library', HOME]))

