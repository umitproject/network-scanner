# -*- coding: utf-8 -*-

# Copyright (C) 2009 Adriano Monteiro Marques.
#
# Author: Daniel Mendes Cassiano <dcassiano@umitproject.org>
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
import sys
import re
from datetime import datetime
from subprocess import Popen, PIPE

import gobject
import gtk
import shlex
import traceback
from gtk import gdk

from higwidgets.higentries import HIGTextEntry
from higwidgets.higtextviewers import HIGTextView
from higwidgets import HIGAlertDialog

from umit.core.Paths import Path
from umit.core.NmapCommand import NmapCommand
from umit.core.NmapParser import nmap_parser_sax
from umit.core.qs.ImportData import QSData
from umit.core.qs.Nmap import Nmap
from umit.core import Ipv6
from umit.core.TargetList import TargetList
from umit.core.UmitLogging import log
from umit.gui.NmapOutputViewer import NmapOutputViewer

#TODO: Import this of core, changing it from ScanNotebook to core

class Status(object):
    """
    Class responsible to handle the status of actions during the QS processing.
    """
    def __init__(self, status=False):
        if status:
            self.status = status
        else:
            self.set_unknown()
            
    def set_empty(self):
        self._status = "empty"
        
    def set_parsing_result(self):
        self._status = "parsing_result"

    def set_scanning(self):
        self._status = "scanning"

    def set_unknown(self):
        self._status = "unknown"
        
    def set_scan_failed(self):
        self._status = "scan_failed"
        
    def set_status(self, status):
        if status in self.available_status:
            self._status = status
        else:
            raise Exception("Unknown status!")
        
    def _verify_status(self, status):
        if self._status == status:
            return True
        return False
    
    def get_status(self):
        return self._status
    
    def get_parsing_result(self):
        return self._verify_status("parsing_result")
    
    def get_parsing_result(self):
        return self._verify_status("parsing_result")

    def get_scanning(self):
        return self._verify_status("scanning")

    def get_empty(self):
        return self._verify_status("empty")

    def get_unknown(self):
        return self._verify_status("unknown")
    
    def get_scan_failed(self):
        return self._verify_status("scan_failed")
        

    status = property(get_status, set_status)
    parsing_result = property(get_parsing_result)
    scanning = property(get_scanning)
    empty = property(get_empty)
    unknown = property(get_unknown)
    scan_failed = property(get_scan_failed)
    
    
class EntryField(object):
    """
    This class is responsible by the main part of QS: the EntryField.
    All logic of completion, data handling and interface is here.
    """
    
    def __init__(self):
        self.qs_data = QSData()
        self.entry = HIGTextEntry()
        self.entry.set_visibility(True)
        self.status = Status()
        self.status.set_empty()
        self.scan_result = Result()
        self.b_text = ""
        self.rgx_is_domain = "^((ht|f)tp(s?)\:\/\/|~/|/)?([\w]+:\w+@)?([a-zA-Z]{1}"
        self.rgx_is_domain += "([\w\-]+\.)+([\w]{2,5}))(:[\d]{1,5})?((/?\w+/)+|/?)"
        self.rgx_is_domain += "(\w+\.[\w]{3,4})?((\?\w+=\w+)?(&\w+=\w+)*)?"
        
        self.completion = gtk.EntryCompletion()
        self.entry.set_max_length(1000)
        
        # add button to launch result in umit
        self.btn_umit = gtk.Button ("Open Result")
        
        self.results_opened = False
        self.nmap_output = None
        
        self.load_data(None)
         
        self.btn_umit.connect("clicked", self._launch_umit, None)
        
        self.entry.show()

        
    def show_results(self):
        """
        Show scan output
        """
        if not self.results_opened:
            self.nmap_output = NmapOutputViewer()
            # remove some buttons
            self.nmap_output.hbox_buttons.remove(self.nmap_output.btn_output_properties)
            self.nmap_output.hbox_buttons.remove(self.nmap_output.btn_refresh)
            self.nmap_output.hbox_buttons.pack_start(self.btn_umit)
            self.vbox.pack_end(self.nmap_output)
            self.vbox.show_all()
            self.results_opened = True
        
    def hide_results(self):
        """
        Hide scan output
        """
        if self.results_opened:
            self.nmap_output.hbox_buttons.remove(self.btn_umit)
            self.vbox.remove(self.nmap_output)
            self.results_opened = False
        
    def menu_to_umit(self, widget, button, time, data=None):
        """
        Here will be the small menu responsible to call Network Scanner.
        """
        if button == 3:
            data.show_all()
            
    def _launch_umit(self, widget, event):
        """
        Here will go the call to NetWork Scanner to display results previously
        loaded here.
        """
        nscanner_call = "umit -f %s" % self.command_execution.get_xml_output_file()
        args = shlex.split(nscanner_call)
        self.command_process = Popen(args, bufsize=1, stdin=PIPE,
                                         stdout=PIPE, stderr=PIPE)

    def load_data(self, option=None):
        """
        Load the data on gtk.ListStore, generate the model and set functions of
        match and signals.
        """
        liststore = gtk.ListStore(str)
            
        if option == "host":
            for _d in self.qs_data.get_target_list():
                liststore.append([_d])
        elif option == "profile":
            for _d in self.qs_data.get_profiles("profile_name"):
                liststore.append([_d])
        elif option == "nmap_options":
            for _d in self.qs_data.get_nmap_options():
                liststore.append([_d])
        else:
            for _d in self.qs_data.get_all().values():
                for _i in _d:
                    liststore.append([_i])
            
        self.completion.set_model(liststore)
        self.completion.set_match_func(self.match_func)
        self.completion.connect('match-selected', self.on_completion_match)
        self.entry.connect('activate', self.on_completion_not_match)
        self.entry.connect('backspace', self.on_backspace)
        self.entry.set_completion(self.completion)
        self.completion.set_text_column(0)

    
    #def load_if_not_complete(self, widget, event):
        #self.load_data("host")
        
  
    def match_func(self, completion, key, iter):
        """
        This function have the job to match and compare the words that was entered 
        on the entry field.
        """
        model = self.completion.get_model()
        modelstr = model[iter][0]
        
        if ' ' in key:
            last_word = " ".join(key.split()[1:])
            if last_word != "":
                return modelstr.lower().startswith(last_word.lower()) or modelstr.lower().startswith(key.lower())
        
        return modelstr.lower().startswith(key.lower())
    
    
    def on_completion_not_match(self, widget):
        """
        This method is called when the autocompletion don't match any result
        or user press Enter.
        """
        target_list = TargetList()

        entered_text = self.entry.get_text()

        # If has a profile
        if len(entered_text) > 1 and entered_text.find(" ") != -1:
            possible_host = entered_text.split(" ")[0]
            possible_profile = " ".join(entered_text.split(" ")[1:])
        else:
            # If is just a domain
            self.b_text = entered_text + " "
            self.entry.set_text(self.b_text)
            possible_host = entered_text
            possible_profile = None

        # Saving the target
        target_list.add_target(possible_host)
            
        self.entry.set_position(-1)
                        
#        if len(self.b_text.split(" ")) > 1:
#            host = self.b_text.split(" ")[0]
#            profile = " ".join(self.b_text.split(" ")[1:])
#        else:
#            host = entered_text
#            profile = None

            
        #Launch the scan
        self.run_scan(possible_host, possible_profile)
        
        #TODO: get the end of the scan here?
        try:
            alive = self.command_execution.scan_state()
            
            while alive:
                alive = self.command_execution.scan_state()

            file = self.command_execution.get_normal_output_file()
            self.show_results()
            self.nmap_output.show_nmap_output(file)
            self.nmap_output.refresh_output()
 
            
            #text_out = self.scan_result.set_nmap_output(possible_host, 
            #                        self.command_execution.get_normal_output(),
            #                        possible_profile)
                    
            #self.buffer.set_text(text_out)
            #self.vbox.pack_start(self.result_text, False, False, 0)
            #self.result_text.show()
        
            self.save_scan(possible_host)
            #del entered_text
        
            #self.load_data("profile")
        
            return True
        
        except:
            pass

        
    def on_completion_match(self, completion, model, iter):
        #get the text entered by the user
        entered_text = self.entry.get_text()
        
        if model[iter][0]:
            
            current_text = model[iter][0]
            # If has a profile
            if len(entered_text) > 1 and entered_text.find(" ") != -1:
                self.b_text = entered_text.split(" ")[0] + " " + current_text + " "
                self.entry.set_text(self.b_text)
                possible_host = entered_text.split(" ")[0]
                possible_profile = current_text
            #elif self.entry.get_text()
            else:
                # If is just a domain
                self.b_text = current_text + " "
                self.entry.set_text(self.b_text)
                possible_host = current_text
                possible_profile = None
                
            self.entry.set_position(-1)    
            data_from_db = self.qs_data.get_from_db()
            
            if current_text in data_from_db.keys():
                text_out = ""
                for _t in data_from_db[current_text]:
                    if _t[0] == "ports" or _t[0] == "stats":
                        pass
                    else:
                        text_out += "%s: %s\n" % (_t[0], _t[1])
                        
                #self.buffer.set_text(text_out)
                #self.vbox.pack_start(self.result_text, False, False, 0)
                #self.result_text.show()
                
    
            self.run_scan(possible_host, possible_profile)
            try:
                alive = self.command_execution.scan_state()
                
                while alive:
                    alive = self.command_execution.scan_state()
                    if not alive:
                        break
                    
                self.show_results()
                file = self.command_execution.get_normal_output_file()
                print "scan finished - %s" % file
                self.nmap_output.show_nmap_output(file)
                self.nmap_output.refresh_output()
                
                #text_out = self.scan_result.set_nmap_output(possible_host, 
                #                self.command_execution.get_normal_output(),
                #                possible_profile)
        
                #self.buffer.set_text(text_out)
                #self.vbox.pack_start(self.result_text, False, False, 0)
                #self.result_text.show()
        
                self.save_scan(possible_host)
        
                #self.load_data("profile")
        
                return True
        
            except:
                print("exception")
                traceback.print_exc(file=sys.stdout)
            
            del data_from_db
                        
            #self.load_data("profile")
            return True
            
    def on_backspace(self, entry):
        self.hide_results()
        self.resize(500,30)
        self.b_text = ""

    def disable_widgets(self):
        self.scan_result.set_sensitive(False)
    
    def enable_widgets(self):
        self.scan_result.set_sensitive(True)
    
    def kill_scan(self):
        try:
            self.command_execution.kill()
        except AttributeError:
            pass

        self.entry.set_text("")
        self.status.set_empty()
        self.disable_widgets()
    
    def run_scan(self, host, profile):
        if re.match(self.rgx_is_domain, host):

            commands = self.qs_data.get_profiles("profile_commands")
            try:
                nmap_option = commands[profile]
            except:
                nmap_option = "-T Aggressive -v -n"

            print "QuickScan: running scan: %s on %s" % (nmap_option, host)
            #
            #
            #
            #
            #ipv6 option
            #check for ipv6 address and -6 to command option 
            #
            #
            #
            #
            if Ipv6.is_ipv6(host):
            	namp_option = nmap_option + " -6"
            
            self.command_execution = NmapCommand('%s %s %s' % (Path.nmap_command_path,
                                                               nmap_option,
                                                               host))
            
            try:
                alive = self.command_execution.scan_state()
                if alive:
                    warn_dialog = HIGAlertDialog(
                    message_format="Scan has not finished yet",
                    secondary_text="Another scan is running in the background.",
                    type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_OK_CANCEL)
                response = warn_dialog.run()
                warn_dialog.destroy()
                
                if response == gtk.RESPONSE_OK:
                    self.kill_scan()
                else:
                    return
            
            except:
                pass
                        
            try:
                self.command_execution.run_scan()
                self.status.set_scanning()
            except OSError, msg:
                warn_dialog = HIGAlertDialog(
                    message_format="Nmap couldn't be found",
                    secondary_text="Umit Quick Scan couldn't find Nmap. " 
                    "Please check your Nmap instalation.",
                    type=gtk.MESSAGE_ERROR)
                warn_dialog.run()
                warn_dialog.destroy()
            except Exception, msg:
                warn_dialog = HIGAlertDialog(
                    message_format="Command is missing!",
                    secondary_text="Please check your profile's command.",
                    type=gtk.MESSAGE_ERROR)
                warn_dialog.run()
                warn_dialog.destroy()
                
                
            self.verify_thread_timeout_id = gobject.timeout_add(2000, 
                self.verify_execution)
            
            return
        
        else:
            self.command_execution = None
            return False

    def save_scan(self, host):
        from umit.core.UmitDB import Scans
        store = Scans(scan_name="Quick Scan on %s" % host,
                      nmap_xml_output=self.command_execution.get_xml_output(),
                      date=datetime.now())
        
    def verify_execution(self):
        try:
            alive = self.command_execution.scan_state()
        except:
            self.disable_widgets()
            self.status.set_scan_failed()
            #self.scan_result.set_nmap_output(self.command_execution.get_error())
            #self.emit("scan-finished")
            return False

        # Maybe this automatic refresh should be eliminated 
        # to avoid processor burning
        #self.scan_result.refresh_nmap_output()
        
        if alive:
            return True
        else:
            #self.parse_result(self.command_execution.get_xml_output_file())
            #self.emit("scan-finished")
            return False
    
class Result(gtk.HPaned):

    __gsignals__ = {
        'scan-finished' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
    }
    
    def __init__(self):
        gtk.HPaned.__init__(self)
        self.status = Status()
        self.status.set_parsing_result()
        self.parsed = None
        
    def set_nmap_output(self, host, msg, command):
        
        # Nmap output in parameter msg
      
        text_out = "Running a %s on %s...\n" % (command, host)
        text_out += "IP: "
                
        if re.compile("\d{1,3}(\.\d{1,3}){3}").search(msg):
            text_out += re.compile("\d{1,3}(\.\d{1,3}){3}").search(msg).group()
        else:
            text_out += "not identified"
                
        text_out += "\tPorts:\t"
        services = []
                
        for reg in msg.split("\n"):
            if reg.find("open") != -1:
                try:
                    text_out += "%s " % re.search("[0-9]+", reg.replace("open", "").split()[0]).group()
                    services.append(reg.replace("open", "").split()[1])
                    flag_open = True
                except AttributeError:
                    pass
                        
            elif reg.find("closed") != -1:
                try:
                    text_out += "%s " % re.search("[0-9]+", reg.replace("closed", "").split()[0]).group()
                    services.append(reg.replace("closed", "").split()[1])
                except AttributeError:
                    pass
                        
        text_out += "\n\t\t\t\tServices:\t"
                        
        for s in services:
            text_out += "%s " % s

            
        return text_out
        
                
if __name__ == "__main__":
    a = EntryField()
