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
"""The Bundled WebServer of UMIT
"""

import os
import sys
import logging
import BaseHTTPServer
import tempfile
import random
import csv
from threading import Thread
from CGIHTTPServer import CGIHTTPRequestHandler
from ConfigParser import ConfigParser, ParsingError, NoOptionError
from Cookie import SmartCookie
from md5 import md5

__revision__ = "299"

__all__ = ["HTTPServer", "UmitRequestHandler"]

logger = logging.getLogger(__name__)


class UmitRequestHandler(CGIHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.session_control_file = os.path.join("/", "tmp", "session.control")
        os.environ['umit_session'] = self.session_control_file
        CGIHTTPRequestHandler.__init__(self, request, client_address, server)


class HTTPServer:
    """The Bundle WebServer of UMIT
    """

    port = 8000
    address = ''
    config_file = "umit.conf"
    temp_dir = "tmp"
    pid_file = "umit.pid"
    document_root = os.path.join(os.path.dirname(__file__),"www")

    def __init__(self):
        """Constructor
        """
        #while Paths is not running
        self.parser = ConfigParser()
        try:
            self.parser.read(self.config_file)
        except ParsingError, err:
            print 'ERROR: %s.\nAborting...'% str(err)
            sys.exit(1)

        if self.parser.has_section('web'):

            if self.parser.has_option('web','port'):
                self.port = self.parser.getint('web','port')

            if self.parser.has_option('web','address'):
                self.address = self.parser.get('web', 'address')

            self.pid_file = os.path.join(os.path.dirname(__file__), \
                                            self.temp_dir, self.pid_file)

        else:
            logger.debug('Config File have *not* a web section')
            raise ParsingError, "No section named: 'web'"

    def run(self):
        """Start the server
        """

        try:
            os.chdir(self.document_root)
        except OSError,err:
            print 'ERROR: %s.\nAborting...'% str(err)
            sys.exit(1)

        server_address = (self.address, self.port)
        httpd = BaseHTTPServer.HTTPServer(server_address, \
                                                UmitRequestHandler)
        httpd.serve_forever()

    def start(self):
        """Start the thread
        """

        pid = os.getpid()
        if os.path.isfile(self.pid_file):
            pid = open(self.pid_file, "r").read()
            raise StandardError, "Server already running (pid %s)"% str(pid)
        else:
            pid_file = open(self.pid_file, "w")
            pid = os.fork()
            if pid > 0:
                pid_file.write(str(pid))
                print "UmitWeb listening on host %s port %d" % (self.address,
                                                                self.port)
                sys.exit(0)
            self.run()

    def shutdown(self):
        """Shut down the server
        """
        session_control_file = os.path.join(os.path.sep, "tmp",
                                            "session.control")
        if not os.path.isfile(self.pid_file):
            raise IOError, "%s: No such file (are umitWeb running?)"% \
                                                            self.pid_file

        reader = csv.reader(open(session_control_file,"r"))
        for row in reader:
            os.unlink(row[1])
        #truncates the session.control file
        open(session_control_file, "w")

        pid_file = open(self.pid_file, "r")
        try:
            os.kill(int(pid_file.read()), 9)
        except OSError:
            pass
        pid_file.close()
        os.remove(self.pid_file)
