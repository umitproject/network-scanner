#!/usr/bin/env python
# Copyright (C) 2008 Adriano Monteiro Marques.
#
# Author: Devtar Singh <devtar@gmail.com>
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

from xml.dom import minidom
from xml.dom.minidom import Document, parse, parseString
from types import StringType, UnicodeType
import string

enc = "utf-8"

def _encode(v):
    if isinstance(v, UnicodeType):
        v = v.encode(enc)
    return v

class XMLElement:

    def __init__(self, doc, el):
        self.doc = doc
        self.el = el

    def __getitem__(self, name):
        a = self.el.getAttributeNode(name)
        if a:
            return _encode(a.value)
        return None

    def __setitem__(self, name, value):
        self.el.setAttribute(name, _encode(value))

    def __delitem__(self, name):
        self.el.removeAttribute(name)

    def __str__(self):
        return _encode(self.doc.toprettyxml())

    def toString(self):
        return _encode(self.doc.toxml())

    def _inst(self, el):
        return XMLElement(self.doc, el)

    def get(self, name, default=None):
        a = self.el.getAttributeNode(name)
        if a:
            return _encode(a.value)
        return _encode(default)

    def add(self, tag, **kwargs):
        el = self.doc.createElement(tag)
        for k, v in kwargs.items():
            el.setAttribute(k, _encode(str(v)))
        return self._inst(self.el.appendChild(el))

    def addText(self, data):
        return self._inst(
            self.el.appendChild(
                self.doc.createTextNode(_encode(data))))

    def addComment(self, data):
        return self._inst(
            self.el.appendChild(
                self.doc.createComment(data)))

    def getText(self, sep=" "):
        rc = []
        for node in self.el.childNodes:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return _encode(string.join(rc, sep))

    def getAll(self, tag):
        return map(self._inst, self.el.getElementsByTagName(tag))

class _Document(Document):

    def writexml(self, writer, indent="", addindent="", newl=""):
        for node in self.childNodes:
            node.writexml(writer, indent, addindent, newl, _encode)


class XMLDocument(XMLElement):

    def __init__(self, tag=None, **kwargs):
        self.doc  = Document()
        XMLElement.__init__(self, self.doc, self.doc)
        if tag:
            self.el = self.add(tag, **kwargs).el

    def parse(self, d):
        self.doc = self.el = parse(d)
        return self

    def parseString(self, d):
        self.doc = self.el = parseString(_encode(d))
        return self
ubt_Parser = XMLDocument
