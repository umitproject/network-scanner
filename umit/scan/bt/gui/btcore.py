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

import platform
import os
import sys

import pygtk
pygtk.require('2.0')
import gtk

if(platform.system()=="Darwin"):
   try:
      import lightblue
   except ImportError:
      print >> sys.stderr, "Error loading LightBlue dependency.Exiting UmitBT..."
      raise
else:
   try:
      import bluetooth
   except ImportError:
      print >> sys.stderr, "Error loading PyBluez dependency. Exiting UmitBT..."
      raise

#from umitCore.I18N import _
from higwidgets.higdialogs import HIGDialog, HIGAlertDialog

import umit.scan.bt.gui.io
import umit.scan.bt.core.path

# globals used due to functions such as set_info and ease of access in io.py. needs redesigning
btname = [""]
btmac = [""]
btmanu = [""]
btmanumac = [""]
btmanuname = [""]
btsdp = [""]
sdpstatus = ""

class btcore:

   def __init__(self):
      global btname
      global btmac
      global btmanu
      global btmanumac
      global btmanuname
      global btsdp
      global sdpstatus

   def scan(self, ScanNotebookPageBT):
      print "Refresh ScanNotebookPageBT and Clear Cache"
      self.clear(ScanNotebookPageBT)
      global btname
      global btmac
      global btsdp
      global sdpstatus
      count = 1
      # Use Lightblue backend on OSX
      if(platform.system()=="Darwin"):
         try:
            btdevices = lightblue.finddevices(getnames=True, length=10)
            for btfield in btdevices:
               if(btfield[1] == ""):
                  btfield[1] = "N/A"
            #encode btname to utf-8
            try:
               btfield[1].encode("utf-8")
            except:
               btfiled[1] = "N/A"
            btname.append(btfield[1])
            btmac.append(btfield[0])
            if (sdpstatus == "Enabled" and (len(btname) > 1)):        
               self.sdp_scan(count)
            else:                        
               btsdp.append({"name":"SDP Disabled"})
            count+=1
         except:
            dlg = HIGAlertDialog(type=gtk.MESSAGE_ERROR, 
                                 message_format=('Scan Process'), 
                                 secondary_text=("One or more Bluetooth devices could not be found"))
            dlg.run()
            dlg.destroy()
            return
      # Use PyBluez on Win32 or Linux
      else:
         try:
            btdevices = bluetooth.discover_devices(flush_cache = True, lookup_names = True)
            # first entry of btdevice is at index 1
            for addr, name in btdevices:		     
               if (name == ""):
                  name = "N/A"
               #encode btname to utf-8
               try:
                  name.encode("utf-8")
               except:
                  name = "N/A"
               btname.append(name)
               btmac.append(addr)                   
               if (sdpstatus == "Enabled" and (len(btname) > 1)):        
                  self.sdp_scan(count)
               else:                        
                  btsdp.append({"name":"SDP Disabled"})
               count+=1
         except:
            dlg = HIGAlertDialog(type=gtk.MESSAGE_ERROR, 
                                 message_format=('Scan Process'), 
                                 secondary_text=("One or more Bluetooth devices could not be found"))
            dlg.run()
            dlg.destroy()
            return                  

      ScanNotebookPageBT.progb.set_text("40%")
      ScanNotebookPageBT.progb.set_fraction(.4)
      self.manufac()
      ScanNotebookPageBT.progb.set_text("75%")
      ScanNotebookPageBT.progb.set_fraction(.75)
      self.map(ScanNotebookPageBT)
      ScanNotebookPageBT.progb.set_text("100%")
      ScanNotebookPageBT.progb.set_fraction(1)
      message_id = ScanNotebookPageBT.status_bar.push(ScanNotebookPageBT.context_id, "Scanning Completed")

   def sdp_scan(self, btid):
      global btmac
      global btsdp
      print "BTID: " + str(btid) + "\n" + btmac[btid]
      if(platform.system()=="Darwin"):
         # Lightblue Output: [('00:0D:93:19:C8:68', 10, 'OBEX Object Push')]. Yet to be tested.
         sdpservices = lightblue.findservices(address=btmac[btid])
      else:	
         sdpservices = bluetooth.find_service(address=btmac[btid])
         btsdp.append(sdpservices)	 

   def load_db(self):
      global btmanumac
      global btmanuname
      count = 0
      if(os.path.exists(os.path.join(path.paths, "UmitBT", "config", "db", "btdb.db"))):
         print "load database"
         btdb_dir = os.path.abspath(os.path.join(path.paths, "UmitBT", "config", "db", "btdb.db"))
         btdb = open(btdb_dir, "rb")
         for line in btdb:
            count+=1
            btbuf1, btbuf2 = line.split(";")
            btmanumac.append(btbuf1)
            btmanuname.append(btbuf2)			 
         btdb.close()
      else:			
         print "ERROR: Can't open btdb!"
         dlg = HIGAlertDialog(None, message_format=('I/O Error'), secondary_text=("Cant open btdb.db"))
         dlg.run()
         dlg.destroy()

   def manufac(self):
      global btname
      global btmac
      global btmanu
      global btmacsearch
      global btnamesearch
      print "manufacturer detection"
      print btmac[1]
      count = 1
      # Load btdb
      self.load_db()
      print "Len : " + str(len(btname))
      while ((len(btname)) > count):
         print "Count"+str(count)
         if(btmanumac.count(btmac[count][:8]) > 0):
            manuindex = btmanumac.index(btmac[count][:8])
            btmanuname[manuindex] = btmanuname[manuindex].replace("\n", "")
            btmanu.append(btmanuname[manuindex])
         else:
            print "Null: " + btmac[count][:8]
            btmanu.append("null")
         count+= 1

   def map(self, ScanNotebookPageBT):    
      global btname
      global btmac
      global btmanu
      count = 1
      while ((len(btname)) > count):         
         if(btmanu[count].find("Apple") > -1 and btmanu[count].find("Applera") == -1):
            pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join("share", "pixmaps", "umit", "apple.png"))
            ScanNotebookPageBT.mapmodel.append([btname[count], pixbuf])
         elif(btmanu[count].find("Google") > -1 ):
            pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join("share", "pixmaps", "umit", "google.png"))
            ScanNotebookPageBT.mapmodel.append([btname[count], pixbuf])	  
         elif(btmanu[count].find("Nokia") > -1 ):
            pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join("share", "pixmaps", "umit", "nokia.png"))
            ScanNotebookPageBT.mapmodel.append([btname[count], pixbuf])
         elif(btmanu[count].find("Microsoft") > -1 or btmanu[count].find("MICROSOFT") > -1):
            pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join("share", "pixmaps", "umit", "microsoft.png"))
            ScanNotebookPageBT.mapmodel.append([btname[count], pixbuf])	  
         elif(btmanu[count].find("Motorola") > -1):
            pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join("share", "pixmaps", "umit", "moto.png"))
            ScanNotebookPageBT.mapmodel.append([btname[count], pixbuf])
         elif(btmanu[count].find("INTEL CORPORATION") > -1):
            pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join("share", "pixmaps", "umit", "intel.png"))
            ScanNotebookPageBT.mapmodel.append([btname[count], pixbuf])	  
         elif(btmanu[count].find("Cisco") > -1 ):
            pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join("share", "pixmaps", "umit", "cisco.png"))
            ScanNotebookPageBT.mapmodel.append([btname[count], pixbuf])
         elif(btmanu[count].find("LG Electronics") > -1 ):
            pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join("share", "pixmaps", "umit", "lg.png"))
            ScanNotebookPageBT.mapmodel.append([btname[count], pixbuf])		  
         elif(btmanu[count].find("Dell") > -1 ):
            pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join("share", "pixmaps", "umit", "dell.png"))
            ScanNotebookPageBT.mapmodel.append([btname[count], pixbuf])	  
         elif(btmanu[count].find("D-Link") > -1 ):
            pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join("share", "pixmaps", "umit", "dlink.png"))
            ScanNotebookPageBT.mapmodel.append([btname[count], pixbuf])
         elif(btmanu[count].find("DoCoMo") > -1 ):
            pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join("share", "pixmaps", "umit", "docomo.png"))
            ScanNotebookPageBT.mapmodel.append([btname[count], pixbuf])
         elif(btmanu[count].find("Samsung") > -1):
            pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join("share", "pixmaps", "umit", "samsung.png"))
            ScanNotebookPageBT.mapmodel.append([btname[count], pixbuf])	  
         #Filter Sony Erricson, Sony Computer Entertainment, then Sony Microsoft
         elif(btmanu[count].find("Sony Ericsson") > -1):
            pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join("share", "pixmaps", "umit", "sony-eric.png"))
            ScanNotebookPageBT.mapmodel.append([btname[count], pixbuf])
         elif(btmanu[count].find("Sony Computer Entertainment") > -1):
            pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join("share", "pixmaps", "umit", "sony-play.png"))
            ScanNotebookPageBT.mapmodel.append([btname[count], pixbuf])	  
         elif(btmanu[count].find("Sony") > -1):
            pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join("share", "pixmaps", "umit", "sony.png"))
            ScanNotebookPageBT.mapmodel.append([btname[count], pixbuf])
         elif(btmanu[count].find("Blaupunkt") > -1 ):
            pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join("share", "pixmaps", "umit", "blaupunkt.png"))
            ScanNotebookPageBT.mapmodel.append([btname[count], pixbuf])	  
         else:
            pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join("share", "pixmaps", "umit", "bt.png"))
            ScanNotebookPageBT.mapmodel.append([btname[count], pixbuf])
         count+=1  

   def set_info(self, ScanNotebookPageBT, btid):
      global btname
      global btmac
      global btmanu
      global btsdp
      global sdpstatus
      sdpbrowseinfo = ""
      btid+=1
      print "Selected: " + str(ScanNotebookPageBT.btmap.get_selected_items()) + "\n" + str(btid)	 
      ScanNotebookPageBT.label.set_text("Device Details\t\t\t\t\n\nName: " + btname[btid] + "\nMAC: " + btmac[btid] + "\nManufacturer: " + btmanu[btid])
      print "Status_select: " + sdpstatus
      print "Found " + str(len(btsdp[btid])) + " Services"            
      if (sdpstatus == "Enabled"):
         if (len(btsdp[btid]) < 1):
            ScanNotebookPageBT.sdpview.get_buffer().set_text("no services found")
            return
         sdpbrowseinfo = "\nFound " + str(len(btsdp[btid])) + " Services"
         for svc in btsdp[btid]:
            try:
               if(str(svc["name"])=="no services found" or str(svc["name"])== ""):
                  ScanNotebookPageBT.sdpview.get_buffer().set_text("no services found")
               else:
                  try:
                     sdpbrowseinfo += "\n\nService Name: " + str(svc["name"]) + "\n Description: " + str(svc["description"])
                     sdpbrowseinfo += "\n Provided By: " + str(svc["provider"]) + "\n Protocol: " + str(svc["protocol"])
                     sdpbrowseinfo += "\n channel/PSM: " + str(svc["port"]) + "\n svc classes: " + str(svc["service-classes"])
                     sdpbrowseinfo += "\n profiles:  " + str(svc["profiles"]) + "\n service id: " + str(svc["service-id"])
                     ScanNotebookPageBT.sdpview.get_buffer().set_text(sdpbrowseinfo)
                  except:  
                     ScanNotebookPageBT.sdpview.get_buffer().set_text("N/A")
                     dlg = HIGAlertDialog(None, message_format=('Error'), secondary_text=("An error occurred while parsing SDP data"))
                     dlg.run()
                     dlg.destroy()
            except:  
               ScanNotebookPageBT.sdpview.get_buffer().set_text("no services found")                   

   def set_sdp(self, status):
      # Status of Enabled or Disabled
      global sdpstatus
      sdpstatus = status

   def clear(self, ScanNotebookPageBT):    
      global btname
      global btmac
      global btmanu
      global btsdp

      btname = [""]
      btmac = [""]
      btmanu = [""]
      btsdp = [""]
      ScanNotebookPageBT.progb.set_text("")	    	    
      ScanNotebookPageBT.progb.set_fraction(0)
      ScanNotebookPageBT.mapmodel.clear()

   def save_scan(self, ScanNotebookPageBT):    
      io.io().save()
      ScanNotebookPageBT.progb.set_text("100%")
      ScanNotebookPageBT.progb.set_fraction(1)
      message_id = ScanNotebookPageBT.status_bar.push(ScanNotebookPageBT.context_id, "File Saved")

   def load_scan(self, ScanNotebookPageBT, filename):     
      #clear previous entries before loading *ubt
      self.clear(ScanNotebookPageBT)
      status = io.io().load(filename) 
      if(str(status)!="None"):
         ScanNotebookPageBT.progb.set_text("0%")
         ScanNotebookPageBT.progb.set_fraction(0)
         message_id = ScanNotebookPageBT.status_bar.push(ScanNotebookPageBT.context_id, "File Load Error Encountered")
         return
      self.map(ScanNotebookPageBT)
      ScanNotebookPageBT.progb.set_text("100%")
      ScanNotebookPageBT.progb.set_fraction(1)
      message_id = ScanNotebookPageBT.status_bar.push(ScanNotebookPageBT.context_id, "File Loaded")
