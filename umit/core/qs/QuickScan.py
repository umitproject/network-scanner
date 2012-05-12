# Copyright (C) 2010 Adriano Monteiro Marques
#
# Author: Diogo Pinheiro <diogormpinheiro@gmail.com>
# Original author: Guilherme Polo <ggpolo@gmail.com>
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

"""
QuickScan
"""

import os
import sys
import time
import signal
import warnings
import subprocess

from umit.gui.qs.App import App
from umit.gui.Utils import verify_config_access
from umit.core.BGProcess import BGRunner
from umit.core.Paths import Path
from umit.core.UmitLogging import log
from umit.core.I18N import _
from umit.core.Version import VERSION
from umit.core.Utils import development_mode

NT = os.name == 'nt'
if NT:
    import win32api
    import win32event
    import servicemanager
else:
    servicemanager = lambda: None
    servicemanager.RunningAsService = lambda: False


class QuickScanControl(object):

    def __init__(self, running_file=None, home_conf=None, verbose=False,
            svc_class=None, svc_path=None):
        if running_file is None or home_conf is None:
            if home_conf is None:
                home_conf = os.path.split(Path.get_umit_conf())[0]
            running_file = os.path.join(home_conf, 'qsrunning')

        self.svc_class = svc_class
        self.svc_path = svc_path
        self.running_file = running_file
        self.home_conf = home_conf
        self.verbose = verbose

    def start(self, from_gui=False):
        """Start QuickScan."""
        if NT:
            bg = BGRunner(self.svc_class, self.svc_path)
            from_gui = False
        else:
            if from_gui:
                # Take care when running from gui
                running_path = Path.get_running_path()
                if running_path not in sys.path:
                    sys.path.append(running_path)
                starter = __import__('quickscan_launcher')
                subprocess.Popen([sys.executable, starter.__file__, 'start'])
            else:
                def post_init():
                    return main('start', sys.path[0], self.home_conf)
                bg = BGRunner(self.running_file, post_init)

        if not from_gui:
            err = bg.start()
            if err:
                return self._error(err)

    def stop(self):
        if NT:
            bg = BGRunner(self.svc_class)
        else:
            bg = BGRunner(self.running_file)

        err = bg.stop()
        if err:
            return self._error(err)

    def running(self):
        if NT:
            bg = BGRunner(self.svc_class)
        else:
            bg = BGRunner(self.running_file)

        return bg.running()

    def cleanup(self, remove_service=False):
        if NT:
            bg = BGRunner(self.svc_class)
            if remove_service:
                err = bg.remove()
                if err:
                    return self._error(err)
        else:
            bg = BGRunner(self.running_file)

        err = bg.cleanup()
        if err:
            return self._error(err)

    def _error(self, error):
        if self.verbose:
            print error
            return 1
        else:
            if NT:
                return win32api.FormatMessage(error)
            else:
                return error

            

def run_quickscan(winhndl=None):
    """
    Run quickscan.
    """
    quickscan_app = App()
    quickscan_app.run()
    
    
def safe_shutdown(rec_signal, frame):
    """
    Remove temp files before quitting.
    """
    log.info("Scheduler finishing..")

    if rec_signal is not None:
        raise SystemExit
    

def start(winhndl=None):
    """
    Start quickscan.
    """
    log.info("QuickScan starting..")

    # Check permissions
    verify_config_access()
    
    
    if not development_mode(default=True):
        # Generating temporary files names
        fd1, stdout_output = tempfile.mkstemp()
        fd2, stderr_output = tempfile.mkstemp()
    
        _stdout = open(stdout_output, "w")
        _stderr = open(stderr_output, "w")
    
        sys.stdout = _stdout
        sys.stderr = _stderr
    
        sys.excepthook = UmitExceptionHook()

    try:
        run_quickscan(winhndl)
    except KeyboardInterrupt:
        # if we are on win32, we should be here in case a WM_CLOSE message
        # was sent.
        safe_shutdown(None, None)
    else:
        # run_scheduler should finish normally when running as a Windows
        # Service
        safe_shutdown(None, None)


def main(cmd, base_path, home_conf, winhndl=None):
    if base_path not in sys.path:
        sys.path.insert(0, base_path)
        
    print base_path
    Path.set_running_path(os.path.abspath(os.path.dirname(base_path)))
    Path.force_set_umit_conf(home_conf)
    
    # Trying to adjust signals when running as a windows service won't work
    # since it needs to be adjusted while on the main thread.
    if not servicemanager.RunningAsService():
        if os.name == "posix":
            signal.signal(signal.SIGHUP, safe_shutdown)
        signal.signal(signal.SIGTERM, safe_shutdown)
        signal.signal(signal.SIGINT, safe_shutdown)

    cmds = {'start': start}
    cmds[cmd](winhndl=winhndl)

    
    
    
class UmitExceptionHook(object):
    def __call__(self, etype, emsg, etb):
        import warnings
        warnings.filterwarnings("error", module = "gtk")
        try:
            import gtk
        except Warning, e:
            print e.message
            sys.exit(-1)
        warnings.resetwarnings()

        from umit.gui.BugReport import CrashReport
        from higwidgets.higdialogs import HIGAlertDialog

        if etype == ImportError:
            d = HIGAlertDialog(type=gtk.MESSAGE_ERROR,
                message_format=_("Import error"),
                secondary_text=_("\nA required module was not "
                    "found.\n\nError:") + " %s" % emsg)
            d.run()
            d.destroy()
            return

        # Getting dependencies versions
        import higwidgets
        import umit.core
        import umit.gui

        # Try to get the correct path to nmap
        from umit.core.Paths import Path
        try:
            nmap_path = Path.nmap_command_path
        except Exception:
            # The configuration file hasn't been set yet, too bad.
            nmap_path = 'nmap'

        gtk_version = "%s.%s.%s" % gtk.gtk_version
        pygtk_version = "%s.%s.%s" % gtk.ver
        higwidgets_version = getattr(higwidgets, "__version__", "< 0.9.5")
        python_version = sys.version
        nmap_version = os.popen2('"%s" -V' % nmap_path)[1].read().strip("\n")
        try:
            osuname = " ".join(os.uname())
        except AttributeError:
            # os.uname is not available under Windows, and other unlikely
            # systems
            try:
                osuname = " ".join(platform.win32_ver())
            except AttributeError:
                osuname = "UNKNOWN"

        umit_version = VERSION
        umitCore_version = getattr(umit.core, "__version__", "< 0.9.5")
        umitGUI_version = getattr(umit.gui, "__version__", "< 0.9.5")

        versions = _("""
Versions:
---
GTK: %s
PyGTK: %s
HIGWidgets: %s
Python: %s
Nmap: %s
Operating System: %s
Umit: %s
UmitCore: %s
UmitGUI: %s
---""") % (gtk_version,
           pygtk_version,
           higwidgets_version,
           python_version,
           nmap_version,
           osuname,
           umit_version,
           umitCore_version,
           umitGUI_version)

        crash_text = cgitb.text((etype, emsg, etb))
        crash_text_dialog = "\n%s\n%s\n" % (versions, crash_text)
        crash_text = "{{{\n%s\n%s\n}}}" % (versions, crash_text)

        #Dialog info
        extrainfo_dialog = "%-17s %s\n%-17s %s\n%-17s %s\n%-17s %s\n" % (
            "sys.platform", sys.platform, "os.name", os.name,
            "Gtk version", '.'.join(map(str, gtk.gtk_version)),
            "Umit version", VERSION)
        crashmsg_dialog = "Crash Report\n%s\n%s\nDescription\n%s\n%s" % (
                '=' * 10, extrainfo_dialog, '-' * 20, crash_text_dialog)

        extrainfo = (
                "%-17s %s\n[[BR]]%-17s %s\n[[BR]]%-17s %s\n"
                "[[BR]]%-17s %s[[BR]]\n" % (
                    "sys.platform", sys.platform, "os.name", os.name,
                    "Gtk version", '.'.join(map(str, gtk.gtk_version)),
                    "Umit version", VERSION))
        crashmsg = (
                "Crash Report\n[[BR]]%s[[BR]]\n[[BR]]%s\n"
                "Description\n%s\n%s" % (
                    '=' * 10, extrainfo, '-' * 20, crash_text))

        # If quickscan started running then gtk.main was invoked. Let's end this
        # main loop now so when the Crash Report is closed, quickscan is also
        # closed.
        if gtk.main_level():
            gtk.main_quit()
            # We registered App().safe_shutdown for the SIGTERM signal,
            # now we can retrieve it and find out the quickscan's main window if
            # it got created.
            safeshutdown_meth = signal.getsignal(signal.SIGTERM)
            mainwindow = getattr(
                    safeshutdown_meth.im_self, 'main_window', None)
            # Disable controls.
            if mainwindow is not None:
                mainwindow.disable_window()

        try:
            cwin = CrashReport("Umit Crash - '%s'" % emsg,
                    crashmsg, description_dialog=crashmsg_dialog)
            cwin.show_all()
            cwin.connect('destroy', gtk.main_quit)
            from umit.gui.App import main_is_frozen
            if main_is_frozen():
                gtk.gdk.threads_enter()
            gtk.main()
            if main_is_frozen():
                gtk.gdk.threads_leave()
        except:
            import traceback
            traceback.print_exc()
            tempfd, tempname = tempfile.mkstemp()
            os.write(tempfd, crashmsg_dialog)
            d = HIGAlertDialog(type=gtk.MESSAGE_ERROR,
                    message_format=_("Bug not reported"),
                    secondary_text=_("A critical error occourried during "
                        "Umit execution, \nand it was not properly reported "
                        "to our bug tracker. The crash description was saved "
                        "to: %s, so you can still report it on our bug "
                        "tracker.") % tempname)
            os.close(tempfd)
            d.run()
            d.destroy()
