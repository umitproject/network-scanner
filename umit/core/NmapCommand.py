#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import os
import re
import sys
import threading
import tempfile
from types import StringTypes

from umit.core.NmapOptions import NmapOptions
from umit.core.OptionsConf import options_file
from umit.core.UmitLogging import log
from umit.core.Paths import Path
from umit.core.I18N import _

try:
    from subprocess import Popen, PIPE
except ImportError, e:
    raise ImportError(str(e) + ".\n" + _("Python 2.4 or later is required."))

if sys.hexversion < 0x2060000:
    # Monkey patch tempfile.NamedTemporaryFile to support the delete parameter
    class _TemporaryFileWrapper(tempfile._TemporaryFileWrapper):
        def __init__(self, delete=True, *args, **kwargs):
            self.delete = delete
            tempfile._TemporaryFileWrapper.__init__(self, *args, **kwargs)

        if os.name != 'nt':
            def close(self):
                if not self.close_called:
                    self.close_called = True
                    self.file.close()
                    if self.delete:
                        os.unlink(self.name)

    def MKNamedTemporaryFile(mode='w+b', bufsize=-1, suffix='',
            prefix=tempfile.template, dir=None, delete=True):
        if dir is None:
            dir = tempfile.gettempdir()

        if 'b' in mode:
            flags = tempfile._bin_openflags
        else:
            flags = tempfile._text_openflags

        if os.name == 'nt' and delete:
            flags |= os.O_TEMPORARY

        fd, name = tempfile._mkstemp_inner(dir, prefix, suffix, flags)
        fobj = os.fdopen(fd, mode, bufsize)
        return _TemporaryFileWrapper(delete, fobj, name)

    tempfile.NamedTemporaryFile = MKNamedTemporaryFile


# shell_state = True avoids python to open a terminal to execute nmap.exe
# shell_state = False is needed to run correctly at Linux
shell_state = (sys.platform == "win32")

log.debug(">>> Platform: %s" % sys.platform)

def split_quoted(s):
    """Like str.split, except that no splits occur inside quoted strings, and
       quoted strings are unquoted."""
    return [x.replace("\"", "") for x in re.findall('((?:"[^"]*"|[^"\s]+)+)',
                                                    s)]

class NmapCommand(object):
    def __init__(self, command=None, nmap_path=None):
        self.xml_output = tempfile.NamedTemporaryFile(delete=False)
        self.normal_output = tempfile.NamedTemporaryFile(delete=False)
        self.stdout_output = tempfile.NamedTemporaryFile(delete=False)
        self.stderr_output = tempfile.NamedTemporaryFile(delete=False)

        log.debug(">>> Created temporary files:")
        log.debug(">>> XML OUTPUT: %s" % self.xml_output.name)
        log.debug(">>> NORMAL OUTPUT: %s" % self.normal_output.name)
        log.debug(">>> STDOUT OUTPUT: %s" % self.stdout_output.name)
        log.debug(">>> STDERR OUTPUT: %s" % self.stderr_output.name)

        self.command_process = None
        self.command_buffer = ""
        self.command_stderr = ""

        self._nmap_path = nmap_path
        if nmap_path is None:
            self._nmap_path = Path.nmap_command_path
        log.debug(">>> Nmap command path: %s" % self._nmap_path)

        if command:
            self.command = command

    def get_command(self):
        if type(self._command) == type(""):
            return self._command.split()
        return self._command

    def set_command(self, command):
        self._command = self._verify(command)

    def _verify(self, command):
        command = self._remove_double_space(command)
        command = self._verify_output_options(command)
        command[0] = self._nmap_path

        return command

    def _verify_output_options(self, command):
        if type(command) == type([]):
            command = " ".join(command)

        # Removing comments from command
        for comment in re.findall('(#.*)', command):
            command = command.replace(comment, '')

        # Removing output options that user may have set away from command
        found = re.findall('(-o[XGASN]{1}) {0,1}', command)

        # Split back into individual options, honoring double quotes.
        splited = split_quoted(command)

        if found:
            for option in found:
                pos = splited.index(option)
                # Removes the element pos and pos+1 from splited list,
                # in case of pos+1 being out of splited's range,
                # just pos is removed then.
                splited[pos:pos+2] = []

        # Saving the XML output to a temporary file
        splited.append('-oX')
        splited.append('%s' % self.xml_output.name)

        # Saving the Normal output to a temporary file
        splited.append('-oN')
        splited.append('%s' % self.normal_output.name)

        # Disable runtime interaction feature
        #splited.append("--noninteractive")


        # Redirecting output
        #splited.append('>')
        #splited.append('%s' % self.stdout_output)

        return splited

    def _remove_double_space(self, command):
        if type(command) == type([]):
            command = " ".join(command)

        ## Found a better solution for this problem
        #while re.findall('(  )', command):
        #    command = command.replace('  ', ' ')


        # The first join + split ensures to remove double spaces on 
        # lists like this:
        # ["nmap    ", "-T4", ...]
        # And them, we must return a list of the command, that's why 
        # we have the second split
        return " ".join(command.split()).split()

    def close(self):
        # Remove temporary files created
        for fobj in (self.xml_output, self.normal_output, self.stdout_output,
                self.stderr_output):
            fobj.close()
            try:
                os.remove(fobj.name)
            except OSError, err:
                # Under Windows we ignore error 32: The process cannot
                # access the file because it is being used by another process.
                if getattr(err, 'winerror', None) != 32:
                    raise

    def kill(self):
        log.debug(">>> Killing scan process %s" % self.command_process.pid)

        if sys.platform != "win32":
            try:
                from signal import SIGKILL
                os.kill(self.command_process.pid, SIGKILL)
            except:
                pass
        else:
            try:
                # Not sure if this works. Must research a bit more about this
                # subprocess's method to see how it works.
                # In the meantime, this should not raise any exception because
                # we don't care if it killed the process as it never killed 
                # it anyway.
                from subprocess import TerminateProcess
                TerminateProcess(self.command_process._handle, 0)
            except:
                pass

    def run_scan(self):
        if self.command:
            #self.command_process = Popen(self.command, bufsize=1, stdin=PIPE,
            #                             stdout=PIPE, stderr=PIPE)

            # Because of problems with Windows, I passed only the file
            # descriptors to  Popen and set stdin to PIPE
            # Python problems... Cross-platform execution of process
            # should be improved

            self.command_process = Popen(self.command, bufsize=1,
                                         stdin=PIPE,
                                         stdout=self.stdout_output.fileno(),
                                         stderr=self.stderr_output.fileno(),
                                         shell=shell_state)
        else:
            raise Exception("You have no command to run! Please, set \
the command before trying to start scan!")

    def scan_state(self):
        if self.command_process is None:
            raise Exception("Scan is not running yet!")

        state = self.command_process.poll()

        # Buffer is not been used anymore
        # This line blocks the GUI execution, once the read method waits until a
        # new content come to be buffered
        #self.command_buffer += self.command_process.stdout.read()

        if state is None:
            return True # True means that the process is still running
        elif state == 0:
            return False # False means that the process had a successful exit
        else:
            self.command_stderr = self.get_error()
            
            log.critical("An error occourried during the scan execution!")
            log.critical('%s' % self.command_stderr)
            log.critical("Command that raised the exception: '%s'" % \
                         " ".join(self.command))
            raise Exception("An error occourried during the scan \
execution!\n'%s'" % self.command_stderr)

    def scan_progress(self):
        """Should return a tuple with the stage and status of the scan 
        execution progress. Will work only when the runtime interaction 
        problem is solved."""
        pass

    def get_raw_output(self):
        raw_desc = open(self.stdout_output.name, "r")
        raw_output = raw_desc.readlines()
        
        raw_desc.close()
        return "".join(raw_output)

    def get_output(self):
        output_desc = open(self.stdout_output.name, "r")
        output = output_desc.read()

        output_desc.close()
        return output

    def get_output_file(self):
        return self.stdout_output.name

    def get_normal_output(self):
        normal_desc = open(self.normal_output.name, "r")
        normal = normal_desc.read()

        normal_desc.close()
        return normal

    def get_xml_output(self):
        xml_desc = open(self.xml_output.name, "r")
        xml = xml_desc.read()

        xml_desc.close()
        return xml

    def get_xml_output_file(self):
        return self.xml_output.name

    def get_normal_output_file(self):
        return self.normal_output.name

    def get_error(self):
        error_desc = open(self.stderr_output.name, "r")
        error = error_desc.read()

        error_desc.close()
        return error

    def __del__(self):
        """
        Remove temp files if they are still present.
        """
        try:
            self.close()
        except OSError:
            # files removed already, good =)
            pass

    command = property(get_command, set_command)
    _command = None


class CommandConstructor:
    def __init__(self, options = {}):
        self.options = {}
        self.option_profile = NmapOptions(options_file)
        for k, v in options.items():
            self.add_option(k, v, False) # TODO: check this place further

    def add_option(self, option_name, args=[], level=False):
        if (not option_name) or \
           (option_name == "None" and not args and not level):
            # this certainly shouldn't be added
            return
        self.options[option_name] = (args, level)

    def remove_option(self, option_name):
        if option_name in self.options:
            self.options.pop(option_name)

    def get_command(self, target):
        splited = ['nmap']

        for option_name in self.options:
            option = self.option_profile.get_option(option_name)
            args, level = self.options[option_name]

            if type(args) in StringTypes:
                args = [args]

            if level:
                splited.append((option['option']+' ')*level)
            elif args:
                args = tuple (args)
                splited.append(option['option'] % args[0])
            else:
                splited.append(option['option'])
            
        splited.append(target)
        return ' '.join(splited)

    def get_options(self):
        return dict([(k, v[0]) for k, v in self.options.items()])

class CommandThread(threading.Thread):
    def __init__(self, command):
        self._stop_event = threading.Event()
        self._sleep = 1.0
        threading.Thread.__init__(self)
        self.command = command

    def run(self):
        #self.command_result = os.popen3(self.command)
        self.command_result = os.system(self.command)

    def join(self, timeout=None):
        self._stop_event.set()
        threading.Thread.join(self, timeout)


##############
# Exceptions #
##############

class WrongCommandType(Exception):
    def __init__(self, command):
        self.command = command

    def __str__(self):
        print "Command must be of type string! Got %s instead." % \
              str(type(self.command))

class OptionDependency(Exception):
    def __init__(self, option, dependency):
        self.option = option
        self.dependency = dependency
    
    def __str__(self):
        return "The given option '%s' has a dependency not commited: %s" %\
               (self.option, self.dependency)

class OptionConflict(Exception):
    def __init__(self, option, option_conflict):
        self.option = option
        self.option_conflict = option_conflict
    
    def __str__(self):
        return "The given option '%s' is conflicting with '%s'" %\
               (self.option, self.option_conflict)

class NmapCommandError(Exception):
    def __init__(self, command, error):
        self.error = error
        self.command = command
    
    def __str__(self):
        return """An error occouried while trying to execute nmap command.

ERROR: %s
COMMAND: %s
""" % (self.error, self.command)


if __name__ == '__main__':
    Path.set_umit_conf(os.path.dirname(sys.argv[0]))
    scan = NmapCommand('%s -T4 192.168.0.101"' % Path.nmap_command_path)
    scan.run_scan()

    try:
        while scan.scan_state():
            print ">>>", scan.get_normal_output()
    except Exception:
        print "Exception caught"

    print ">>>", scan.get_normal_output()
    print "Scan is finished!"
