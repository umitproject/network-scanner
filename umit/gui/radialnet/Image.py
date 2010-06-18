# vim: set encoding=utf-8 :

# Copyright (C) 2007 Adriano Monteiro Marques
#
# Author: João Paulo de Souza Medeiros <ignotus21@gmail.com>
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
import sys
import gtk
import array

from umit.core.Paths import Path


FORMAT_RGBA = 4
FORMAT_RGB  = 3


def get_pixels_for_cairo_image_surface(pixbuf):
    """
    This method return the imgage stride and a python array.ArrayType
    containing the icon pixels of a gtk.gdk.Pixbuf that can be used by
    cairo.ImageSurface.create_for_data() method.
    """
    data = array.ArrayType('c')
    format = pixbuf.get_rowstride() / pixbuf.get_width()

    i = 0
    j = 0
    while i < len(pixbuf.get_pixels()):

        b, g, r = pixbuf.get_pixels()[i:i+FORMAT_RGB]

        if format == FORMAT_RGBA:
            a = pixbuf.get_pixels()[i + FORMAT_RGBA - 1]
        elif format == FORMAT_RGB:
            a = '\xff'
        else:
            raise TypeError, 'unknown image format'

        data[j:j+FORMAT_RGBA] = array.ArrayType('c', [r, g, b, a])

        i += format
        j += FORMAT_RGBA

    return (FORMAT_RGBA * pixbuf.get_width(), data)



class Image:
    """
    """
    def __init__(self, path=None):
        """
        """
        self.__path = path
        self.__cache = dict()


    def set_path(self, path):
        """
        """
        self.__path = path


    def get_pixbuf(self, icon, image_type='png'):
        """
        """
        if self.__path is None:
            return False

        if icon + image_type not in self.__cache:

            file = self.get_icon(icon, image_type)
            self.__cache[icon + image_type] = gtk.gdk.pixbuf_new_from_file(file)

        return self.__cache[icon + image_type]


    def get_icon(self, icon, image_type='png'):
        """
        """
        if self.__path is None:
            return False

        return os.path.join(self.__path, icon + "." + image_type)




class Pixmaps(Image):
    """
    """
    def __init__(self):
        """
        """
        Image.__init__(self, Path.pixmaps_dir)



class Icons(Image):
    """
    """
    def __init__(self):
        """
        """
        
        # Note integration:  May be icons shound't live within pixmaps_dir
        Image.__init__(self, os.path.join(Path.pixmaps_dir, "radialnet",
                                          "icons"))



class Application(Image):
    """
    """
    def __init__(self):
        """
        """
        
        # Note integration:  May be icons shound't live within pixmaps_dir
        # And may be this class is useless now.
        # TODO: Is it useless?
        Image.__init__(self, os.path.join(Path.pixmaps_dir,"radialnet",
                                          "application"))
