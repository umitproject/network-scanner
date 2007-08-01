#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import locale

LC_ALL = locale.setlocale(locale.LC_ALL, '')
LANG, ENC = locale.getdefaultlocale()
ERRORS = "ignore"

# If not correct locale could be retrieved, set en_US.utf8 as default
if ENC == None:
    ENC = "utf8"

if LANG == None:
    LANG = "en_US"

try:
    import gettext
    from gettext import gettext as _

    gettext.install('umit', unicode=True)

except ImportError:
    # define _() so program will not fail
    import __builtin__
    __builtin__.__dict__["_"] = str


def enc(string):
    """Encoding conversion. This function is entended to receive a locale
    created string with locale encoding and return an utf8 string.
    """
    # FIXME: Urgent! Find a way to make the encodings work here, decoding
    # from the correct codec and encoding to utf8, which should be the
    # pattern here. Currently, this only removes the chars that it can't encode,
    # and thus, the text may be very hard to understand, but yet, no error will
    # occour
    string = string.decode("utf8", ERRORS).encode("utf8", ERRORS)

    return string

if __name__ == '__main__':
    print _('UMIT - The nmap frontend')
