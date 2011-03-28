# Copyright (C) 2007 Adriano Monteiro Marques <py.adriano@gmail.com>
#
# Author: Maxim Gavrilov <lovelymax@gmail.com>
# Lua stub script: Diman Todorov <diman.todorov@gmail.com>
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
Module for parsing Lua NSE scripts

Trying to use native script interpretator if installed and using
regex search elsewhere.
"""
import re
import os.path
from subprocess import Popen, PIPE
from NmapFetch import NmapFetchScripts

from umit.core.UmitLogging import log
from umit.core.I18N import _

class ScriptParseException(Exception):
    """
    Can't parse script exception
    """
    pass

class ScriptParser(object):
    """
    Base class for parsers

    Sets filename and data members, initialize empty attr dictionary.
    Use attr member for get parsing resulting values
    """
    def __init__(self, filename):
        self.filename = NmapFetchScripts().fetchfile(filename)
        self.attr = dict()
        f = file(self.filename, 'r')
        self.data = f.read()
        f.close()

class LuaReParser(ScriptParser):
    """
    Regex Lua script parser
    """
    def __init__(self, filename):
        """
        Constructor parses given filename
        """
        ScriptParser.__init__(self, filename)
        
        self.keywords = ['id', 'description', 'author', 'license', 'version', 'categories']
        
        self._get_attr('id')
        self._get_attr('description')
        self._get_attr('author')
        self._get_attr('license')
        self._get_attr_list('categories')
        self.attr['content'] = self._get_content()
        if self._get_function('portrule'):
            self.attr['rule'] = 'port'
        elif self._get_function('hostrule'):
            self.attr['rule'] = 'host'
        else:
            self.attr['rule'] = None
        self.attr['version'] = self._get_attr('version')
        self.attr['version_'] = self._get_attr_('version')
        
    def _get_attr_list(self, listname):
        r = re.findall(listname + '\s*=\s*{([^\}]*)}', self.data)
        if r:
            l = [self._normilize(tag) for tag in re.findall('"([^\"]+)"', r[0])]
            self.attr[listname] = ",".join(l)
        
    def _get_attr(self, attrname):
        r = re.findall(attrname + '\s*=\s*"([^\"]+)"', self.data)
        if r:
            self.attr[attrname] = self._normilize(r[0])
            
    def _get_attr_(self, attrname):
        r = re.findall(attrname + '\s*=\s*"([^\"]+)"', self.data)
        if r:
            return self._normilize(r[0])
        else:
            return ""

    def _get_function(self, funcname):
        r = re.findall(funcname + '\s*=\s*function', self.data)
        return bool(r)
    
    def _get_content(self):
        content = ""
        lines = self.data.split('\n')
        for line in lines:
            aux = True
            for key in self.keywords:
                if line.startswith(key):
                    aux = False
            if aux:
                content = content + line + '\n'
        first_line = re.search('[^\n]', content).start()
        return content[first_line:]

    def _normilize(self, string):
        string = string.replace('\n', ' ')
        string = string.replace('\\', ' ')
        string = string.replace('   ', ' ')
        string = string.replace('   ', '\n')
        return " ".join(string.split(" ")).strip()
        # more script-related breaks
        #return "\n".join([" ".join(s.split(" ")).strip()
        #                  for s in string.replace('\\', '\n').split("\n")])

class LuaNativeParser(ScriptParser):
    """
    Lua script parser uses installed Lua interpretator
    """
    stub_header="""
function show(s)
  if s == nil then
    x = 'nil'
  else
    x = string.gsub(s, '\\n', '\\\\n')
  end
  print(x)
end

function showlist(s)
  if s == nil then
     x = 'nil'
  else
     x = table.concat(s, ',')
  end
  print(x)
end
"""

    stub_output="""
    show(%(droz)sid)
    show(%(droz)sdescription)
    show(%(droz)sauthor)
    show(%(droz)slicense)
    showlist(%(droz)scategories)
    show(type(%(droz)sportrule))
    show(type(%(droz)shostrule))
    show(%(droz)sversion)
"""    

    stub_file="""
    %(stub_header)s
--while true do
  name = io.read()
--    if name == 'quit' then
--      break
--    end
  local narf = loadfile(name)
  if narf == nil then
    print('ERROR')
  else
    local zod = coroutine.create(narf)
    coroutine.resume(zod)
    local droz = debug.getfenv(zod)
    %(stub_output)s
  end
--end
""" % {'stub_header' : stub_header,
       'stub_output' : stub_output % {'droz' : 'droz.'}}

    stub_data="%(data)s" + """
    %(stub_header)s
    %(stub_output)s
""" % {'stub_header' : stub_header,
       'stub_output' : stub_output % {'droz' : ''}}

    def __init__(self, filename):
        """
        Constructor parses given filename
        """
        ScriptParser.__init__(self, filename)
        p = Popen(["lua", "-e", self.stub_file, "-i"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
         # TODO: find some way to interact line-by-line
         #       this prevent Lua interpretator from running many times
         #       and save much time
        (output, error) = p.communicate(self.filename + "\nquit\n")
        self._parse_output(output)

    def _parse_output(self, output):
        try:
            l = output.split('\n')
            self._translate('id', l[0])
            self._translate('description', l[1])
            self._translate('author', l[2])
            self._translate('license', l[3])
            self._translate('categories', l[4])
            if l[5] != "nil":
                self.attr['rule'] = 'port'
            elif l[6] != "nil":
                self.attr['rule'] = 'host'
            else:
                self.attr['rule'] = 'unknown'
            self._translate('version', l[7])
        except IndexError:
            raise ScriptParseException
        
    def _translate(self, attrname, s):
        if s == 'nil':
            return
        lines = [x.strip() for x in s.split('\\n')]
        self.attr[attrname] = "\n".join(lines)


# Trying to use installed Lua for parsing
LuaParser = LuaReParser
try:
    p = Popen(["lua", "-v"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, version_info = p.communicate()
    del p
    if version_info.startswith('Lua 5.'):
        log.warning(_("LuaParser: Native Lua parser selected"))
        LuaParser = LuaNativeParser
    else:
        log.warning(_("LuaParser: Your Lua version is too old so regexp parsing will be used"))
except OSError, e:
    log.warning(_("LuaParser: Can't find lua interpreter so regexp parsing will be used"))

if __name__ == "__main__":
    parser = LuaNativeParser('SMTP_openrelay_test.nse')
    print parser.attr
    
