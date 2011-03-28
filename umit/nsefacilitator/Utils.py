# Copyright (C) 2007 Adriano Monteiro Marques <py.adriano@gmail.com>
#
# Author: Maxim Gavrilov <lovelymax@gmail.com>
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

"""
Aux module
"""
import gtk
from higwidgets.higscrollers import HIGScrolledWindow
from higwidgets.higdialogs import HIGAlertDialog

def _alert(header, text):
    """
    Show alert dialog with specified header and text
    """
    alert = HIGAlertDialog(
        message_format='<b>%s</b>' % header,
        secondary_text=text
        )
    alert.run()
    alert.destroy()

def scroll_wrap(widget, hig = True):
    """
    Wrap widget into scroll control
    """
    scroll = [gtk.ScrolledWindow, HIGScrolledWindow][hig]()
    scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    scroll.set_shadow_type(gtk.SHADOW_IN)
    scroll.add(widget)
    return scroll
    
