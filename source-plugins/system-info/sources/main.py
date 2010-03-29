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

import os, sys
from functools import update_wrapper
from umit.plugin.Engine import Plugin

if os.name != "posix":
    raise Exception("I need Linux to work")

def trace(f):
    def newf(*args, **kw):
        print "calling %s with args %s, %s" % (f.__name__, args, kw)
        return f(*args, **kw)
    return update_wrapper(newf, f)

class SystemInfo(Plugin):
    def start(self, reader):
        pass

    def stop(self):
        pass

    @trace
    def get_routes(self):
        return "".join(os.popen("route -n").readlines())

    @trace
    def get_ifaces(self):
        return "".join(os.popen("ifconfig -a").readlines())

    @trace
    def get_name(self):
        return " ".join(os.uname())

__plugins__ = [SystemInfo]
