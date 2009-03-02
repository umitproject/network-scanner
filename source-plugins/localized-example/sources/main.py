#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2008 Adriano Monteiro Marques
#
# Author: Francesco Piccinno <stack.box@gmail.com>
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

import gettext

from umit.plugin.Core import Core
from umit.plugin.Engine import Plugin
from umit.plugin.Atoms import StringFile

_ = str

class Localize(Plugin):
    def start(self, reader):
        cat = reader.bind_translation("localizer")

        if cat:
            global _
            _ = cat.gettext

        print _("What the hell are you doing?")

    def stop(self):
        print _("Stopping localize ...")

__plugins__ = [Localize]
