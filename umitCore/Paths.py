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

import os
import os.path
import re

from umitCore.Logging import log
from umitCore.UmitConfigParser import UmitConfigParser
from umitCore.BasePaths import base_paths, HOME
from umitCore.I18N import _


#######
# Paths
class Paths(object):
    """Paths
    """
    config_parser = UmitConfigParser()
    paths_section = "paths"
    
    directories_list = ["locale_dir",
                        "pixmaps_dir",
                        "config_dir",
                        "misc_dir",
                        "docs_dir"]
    
    config_files_list = ["config_file",
                         "target_list",
                         "profile_editor",
                         "wizard",
                         "scan_profile",
                         "recent_scans",
                         "options",
                         "umitdb",
                         "umit_version"]
    
    share_files_list = ["umit_op",
                        "umit_opi",
                        "umit_opt",
                        "umit_opf"]

    misc_files_list = ["services_dump",
                       "os_dump",
                       "os_classification"]
    
    other_settings = ["nmap_command_path"]

    config_file_set = False
    
    def set_umit_conf(self, umit_conf):
        self.using_main = False

        # Place supposed to have the user's config file
        supposed_user_conf = os.path.join(base_paths['user_dir'], base_paths['config_file'])

        config_file = supposed_user_conf
        if os.path.exists(supposed_user_conf)\
               and check_access(supposed_user_conf, os.R_OK):
            self.config_parser.read(config_file)
            log.debug(">>> Using config files in user home directory: %s" % config_file)

        elif not os.path.exists(supposed_user_conf)\
                 and not check_access(base_paths['user_dir'], os.R_OK and os.W_OK):
            result = create_user_dir(umit_conf, HOME)
            config_file = result['config_file']
            self.config_parser.read(config_file)
            [self.__setattr__(opt, result[opt]) for opt in result]
            log.debug(">>> Using recently created config files in user home: %s" % config_file)

        else:
            self.using_main = True
            config_file = umit_conf
            self.config_parser.read(config_file)
            log.debug(">>> Using main config file: %s" % config_file)

        # Should make the following only after reading the umit.conf file
        self.config_file = config_file
        self.config_file_set = True

        log.debug(">>> Config file: %s" % config_file)

    def root_dir(self):
        """Retrieves root dir on current filesystem"""
        curr_dir = os.getcwd()
        while True:
            splited = os.path.split(curr_dir)[0]
            if curr_dir == splited:
                break
            curr_dir = splited

        log.debug(">>> Root dir: %s" % curr_dir)
        return curr_dir


    def __getattr__(self, name):
        if self.config_file_set:
            if name in self.directories_list or name in self.other_settings:
                return return_if_exists(self.config_parser.get(self.paths_section, name))
            elif name in self.config_files_list:
                return return_if_exists(os.path.join(self.config_parser.get(self.paths_section, "config_dir"),
                                                     base_paths[name]))
            elif name in self.share_files_list:
                return return_if_exists(os.path.join(self.config_parser.get(self.paths_section, "pixmaps_dir"),
                                                     base_paths[name]))
            elif name in self.misc_files_list:
                return return_if_exists(os.path.join(self.config_parser.get(self.paths_section, "misc_dir"),
                                                     base_paths[name]))
        
            try:
                return self.__dict__[name]
            except:
                raise NameError(name)
        else:
            raise Exception("Must set config file location first")

    def __setattr__(self, name, value):
        if name in self.directories_list or name in self.other_settings:    
            self.config_parser.set(self.paths_section, name, value)
        else:
            self.__dict__[name] = value
    

####################################
# Functions for directories creation

def create_user_dir(main_config, user_home):
    log.debug(">>> Create user dir at given home: %s" % user_home)
    log.debug(">>> Using %s as source" % main_config)
    main_umit_conf = UmitConfigParser()
    main_umit_conf.read(main_config)
    paths_section = "paths"
    
    user_dir = os.path.join(user_home, base_paths['config_dir'])
    
    if os.path.exists(user_home)\
           and os.access(user_home, os.R_OK and os.W_OK)\
           and not os.path.exists(user_dir):
        os.mkdir(user_dir)
        log.debug(">>> Umit user dir successfully created! %s" % user_dir)
    else:
        log.warning(">>> No permissions to create user dir!")
        return False

    main_dir = os.path.split(main_config)[0]
    copy_config_file("options.xml", main_dir, user_dir)
    copy_config_file("profile_editor.xml", main_dir, user_dir)
    copy_config_file("recent_scans.txt", main_dir, user_dir)
    copy_config_file("scan_profile.usp", main_dir, user_dir)
    copy_config_file("target_list.txt", main_dir, user_dir)
    copy_config_file("umit_version", main_dir, user_dir)
    copy_config_file("umit.db", main_dir, user_dir)
    copy_config_file("wizard.xml", main_dir, user_dir)

    return dict(user_dir = user_dir,
                config_dir = user_dir,
                config_file = copy_config_file("umit.conf", os.path.split(main_config)[0], user_dir))

def copy_config_file(filename, dir_origin, dir_destiny):
    log.debug(">>> copy_config_file %s to %s" % (filename, dir_destiny))
    
    origin = os.path.join(dir_origin, filename)
    destiny = os.path.join(dir_destiny, filename)
    
    if not os.path.exists(destiny):
        # Quick copy
        open(destiny, 'w').write(open(origin).read())
    return destiny

def check_access(path, permission):
    return os.path.exists(path) and os.access(path, permission)

def return_if_exists(path):
    if os.path.exists(path):
        return os.path.abspath(path)
    raise Exception("File '%s' does not exist or could not be found!" % path)

#########
# Singleton!
Path = Paths()

if __name__ == '__main__':
    #create_user_dir(os.path.expanduser("~"))
    __file__ = ".."
    Path.set_umit_conf(os.path.join(os.path.split(__file__)[0], "config", "umit.conf"))

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
    print ">>> UMIT_OP:", Path.umit_op
    print ">>> UMIT_OPI:", Path.umit_opi
    print ">>> UMIT_OPT:", Path.umit_opt
    print ">>> UMIT_OPF:", Path.umit_opf
    print ">>> UMITDB:", Path.umitdb
    print ">>> SERVICES DUMP:", Path.services_dump
    print ">>> OS DB DUMP:", Path.os_dump
    print ">>> UMIT VERSION:", Path.umit_version
    print ">>> OS CLASSIFICATION DUMP:", Path.os_classification
    print ">>> NMAP COMMAND PATH:", Path.nmap_command_path
