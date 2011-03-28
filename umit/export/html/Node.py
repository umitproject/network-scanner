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
margin-left:auto; margin-right:auto;
text-align:center;
font:12px Arial, Helvetica, sans-serif;
background-color:#FFCC66;
color: #000000;
}

h1
{
font:14px Arial, Helvetica, sans-serif;
}


h2
{
font-style:oblique;
font-weight:bold;
font:13px Arial, Helvetica, sans-serif;
}


tr
{
/*
border-style: hidden;*/
font:11px Arial, Helvetica, sans-serif;
}
td
{
/*
border-color: black;
border-style: solid;*/
font:11px Arial, Helvetica, sans-serif;
}


pre
{
background-color: #FFFFCC;
margin-left: auto;
margin-right: auto;
}

table
{ 

font-family: sans;
font-size: 9pt;

background-color: #FFFFCC;
border-style: hidden;
margin-left: auto;
margin-right: auto;
border-color: green;
border: 0.5px solid black;
border-collapse: collapse;
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
    