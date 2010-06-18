#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 Adriano Monteiro Marques
#
# Author: Luís A. Bastião Silva <luis.kop@gmail.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import os
import sys

from umit.core.I18N import _
from umit.core.Paths import Path, check_access

from higwidgets.higdialogs import HIGAlertDialog

def verify_config_access():
    """
    Verify config access, detecting if is possible to write and read files
    """
    if (not check_access(Path.config_file, os.R_OK and os.W_OK )):
        error_text = _('''You do not have access to config files!\nPlease run Umit as root or change permissions %s 
        ''' % Path.config_dir)

        d = HIGAlertDialog(message_format=_('Permission Denied'),
                            secondary_text=error_text)
        d.run()
        sys.exit(0)