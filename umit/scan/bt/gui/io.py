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

import os
import string
import sys

import pygtk
pygtk.require('2.0')
import gtk

from higwidgets.higdialogs import HIGAlertDialog

import umit.scan.bt.gui.btcore
import umit.scan.bt.core.ubt_parser


class io:

    def __init__(self):
        self.count = 0

    def save(self):
        print "save ubt"
        count = self.count
        save_file = self.file_browse(gtk.FILE_CHOOSER_ACTION_SAVE)
        if (save_file == None):
            print "error creating file to save"
        save_file, extension = os.path.splitext(save_file)
        save_file = save_file + ".ubt"
        string = ""
        doc = ubt_parser.XMLDocument("UmitBT", version="2.0")
        while (len(btcore.btname)-1) > count:
            count += 1
            table = doc.add("table", name="device"+str(count))
            table.add("device"+str(count), name="BTname", value=btcore.btname[count])            
            table.add("device"+str(count), name="BTmac", value=btcore.btmac[count])            
            table.add("device"+str(count), name="BTmanu", value=btcore.btmanu[count])
            print "LEN : " + str(len(btcore.btsdp))
            if len(btcore.btsdp[count]) > 2:
                for svc in btcore.btsdp[count]:
                    table.add("device"+str(count), name="BTsdpname", value=str(svc["name"]))
                    table.add("device"+str(count), name="BTsdpdesc", value=str(svc["description"]))
                    table.add("device"+str(count), name="BTsdpprov", value=str(svc["provider"]))
                    table.add("device"+str(count), name="BTsdpproto", value=str(svc["protocol"]))
                    table.add("device"+str(count), name="BTsdppsm", value=str(svc["port"]))
                    table.add("device"+str(count), name="BTsdpclass", value=str(svc["service-classes"]))
                    table.add("device"+str(count), name="BTsdpprof", value=str(svc["profiles"]))
                    table.add("device"+str(count), name="BTsdpservid", value=str(svc["service-id"]))
            else:
                table.add("device"+str(count), name="BTsdpname", value="no services found")
        string = doc
        outfile = open (save_file, "w")
        outfile.write(string.doc.toprettyxml(" "))
        outfile.close()
        print "UBT file saved"

    def load(self, filename):    
        try:
            load_file = filename#self.file_browse(gtk.FILE_CHOOSER_ACTION_OPEN)#TODO give load file from during function al
            inFile = open(load_file, "rb")
            buffer, extension = os.path.splitext(load_file)
        except:            
            dlg = HIGAlertDialog(None, message_format=('I/O Error'), secondary_text=("Cant open UmitBT file"))
            dlg.run()
            dlg.destroy()
            print sys.exc_info()[0]            
            return sys.exc_info()[0]
        print "clear memory then load ubt file"
        self.clear_buffer()         
        count = self.count
        print "OPEN FILENAME : " + load_file
        if(load_file and extension == ".ubt"):
            xml_load = inFile.read()
            ndoc = ubt_parser.XMLDocument()
            ndoc.parseString(str(xml_load))
            root = ndoc.getAll("UmitBT")
            if root:
                db = root[0]
                print "Database:", db["ubt"]
                for table in db.getAll("table"):
                    print "Table:", table["name"]
                    count+=1
                    svc = {}
                    for field in db.getAll("device"+str(count)):
                        print "Field:", field["name"], "- Type:", field["value"]
                        if(field["value"]==""):
                            field["value"]=="-"
                        if(field["name"] == "BTname"):
                            btcore.btname.append(field["value"])
                        elif(field["name"] == "BTmac"):
                            btcore.btmac.append(field["value"])
                        elif(field["name"] == "BTmanu"):
                            btcore.btmanu.append(field["value"])
                        elif(field["name"] == "BTsdpname"):
                            svc["name"] = str(field["value"])
                        elif(field["name"] == "BTsdpdesc"):
                            svc["description"] = str(field["value"])
                        elif(field["name"] == "BTsdpprov"):
                            svc["provider"] = str(field["value"])
                        elif(field["name"] == "BTsdpproto"):
                            svc["protocol"] = str(field["value"])
                        elif(field["name"] == "BTsdppsm"):
                            svc["port"] = str(field["value"])
                        elif(field["name"] == "BTsdpclass"):
                            svc["service-classes"] = str(field["value"])
                        elif(field["name"] == "BTsdpprof"):
                            svc["profiles"] = str(field["value"])
                        elif(field["name"] == "BTsdpservid"):
                            svc["service-id"] = str(field["value"])
                        else:
                            print "I/O error encountered!"
                    btcore.btsdp.append(svc)                        
        else:
            print "File Load error!"
            dlg = HIGAlertDialog(None, message_format=('I/O Error'), secondary_text=("The file isn't a valid UmitBT file"))
            dlg.run()
            dlg.destroy()
        print "UBT file loaded"

    def clear_buffer(self):
        btcore.btname = [""]
        btcore.btmac = [""]
        btcore.btmanu = [""]
        btcore.btsdp = [""]

