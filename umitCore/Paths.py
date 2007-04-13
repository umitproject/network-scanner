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


umit_conf_dir = "config/umit"
umit_conf = os.path.join(umit_conf_dir, "umit.conf")


log.debug(">>> Config dir: %s" % umit_conf_dir)
log.debug(">>> Config file: %s" % umit_conf)



#######
# Paths
class Paths(object):
    """Paths
    """

    paths_section = "paths"
    
    def __init__(self):
        self.search = BasicSearch()
        self.umit_conf = UmitConfigParser()
        self.using_main = False

        # Place supposed to have the user's config file
        supposed_user_conf = os.path.join(base_paths['user_dir'], base_paths['config_file'])

        if os.path.exists(supposed_user_conf) and self.search.check_access(supposed_user_conf, os.R_OK):
            self.config_file = supposed_user_conf
            self.umit_conf.read(self.config_file)
        elif not os.path.exists(supposed_user_conf) and \
             not self.search.check_access(base_paths['user_dir'], os.R_OK and os.W_OK):
            result = create_user_dir(HOME)
            self.umit_conf.read(result['config_file'])
            [self.__set_it(opt, result[opt]) for opt in result]
        else:
            self.using_main = True
            self.config_file = umit_conf
            self.umit_conf.read(self.config_file)

        log.debug('>>> Config file: %s' % self.config_file)
        log.debug(">>> Umit config file successfully instanciated")

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

    #########
    # GET IT!
    def __get_it(self, option, default = False):
        log.debug(">>> __get__it option: %s" % option)
        if default:
            return self.umit_conf.get(self.paths_section, option, default)
        
        return self.umit_conf.get(self.paths_section, option)

    #########
    # SET IT!
    def __set_it(self, option, content):
        log.debug(">>> __set__it option: %s" % option)
        self.umit_conf.set(self.paths_section, option, content)
    

    def get_i18n_dir(self):
        """Tries to retrieve i18n directory absolute location
        Raise PathNotFound Exception if can't find it
        """
        return self.__get_it('i18n_dir')
    
    def set_i18n_dir(self, path):
        """Verify the existance of this path, and if it really contains i18n files
        If we already know umit.conf location, write this information on it
        """
        self.__set_it('i18n_dir', path)

    def get_pixmaps_dir(self):
        """Tries to retrieve pixmaps directory absolute location.
        Raise PathNotFound Exception if can't find it
        """
        return self.__get_it('pixmaps_dir')
    
    def set_pixmaps_dir(self, path):
        """Verify the existance of this path, and if it really contains pixmap files
        If we already know umit.conf location, write this information on it
        """
        self.__set_it('pixmaps_dir', path)

    def get_config_dir(self):
        """Tries to retrieve config files directory absolute location.
        Raise PathNotFound Exception if can't find it
        """
        return self.__get_it('config_dir')

    def set_config_dir(self, path):
        """Verify the existance of this path, and if it really contains the config file
        If we already know umit.conf location, write this information on it
        """
        self.__set_it('config_dir', path)

    def get_config_file(self):
        """Get UMIT config file
        """
        return self.__get_it('config_file')

    def set_config_file(self, config_file):
        """Set UMIT config file
        """
        self.__set_it('config_file', config_file)

    def set_user_dir(self, path):
        """Define user's UMIT directory location. If path doesn't exist nor have acces
        permissions, raises PathNotFound and PathAccessDenied Exceptions respectivately
        """
        self.__set_it('user_dir', path)

    def get_user_dir(self):
        """Tries to retrieve config files directory absolute location.
        Raise PathNotFound Exception if can't find it
        """
        self.__get_it('user_dir')

    def get_target_list(self):
        return self.__get_it('target_list')
        
    def set_target_list(self, target_list):
        self.__set_it('target_list', target_list)

    def get_profile_editor(self):
        return self.__get_it('profile_editor')

    def set_profile_editor(self, profile_editor):
        self.__set_it('profile_editor', profile_editor)

    def get_wizard(self):
        return self.__get_it('wizard')
        
    def set_wizard(self, wizard):
        self.__set_it('wizard', wizard)

    def get_scan_profile(self):
        return self.__get_it('scan_profile')

    def set_scan_profile(self, scan_profile):
        self.__set_it('scan_profile', scan_profile)

    def get_recent_scans(self):
        return self.__get_it('recent_scans')

    def set_recent_scans(self, recent_scans):
        self.__set_it('recent_scans', recent_scans)

    def get_umit_op(self):
        return self.__get_it('umit_op')

    def set_umit_op(self, op):
        self.__set_it('umit_op', op)

    def get_options(self):
        return self.__get_it('options')

    def set_options(self, path):
        self.__set_it('options', path)

    def get_umit_opi(self):
        return self.__get_it('umit_opi')

    def set_umit_opi(self, path):
        self.__set_it('umit_opi', path)

    def get_umit_opt(self):
        return self.__get_it('umit_opt')

    def set_umit_opt(self, path):
        self.__set_it('umit_opt', path)

    def get_umit_opf(self):
        return self.__get_it('umit_opf')

    def set_umit_opf(self, path):
        self.__set_it('umit_opf', path)

    def get_umitdb(self):
        return self.__get_it('umitdb')

    def set_umitdb(self, path):
        self.__set_it('umitdb', path)

    def get_services(self):
        return self.__get_it('services')

    def set_services(self, path):
        self.__set_it('services', path)

    def get_os_db(self):
        return self.__get_it('os_db')

    def set_os_db(self, path):
        self.__set_it('os_db', path)

    def get_os_fingerprints(self):
        return self.__get_it('os_fingerprints')

    def set_os_fingerprints(self, path):
        self.__set_it('os_fingerprints', path)

    def get_services_dump(self):
        return self.__get_it('services_dump')

    def set_services_dump(self, path):
        self.__set_it('services_dump', path)

    def get_os_dump(self):
        return self.__get_it('os_dump')
    
    def set_os_dump(self, path):
        self.__set_it('os_dump', path)

    def get_umit_version(self):
        return self.__get_it('umit_version')

    def set_umit_version(self, path):
        self.__set_it('umit_version', path)

    def get_os_classification(self):
        return self.__get_it('os_classification')

    def set_os_classification(self, path):
        self.__set_it('os_classification', path)

    def get_umit_icon(self):
        return self.__get_it('umit_icon')

    def set_umit_icon(self, path):
        self.__set_it('umit_icon', path)

    def get_nmap_command_path(self):
        return self.__get_it("nmap_command_path")

    def set_nmap_command_path(self, path):
        self.__set_it("nmap_command_path", path)

    i18n_dir = property(get_i18n_dir, set_i18n_dir, doc=_("i18n_dir"))
    pixmaps_dir = property(get_pixmaps_dir, set_pixmaps_dir, doc=_("pixmaps_dir"))
    config_dir = property(get_config_dir, set_config_dir, doc=_("config_dir"))
    user_dir = property(get_user_dir, set_user_dir, doc=_("user_dir"))
    config_file = property(get_config_file, set_config_file, doc=_("config_file"))
    target_list = property(get_target_list, set_target_list, doc=_("target_list"))
    profile_editor = property(get_profile_editor, set_profile_editor, doc=_("profile_editor"))
    wizard = property(get_wizard, set_wizard, doc=_("wizard"))
    scan_profile = property(get_scan_profile, set_scan_profile, doc=_("scan_profile"))
    recent_scans = property(get_recent_scans, set_recent_scans, doc=_("recent_scans"))
    options = property(get_options, set_options, doc=_("options"))
    umit_op = property(get_umit_op, set_umit_op, doc=_("umit_op"))
    umit_opi = property(get_umit_opi, set_umit_opi, doc=_("umit_opi"))
    umit_opt = property(get_umit_opt, set_umit_opt, doc=_("umit_opt"))
    umit_opf = property(get_umit_opf, set_umit_opf, doc=_("umit_opf"))
    umitdb = property(get_umitdb, set_umitdb, doc=_("umitdb"))
    services_dump = property(get_services_dump, set_services_dump, doc=_("services_dump"))
    os_dump = property(get_os_dump, set_os_dump, doc=_("os_dump"))
    umit_version = property(get_umit_version, set_umit_version)
    os_classification = property(get_os_classification, set_os_classification)
    umit_icon = property(get_umit_icon, set_umit_icon)
    nmap_command_path = property(get_nmap_command_path, set_nmap_command_path)


    _i18n_dir = None
    _pixmaps_dir = None
    _config_dir = None
    _user_dir = None
    _config_file = None
    _target_list = None
    _profile_editor = None
    _wizard = None
    _scan_profile = None
    _recent_scans = None
    _options = None
    _umit_op = None
    _umit_opi = None
    _umit_opt = None
    _umit_opf = None
    _umitdb = None
    _services_dump = None
    _os_dump = None
    _umit_version = None
    _os_classification = None
    _umit_icon = None
    _nmap_command_path = None


###########
# Searching
class BasicSearch(object):
    UMIT_DIRECTORIES = ['umitCore', 'umitGUI', 'share']
    UMIT_FILES = ['umit']
    
    def check_access(self, path, permission):
        return os.path.exists(path) and os.access(path, permission)

    def get_file_list(self, path):
        return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    def get_dir_list(self, path):
        return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

    def search_directory(self, path, directory):
        if self.check_access(path, os.R_OK):
            dir_list = self.get_dir_list(path)
            
            if type(directory) == type([]):
                for d in directory:
                    if d not in dir_list:
                        break
                else:
                    return path
                return False
            if type(directory) == type(""):
                if directory in dir_list:
                    return path
                return False
        
        raise Exception # PathAccessDenied Exception

    def search_dir_with_file(self, path, filename):
        """Search for an specified file inside the directory tree of a given path
        """
        if self.check_access(path, os.R_OK):
            if filename in self.get_file_list(path):
                return path
        return False

    def search_file(self, path, filename):
        """Search for an specified file inside the directory tree of a given path
        """
        if self.check_access(path, os.R_OK):
            if filename in self.get_file_list(path):
                return os.path.join(path, filename)
        return False
        

    def search_pattern(self, path, pattern):
        """Search for a  filename that matches the given patern. Return first found
        """
        if self.check_access(path, os.R_OK):
            file_regex = re.compile(pattern)

            for f in self.get_file_list(path):
                if file_regex.match(f):
                    return os.path.join(path, f)
            return False
        
        raise PathNotFound

    def search_dir_pattern(self, path, pattern):
        """Search for a  filename that matches the given patern
        """
        if self.check_access(path, os.R_OK):
            file_regex = re.compile(pattern)

            for f in self.get_file_list(path):
                if file_regex.match(f):
                    return path
            return False
        
        raise PathNotFound
    
    def search_path_with_files(self, path, files):
        if self.check_access(path, os.R_OK):
            file_list = self.get_file_list(path)

            if type(files) == type([]):
                for f in files:
                    if f not in file_list:
                        break
                else:
                    return path
                return False
            elif type(files) == type(''):
                if files in self.get_file_list(path):
                    return path
                return False
            
            raise Exception # WrongSearchParameters

    def check_umit_dir(self, path):
        log.debug("check_umit_dir (argument): %s" % path)
        dir_content = os.listdir(path)
        
        for directory in self.UMIT_DIRECTORIES:
            log.debug("Checking if directory %s exists" % directory)
            if directory not in dir_content:
                return False
        
        for umit_file in self.UMIT_FILES:
            log.debug("Checking if umit file %s exists" % umit_file)
            if umit_file not in dir_content:
                return False
        return True

    def search_extensions(self, path, extensions):
        """Verify if a given path contains given extensions.
        The path must contain every given extension, else returns False
        """
        if self.check_access(path, os.R_OK):
            file_list = self.get_file_list(path)

            if type(extensions) == type([]):
                for ext in extensions:
                    ext_regex = re.compile('^.*%s$' % re.escape(ext))
                    for f in file_list:
                        if ext_regex.match(f):
                            break
                    else:
                        return False
                return path
            elif type(extensions) == type(''):
                ext_regex = re.compile('^.*%s$' % re.escape(extensions))
                for f in file_list:
                    if ext_regex.match(f):
                        return path
                else:
                    return False
            raise Exception # WrongSearchParameters
        
        raise Exception # PathNotFound Exception


####################################
# Functions for directories creation

def create_user_dir(user_home):
    log.debug(">>> Create user dir at given home: %s" % user_home)
    main_umit_conf = UmitConfigParser()
    main_umit_conf.read(umit_conf)
    paths_section = "paths"
    
    user_dir = os.path.join(user_home, base_paths['config_dir'])
    
    if os.path.exists(user_home) and os.access(user_home, os.R_OK and os.W_OK)\
           and not os.path.exists(user_dir):
        os.mkdir(user_dir)
        log.debug(">>> Umit user dir successfully created! %s" % user_dir)
    else:
        log.warning(">>> No permissions to create user dir!")
        return False

    return dict(user_dir = user_dir,
                config_dir = user_dir,
                config_file = copy_config_file("umit.conf", umit_conf_dir, user_dir),
                target_list = copy_config_file("target_list.txt", umit_conf_dir, user_dir),
                recent_scans = copy_config_file("recent_scans.txt", umit_conf_dir, user_dir),
                scan_profile = copy_config_file("scan_profile.usp", umit_conf_dir, user_dir),
                profile_editor = copy_config_file("profile_editor.xml", umit_conf_dir,
                                                  user_dir),
                options = copy_config_file("options.xml", umit_conf_dir, user_dir),
                wizard = copy_config_file("wizard.xml", umit_conf_dir, user_dir),
                i18n_dir = main_umit_conf.get(paths_section, "i18n_dir"),
                services_dump = main_umit_conf.get(paths_section, "services_dump"))

def copy_config_file(filename, dir_origin, dir_destiny):
    log.debug(">>> copy_config_file %s to %s" % (filename, dir_destiny))
    
    origin = os.path.join(dir_origin, filename)
    destiny = os.path.join(dir_destiny, filename)
    
    if not os.path.exists(destiny):
        # Quick copy
        open(destiny, 'w').write(open(origin).read())
    return destiny

#########
# Singleton!
Path = Paths()
Search = BasicSearch()

if __name__ == '__main__':
    #Path.umit_conf.write(open('/tmp/teste', 'w'))
    #log.critical(Search.search_directory("/home/adriano", ["po"]))
    print ">>> I18N DIR:", Path.i18n_dir
    print ">>> PIXMAPS DIR:", Path.pixmaps_dir
    print ">>> CONFIG DIR:", Path.config_dir
    print ">>> CONFIG FILE:", Path.config_file
    print ">>> USER DIR:", Path.user_dir
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
    print ">>> UMIT ICON:", Path.umit_icon
