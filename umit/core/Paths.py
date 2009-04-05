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

from umit.core.UmitLogging import log
from umit.core.UmitConfigParser import UmitConfigParser
from umit.core.TempConf import create_temp_conf_dir
from umit.core.Version import VERSION
from umit.core.BasePaths import base_paths, HOME
from umit.core.BasePaths import CONFIG_DIR, LOCALE_DIR, MISC_DIR
from umit.core.BasePaths import ICONS_DIR, PIXMAPS_DIR, DOCS_DIR
from umit.merger import file_merger, dir_creator, nt_appdata

def root_dir():
    """Retrieves root dir on current filesystem"""
    curr_dir = os.getcwd()
    while True:
        splited = os.path.dirname(curr_dir)
        if curr_dir == splited:
            break
        curr_dir = splited

    log.debug(">>> Root dir: %s" % curr_dir)
    return curr_dir

#######
# Paths
class Paths(object):
    """Paths
    """
    config_parser = UmitConfigParser()
    paths_section = "paths"

    hardcoded = ["locale_dir",
                 "pixmaps_dir",
                 "icons_dir",
                 "misc_dir",
                 "config_dir",
                 "docs_dir"]

    config_files_list = ["config_file",
                         "profile_editor",
                         "wizard",
                         "scan_profile",
                         "options",
                         "umitdb_ng",
                         "tl_conf",
                         "tl_colors_std",
                         "sched_schemas",
                         "sched_profiles",
                         "sched_log",
                         "smtp_schemas",
                         "umit_version"]

    empty_config_files_list = ["target_list",
                               "recent_scans",
                               "umitdb"]

    share_files_list = ["umit_opt",
                        "umit_opf"]

    misc_files_list = ["services_dump",
                       "os_dump",
                       "os_classification",
                       "sched_running"]

    other_settings = ["nmap_command_path"]

    config_file_set = False

    def _parse_and_set_dirs(self, config_file, config_dir):
        """Parse the given config_file and then set the directories."""
        # Parsing the umit main config file
        self.config_parser.read(config_file)

        # Should make the following only after reading the umit.conf file
        self.config_dir = config_dir
        self.config_file = config_file
        self.config_file_set = True
        self.locale_dir = LOCALE_DIR
        self.pixmaps_dir = PIXMAPS_DIR
        self.icons_dir = ICONS_DIR
        self.misc_dir = MISC_DIR
        self.docs_dir = DOCS_DIR

        log.debug(">>> Config file: %s" % config_file)
        log.debug(">>> Locale: %s" % self.locale_dir)
        log.debug(">>> Pixmaps: %s" % self.pixmaps_dir)
        log.debug(">>> Icons: %s" % self.icons_dir)
        log.debug(">>> Misc: %s" % self.misc_dir)
        log.debug(">>> Docs: %s" % self.docs_dir)

    def get_running_path(self):
        return self.__runpath

    def set_running_path(self, path):
        """
        Sets path for current umit instance.
        """
        self.__runpath = path

    def get_umit_conf(self):
        """
        Returns umit conf file being used.
        """
        if self.config_file_set:
            return self.config_file

    def force_set_umit_conf(self, config_dir):
        if not os.path.exists(config_dir):
            raise Exception("Path specified (%r) does not exist" % config_dir)

        config_file = os.path.join(config_dir, base_paths['config_file'])
        self._parse_and_set_dirs(config_file, config_dir)

    def set_umit_conf(self, base_dir):
        main_config_dir = ""
        main_config_file = ""

        if (os.path.exists(CONFIG_DIR) and
                os.path.exists(os.path.join(CONFIG_DIR,
                    base_paths['config_file']))):
            main_config_dir = CONFIG_DIR

        elif (
                os.path.exists(os.path.join(base_dir, CONFIG_DIR)) and
                os.path.exists(os.path.join(
                    base_dir, CONFIG_DIR, base_paths['config_file']))):
            main_config_dir = os.path.join(base_dir, CONFIG_DIR)

        elif (
                os.path.exists(os.path.join(os.path.dirname(base_dir),
                    CONFIG_DIR)) and
                os.path.exists(os.path.join(os.path.dirname(base_dir),
                    CONFIG_DIR, base_paths['config_file']))):
            main_config_dir = (
                    os.path.join(os.path.dirname(base_dir), CONFIG_DIR))

        else:
            # XXX This is bad, it doesn't create temporary configuration
            # files for everything that umit uses nowadays.
            main_config_dir = create_temp_conf_dir(VERSION)

        # Main config file, based on the main_config_dir got above
        main_config_file = os.path.join(main_config_dir,
                base_paths['config_file'])

        # This is the expected place in which umit.conf should be placed
        supposed_file = os.path.join(base_paths['user_dir'],
                base_paths['config_file'])
        config_dir = ""
        config_file = ""

        if os.path.exists(supposed_file)\
               and check_access(supposed_file, os.R_OK and os.W_OK):
            config_dir = base_paths['user_dir']
            config_file = supposed_file
            log.debug(">>> Using config files in user home directory: %s" \
                      % config_file)

            # Verify if an old ~/.umit exists, and merge into user
            # localappdata (Windows only).
            backup = nt_appdata.merge()
            if backup is not None:
                log.debug(">>> Merging config files from %r to %r (new "
                        "configdir already exists)" % (backup, config_dir))
                file_merger(backup, config_dir, True, *userdir_files)

        elif not os.path.exists(supposed_file)\
                and not check_access(base_paths['user_dir'],
                        os.R_OK and os.W_OK):

            # Before attemping to create a new user directory, merge the older
            # ~/.umit to user localappdata (Windows only).
            backup = nt_appdata.merge()
            if backup is not None:
                log.debug(">>> Merging config files from %r to %r" % (
                    backup, config_dir))
                file_merger(backup, config_dir, True, *userdir_files)

            try:
                result = create_user_dir(os.path.join(
                    main_config_dir, base_paths['config_file']), HOME)
                if not isinstance(result, dict):
                    raise Exception()
            except:
                log.debug(">>> Failed to create user home")
            else:
                config_dir = result['config_dir']
                config_file = result['config_file']
                log.debug(">>> Using recently created config files in "
                        "user home: %s" % config_file)

        if config_dir and config_file:
            # Either base_paths['user_dir'] existed or it just got created.
            #
            # In both cases it is possible that config merge is necessary,
            # if the path already existed then it is possible that:
            #   1) there are newer config files that need merging;
            #   2) there are newer config dirs that need copying;
            #   3) maybe there was an ~/.umit which got merged into user's
            #      local appdata and now configuration files need be merged
            #      [Windows only].
            # if it just got created then:
            #   See 3) above.
            dir_creator(config_dir, *userdir_dirs)
            file_merger(main_config_dir, config_dir, False, *userdir_files)
        else:
            log.debug(">>> There is no way to create nor use home config.")
            log.debug(">>> Trying to use main configuration files...")

            config_dir = main_config_dir
            config_file = main_config_file

        self._parse_and_set_dirs(config_file, config_dir)


    def __getattr__(self, name):
        if self.config_file_set:
            if name in self.other_settings:
                return self.config_parser.get(self.paths_section, name)

            elif name in self.hardcoded:
                return self.__dict__[name]

            elif name in self.config_files_list:
                return return_if_exists(os.path.join(
                    self.__dict__['config_dir'], base_paths[name]))

            elif name in self.empty_config_files_list:
                return return_if_exists(os.path.join(
                    self.__dict__['config_dir'], base_paths[name]),
                    True)

            elif name in self.share_files_list:
                return return_if_exists(os.path.join(
                    self.__dict__['pixmaps_dir'], base_paths[name]))

            elif name in self.misc_files_list:
                return return_if_exists(os.path.join(
                    self.__dict__["misc_dir"], base_paths[name]))

            try:
                return self.__dict__[name]
            except:
                raise NameError(name)
        else:
            raise Exception("Must set config file location first")

    def __setattr__(self, name, value):
        if name in self.other_settings:
            self.config_parser.set(self.paths_section, name, value)
        else:
            self.__dict__[name] = value

####################################
# Functions for directories creation

# The names listed here will be copied/merged into the user config directory.
userdir_files = (
        "umit.conf", "options.xml", "profile_editor.xml", "scan_profile.usp",
        "wizard.xml", "umit_version", "umitng.db", "timeline-settings.conf",
        "tl_colors_evt_std.conf", "scheduler-schemas.conf",
        "scheduler-profiles.conf", "scheduler.log", "smtp-schemas.conf")
userdir_dirs = ("plugins", "plugins-download", "plugins-temp")

def create_user_dir(config_file, user_home):
    log.debug(">>> Create user dir at given home: %s" % user_home)
    log.debug(">>> Using %s as source" % config_file)

    user_dir = os.path.join(user_home, base_paths['config_dir'])

    if os.path.exists(user_home):
        if os.access(user_home, os.R_OK and os.W_OK):
            if not os.path.exists(user_dir):
                os.mkdir(user_dir)
                for dirname in userdir_dirs:
                    os.mkdir(os.path.join(user_dir, userdir_dirs))
                log.debug(">>> Umit user dir (%r) successfully "
                        "created!" % user_dir)
            else:
                log.debug(">>> Umit user dir (%r) already exists" % user_dir)
        else:
            log.warning(">>> No permissions to create user dir!")
            return False

    main_dir = os.path.dirname(config_file)
    for name in userdir_files:
        copy_config_file(name, main_dir, user_dir)

    return dict(user_dir = user_dir,
                config_dir = user_dir,
                config_file = os.path.join(user_dir, 'umit.conf'))

def copy_config_file(filename, dir_origin, dir_destiny):
    log.debug(">>> copy_config_file %s to %s" % (filename, dir_destiny))

    origin = os.path.join(dir_origin, filename)
    if not os.path.exists(origin):
        return

    destiny = os.path.join(dir_destiny, filename)

    if not os.path.exists(destiny):
        # Quick copy
        origin_file = open(origin, 'rb')
        destiny_file = open(destiny, 'wb')
        destiny_file.write(origin_file.read())
        origin_file.close()
        destiny_file.close()
    return destiny

def check_access(path, permission):
    if isinstance(path, basestring):
        return os.path.exists(path) and os.access(path, permission)
    return False

def return_if_exists(path, create=False):
    path = os.path.abspath(path)
    if os.path.exists(path):
        return path
    elif create:
        f = open(path, "w")
        f.close()
        return path
    raise Exception("File '%s' does not exist or could not be found!" % path)

############
# Singleton!
Path = Paths()

if __name__ == '__main__':
    Path.set_umit_conf(os.path.dirname(sys.argv[0]))

    print ">>> SAVED DIRECTORIES:"
    print ">>> LOCALE DIR:", Path.locale_dir
    print ">>> PIXMAPS DIR:", Path.pixmaps_dir
    print ">>> CONFIG DIR:", Path.config_dir
    print
    print ">>> FILES:"
    print ">>> CONFIG FILE:", Path.config_file
    print ">>> TARGET_LIST:", Path.target_list
    print ">>> PROFILE_EDITOR:", Path.profile_editor
    print ">>> WIZARD:", Path.wizard
    print ">>> SCAN_PROFILE:", Path.scan_profile
    print ">>> RECENT_SCANS:", Path.recent_scans
    print ">>> OPTIONS:", Path.options
    print
    print ">>> UMIT_OPT:", Path.umit_opt
    print ">>> UMIT_OPF:", Path.umit_opf
    print ">>> UMITDB:", Path.umitdb
    print ">>> UMITDB (New generation):", Path.umitdb_ng
    print ">>> SERVICES DUMP:", Path.services_dump
    print ">>> OS DB DUMP:", Path.os_dump
    print ">>> UMIT VERSION:", Path.umit_version
    print ">>> OS CLASSIFICATION DUMP:", Path.os_classification
    print ">>> NMAP COMMAND PATH:", Path.nmap_command_path
