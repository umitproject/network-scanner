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
Core module for configuration support
"""

import os, os.path
from urlparse import urlparse

from NmapFetch import NmapFetchScripts, get_file_list
from nseScript import Script
from nseDownloader import DownloaderManager
from luaParser import ScriptParseException

NSECONFIG = os.path.expanduser("~/.umit/nseconfig")

class ConfigItem(object):
    """
    Base class for all possible configuration items

    All source children must provide reload_scripts(subcall) method which returns list of scripts
    from ones source.

    All install childern must provide install(name, data) method which tries to create script file
    in ones location.
    """
    def __init__(self, type_, path, config):
        """
        Construct item with selected type and path contained link to parent config object
        """
        self.type = type_
        self.path = path
        self.config = config

    def save(self):
        """
        Return item's string representation
        """
        return self.type + "\t" + self.path
    
    def __cmp__(self, other):
        """
        Comparing order is type -> path
        """
        return cmp(self.type, self.type) or cmp(self.path, other.path)

    def __repr__(self):
        return self.type + ':' + self.path

    def __str__(self):
        return self.type + '\t' + self.path

class SourceFileItem(ConfigItem):
    """
    Single local file source item
    """
    def __init__(self, path, config):
        """
        Constructor
        """
        ConfigItem.__init__(self, 'FILE', path, config)

    def reload_scripts(self, subcall = None):
        """
        Return list with single loaded file
        """
        res = []
        if subcall:
            subcall((0, 1))
        try:
            script = Script()
            script.load_file(self.path)
            res = [script]
        except ScriptParseException:
            pass
        if subcall:
            subcall((1,1))
        return res
        
class SourceDirItem(ConfigItem):
    """
    Directory of local files source item
    """
    def __init__(self, path, config):
        """
        Constructor
        """
        ConfigItem.__init__(self, 'DIR', path, config)

    def reload_scripts(self, subcall = None):
        """
        Return list of parsed script files from directory
        """
        res = []
        filelist = [x for x in get_file_list(self.path) if x.endswith('.nse')]
        for i, name in enumerate(filelist):
            if subcall:
                subcall((i, len(filelist)))
            fullname = os.path.join(self.path, name)
            try:
                script = Script()
                script.load_file(fullname)
                res.append(script)
            except ScriptParseException:
                pass
        if subcall:
            subcall((len(filelist), len(filelist)))
        return res        

class SourceURLItem(ConfigItem):
    """
    Single Web-based script file source
    """
    def __init__(self, path, config):
        """
        Constructor
        """
        ConfigItem.__init__(self, 'URL', path, config)

    def reload_scripts(self, subcall = None):
        """
        Return list with single downloaded and installed file
        """
        script = None
        if subcall: subcall((0, 1))
        data = self.config.download(self.path)
        if not data:
            return []
        name = urlparse(self.path)[2].split('/')[-1]
        installed_path = self.config.install_script(name, data)
        if installed_path:
            script = Script()
            script.load_file(installed_path)
            script.url = self.path
        if subcall: subcall((1, 1))
        if not script:
            return []
        return [script]
        

class SourceURLBaseItem(ConfigItem):
    """
    Web-based catalog of scripts source
    """
    def __init__(self, path, config):
        """
        Constructor
        """
        ConfigItem.__init__(self, 'URLBASE', path, config)
        
    def reload_scripts(self, subcall = None):
        """
        Return list of parsed scripts from downloaded catalog
        """
        from nseBase import ScriptBase
        if subcall: subcall((0, 1))
        data = self.config.download(self.path)
        if not data:
            return []
        base = ScriptBase(None)
        base.load_from_text(data)
        if subcall: subcall((1, 1))
        return base.get_scripts()
    
class InstallDirItem(ConfigItem):
    """
    Directory for installing downloadable scripts
    """
    def __init__(self, path, config):
        """
        Constructor
        """
        ConfigItem.__init__(self, 'INSTALLDIR', path, config)

    def install(self, name, data):
        """
        Trying to install script with given name and context to ones location.
        Return installed path on succees and None elsewhere.
        """
        fullpath = os.path.join(self.path, name)
        try:
            f = file(fullpath, "wb")
            f.write(data)
            f.close()
        except IOError, e:
            return None
        return fullpath

class HTTPProxyItem(ConfigItem):
    """
    HTTP proxy settings item
    """
    def __init__(self, path, config):
        """
        Constructor
        """
        ConfigItem.__init__(self, 'HTTPPROXY', path, config)

    def apply(self, proxies):
        """
        Setup proxy settings
        """
        proxies['http'] = self.path

class FTPProxyItem(ConfigItem):
    """
    FTP proxy settings item
    """
    def __init__(self, path, config):
        """
        Constructor
        """
        ConfigItem.__init__(self, 'FTPPROXY', path, config)

    def apply(self, proxies):
        """
        Setup proxy settings
        """
        proxies['ftp'] = self.path
        
class ScriptConfig(object):
    """
    Hold NSE Facilitator configuration settings
    """
    def __init__(self, filename = NSECONFIG):
        """
        Constructor don't load configuration file itselfs, use load() method after creation.
        """
        self.filename = filename
        self.downloader = DownloaderManager()
        self.reset()

    def __repr__(self):
        return "<ScriptConfig: %d sources>" % len(self.sources)
    
    def reset(self):
        """
        Reset configuration to empty state
        """
        self.sources = []
        self.install = []
        self.settings = []
        self.comments = []

    def get_proxies(self):
        """
        Return proxies dictionary
        """
        proxies = dict()
        for s in self.settings:
            s.apply(proxies)
        return proxies

    def set_proxies(self, proxies):
        """
        Set proxies settings
        """
        self.remove_item('HTTPPROXY')
        self.remove_item('FTPPROXY')
        if proxies.has_key('http'):
            self.add_item('HTTPPROXY', proxies['http'])
        if proxies.has_key('ftp'):
            self.add_item('FTPPROXY', proxies['ftp'])
        
    def download(self, url):
        """
        Download specified url from Web
        """
        proxies = self.get_proxies()
        self.downloader.set_proxies(proxies)
        return self.downloader.download(url)
    
    def install_script(self, name, data):
        """
        Install script with given name and contest using install items
        """
        if not data:
            return None
        for i in self.install:
            installed_path = i.install(name, data)
            if installed_path:
                return installed_path
        return None

    def set_default(self):
        """
        Reset configurtion to default state: take Nmap fetch directories as source
        """
        self.reset()
        dirs = [d for d in NmapFetchScripts().fetchdirs() if os.path.exists(d)]
        self.install = [InstallDirItem(d, self) for d in dirs if os.path.isdir(d)]
        self.sources = [SourceDirItem(d, self) for d in dirs]

    def get_sources(self):
        """
        Return list of sources without dublications
        """
        res = list(self.install)
        res.extend([x for x in self.sources if not x in self.install])
        return res

    def get_dirs(self):
        """
        Get source directories
        """
        return [x.path for x in self.sources if type(x) == SourceDirItem]

    def add_item(self, type_,  path):
        """
        Add new configuration item with specified type and path
        """
        sources = {
            'FILE' : SourceFileItem,
            'DIR'  : SourceDirItem,
            'URL'  : SourceURLItem,
            'URLBASE' : SourceURLBaseItem
        }
        install = {
            'INSTALLDIR' : (InstallDirItem, SourceDirItem)
        }
        settings = {
            'HTTPPROXY' : HTTPProxyItem,
            'FTPPROXY'  : FTPProxyItem
        }
        if type_ in sources:
            self.sources.append(sources[type_](path, self))
        elif type_ in install:
            self.install.append(install[type_][0](path, self))
            self.sources.append(install[type_][1](path, self))
        elif type_ in settings:
            self.remove_item(type_)
            self.settings.append(settings[type_](path, self))

    def remove_item(self, type_, path = None):
        """
        Remove item with specified type and path if exists
        """
        def with_path(s):
            return s.type != type_ or s.path != path
        def without_path(s):
            return s.type != type_
        if path:
            f = with_path
        else:
            f = without_path
        self.sources = filter(f, self.sources)
        self.install = filter(f, self.install)
        self.settings = filter(f, self.settings)
        
    def load_from_text(self, data):
        """
        Load configuration from string representation
        """
        self.reset()
        for line in data.splitlines():
            line = line.lstrip()
            if not line or line.startswith('#'): # empty or commented line
                self.comments.append(line)
                continue
            type_ = line.split()[0]
            path = line[line.find(type_) + len(type_):].strip()
            self.add_item(type_, path)

    def save_to_text(self):
        """
        Save configuration to string representation
        """
        res = []
        res.append("\n".join([x.save() for x in self.install]))
        res.append("\n")
        res.append("\n".join([x.save() for x in self.sources if not x in self.install]))
        res.append("\n")
        res.append("\n".join([x.save() for x in self.settings]))
        res.append("\n".join(self.comments))
        return "".join(res)
    
    def load(self):
        """
        Load configuration from own file name
        """
        if not self.filename:
            return
        try:
            f = open(self.filename, "r")
            data = f.read()
            f.close()
            self.load_from_text(data)
        except IOError:
            self.set_default()

    def save(self):
        """
        Save configuration to own file name
        """
        if not self.filename:
            return
        f = open(self.filename, "w")
        f.write(self.save_to_text())
        f.close()

    def create_script_list(self, callback = None):
        """
        Create script list from all reloaded sources

        Callback must be in form callback(src, all, current) where src is the current
        source, all and current are tuples with progress of whole operation
        and current source parsing in form (current item, total items)
        """
        def subcallback(callback, src, all):
            def subcallback_impl(current):
                callback(src, all, current)
            if not callback:
                return None
            return subcallback_impl
        scripts = []
        for i, src in enumerate(self.sources):
            subcall = subcallback(callback, src, (i, len(self.sources)))
            if subcall: subcall(None) # send current=None for every new source
            scripts.extend(src.reload_scripts(subcall))
        return scripts

if __name__ == "__main__":
    from nseBase import ScriptBase
    def callback(src, all, current):
        print src, all, current
        return True
    config = ScriptConfig()
    config.load()
    base = ScriptBase(config)
    base.reload(callback)
    base.save()
    config.save()
    #print base
    #base.save()
    #config.save()
    
