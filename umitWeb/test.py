#!/usr/bin/env python
# Copyright (C) 2005 Insecure.Com LLC.
#
# Author: Rodolfo da Silva Carvalho <rodolfo.ueg@gmail.com>
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
"""Responsible by tests of umitWeb package
"""

import os
import unittest
from umitWeb.CGI import Request
from cgi import FieldStorage
from Cookie import SimpleCookie
from umitWeb.HtmlBuilder import HtmlTag, BaseTag


__revision__ = "299"


class TestBaseTag(unittest.TestCase):
    """Class to test html tags generation
    """

    def setUp(self):
        """Sets up class to run the tests
        """
        self.baseTag = BaseTag(id="test1", style="font-family:sans-serif")
        self.baseTag.name = "tag"

    def testProperties(self):
        """test the properties of a tag
        """
        self.assertEqual(self.baseTag.properties, dict(id="test1", \
                                           style="font-family:sans-serif"))
        self.assertEqual(repr(self.baseTag), "<tag style='font-family:sans"+ \
                                            "-serif' id='test1' />")

    def testChilds(self):
        """test method related with childs
        """
        html = HtmlTag()
        html.add_child("some text")
        self.baseTag.add_child(html)
        self.assertEqual(self.baseTag.childs, [html])
        self.assertEqual(self.baseTag.get_child("some text"), html)
        self.assertEqual(self.baseTag.remove_child(html), True)
        self.assertEqual(self.baseTag.childs, [])

    def testSetProperties(self):
        """test methods related with properties
        """
        self.assertEqual(self.baseTag.get_property("id"), "test1")
        self.baseTag.set_property("class", "tag")
        self.assertEqual(self.baseTag.get_property("class"), "tag")

    def testTagBuild(self):
        """test the tag building
        """
        self.assertTrue(self.baseTag.build_tag().endswith("/>"))
        self.baseTag.long_tag = True
        self.assertTrue(self.baseTag.build_tag().endswith("</tag>"))


class TestRequest(unittest.TestCase):
    """Tests the Request object
    """

    def setUp(self):
        """Sets up class to run the tests
        """
        self.fields = FieldStorage()
        self.cookies = SimpleCookie()
        self.server_info = os.environ
        self.req = Request(self.fields, self.cookies, self.server_info)

    def testAttributes(self):
        """test the attributes of the request
        """
        self.assertEqual(self.req.parameters, self.fields)
        self.assertEqual(self.req.cookies, self.cookies)
        self.assertEqual(self.req.server, self.server_info)


if __name__ == "__main__":
    suite = unittest.TestSuite()