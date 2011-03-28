# Copyright (C) 2007 Adriano Monteiro Marques <py.adriano@gmail.com>
#
# Author: Maxim Gavrilov <lovelymax@gmail.com>
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
Nmap fetch file facilities and according functionality
"""
import os, os.path
import sys

def check_access(path, permission):
    """
    Check if file exists and has necessory permissions
    """
    return os.path.exists(path) and os.access(path, permission)

def get_file_list(path):
    """
    Return list of files from specified directory with read access to them
    """
    result = []
    try:
        for filename in os.listdir(path):
            fullpath = os.path.join(path, filename)
            if os.path.isfile(fullpath) and check_access(fullpath, os.R_OK):
                result.append(fullpath)
    except OSError:
        pass
    return result

# aux nmap_fetchfile functions
class NmapFetch(object):
    """
    Singletone object for providing Nmap fetch functionality
    """
    # Singletone for optimization
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(NmapFetch, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    _initialized = False
    def __init__(self):
        if not self._initialized:
            self.dirs = self.__fetchdirs()
            self._initialized = True

    def fetchdirs(self):
        """
        Return fetching directories
        """
        return self.dirs

    def fetchfile(self, filename):
        """
        Return full path from (possible) short filename
        """
        for path in self.fetchdirs():
            fullpath = os.path.join(path, filename)
            if check_access(fullpath, os.R_OK):
                return fullpath
        return None

    def get_file_list(self):
        """
        Return completely file list from fetching directories
        """
        result = []
        for path in self.fetchdirs():
            result.extend(get_file_list(path))
        return result

    def nmap_path(self, path):
        """
        Return shortest path according to Nmap fetch directories
        """
        fullpath = os.path.abspath(path)
        for p in self.fetchdirs():
            if fullpath.startswith(p):
                return fullpath[len(p)+1:] # XXX: check +1 (removing last slash) on Windows
        return fullpath

    def __fetchdirs(self):
        # standart Nmap searching directories (see nmap.cc:nmap_fetchfile function)
        def varpath():
            return os.path.expandvars("${NMAPDIR}")
        def uidpath():
            return os.path.join(pwd.getpwuid(os.getuid()).pw_dir, ".nmap")
        def euidpath():
            return os.path.join(pwd.getpwuid(os.geteuid()).pw_dir, ".nmap")
        def userpath():
            return os.path.expanduser("~")
        def datadirpath_win():
            return "c:\\nmap"
        def datadirpath2_win():
            return "c:\\Program Files\\nmap"
        def datadirpath():
            return "/usr/share/nmap/"
        def datadirpath2():
            return "/usr/local/share/nmap/"
        def currentpath():
            return "."

        if sys.platform != 'win32':
            import pwd
            checklist = [varpath, uidpath, euidpath, datadirpath, datadirpath2, currentpath]
        else:
            checklist = [varpath, userpath, datadirpath_win, datadirpath2_win, currentpath]

        paths = [os.path.abspath(f()) for f in checklist]
        # XXX: not stable
        return list(set(paths))

class NmapFetchScripts(NmapFetch):
    """
    Singletone object for providing Nmap script fetching functionality
    """
    # Singletone for optimization
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance
    
    _initialized = False
    def __init__(self):
        if not self._initialized:
            NmapFetch.__init__(self)
            self.dirs = [os.path.join(d, "scripts") for d in self.dirs]

    def get_file_list(self):
        """
        Return list of avaliable scripts in fetching directories
        """
        return [f for f in NmapFetch.get_file_list(self) if f.endswith(".nse")]

if __name__ == "__main__":
    print NmapFetch().fetchdirs()
    print NmapFetchScripts().fetchdirs()
