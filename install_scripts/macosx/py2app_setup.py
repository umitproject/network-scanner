# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Authors: Adriano Monteiro Marques <adriano@umitproject.org>
#          Cleber Rodrigues <cleber.gnu@gmail.com>
#                           <cleber@globalred.com.br>
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
# Override the setup name in the main setup.py
from setuptools import setup

BIN_DIRNAME = 'bin'

py2app_options = dict(
        app = [os.path.join(BIN_DIRNAME, 'umit')],
        options = {'py2app': {'argv_emulation': True, 'compressed': True}},
        setup_requires = ["py2app"]
        )
