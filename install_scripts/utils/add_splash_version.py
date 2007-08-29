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

import sys
import os
import os.path

try:
    import Image, ImageDraw, ImageFont
except:
    print ">>> PIL not available. Couldn't update splash version"
    sys.exit(1)


def add_version(base_dir, version, revision):
    print ">>> Adding the version number to splash screen"

    BASE_DIR = os.path.join("install_scripts", "utils")
    FONT = os.path.join(BASE_DIR, "fonts", "FreeSansBold.ttf")
    TEMPLATE = os.path.join(BASE_DIR, "images", "splash.png")

    if os.path.exists(FONT) and os.path.exists(TEMPLATE):
        splash = Image.open(TEMPLATE)
        font = ImageFont.truetype(FONT, 30)
        font2 = ImageFont.truetype(FONT, 10)

        edit_splash = ImageDraw.Draw(splash)
        edit_splash.text((450, 155), version, font=font, fill="#000")
        edit_splash.text((450, 182), "Rev. %s" % revision, font=font2, fill="#000")

        splash.save(os.path.join(base_dir, "share", "pixmaps", "splash.png"))
    else:
        print ">>> COULDN'T FIND TEMPLATE (%s) OR FONT (%s)" % (TEMPLATE, FONT)
