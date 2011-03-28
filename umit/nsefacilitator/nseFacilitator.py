#!/usr/bin/python
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

__doc__ = """
Run the command line NSE Facilitator tool.

This is standalon command line program for manage NSE scripts.

Commands:
reload - reload all sources
install - install selected scripts
installall - install all script not yet installed
upgrade - upgrade selected scripts to newest version
upgradeall - upgrade all installed scripts to newest version
remove - remove selected scripts
list - print list of installed scripts
genbase - generate base from directory with scripts

usage: nseFacilitator.py <command> [<scriptname1>, <scriptname2>, ...]
"""

import sys
from optparse import OptionParser

from nseBase import ScriptBase, ScriptItem
from nseConfig import ScriptConfig

__all__ = [] # no exports

def parse_args():
    parser = OptionParser()
    return parser.parse_args()[1]

def help():
    print __doc__

def genbase(command, args):
    prefix = command[len("genbase"):]
    if prefix and prefix[0] == '=':
        prefix = prefix[1:]
        
    conf = ScriptConfig(None)
    for path in args:
        conf.add_item('DIR', path)
    base = ScriptBase(conf)
    base.reload()
    if prefix:
        base.set_url_prefix(prefix)
    base.save('nsebase')

def callback(src, all, current):
    if current is None:
        print "%d(%d) %s %s" % (all[0] + 1, all[1], src.type, src.path)
        
if __name__ == "__main__":
    args = parse_args()
    if not args:
        help()
        sys.exit(0)

    conf = ScriptConfig()
    conf.load()
    base = ScriptBase(conf)
    base.load()

    command, args = args[0], args[1:]
    if command == "reload":
        base.reload(callback=callback)
    elif command == "install":
        for name in args:
            base.install(name)
    elif command == "installall":
        base.install_all()
    elif command == "remove":
        for name in args:
            base.remove(name)
    elif command == "upgrade":
        for name in args:
            base.upgrade(name)
    elif command == "upgradeall":
        base.upgrade_all()
    elif command == "list":
        states = {
            ScriptItem.STATE_NOT_INSTALLED : " ",
            ScriptItem.STATE_UPGRADABLE : "U",
            ScriptItem.STATE_INSTALLED : "I" 
        }
        name_dict = dict([(item.name, item) for item in base.get_script_items()])
        for name in sorted(name_dict.keys()):
            print states[name_dict[name].get_state()], name
    elif command.startswith("genbase"):
        genbase(command, args)
    else:
        help()
        sys.exit(0)
    base.save()
    conf.save()
