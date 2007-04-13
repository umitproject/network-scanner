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
"""CGIs
"""

import os
import sys
import cgi
import csv
import types
import tempfile
import random
import pickle
import Cookie
from md5 import md5
from ConfigParser import ConfigParser, ParsingError, NoOptionError
from umitCore import NmapCommand
from umitWeb.HtmlBuilder import LinkTag, HtmlTag, HeadTag, BodyTag

__revision__ = "299"
__all__ = ["Request", "BasicCGI"]


class SessionWrapper:
    def __init__(self):
        self.control_file = os.environ['umit_session']
        self.session = {}
        sess_file = self.open_control_file()

        self.csv_reader = csv.reader(sess_file)
        data = [_data for _data in self.csv_reader]
        sessid = ""
        cookies = Cookie.SimpleCookie(os.environ['HTTP_COOKIE'])
        sessid = cookies.get('UMITSESSID', '')
        session_exists = False
        if sessid:
            sessid = sessid.value
            for e_data in data:
                if sessid == e_data[0]:
                    session_exists = True
                    self.session_file = e_data[1]
                    break

        if not session_exists:
            s_file = tempfile.mkstemp()
            self.session_file = s_file[1]
            sessid = md5(os.environ['REMOTE_ADDR']+ \
                      os.environ['HTTP_USER_AGENT']).hexdigest()
            sessid += str(int(random.random()*1e+7))
            cookies['UMITSESSID'] = sessid
            cookie_array = {}
            os.environ['HTTP_COOKIE'] = ";".\
                                join(["%s=%s" % (c.key, c.value) \
                                        for c in cookies.values()])
            self.csv_writer = csv.writer(self.open_control_file("a"))
            self.csv_writer.writerow([sessid, self.session_file])

    def open_control_file(self, mode="r"):
        try:
            sess_file = open(self.control_file, mode)
        except IOError:
            sess_file = open(self.control_file, "w")
        return sess_file

    def __getattribute__(self, name):
        return self.get_dict().__getattribute__(name)

    def __getitem__(self, name):
        reader = csv.reader(open(self.session_file, "r"))
        print name
        for row in reader:
            if row[0] == name:
                return pickle.loads(row[1])
        raise KeyError

    def __setitem__(self, key, value):
        key_exists = False
        data = [_data for _data in csv.reader(open(self.session_file, "r"))]
        for index, element in enumerate(data):
            if element[0] == key:
                data[index][1] = pickle.dumps(value)
                exists = True
                break

        if not key_exists:
            data.append([key, pickle.dumps(value)])

        writer = csv.writer(open(self.session_file, "w"))
        writer.writerows(data)

    def __iter__(self):
        return self.get_dict().__iter__()

    def __str__(self):
        return self.get_dict().__str__()

    def __repr__(self):
        return self.get_dict().__repr__()

    def get(self, key, default_value=None):
        try:
            return self[key]
        except KeyError:
            return default_value

    def get_dict(self):
        ret_value = {}
        for row in csv.reader(open(self.session_file, "r")):
            ret_value[row[0]] = pickle.loads(row[1])
        return ret_value


class Request:
    """Basic HTTP request definition
    """

    def __init__(self, field_storage, cookies, session, server_info):
        """Constructor
        """

        self.parameters = field_storage
        self.cookies = cookies
        self.server = server_info
        self.session = session

    def get_parameter(self, parameter):
        """Retrieve a parameter (GET) or a form field (POST)
        """

        if self.parameters.has_key(parameter):
            return self.parameters[parameter].value
        else:
            return ""

    def set_cookie(self, name, value):
        """set a cookie
        """

        self.cookies[name] = value

    def get_cookie(self, name):
        """get acookie
        """

        if self.cookies.has_key(name):
            return self.cookies[name]
        else:
            return None


class BasicCGI:
    """This is the basic class for all CGIs processed by umitWeb.
    It separate the 'get' and 'post' method, to be handled by separate
    methods.
    """

    def __init__(self):
        """Constructor
        """

        self.headers = ""
        self.body = ""
        self.headers_sent = False
        self.body_sent = False

    def process_request(self):
        """Find the best way to handle the request.
        """
        session = SessionWrapper()
        cookie = Cookie.SimpleCookie(os.environ['HTTP_COOKIE'])
        request = Request(cgi.FieldStorage(), cookie, session, os.environ)
        if os.environ['REQUEST_METHOD'].lower() == "get":
            self.do_get(request)
        else:
            self.do_post(request)
        if not self.body_sent:
            self.send(request)

    def do_get(self, request):
        """process requests made by GET method
        """

        pass

    def do_post(self, request):
        """process requests made by POST method
        """

        pass

    def add_header(self, header):
        """Add a header to HTTP headers
        """
        if type(header) in types.StringTypes:
            self.headers += header
        else:
            self.headers += repr(header)

    def add_cookie(self, cookie):
        """Set a cookie value
        """

        self.add_header(cookie)

    def set_content_type(self, content_type):
        """Sets the content type
        """

        header = "Content-type: %s\n" % content_type
        self.add_header(header)

    def end_headers(self,request=None):
        """Finalize and print HTTP headers
        """
        if request is not None:
            print request.cookies
        print self.headers, "\n\n"
        self.headers_sent = True

    def write(self, text):
        """Write content into page
        """
        if type(text) not in types.StringTypes:
            text = repr(text)
        self.body += text

    def send(self,request=None):
        """Send the body (and header, if not sent) to the client
        """
        if not self.headers_sent:
            self.end_headers(request)

        print self.body
        self.body_sent = True

    def write_error(self, message):
        self.set_content_type("text/html")
        self.write("<html><head><link rel='stylesheet' " + \
                    "href='/css/style.css'/></head>")
        self.write("<body><center><img src='/images/umit_project.png'/>")
        self.write("<H2>ERROR</H2>")
        self.write("<h3>%s</h3>" % message)
        self.write("<a href='javascript:history.go(-1)'>back</a>")
        self.write("</center></body></html>")
        self.send()