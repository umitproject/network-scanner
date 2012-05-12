# Copyright (C) 2008 Adriano Monteiro Marques.
#
# Author: Luis A. Bastiao Silva <luis.kop@gmail.com>
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


HEADER = "<html>"
HEADER_C = "<html>"
TITLE = "<title>"
TITLE_C = "</title>"
BL = "<br />"

STYLE = """

body {
  margin: 0;
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 13px;
  line-height: 18px;
  color: #333333;
  background-color: #ffffff;
}

.container {
  width: 940px;
  margin-right: auto;
  margin-left: auto;
  *zoom: 1;
}

.row-fluid {
  width: 100%;
  *zoom: 1;
}

.hero-unit {
  padding: 20px;
  margin-bottom: 10px;
  margin-bottom: 20px;
  background-color: #eeeeee;
  -webkit-border-radius: 6px;
     -moz-border-radius: 6px;
          border-radius: 4px;
}

.well {
  min-height: 20px;
  padding: 19px;
  margin-bottom: 20px;
  background-color: #f5f5f5;
  border: 1px solid #eee;
  border: 1px solid rgba(0, 0, 0, 0.05);
  -webkit-border-radius: 4px;
     -moz-border-radius: 4px;
          border-radius: 4px;
  -webkit-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.05);
     -moz-box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.05);
          box-shadow: inset 0 1px 1px rgba(0, 0, 0, 0.05);
}

h2,
h3,
h4 {
  margin: 0;
  font-family: inherit;
  font-weight: bold;
  text-rendering: optimizelegibility;
}

h2.umit-title {
  margin-left: 150px;
  font-size: 25px;
  line-height: 1;
  letter-spacing: -1px;
  color:#A30517;
}

h3 {
  font-size: 18px;
  line-height: 27px;
}

h3.nmap-command {
  color : #A30517;
  text-decoration : underline;
}

h3.umit-result-title {
  color:#0088cc;
}

h4 {
  font-size: 14px;
  line-height: 18px;
}

.umit-ip {
    color:#A30517;
}


table {
  max-width: 100%;
  background-color: transparent;
  border-collapse: collapse;
  border-spacing: 0;
}

.table {
  width: 100%;
  margin-bottom: 18px;
}

.table th,
.table td {
  padding: 8px;
  line-height: 18px;
  text-align: left;
  vertical-align: top;
  border-top: 1px solid #dddddd;
}

.table th {
  font-weight: bold;
}

.table thead th {
  vertical-align: bottom;
}

.table tbody + tbody {
  border-top: 2px solid #dddddd;
}

hr {
  margin: 18px 0;
  border: 0;
  border-top: 1px solid #eeeeee;
  border-bottom: 1px solid #ffffff;
}

strong {
  font-weight: bold;
}

.span12 {
  width: 940px;
}

"""


"""
Tree of HTML tags
<html>
  childs
    ...
       ...
       ...
       ...
</html>

"""


class Node(object):
    def __init__(self, tag_name, attr=None, text = "" ):
        """
        @param tag_name name of tag (could be None)
        @param attr is a list that contains dicts   [{name and value}, ...]
        """
        
        self.tag = tag_name
        self.attr = attr
        self.childs = []
        self.text = text

    def add_child(self, node):
        """
        Add Childs
        """
        assert node != None 
        self.childs.append(node)

    def get_childs(self):
        return self.childs
    
    def get_html(self):
        """
        -- recursive code 
        returns a html string 
        """
        if self.tag == None :
            return self.text

        str = self.tag 
        
        # Fill Attributes of tag
        if self.attr!=None:
            for attr in self.attr:
                str = str + " "
                str = str + attr['name'] + "=\"" + attr['value']+"\""
            
        ch = ""
        for child in self.childs:
            s = child.get_html()
            if s != []:
                ch = ch + "\n" + s

        open = "<%s>" % str 
        close = "</%s>" % self.tag
        if self.text == "":
            result = open + ch + "\n" + close
        else:
            result = open + ch + self.text + "\n" + close
        return result
    
