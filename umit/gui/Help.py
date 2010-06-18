#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 Adriano Monteiro Marques
#
# Authors: Luís A. Bastião Silva <luis.kop@gmail.com>
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

import re

import webbrowser
from higwidgets.higdialogs import HIGAlertDialog
from umit.core.Paths import Path
from umit.core.Utils import open_url_as

from umit.core.UmitLogging import log
from umit.core.I18N import _
import os
from os.path import abspath, join, exists

"""
The goal of this module is management help stuff, like open help as browser, etc.
"""
def get_filename(url):
        p = re.compile('([a-zA-Z0-9_]*)\.html')
        list_str = p.findall(url)
        result = ""
        if len(list_str) != 0:
                result = list_str.pop(0) + ".html"
        return result
        


def show_help(parent,url):
        import webbrowser
        url_final = get_filename(url)
        doc_path = abspath(join(Path.docs_dir, url_final))
        log.warning(">>> Openning documentation: %s" % doc_path)
        if exists(doc_path) and os.access(doc_path, os.R_OK):
            webbrowser.open("file://%s" % doc_path, new=open_url_as())
        else:
            d = HIGAlertDialog(parent=parent,
                               message_format=_("Couldn't find \
documentation files!"),
                               secondary_text=_("""Umit couldn't find the \
documentation files. Please, go to Umit's website and have the latest \
documentation in our Support & Development section."""))
            d.run()
            d.destroy()