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

import os
import sys


######################
# Platform recognition
PLATFORM = sys.platform
if os.name == 'nt':
    from win32com.shell import shell, shellcon
    # See http://msdn.microsoft.com/en-us/library/bb762181(VS.85).aspx
    # for SHGetFolderPath reference.
    HOME = shell.SHGetFolderPath(0, shellcon.CSIDL_LOCAL_APPDATA, 0, 0)
    UMIT_CFG_DIR = 'umit'
else:
    HOME = os.path.expanduser("~")
    UMIT_CFG_DIR = '.umit'

CURRENT_DIR = os.getcwd()

if hasattr(sys, 'frozen'):
    if sys.frozen == 'macosx_app':
        main_dir = os.environ['RESOURCEPATH']
    else:
        main_dir = os.path.dirname(sys.executable)
else:
    # Look for files relative to the script path to allow running within
    # the build directory.
    main_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    if not os.path.exists(os.path.join(main_dir, 'share')):
        # This umit instance is living on bin/, so we look one level
        # down in the path to still be able to run within a svn source
        # checkout.
        main_dir = os.path.abspath(os.path.join(main_dir, os.path.pardir))

CONFIG_DIR = os.path.join(main_dir, "share", "umit", "config")
LOCALE_DIR = os.path.join(main_dir, "share", "locale")
MISC_DIR = os.path.join(main_dir, "share", "umit", "misc")
ICONS_DIR = os.path.join(main_dir, "share", "icons", "umit")
PIXMAPS_DIR = os.path.join(main_dir, "share", "pixmaps", "umit")
PLUGINS_DIR = os.path.join(main_dir, "share", "umit", "plugins")
DOCS_DIR = os.path.join(main_dir, "share", "doc", "umit", "html")
STYLES_DIR = os.path.join(main_dir, "share", "umit", "styles")
LANGUAGES_DIR = os.path.join(main_dir, "share", "umit", "languages")

base_paths = dict(config_file = 'umit.conf',
                  config_dir = UMIT_CFG_DIR,
                  user_dir = os.path.join(HOME, UMIT_CFG_DIR),
                  scan_profile = 'scan_profile.usp',
                  profile_editor = 'profile_editor.xml',
                  recent_scans = 'recent_scans.txt',
                  target_list = 'target_list.txt',
                  wizard = 'wizard.xml',
                  options = 'options.xml',
                  umit_opf = 'umit.opf',
                  umit_opt = 'umit.opt',
                  pixmaps_dir = PIXMAPS_DIR,
                  plugins_dir = PLUGINS_DIR,
                  i18n_dir = LOCALE_DIR,
                  i18n_message_file = 'umit.mo',
                  scan_results_extension = 'usr',  # comes from umit scan result
                  scan_profile_extension = 'usp',  # comes from umit scan profile
                  user_home = HOME,
                  basic_search_sequence = [HOME, CURRENT_DIR],
                  config_search_sequence = [HOME, CURRENT_DIR],
                  pixmaps_search_sequence = [os.path.join(CURRENT_DIR, PIXMAPS_DIR),
                                             HOME],
                  i18n_search_sequence = [os.path.join(CURRENT_DIR, LOCALE_DIR), HOME],
                  umitdb = "umit.db",

                  # new generation database
                  umitdb_ng = "umitng.db",

                  # timeline configuration
                  tl_conf = "timeline-settings.conf",
                  tl_colors_std = "tl_colors_evt_std.conf",
                  
                  # scheduler
                  sched_schemas = "scheduler-schemas.conf",
                  sched_profiles = "scheduler-profiles.conf",
                  sched_log = "scheduler.log",

                  # smtp
                  smtp_schemas = "smtp-schemas.conf",

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
                           pixmaps_search_sequence = [os.path.join(CURRENT_DIR, PIXMAPS_DIR),
                                                      '/usr/share/pixmaps/umit',
                                                      '/opt/umit', HOME],
                           i18n_search_sequence = [os.path.join(CURRENT_DIR, LOCALE_DIR),
                                                   '/usr/share/locale',
                                                   HOME, CURRENT_DIR]))
elif PLATFORM == 'win32':
    PROGRAM_FILES = os.environ.get("PROGRAMFILES", "\\")
    UMIT_DIR = os.path.join(PROGRAM_FILES, "Umit")
    PIXMAPS_DIR = os.path.join(UMIT_DIR, PIXMAPS_DIR)
    
    base_paths.update(dict(\
        basic_search_sequence = [UMIT_DIR, PROGRAM_FILES, HOME, CURRENT_DIR],
        config_search_sequence = [UMIT_DIR, PROGRAM_FILES, HOME, CURRENT_DIR],
        pixmaps_search_sequence = [PIXMAPS_DIR, PROGRAM_FILES,
                                   os.path.join(CURRENT_DIR, PIXMAPS_DIR),
                                   HOME],
        i18n_search_sequence = [UMIT_DIR, PROGRAM_FILES,
                                os.path.join(CURRENT_DIR, LOCALE_DIR), HOME],))

elif PLATFORM == 'darwin':
    base_paths.update(dict(user_home = HOME,
                           basic_search_sequence = [os.path.join(HOME, 'Applications'),
                                                    '/Local', '/Network',
                                                    '/System/Library', HOME]))

