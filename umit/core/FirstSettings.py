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

"""
This class is maded to load first settings of config file aware that
should be redundante code.
It's needed to break import cycle barriers


It's only for GSoC

"""
from os import R_OK, W_OK, access, mkdir, getcwd, environ, getcwd
from os.path import exists, join, split, abspath, dirname
from tempfile import mktemp
from types import StringTypes


import os
from umit.core.BasePaths import base_paths, HOME
from umit.core.BasePaths import CONFIG_DIR
from ConfigParser import ConfigParser
from umit.core.Version import VERSION

def check_access(path, permission):
    if type(path) in StringTypes:
        return exists(path) and access(path, permission)
    return False



class UmitConfigParser(ConfigParser):
    filenames = None
    fp = None
    
    def __init__(self, *args):
        ConfigParser.__init__(self, *args)

    def set(self, section, option, value):
        if not self.has_section(section):
            self.add_section(section)
        
        ConfigParser.set(self, section, option, value)

    def read(self, filename):
        self.filenames = ConfigParser.read(self, filename)
        return self.filenames

    def readfp(self, fp, filename=None):
        ConfigParser.readfp(self, fp, filename)
        self.fp = fp
        self.filenames = filename
        
        
class Paths(object):
    """Paths
    """
    config_parser = UmitConfigParser()
    def update_config_dir(self, config_dir):
        # Do any updates of configuration files. Not yet implemented.
        pass
    def check_version(self, config_dir):
        version_file = join(config_dir, base_paths['umit_version'])

        if exists(version_file):
            ver = open(version_file).readline().strip()


            if VERSION == ver:
                return True
        return False
    def set_umit_conf(self, base_dir):
        main_config_dir = ""
        main_config_file = ""
        if exists(CONFIG_DIR) and \
            exists(join(CONFIG_DIR, base_paths['config_file'])):
            main_config_dir = CONFIG_DIR

        elif exists(join(base_dir, CONFIG_DIR)) and\
            exists(join(base_dir,
                        CONFIG_DIR,
                        base_paths['config_file'])):
            main_config_dir = join(base_dir, CONFIG_DIR)

        elif exists(join(split(base_dir)[0], CONFIG_DIR)) and \
            exists(join(split(base_dir)[0],
                        CONFIG_DIR,
                        base_paths['config_file'])):
            main_config_dir = join(split(base_dir)[0], CONFIG_DIR)

        else:
            main_config_dir = create_temp_conf_dir(VERSION)

        # Main config file, based on the main_config_dir got above
        main_config_file = join(main_config_dir, base_paths['config_file'])

        # This is the expected place in which umit.conf should be placed
        supposed_file = join(base_paths['user_dir'], base_paths['config_file'])
        config_dir = ""
        config_file = ""

        if exists(supposed_file)\
               and check_access(supposed_file, R_OK and W_OK):
            config_dir = base_paths['user_dir']
            config_file = supposed_file

        elif not exists(supposed_file)\
             and not check_access(base_paths['user_dir'],
                                  R_OK and W_OK):
            try:
                result = create_user_dir(join(main_config_dir,
                                              base_paths['config_file']),
                                         HOME)
                if type(result) == type({}):
                    config_dir = result['config_dir']
                    config_file = result['config_file']
                else:
                    raise Exception()
            except:
                print ">>> Failed to create user home"

        if config_dir and config_file:
            # Checking if the version of the configuration files are the same
            # as this Umit's version
            if not self.check_version(config_dir):
                self.update_config_dir(config_dir)

        else:
            config_dir = main_config_dir
            config_file = main_config_file

        # Parsing the umit main config file
        self.config_parser.read(config_file)

Path = Paths()
Path.set_umit_conf(os.path.split('umit'))

        
        
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
            raise Exception('No general settings config file ')
        self.attributes = {} 
    def boolean_sanity(self, attr):
        if attr == True or \
           attr == "True" or \
           attr == "true" or \
           attr == "1":

            return 1

        return 0

    
    def _get_it(self, p_name, default):
        return self.parser.get(self.section_name, p_name, default)

    def _set_it(self, p_name, value):
        self.parser.set(self.section_name, p_name, value)
        
    def get_log(self):
        """
        return str: (None, Debug or File)
        """
        return self._get_it("log", "None")
    def set_log(self, log):
        self._set_it("log", log)
        
    def get_log_file(self):
        return self._get_it("log_file", "umit.log")
    def set_log_file(self, filename):
        self._set_it("log_file", filename)
    
    
    log = property(get_log, set_log)
    log_file = property(get_log_file, set_log_file)

        
        
        
        
        