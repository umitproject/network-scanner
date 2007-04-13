# Copyright (C) 2005 Insecure.Com LLC.
#
# Author: Adriano Monteiro Marques   <py.adriano@gmail.com>
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

import re

from umitCore.Paths import Path
from umitCore.UmitConfigParser import UmitConfigParser

from ConfigParser import NoSectionError

class NmapOutputHighlight(UmitConfigParser, object):
    setts = ["bold", "italic", "underline", "text", "highlight", "regex"]
    
    def __init__(self, *args):
        UmitConfigParser.__init__(self, *args)
        self.read(Path.config_file)

    def __get_it(self, p_name):
        property_name = "%s_highlight" % p_name

        try:
            return self.sanity_settings([self.get(property_name, prop, True) \
                                         for prop in self.setts])
        except:
            settings = []
            prop_settings = self.default_highlights[p_name]
            settings.append(prop_settings["bold"])
            settings.append(prop_settings["italic"])
            settings.append(prop_settings["underline"])
            settings.append(prop_settings["text"])
            settings.append(prop_settings["highlight"])
            settings.append(prop_settings["regex"])

            self.__set_it(p_name, settings)

            return settings

    def __set_it(self, property_name, settings):
        property_name = "%s_highlight" % property_name
        settings = self.sanity_settings(settings)

        [self.set(property_name, self.setts[pos], settings[pos]) \
         for pos in xrange(len(settings))]

    def sanity_settings(self, settings):
        """This method tries to convert insane settings to sanity ones ;-)
        If user send a True, "True" or "true" value, for example, it tries to
        convert then to the integer 1.
        Same to False, "False", etc.

        Sequence: [bold, italic, underline, text, highlight, regex]
        """
        
        settings[0] = self.boolean_sanity(settings[0])
        settings[1] = self.boolean_sanity(settings[1])
        settings[2] = self.boolean_sanity(settings[2])

        tuple_regex = "[\(\[]\s?(\d+)\s?,\s?(\d+)\s?,\s?(\d+)\s?[\)\]]"
        if type(settings[3]) == type(""):
            settings[3] = [int(t) for t in re.findall(tuple_regex, settings[3])[0]]

        if type(settings[4]) == type(""):
            settings[4]= [int(h) for h in re.findall(tuple_regex, settings[4])[0]]

        return settings

    def boolean_sanity(self, attr):
        if attr == True or attr == "True" or attr == "true" or attr == "1":
            return 1
        return 0

    def get_date(self):
        return self.__get_it("date")

    def set_date(self, settings):
        self.__set_it("date", settings)

    def get_hostname(self):
        return self.__get_it("hostname")

    def set_hostname(self, settings):
        self.__set_it("hostname", settings)

    def get_ip(self):
        return self.__get_it("ip")

    def set_ip(self, settings):
        self.__set_it("ip", settings)

    def get_port_list(self):
        return self.__get_it("port_list")

    def set_port_list(self, settings):
        self.__set_it("port_list", settings)

    def get_open_port(self):
        return self.__get_it("open_port")

    def set_open_port(self, settings):
        self.__set_it("open_port", settings)

    def get_closed_port(self):
        return self.__get_it("closed_port")

    def set_closed_port(self, settings):
        self.__set_it("closed_port", settings)

    def get_filtered_port(self):
        return self.__get_it("filtered_port")

    def set_filtered_port(self, settings):
        self.__set_it("filtered_port", settings)

    def get_details(self):
        return self.__get_it("details")

    def set_details(self, settings):
        self.__set_it("details", settings)

    def get_enable(self):
        enable = True
        try:
            enable = self.get("output_highlight", "enable_highlight")
        except NoSectionError:
            self.set("output_highlight", "enable_highlight", str(True))
        
        if enable == "False" or enable == "0" or enable == "":
            return False
        return True

    def set_enable(self, enable):
        if enable == False or enable == "0" or enable == None or enable == "":
            self.set("output_highlight", "enable_highlight", str(False))
        else:
            self.set("output_highlight", "enable_highlight", str(True))

    date = property(get_date, set_date)
    hostname = property(get_hostname, set_hostname)
    ip = property(get_ip, set_ip)
    port_list = property(get_port_list, set_port_list)
    open_port = property(get_open_port, set_open_port)
    closed_port = property(get_closed_port, set_closed_port)
    filtered_port = property(get_filtered_port, set_filtered_port)
    details = property(get_details, set_details)
    enable = property(get_enable, set_enable)

    # These settings are made when there is nothing set yet. They set the "factory" \
    # default to highlight colors
    default_highlights = {"date":{"bold":str(True),
                            "italic":str(False),
                            "underline":str(False),
                            "text":[0, 0, 0],
                            "highlight":[65535, 65535, 65535],
                            "regex":"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}\s.{1,4}"},
                          "hostname":{"bold":str(True),
                            "italic":str(True),
                            "underline":str(True),
                            "text":[0, 111, 65535],
                            "highlight":[65535, 65535, 65535],
                            "regex":"(\w{2,}://)*\w{2,}\.\w{2,}(\.\w{2,})*(/[\w{2,}]*)*"},
                          "ip":{"bold":str(True),
                            "italic":str(False),
                            "underline":str(False),
                            "text":[0, 0, 0],
                            "highlight":[65535, 65535, 65535],
                            "regex":"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"},
                          "port_list":{"bold":str(True),
                            "italic":str(False),
                            "underline":str(False),
                            "text":[0, 1272, 28362],
                            "highlight":[65535, 65535, 65535],
                            "regex":"PORT\s+STATE\s+SERVICE(\s+VERSION)?\s.*"},
                          "open_port":{"bold":str(True),
                            "italic":str(False),
                            "underline":str(False),
                            "text":[0, 41036, 2396],
                            "highlight":[65535, 65535, 65535],
                            "regex":"\d{1,5}/.{1,5}\sopen\s.*"},
                          "closed_port":{"bold":str(False),
                            "italic":str(False),
                            "underline":str(False),
                            "text":[65535, 0, 0],
                            "highlight":[65535, 65535, 65535],
                            "regex":"\d{1,5}/.{1,5}\sclosed\s.*"},
                          "filtered_port":{"bold":str(False),
                            "italic":str(False),
                            "underline":str(False),
                            "text":[38502, 39119, 0],
                            "highlight":[65535, 65535, 65535],
                            "regex":"\d{1,5}/.{1,5}\sfiltered\s.*"},
                          "details":{"bold":str(True),
                            "italic":str(False),
                            "underline":str(True),
                            "text":[0, 0, 0],
                            "highlight":[65535, 65535, 65535],
                            "regex":"^(\w{2,}[\s]{,3}){,4}:"}}


if __name__ == "__main__":
    """
    u = NmapOutputHighlight()
    u.date = (1, 0, 0, (0, 0, 0), (65535, 65535, 65535),
              "\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}\s.{1,4}")
    u.hostname = (1, 0, 1, (0, 0, 0), (65535, 65535, 65535), "(\w+[\.]?)+")
    u.ip = (1, 0, 0, (0, 0, 0), (65535, 65535, 65535),
            "[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}")
    u.port_list = (1, 0, 0, (0, 0, 0), (65535, 65535, 65535),
                   "PORT\s+STATE\s+SERVICE(\s+VERSION)?")
    u.open_port = (1, 0, 0, (0, 0, 0), (0, 65535, 0), "\d{1,5}/.{1,5}\sopen\s.*")
    u.closed_port = (1, 0, 0, (0, 0, 0), (65535, 0, 0), "\d{1,5}/.{1,5}\sclosed\s.*")
    u.filtered_port = (1, 0, 0, (0, 0, 0), (0, 65535, 65535), "\d{1,5}/.{1,5}\sfiltered\s.*")
    u.details = (1, 0, 0, (0, 0, 0), (65535, 65535, 65535), ".+:.+")
    u.enable = True

    print "Date", u.date
    print "Hostname", u.hostname
    print "Ip", u.ip
    print "Port list", u.port_list
    print "Open port", u.open_port
    print "Closed port", u.closed_port
    print "Filtered port", u.filtered_port
    print "Details", u.details
    """
    
