#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2009 Adriano Monteiro Marques
#
# Author:  Guilherme Polo <ggpolo@gmail.com>
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
import sys
import errno
import signal

NT = os.name == 'nt'

try:
    DEVNULL = os.devnull
except AttributeError:
    DEVNULL = '/dev/null'

try:
    import pywintypes
    import win32event
    import win32service
    import win32serviceutil
except ImportError:
    if NT:
        # If we are on Windows then the above modules are totally required
        raise
    else:
        # Otherwise we make this dummy thing so we can define the
        # WindowsService class elsewhere.
        class win32serviceutil:
            class ServiceFramework:
                pass
        win32serviceutil = win32serviceutil()


class UNIXDaemon(object):

    def __init__(self, pidfilename, post_init=None):
        self._pidfilename = pidfilename
        self._post_init = post_init

    def running(self):
        """
        Return True if the daemon is still running, False otherwise.
        """
        pid = self._get_pid()
        if isinstance(pid, int):
            res = self._stopped(pid)
            if isinstance(res, tuple):
                # It is assumed the process is still running if it gives an
                # error different than "No such process".
                return True
            else:
                return not bool(res)
        else:
            return False

    def stop(self):
        if self.running():
            return self.cleanup()

    def cleanup(self):
        pid = self._get_pid()
        if not isinstance(pid, int):
            # Assuming that some error related to the pidfile not being
            # present was returned, meaning there is no cleanup to perform.
            return
        err = self._finish(pid)
        if err:
            return err

        return self._remove_pidfile()

    def start(self):
        # Perform cleanup before starting a new daemon, if necessary
        if self._get_pid():
            # Finish the daemon before continuing
            self.stop()

        self._daemon_init()

        pid = os.getpid()
        f_pid = open(self._pidfilename, 'w')
        f_pid.write("%d" % pid)
        f_pid.close()

        if self._post_init:
            self._post_init()

    def _stopped(self, pid):
        try:
            os.kill(pid, 0)
        except OSError, err:
            if err.errno == errno.ESRCH: # OS Error 3: No such process
                return 1
            # Could be OS Error 1: Operation not permitted
            return -1, err

    def _finish(self, pid):
        err = self._stopped(pid)
        if isinstance(err, tuple):
            # Error occurred
            return err[1]

        if not err:
            # Try finishing it now
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError, err:
                return err

    def _get_pid(self):
        try:
            return int(open(self._pidfilename, 'r').read())
        except IOError, err:
            return err

    def _remove_pidfile(self):
        try:
            os.remove(self._pidfilename)
        except OSError, err:
            # maybe control file just got deleted
            return err

    def _daemon_init(self, new_cwd='/', umask=0):
        pid = os.fork()
        if pid:
            # parent terminates
            sys.exit(0)

        # child 1 continues
        os.setsid() # Become session leader

        signal.signal(signal.SIGHUP, signal.SIG_IGN)
        pid = os.fork()
        if pid:
            # child 1 terminates
            sys.exit(0)

        # child 2 continues
        os.umask(0)

        if new_cwd is not None:
            os.chdir(new_cwd)

        # Redirect stdin, stdout, and stderr to DEVNULL
        for fobj in (sys.stdin, sys.stdout, sys.stderr):
            fobj.close()
        sys.stdin = open(DEVNULL, 'r')
        sys.stdout = open(DEVNULL, 'a+')
        sys.stderr = open(DEVNULL, 'a+')

        # Success!

class WindowsService(win32serviceutil.ServiceFramework):
    def __init__(self, name):
        win32serviceutil.ServiceFramework.__init__(self, name)
        self.hndl_waitstop = win32event.CreateEvent(None, False, False, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hndl_waitstop)

    def SvcDoRun(self):
        self.run()

class WindowsServiceController(object):
    def __init__(self, service_class, service_path=None):
        self.service_class = service_class
        self.service_path = service_path

    def running(self):
        """Return True if the service is still running, False otherwise."""
        try:
            status = win32serviceutil.QueryServiceStatus(
                    self.service_class._svc_name_)
        except pywintypes.error:
            # Service is not installed, assuming it is not running
            return False
        # status is a _SERVICE_STATUS struct (check msdn for that),
        # status[1] contains the current state for the given service.
        if status[1] == win32service.SERVICE_RUNNING:
            return True
        return False

    def remove(self):
        if self.running():
            self.stop()
        return win32serviceutil.HandleCommandLine(self.service_class,
                argv=('', 'remove'))

    def install(self):
        # Always use the complete path to the module containing
        # service_class so this doesn't fail when starting from Umit.
        # This should be equivalent to the service class string that would
        # be generated if we were running umit_scheduler.py from the command
        # line.
        if self.service_path:
            path = os.path.abspath(self.service_path)
            svc_class_string = "%s.%s" % (
                    os.path.splitext(path)[0], self.service_class.__name__)
        else:
            svc_class_string = None
        return win32serviceutil.HandleCommandLine(self.service_class,
                svc_class_string, argv=('', 'install'))

    def stop(self):
        return win32serviceutil.HandleCommandLine(self.service_class,
                argv=('', 'stop'))

    def start(self):
        # Perform cleanup before starting the service, if necessary
        if self.running():
            # Stop the service before continuing
            self.stop()

        cls = self.service_class

        try:
            win32serviceutil.QueryServiceStatus(cls._svc_name_)
        except pywintypes.error:
            # Service not installed yet, will install it now
            err = self.install()
            if err:
                return err

        return win32serviceutil.HandleCommandLine(cls, argv=('', 'start'))

    def cleanup(self):
        pass


if NT:
    BaseControl = WindowsServiceController
else:
    BaseControl = UNIXDaemon

class BGRunner(BaseControl):
    def __init__(self, *args, **kwargs):
        BaseControl.__init__(self, *args, **kwargs)
