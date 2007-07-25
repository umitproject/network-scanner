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

import urllib
import urllib2

from tempfile import mktemp

group_id = "142490"
atid = "752647"

sf_site = "http://www.sourceforge.net/"
sf_project_site = sf_site + "projects/umit/"
sf_bug_tracker_page = sf_site + "tracker/?group_id=%s&atid=%s" % (group_id, atid)
sf_bug_tracker_submit = sf_site + "tracker/index.php"


class BugRegister(object):
    def __init__(self):
        try:
            urllib.urlopen(sf_site)
        except:
            return None

        self.group_id = group_id
        self.atid = atid
        self.func = "postadd"
        self.is_private = "1"
        self.category_id = "862568"
        self.artifact_group_id = "100" # None
        self.assigned_to = "855755" # boltrix
        self.priority = "5"
        self.summary = "Testing umit bug reporter"
        self.details = "Just testing the umit dialog to report bugs directly from the interface!\
 py.adriano@gmail.com"
        self.input_file = ""
        self.file_description = ""
        self.submit = "SUBMIT"

    def report(self):
        data = urllib.urlencode({"group_id":self.group_id,
                                 "atid":self.atid,
                                 "func":self.func,
                                 "is_private":self.is_private,
                                 "category_id":self.category_id,
                                 "artifact_group_id":self.artifact_group_id,
                                 "assigned_to":self.assigned_to,
                                 "priority":self.priority,
                                 "summary":self.summary,
                                 "details":self.details,
                                 "input_file":self.input_file,
                                 "file_description":self.file_description,
                                 "submit":self.submit})

        # The submit page source code points that the info should be set using POST method
        # But, it only worked sending it through GET method. So, I decided to send using
        # both methods, to insure that it's going to work.
        request = urllib2.Request(sf_bug_tracker_submit + "?" + data, data)
        response = urllib2.urlopen(request)

        tfile = mktemp()
        open(tfile, "w").write(response.read())
        return tfile

if __name__ == "__main__":
    bug = BugRegister()
    bug.report()
