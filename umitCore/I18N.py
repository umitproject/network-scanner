# Copyright (C) 2005 Insecure.Com LLC.
#
# Author: Adriano Monteiro Marques <py.adriano@gmail.com>
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

from umitCore.Logging import log

LC_ALL = ""
try:
    import locale
    LC_ALL = locale.setlocale(locale.LC_ALL, '')
except:
    pass

try:
    import gettext
    from gettext import gettext as _
    
    gettext.install('umit', unicode=True)

except ImportError:
    log.critical("You don't have gettext module, no internationalization will be used.")
    
    # define _() so program will not fail
    import __builtin__
    __builtin__.__dict__["_"] = str


if __name__ == '__main__':
    print _('UMIT - The nmap frontend')
