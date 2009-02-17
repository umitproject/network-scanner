#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2007 Insecure.Com LLC.
#
# Author: Guilherme Polo <ggpolo@gmail.com>
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
Core Scheduler Controller
"""

# If you want to start Scheduler at system startup, please, especify here
# umit config dir. XXX outdated comment
# CONFIG_DIR = /home/myuser/.umit
CONFIG_DIR = ''

import os
import sys
import signal

from umitCore.BGProcess import WindowsService
from umitCore import Scheduler
from umitCore.I18N import _
from umitCore.Paths import Path

HOME_CONF = None
RUNNING_FILE = None


class UMITSchedulerWinService(WindowsService):
    _svc_name_ = 'umit-scheduler'
    _svc_display_name_ = "%s service" % _svc_name_
    _svc_description_ = _svc_display_name_
    _exe_args_ = None # This is defined at bottom

    def __init__(self, args):
        WindowsService.__init__(self, args)

    def run(self):
        # _exe_args_ will be our sys.argv when this runs as a Windows service
        Scheduler.main('start', winhndl=self.hndl_waitstop, *sys.argv[1:])


def setup_homedir(usethis):
    """
    Setting umit home directory.
    """
    Path.force_set_umit_conf(usethis)

    global HOME_CONF, RUNNING_FILE

    HOME_CONF = os.path.split(Path.get_umit_conf())[0]
    RUNNING_FILE = os.path.join(HOME_CONF, 'schedrunning')


def usage():
    """
    Show help
    """
    try:
        program_name = __file__
    except AttributeError:
        if hasattr(sys, 'frozen'):
            program_name = sys.executable
        else:
            program_name = sys.argv[0]
    print (_("Usage:") +
            (" %s start|stop|cleanup|running <config_dir>" % program_name))


def main(args, verbose=True):
    # Quoting paths since they may contain spaces
    UMITSchedulerWinService._exe_args_ = '"%s" "%s"' % (sys.path[0], HOME_CONF)

    schedcontrol = Scheduler.SchedulerControl(RUNNING_FILE, HOME_CONF,
            verbose, UMITSchedulerWinService)
    cmds = {"start": schedcontrol.start,
            "stop": schedcontrol.stop,
            "cleanup": schedcontrol.cleanup,
            "running": schedcontrol.running
            }

    cmd_args = ()
    try:
        if args[0] == 'cleanup':
            cmd_args += (True, )
        return cmds[args[0]](*cmd_args)
    except KeyError, e:
        if verbose:
            print "Invalid command especified: %s" % e
            usage()
        return 1

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        usage()
        sys.exit(0)

    if CONFIG_DIR: # forcing especified dir
        setup_homedir(CONFIG_DIR)
    else:
        try:
            setup_homedir(sys.argv[2])
        except IndexError: # no path especified
            setup_homedir(os.path.join(os.path.expanduser("~"), '.umit'))

    sys.exit(main(sys.argv[1:]))
