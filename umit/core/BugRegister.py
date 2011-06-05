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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import re
import urllib
import urllib2
from tempfile import mktemp

from umit.core.Version import VERSION

trac_site="http://trac.umitproject.org/"
trac_new_ticket=trac_site + "newticket"
trac_submit=trac_new_ticket


class BugRegister(object):
    def __init__(self):
        self.summary = ""
        self.details = ""
        self.input_file = ""
        self.file_description = ""
        self.submit = "submit"
        self.cc = ""
        self.reporter = "user"
        self.keywords = "user crash"
        self.milestone = "Umit %s" % VERSION
        self.version = "current svn"
        self.assigned_to = "boltrix"
        self.component = "Documentation"
        self.type = "defect"

    # Function to get the cookie of headers
    def __get_cookie(self, header, name):
        """
        Receive header and the name intended to find
        Returns the value or None if not found
        """
        try:
            pattern = r".*%s=([^;]+)[;]{0,1}.*" % name 
            return re.findall(pattern, header['Set-cookie'])[0]
        except Exception, ex:
            return None



    def report(self):
        f = urllib2.urlopen(trac_new_ticket)

        # Get cookie trac_session
        trac_session = self.__get_cookie(f.headers, "trac_session")
        # Get value of __FORM_TOKEN
        trac_form = self.__get_cookie(f.headers, "trac_form_token")
        if (trac_form is None or trac_session is None):
            return None

        query = {
                "field_summary": self.summary,
                "__FORM_TOKEN": trac_form,
                "field_type": self.type,
                "field_description": self.details,
                "field_milestone": self.milestone,
                #"field_component":self.component,
                "field_version": self.version,
                "field_keywords": self.keywords,
                #"owner":self.assigned_to,
                "cc": self.cc,
                "author": self.reporter,
                #"attachment":self.input_file,
                "field_status": "new",
                "action": "create",
                "submit": self.submit
                }
        if self.component:
            query['field_component'] = self.component
        data = urllib.urlencode(query)

        request = urllib2.Request(trac_new_ticket, data)
        request.add_header("Cookie", "trac_session=%s; \
                           trac_form_token=%s" % (trac_session, trac_form))

        response = urllib2.urlopen(request)
        return response.geturl()

if __name__ == "__main__":
    bug = BugRegister()
    bug.report()
