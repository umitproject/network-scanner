# Copyright (C) 2007 Adriano Monteiro Marques
#
# Authors: Guilherme Polo <ggpolo@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

"""
GUI for displaying Scheduler log.
"""

import os
import gtk
import gobject

from umit.core.I18N import _
from umit.core.Paths import Path

SCHEDLOG = Path.sched_log

class SchedLog(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)

        self.logstat = None
        self.file_content = open(SCHEDLOG, "r")
        self.content = self.file_content.read()

        self.textview = gtk.TextView()
        self.textbuffer = gtk.TextBuffer()

        self.connect('realize', self._on_realize)
        gobject.timeout_add(2000, self._load_sched_log)

        self.__set_props()
        self.__layout()

    def _on_realize(self, event):
        """
        On window realize, show log content.
        """
        self._load_sched_log()


    def _load_sched_log(self):
        """
        Load scheduler log contents into textview.
        """
        newstat = os.stat(SCHEDLOG).st_mtime
        if newstat != self.logstat:
            if self.logstat:
                self.textbuffer.set_text("")
                self.content = self.content + self.file_content.read()

            self.logstat = newstat

            end_iter = self.textbuffer.get_end_iter()
            self.textbuffer.insert(end_iter, self.content)
            self.textview.scroll_to_mark(self.textbuffer.get_insert(), 0)

        return True


    def __set_props(self):
        """
        Set widget properties.
        """
        self.set_title(_("Scheduler Log"))
        self.textview.set_editable(False)
        self.textview.set_buffer(self.textbuffer)


    def __layout(self):
        """Layout window widgets."""
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.textview)
        sw.set_size_request(520, 325)

        self.add(sw)
