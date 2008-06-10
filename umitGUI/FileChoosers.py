#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
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

import gtk

from umitCore.I18N import _

class AllFilesFileFilter(gtk.FileFilter):
    def __init__(self):
        gtk.FileFilter.__init__(self)

        pattern = "*"
        self.add_pattern(pattern)
        self.set_name(_("All Files (%s)") % pattern)
        
class ProfileFileFilter(gtk.FileFilter):
    def __init__(self):
        gtk.FileFilter.__init__(self)

        pattern = "*.usp"
        self.add_pattern(pattern)
        self.set_name(_("Umit Scan Profile (%s)") % pattern)

class ResultsFileFilter(gtk.FileFilter):
    def __init__(self):
        gtk.FileFilter.__init__(self)

        pattern = "*.usr"
        self.add_pattern(pattern)
        self.set_name(_("Umit Scan Results (%s)") % pattern)

class RegularDiffiesFileFilter(gtk.FileFilter):
    def __init__(self):
        gtk.FileFilter.__init__(self)

        pattern = "*.urd"
        self.add_pattern(pattern)
        self.set_name(_("Umit Regular Diff (%s)") % pattern)

class HtmlDiffiesFileFilter(gtk.FileFilter):
    def __init__(self):
        gtk.FileFilter.__init__(self)

        pattern = "*.html"
        self.add_pattern(pattern)
        self.set_name(_("Umit HTML Diff (%s)") % pattern)

class ProfileFileChooserDialog(gtk.FileChooserDialog):
    def __init__(self, title="", parent=None,
                 action=gtk.FILE_CHOOSER_ACTION_OPEN,
                 buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                          gtk.STOCK_OPEN, gtk.RESPONSE_OK), backend=None):

        gtk.FileChooserDialog.__init__(self, title, parent,
                                       action, buttons)

        for f in (ProfileFileFilter(), AllFilesFileFilter()):
            self.add_filter(f)

class AllFilesFileChooserDialog(gtk.FileChooserDialog):
    def __init__(self, title="", parent=None,
                 action=gtk.FILE_CHOOSER_ACTION_OPEN,
                 buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                          gtk.STOCK_OPEN, gtk.RESPONSE_OK), backend=None):

        gtk.FileChooserDialog.__init__(self, title, parent,
                                       action, buttons)

        self.add_filter(AllFilesFileFilter())

class ResultsFileChooserDialog(gtk.FileChooserDialog):
    def __init__(self, title="", parent=None,
                 action=gtk.FILE_CHOOSER_ACTION_OPEN,
                 buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                          gtk.STOCK_OPEN, gtk.RESPONSE_OK), backend=None):

        gtk.FileChooserDialog.__init__(self, title, parent,
                                       action, buttons)

        for f in (ResultsFileFilter(), AllFilesFileFilter()):
            self.add_filter(f)

class SaveResultsFileChooserDialog(gtk.FileChooserDialog):
    def __init__(self, title="", parent=None,
                 action=gtk.FILE_CHOOSER_ACTION_SAVE,
                 buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                          gtk.STOCK_SAVE, gtk.RESPONSE_OK), backend=None):

        gtk.FileChooserDialog.__init__(self, title, parent, action, buttons)

        for f in (ResultsFileFilter(), AllFilesFileFilter()):
            self.add_filter(f)

class FullDiffiesFileChooserDialog(gtk.FileChooserDialog):
    def __init__(self, title="", parent=None,
                 action=gtk.FILE_CHOOSER_ACTION_OPEN,
                 buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                          gtk.STOCK_OPEN, gtk.RESPONSE_OK), backend=None):

        gtk.FileChooserDialog.__init__(self, title, parent,
                                       action, buttons)

        for f in (RegularDiffiesFileFilter(), HtmlDiffiesFileFilter()):
            self.add_filter(f)

class SingleDiffiesFileChooserDialog(gtk.FileChooserDialog):
    def __init__(self, title="", parent=None,
                 action=gtk.FILE_CHOOSER_ACTION_OPEN,
                 buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                          gtk.STOCK_OPEN, gtk.RESPONSE_OK), backend=None):

        gtk.FileChooserDialog.__init__(self, title, parent,
                                       action, buttons)

        self.add_filter(RegularDiffiesFileFilter())

class DirectoryChooserDialog(gtk.FileChooserDialog):
    def __init__(self, title="", parent=None,
                 action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                 buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                          gtk.STOCK_OPEN, gtk.RESPONSE_OK), backend=None):

        gtk.FileChooserDialog.__init__(self, title, parent, action, buttons)
