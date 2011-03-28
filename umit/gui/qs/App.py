# -*- coding: utf-8 -*-

# Copyright (C) 2009 Adriano Monteiro Marques.
#
# Author: Daniel Mendes Cassiano <dcassiano@umitproject.org>
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
import sys
import gtk

from umit.core.Paths import Path
from umit.gui.qs.Main import Main

class App(Main):
    """
    This module will manage all QS app.
    """
    
    def __init__(self):
        Path.set_umit_conf(os.path.dirname(sys.argv[0]))
        Path.set_running_path(os.path.abspath(os.path.dirname(sys.argv[0])))
        
    def run(self):
        Main.__init__(self)
        # Run main loop
        gtk.main()
        
    def safe_shutdown(self, signum, stack):
        log.debug("\n\n%s\nSAFE SHUTDOWN!\n%s\n" % ("#" * 30, "#" * 30))
        log.debug("SIGNUM: %s" % signum)

        self._exit_cb()
        sys.exit(signum)
        
if __name__ == "__main__":
    a = App()
    gtk.main()