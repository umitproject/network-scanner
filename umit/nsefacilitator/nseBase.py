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

"""Core module for all script management operations

ScriptItem holds all known versions of the scripts with the same name.
ScriptBase is ScriptItem's container with script management operations
install/upgrade/remove support.
"""
import os.path
from nseScript import Script
from nseConfig import ScriptConfig

NSEBASE = os.path.expanduser("~/.umit/nsebase") # default path to script base

class ScriptItem(object):
    """
    Single script item in script base, manage versions and according functionality
    """
    STATE_NOT_INSTALLED = 0
    STATE_UPGRADABLE = 1
    STATE_INSTALLED = 2
    
    def __init__(self, script):
        """
        Construct script item contained one inital script
        """
        self.script_list = [script]
        self.name = script.name

    def __repr__(self):
        current = self.get_last_installed()
        last = self.get_last_version()
        if current and last.version == current.version:
            return "<ScriptItem: %s (%d) current version %s>" % (self.name,
                                                                 len(self.script_list),
                                                                 str(current.version))
        if not current:
            return "<ScriptItem: %s (%d) not installed, newest %s>" % (self.name,
                                                                       len(self.script_list),
                                                                       str(last.version))
        return "<ScriptItem: %s (%d) current version %s, newest %s>" % (self.name,
                                                                        len(self.script_list),
                                                                        str(current.version),
                                                                        str(last.version))
    
    def add(self, script):
        """
        Add script to script item. Script name must be the same to ScriptItem one.
        """
        if self.name != script.name:
            raise Exception, "Trying to add script '%s' to ScriptItem '%s'" % (script.name, self.name)
        self.script_list.append(script)
        self._prepare()
        
    def _prepare(self):
        """
        Internal method for keeping scripts set in order
        """
        self.script_list.sort(key=Script.get_version)

    def get_scripts(self):
        """
        Return script list sorted in version order
        """
        return self.script_list
    
    def get_last_installed(self):
        """
        Return last installed version of script
        """
        result = None
        for script in self.script_list:
            if script.are_installed():
                result = script
        return result

    def get_last_version(self):
        """
        Return last known version of script
        """
        return self.script_list[-1]

    def get_state(self):
        """
        Return script state:
        STATE_NOT_INSTALLED - this script has not yet been installed
        STATE_INSTALLED - script has been installed and have the newest known version
        STATE_UPGRADABLE - script has been installed, but newer version are known
        """
        last = self.get_last_installed()
        if last is None:
            return self.STATE_NOT_INSTALLED
        if last.version == self.get_last_version().version:
            return self.STATE_INSTALLED
        return self.STATE_UPGRADABLE

    def install(self, config):
        """
        Install or upgrade script to newest version.
        config - ScriptConfig object
        """
        self.get_last_version().install(config)
        # TODO: scripts reparsing needed to remove items rewrited by install
        
    def remove(self):
        """
        Remove all installed scripts
        """
        for script in self.script_list:
            if script.are_installed():
                try:
                    script.remove()
                except OSError, e:
                    # TODO: show a message to user
                    print "%s:%s" % (script.path, str(e))
                
    def save_as_text(self):
        """
        Save all contained scripts into ScriptBase format
        """
        result = []
        for script in self.script_list:
            result.append(script.save_as_text())
            result.append("\n")
        return "".join(result)
    
class ScriptBase(object):
    """
    Contains all known scripts information in form of ScriptItem collection
    and provide method for script management.
    """
    def __init__(self, config):
        """
        Construct script base corresponding to configuration object.
        """
        self.config = config
        self.reset()

    def __repr__(self):
        return "<ScriptBase: " + str(self.get_script_items()) + ">"

    def get_config(self):
        """
        Return this base configuration object
        """
        return self.config
    
    def set_default(self):
        """
        Reset base to default state
        """
        self.reset()

    def get_script_items(self):
        """
        Return list of script items
        """
        return self.name_map.values()

    def get_scripts(self):
        """
        Return plain list of all known scripts
        """
        return [s for i in self.get_script_items() for s in i.get_scripts()]
    
    def reset(self):
        """
        Reset base to empty state
        """
        self.name_map = {}
        self.categories = set()

    def set_url_prefix(self, prefix):
        """
        Remove all scripts 'path' members and set downloadable URL according to prefix.
        This method using for generated server side URLBASE based on some script directories.
        """
        for item in self.get_script_items():
            for script in item.get_scripts():
                script.set_url_prefix(prefix)
            
    def reload(self, callback = None):
        """
        Reload base from corresponding configuration sources 
        """
        self.config.load()
        scripts = self.config.create_script_list(callback=callback)
        self.from_list(scripts)

    def install(self, scriptname):
        """
        Install script by name
        """
        item = self.name_map.get(scriptname, None)
        if item:
            item.install(self.config)

    def install_all(self):
        """
        Install all not yet installed scripts
        """
        for item in self.get_script_items():
            if item.get_state() == ScriptItem.STATE_NOT_INSTALLED:
                item.install(self.config)

    def remove(self, scriptname):
        """
        Remove script by name
        """
        item = self.name_map.get(scriptname, None)
        if item:
            item.remove()

    def upgrade(self, scriptname):
        """
        Upgrade script to newest version by name
        """
        item = self.name_map.get(scriptname, None)
        if item:
            if item.get_state() == ScriptItem.STATE_UPGRADABLE:
                item.install(self.config)

    def upgrade_all(self):
        """
        Upgrade all installed scripts to newest versions
        """
        for item in self.get_script_items():
            if item.get_state() == ScriptItem.STATE_UPGRADABLE:
                item.install(self.config)
    
    def from_list(self, script_list):
        """
        Fill base from list of scripts
        """
        self.reset()
        for script in script_list:
            sublist = self.name_map.get(script.name, None)
            if sublist:
                sublist.add(script)
            else:
                sublist = ScriptItem(script)
            self.name_map[script.name] = sublist
            self.categories.update(script.categories)
        
    def load_from_text(self, data):
        """
        Fill base from string data, contains scripts descriptions
        """
        self.reset()
        d = {}
        cur = None
        script_list = []
        for i, line in enumerate(data.splitlines()):
            line = line.strip()
            if not line:
                if d:
                    if not d.has_key('name'):
                        print "Script before line %d have no 'name' parameter" % i
                    else:
                        script = Script()
                        script.load(d)
                        script_list.append(script)
                    d = {}
                    cur = None
                continue
            sep = line.find(':')
            if sep != -1 and line[sep - 1] == '\\':
                sep = -1
            line = line.replace('\\:', ':')
            if cur is None and sep == -1:
                print "Unknown attribute at line %d" % i
                continue
            if sep != -1:
                cur = line[:sep].strip().lower()
                line = line[sep+1:].strip()
                if line == '.': line = ''
                d[cur] = line
            else:
                if line == '.': line = ''
                d[cur] = d[cur] + '\n' + line
        self.from_list(script_list)
        
    def load(self, filename = NSEBASE):
        """
        Fill base from file
        """
        self.reset()
        try:
            f = open(filename, "r")
            data = f.read()
            f.close()
            self.load_from_text(data)
        except IOError:
            self.set_default()

    def save_as_text(self):
        """
        Return base saved in string format
        """
        res = []
        for script in self.get_scripts():
            res.append(script.save_as_text())
            res.append('\n')
        return "".join(res)
        
    def save(self, filename = NSEBASE):
        """
        Save base to selected file
        """
        f = open(filename, "w")
        f.write(self.save_as_text())
        f.close()

if __name__ == "__main__":
    base = ScriptBase()
    base.load()
    print base
    base.save()
    
    
