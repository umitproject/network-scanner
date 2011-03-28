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
Core module for generic script metainformation support

Module provides Script object which represents single local/remote script.
"""

import os.path
#from NmapFetch import NmapFetchScripts
from md5 import md5
from sha import sha
from luaParser import LuaParser

SAVEORDER = ['Name', 'ID', 'Description', 'Type', 'Author',
             'License', 'Categories', 'Rule', 'Version',
             'Path', 'URL', 'Size', 'MD5', 'SHA1', 'GPG']

class ScriptNotInstalled(Exception):
    """
    Exception raised when local operations are performed undo not installed scripts.
    """
    pass

class HashSumFailed(Exception):
    """
    Exception raised when MD5 or SHA1 sums of downloaded file are invalid
    """
    pass

class Script(object):
    """
    Single separate script metainformation object
    """
    def get_version(self):
        """
        Return script version
        """
        return self.version
    
    def _parse_version(self, version):
        """
        Align version till 3-digets tuple
        """
        if not version:
            return (0, 0, 0)
        res = [int(x) for x in version.split('.')] + [0, 0, 0]
        return tuple(res[0:3])

    def _parse_categories(self, categories):
        """
        Convert list of categories into set
        """
        if not categories.strip():
            return set(["untagged"])
        return set([c.strip() for c in categories.split(',')])

    def set_url_prefix(self, prefix):
        """
        Replace local path into Web-based
        """
        if self.path:
            self.url = prefix + os.path.basename(self.path)
            self.path = None

    def remove(self):
        """
        Remove local script
        """
        if not self.path:
            raise ScriptNotInstalled
        os.remove(self.path)
        self.path = ''

    def calculate_hash(self, data):
        m = md5()
        m.update(data)
        s = sha()
        s.update(data)
        return m.hexdigest(), s.hexdigest()
        
    def load(self, d):
        """
        Load script from dictionary
        """
        self.name = d['name']
        self.id = d.get('id', self.name)
        self.type = d.get('type', "nse")
        self.description = d.get('description', '')
        self.author = d.get('author', '')
        self.license = d.get('license', 'unknown')
        self.categories = self._parse_categories(d.get('categories', 'untagged'))
        self.rule = d.get('rule', 'unknown')
        self.version = self._parse_version(d.get('version', '0.0.0'))
        self.path = d.get('path', '')#NmapFetchScripts().fetchfile(d.get('path', ''))
        self.url = d.get('url', '')
        self.size = int(d.get('size', 0))
        self.md5 = d.get('md5', '')
        self.sha1 = d.get('sha1', '')
        self.gpg = d.get('gpg', '')

    def save_as_text(self):
        """
        Save text as text. Load are parsed bu ScriptBase object!
        """
        d = self.save()
        res = []
        for k in SAVEORDER:
            v = d.get(k.lower(), None)
            if v:
                v = "\n".join([x.replace(':', '\\:') or "." for x in str(v).splitlines()])
                res.append("%s: %s\n" % (k, v))
        return "".join(res)
        
    def save(self):
        """
        Return dictionary with script parameters
        """
        d = {}
        d['name'] = self.name
        if self.id != self.name:
            d['id'] = self.id
        if self.type != 'nse':
            d['type'] = self.type
        if self.description:
            d['description'] = self.description
        if self.author:
            d['author'] = self.author
        if self.license != 'unknown':
            d['license'] = self.license
        if self.categories != set(['untagged']):
            d['categories'] = ", ".join(self.categories)
        if self.rule != 'unknown':
            d['rule'] = self.rule
        if self.version != (0, 0, 0):
            d['version'] = '%d.%d.%d' % self.version
        if self.path:
            d['path'] = self.path #NmapFetchScripts().nmap_path(self.path)
        if self.url:
            d['url'] = self.url
        if self.size > 0:
            d['size'] = self.size
        if self.md5:
            d['md5'] = self.md5
        if self.sha1:
            d['sha1'] = self.sha1
        if self.gpg:
            d['gpg'] = self.gpg
        return d

    def load_file(self, filename):
        """
        Parse script file (currently only Lua) for metainformation
        """
        self.filename = filename #NmapFetchScripts().fetchfile(filename)

        f = file(self.filename, 'r')
        self.data = f.read()
        f.close()

        d = {}
        d['name'], type_ = os.path.splitext(os.path.basename(filename))
        d['type'] = type_[1:] # dot
        d['path'] = filename
        d['url'] = None
        d['size'] = len(self.data)
        d['md5'], d['sha1'] = self.calculate_hash(self.data)

        params = None
        if not params:
            parser = LuaParser(filename)
            d.update(parser.attr)
        self.load(d)

    def are_installed(self):
        """
        Returns are this script is local installed
        """
        return bool(self.path)

    def install(self, config):
        """
        Install script from url to the install directory provided by config
        
        Can raise IOError in case of no permissions to write in install directory
        """
        if self.are_installed():
            return None
        if not self.url:
            return None
        data = config.download(self.url)
        md5, sha1 = self.calculate_hash(data)
        if self.md5 and self.md5 != md5:
            raise HashSumFailed
        if self.sha1 and self.sha1 != sha1:
            raise HashSumFailed
        installed_path = config.install_script(self.name + "." + self.type, data)
        #print installed_path
        if installed_path:
            self.path = installed_path
        return installed_path

    def __repr__(self):
        type_ = ["URLScript", "LocalScript"][bool(self.path)]
        return "<%s: %s>" % (type_, self.name)
