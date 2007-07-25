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

import os
import os.path
import Image, ImageDraw, ImageFont


print ">>> Adding the version number to splash screen"

splash = Image.open(os.path.join("utils", "images", "splash.png"))
font = ImageFont.truetype(os.path.join("utils", "fonts", "FreeSansBold.ttf"), 30)
umit_version = open(os.path.join("config", "umit_version")).readlines()[0]

edit_splash = ImageDraw.Draw(splash)
edit_splash.text((450, 165), umit_version, font=font, fill="#000")

splash.save(os.path.join("share", "pixmaps", "splash.png"))
