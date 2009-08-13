# Copyright (C) 2009 Adriano Monteiro Marques
#
# Author:  Guilherme Polo <ggpolo@gmail.com>
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

class FileMissingError(Exception):
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return "File %r is missing." % self.filename

class OriginError(FileMissingError):
    def __init__(self, filename):
        super(OriginError, self).__init__(filename)

class DestinationError(FileMissingError):
    def __init__(self, filename):
        super(DestinationError, self).__init__(filename)
