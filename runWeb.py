#!/usr/bin/env python
import sys
from umitWeb.WebServer import HTTPServer

httpd = HTTPServer()
if len(sys.argv) != 2:
    print "Usage: %s {start|stop}"% sys.argv[0]
else:
    if sys.argv[1] == "start":
        httpd.start()
    elif sys.argv[1] == "stop":
        httpd.shutdown()
    else:
        print "Usage: %s {start|stop}"% sys.argv[0]