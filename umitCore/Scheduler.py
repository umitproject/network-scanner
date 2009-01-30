# Copyright (C) 2007 Insecure.Com LLC.
#
# Original author: Adriano Monteiro Marques
# Now maintained and updated by: Guilherme Polo <ggpolo@gmail.com>
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

"""
Job scheduler
"""

import os
import sys
import time
import signal
import warnings
from os.path import join
from ConfigParser import ConfigParser

# There is some bug running more than one scan at same time.

class Scheduler(object):
    """
    Schedules schemas to run.
    """

    def __init__(self, schemas_file, profiles_file):
        self.schemas_file = schemas_file
        self.profiles_file = profiles_file
        self.schemas_stat = None
        self.profiles_stat = None

    def parse_schemas(self):
        """
        Parse schemas set in file.
        """
        self.schemas = [ ]

        self.schema_parser = ConfigParser()
        self.schema_parser.read(self.schemas_file)

        for sec in self.schema_parser.sections():
            self.schemas.append(SchedSchema(self.schema_parser, sec))

    
    def check_for_changes(self):
        """
        If schemas file or profiles file changed since last check, 
        reparse schemas.
        """
        try:
            new_sstat = os.stat(self.schemas_file)
            new_pstat = os.stat(self.profiles_file)
        except OSError: # file was being saved (probably) when this got called
            time.sleep(.1)
            new_sstat = os.stat(self.schemas_file)
            new_pstat = os.stat(self.profiles_file)

        new_sstat = new_sstat.st_mtime
        new_pstat = new_pstat.st_mtime

        if new_sstat != self.schemas_stat or new_pstat != self.profiles_stat:
            log.debug("Schemas file changed since last check")
            self.schemas_stat = new_sstat
            self.profiles_stat = new_pstat
            self.parse_schemas()


    def _get_schemas_stat(self):
        """
        Get latest os.stat for schemas file.
        """
        return self.__schemas_stat


    def _set_schemas_stat(self, stat):
        """
        Set current os.stat for schemas file.
        """
        self.__schemas_stat = stat


    def _get_profiles_stat(self):
        """
        Get latests os.stat for profiles file.
        """
        return self.__profiles_stat


    def _set_profiles_stat(self, stat):
        """
        Set current os.stat for profiles file.
        """
        self.__profiles_stat = stat


    def _get_schemas_file(self):
        """
        Get schemas file.
        """
        return self.__schemasf


    def _set_schemas_file(self, sfile):
        """
        Set schemas file.
        """
        try:
            os.stat(sfile)
        except OSError, e:
            log.error("%s" % e)
            sys.exit(0)

        self.__schemasf = sfile


    def _get_profiles_file(self):
        """
        Get profiles file.
        """
        return self.__profilesf


    def _set_profiles_file(self, pfile):
        """
        Set profiles file.
        """
        try:
            os.stat(pfile)
        except OSError, e:
            log.error("%s" % e)
            sys.exit(0)

        self.__profilesf = pfile


    # Properties
    schemas_file = property(_get_schemas_file, _set_schemas_file)
    profiles_file = property(_get_profiles_file, _set_profiles_file)
    schemas_last_stat = property(_get_schemas_stat, _set_schemas_stat)
    profiles_last_stat = property(_get_profiles_stat, _set_profiles_stat)


class SchedSchema(object):
    """
    Parse scheduled schemas.
    """

    def __init__(self, schema_parser, schema_name):
        self.profile_opts = {
            # Task execution time
            'hour':self._set_hour,
            'minute':self._set_minute,
            'month':self._set_month,
            'day':self._set_day,
            'weekday':self._set_weekday,
        }

        self.options = { 
            # Task scheduling profile
            'profile':self._set_profile,
            # Task command
            'command':self._set_command,
            # Task options
            'enabled':self._set_enabled,
            'addtoinv':self._set_addtoinv,
            'saveto':self._set_saveto,
            'mailto':self._set_mailto,
            'smtp':self._set_smtp
        }

        self.__schema_name = schema_name
        self.schema_parser = schema_parser
        self.last_check = None
        self.cron_parser = CronParser()
        self.profiles = Path.sched_profiles
        self.setup_schema(self.schema_name)


    def job_to_run(self):
        """
        Check if there is a scheduled job for now and if there is,
        return True, otherwise False.
        """
        cur_time = time.localtime()

        # check if we should check for job or not
        if self.last_check and cur_time[1] == self.last_check[1] and \
            cur_time[2] == self.last_check[2] and \
            cur_time[3] == self.last_check[3] and \
            cur_time[4] == self.last_check[4] and \
            cur_time[6] == self.last_check[6]:

            return False # too early to run a job again!

        if cur_time[1] in self.month and cur_time[2] in self.day \
            and cur_time[3] in self.hour and cur_time[4] in self.minute \
            and cur_time[6] in self.weekday:
            
            self.last_check = cur_time
            return True # there is a job to run!


    def setup_schema(self, name):
        """
        Setup schema.
        """
        if self.schema_parser.has_section(name):
            for opt in self.schema_parser.options(name):
                if opt in self.options.keys():
                    self.options[opt](self.schema_parser.get(name, opt))

            self.load_profile()


    def load_profile(self):
        """
        Load scheduling profile for current schema.
        """
        p_cfg = ConfigParser()
        p_cfg.read(self.profiles)

        if p_cfg.has_section(self.profile):
            for opt in p_cfg.options(self.profile):
                if opt in self.profile_opts.keys():
                    self.profile_opts[opt](p_cfg.get(self.profile, opt))


    def _get_schema_name(self):
        """
        Return schema name set.
        """
        return self.__schema_name


    def _get_last_check(self):
        """
        Return when last check happened.
        """
        return self.__lcheck


    def _set_last_check(self, when):
        """
        Set last check time.
        """
        self.__lcheck = when


    # Schema Profile
    def _get_profile(self):
        return self.__profile


    def _set_profile(self, profile):
        """
        Set scheduling profile for current schema.
        """
        self.__profile = profile


    # Job time
    def _get_month(self):
        return self.__month


    def _set_month(self, month):
        """
        Parse and set month.
        """
        self.__month = self.cron_parser.parse_month(month)


    def _get_day(self): 
        return self.__day


    def _set_day(self, day):
        """
        Parse and set day.
        """
        self.__day = self.cron_parser.parse_day(day)


    def _get_weekday(self): 
        return self.__weekday


    def _set_weekday(self, weekday):
        """
        Parse and set weekday.
        """
        self.__weekday = self.cron_parser.parse_weekday(weekday)


    def _get_hour(self): 
        return self.__hour


    def _set_hour(self, hour):
        """
        Parse and set hour.
        """
        self.__hour = self.cron_parser.parse_hour(hour)


    def _get_minute(self): 
        return self.__minute


    def _set_minute(self, minute):
        """
        Parse and set minute.
        """
        self.__minute = self.cron_parser.parse_minute(minute)


    # Job Command
    def _get_command(self):
        """
        Get job command.
        """
        return self.__command


    def _set_command(self, command):
        """
        Set command for job.
        """
        self.__command = command


    # Job Options
    def _get_enabled(self):
        """
        Returns True if job should run, otherwise, False.
        """
        return self.__enabled


    def _set_enabled(self, enable):
        """
        Set if job should run or not.
        """
        self.__enabled = enable


    def _get_addtoinv(self):
        """
        Returns True if job result should be stored in Inventory, otherwise,
        False.
        """
        return self.__addtoinv


    def _set_addtoinv(self, add):
        """
        Sets job result to be added to Inventory, or not.
        """
        self.__addtoinv = add


    def _get_saveto(self):
        """
        Get file that stores job results.
        """
        return self.__savefile


    def _set_saveto(self, save_dir):
        """
        Set a file to store job results.
        """
        if save_dir:
            self.__savefile = os.path.join(save_dir, self.schema_name + ".xml")
        else:
            self.__savefile = None
        

    def _get_mailto(self):
        """
        Get email set to receive job results.
        """
        return self.__mail


    def _set_mailto(self, mail): 
        """
        Set an email to receive job results.
        """
        self.__mail = mail

    
    def _get_smtp(self):
        """
        Get smtp profile to use for sending email.
        """
        return self.__smtp


    def _set_smtp(self, smtp):
        """
        Set a smtp profile for sending email.
        """
        self.__smtp = smtp


    # Properties
    profile = property(_get_profile, _set_profile)
    month = property(_get_month, _set_month)
    day = property(_get_day, _set_day)
    weekday = property(_get_weekday, _set_weekday)
    hour = property(_get_hour, _set_hour)
    minute = property(_get_minute, _set_minute)
    command = property(_get_command, _set_command)
    enabled = property(_get_enabled, _set_enabled)
    addtoinv = property(_get_addtoinv, _set_addtoinv)
    saveto = property(_get_saveto, _set_saveto)
    mailto = property(_get_mailto, _set_mailto)
    smtp = property(_get_smtp, _set_smtp)

    last_check = property(_get_last_check, _set_last_check)
    schema_name = property(_get_schema_name)


def load_smtp_profile(smtp):
    """
    Load a smtp schema.
    """
    schema = ConfigParser()
    schema.read(Path.smtp_schemas)
    
    if not schema.has_section(smtp):
        raise Exception("Inconsistence in scheduling schemas within smtp \
schemas, you tried to use the following smtp schema: %s, but it doesn't \
exist." % smtp)
 
    smtp_dict = { 'auth': '',
                  'user': '',
                  'pass': '',
                  'server': '',
                  'port': '',
                  'tls': '',
                  'mailfrom': '',
                }

    for item in schema.items(smtp):
        smtp_dict[item[0]] = item[1]

    return smtp_dict


def decide_output(ofile):
    """
    Choose a better or the same output path.
    """
    output = None
    file_path = os.path.abspath(ofile)

    if os.path.exists(os.path.split(file_path)[0]): # path exists at least
        try: # try to open file in read mode
            f = open(ofile, 'r')
            f.close()
            # if we are still here, file exists, this is bad ;/ (not so bad)
            count = 1
            
            # file name without extension
            cut = ofile.find('.xml')
            orig = ofile[:cut]
            
            while os.path.isfile(ofile):
                ofile = orig + "_%d.xml" % count # try appending extra extension
                
                count += 1
            
            warnings.warn("File will be saved as %s" % ofile, Warning)
            
        except IOError: # file didnt exist and path exists, this is good!
            pass
            
        output = ofile
        
    return output


def calc_next_time():
    """
    Calculate next time to check for changes and jobs.
    """
    tt = time.localtime(time.time() + 60)
    tt = tt[:5] + (0,) + tt[6:]
    return time.mktime(tt)


running_scans = { }

def run_scheduler(sched):
    """
    Run scheduler forever.
    """
    next_time = calc_next_time()
    scount = 0 # number of scans running

    while 1: # run forever and ever ;)
        current_time = time.time()

        if current_time < next_time:
            time.sleep(next_time - current_time + .1)

        # check if time has changed by more than two minutes (clock changes)
        if abs(time.time() - next_time) > 120:
            # reset timer
            next_time = calc_next_time()

        sched.check_for_changes()

        for schema in sched.schemas:
            if schema.job_to_run():
                if not int(schema.enabled): # schema disabled, neeexxt!
                    continue

                name = schema.schema_name
                log.info("Scheduled schema to run: %s" % name)

                if not schema.command:
                    log.warning("No command set for schema %s, \
skipping!" % name)
                    continue

                scan = NmapCommand(schema.command)
                scan.run_scan()

                running_scans[scount] = (scan, schema.saveto, schema.mailto,
                                         name, schema.addtoinv, schema.smtp)
                scount += 1 # more one scan running
        
        for running, opts in running_scans.items():
            scan = opts[0]

            try:
                scan_state = scan.scan_state()
            except Exception, err:
                log.critical("Scheduled schema '%s' failed to run. \
Reason: %s" % (schema.schema_name , err))
                continue

            if not scan_state: # scan finished
                log.info("Scan finished: %s" % opts[3])
            
                if opts[1]: # save xml output
                    saveto = decide_output(opts[1])
                    f = open(saveto, 'w')
                    f.write(open(scan.get_xml_output_file(), 'r').read())
                    f.close()
                    log.info("Scan output saved as: %s" % saveto)
                
                if opts[2]: # mail output
                    recipients = opts[2].split(',')
                    log.info("Scan output will be mailed to: \
%s" % recipients)

                    smtp = load_smtp_profile(opts[5])

                    auth = int(smtp['auth'])
                    tls = int(smtp['tls'])
                    mailfrom = smtp['mailfrom']
                    user = smtp['user']
                    passwd = smtp['pass']
                    server = smtp['server']
                    port = smtp['port']
                    curr_time = time.ctime()
                    orig_output = scan.get_xml_output_file()
                    new_file_output = curr_time + "-" + opts[3]

                    fd_wcont = open(new_file_output, 'w')
                    for line in open(orig_output, 'r'):
                        fd_wcont.write(line)
                    fd_wcont.close()

                    email = Email(mailfrom, recipients, server, None,
                                  user, passwd, tls, port)
                    email.sendmail(_("UMIT: Status Report for scheduled \
schema \"%s\"" % opts[3]), _("There was a scheduled job that finished \
now: %s\nFollows an attachment of job output." % curr_time), new_file_output)
                    os.remove(new_file_output)

                if int(opts[4]): # add to inventory
                    log.info("Scan results being added to Inventory \
%s" % opts[3])
                    xmlstore = XMLStore(Path.umitdb_ng, False)
                    try:
                        xmlstore.store(scan.get_xml_output_file(),
                                inventory=opts[3])
                    finally:
                        xmlstore.close() # close connection to the database
                    log.info("Scan finished insertion on Inventory \
%s" % opts[3])
                    
                scan.close() # delete temporary files
                scount -= 1 # one scan finished
                del running_scans[running]
            
        next_time += 60


def safe_shutdown(rec_signal, frame):
    """
    Remove temp files before quitting.
    """
    log.info("Scheduler finishing..")
    
    if running_scans:
        scans_count = len(running_scans)
        log.debug("%d scan%s to cleanup" % (scans_count, 
                                            (scans_count > 1) and 's' or ''))

    for args in running_scans.values():
        scan = args[0]
        scan.close()

    log.info("Scheduler finished sucessfully!")

    raise SystemExit


def start(schema_file=None, profile_file=None):
    """
    Start scheduler.
    """
    log.info("Scheduler starting..")

    if not schema_file:
        schema_file = Path.sched_schemas
    if not profile_file:
        profile_file = Path.sched_profiles

    s = Scheduler(schema_file, profile_file)

    log.info("Scheduler started, using schemas file '%s' and scheduling file \
'%s'" % (schema_file, profile_file))

    try:
        run_scheduler(s)
    except KeyboardInterrupt:
        # if we are on win32, we should be here in case a WM_CLOSE message
        # was sent.
        safe_shutdown(None, None)


if __name__ == "__main__":    
    sys.path.insert(0, sys.argv[1])

    from umitCore.Paths import Path
    Path.set_umit_conf(join(sys.argv[3]), True)

    from umitCore.UmitLogging import file_log
    from umitCore.I18N import _
    from umitCore.CronParser import CronParser
    from umitCore.NmapCommand import NmapCommand
    from umitCore.Email import Email
    from umitDB.XMLStore import XMLStore

    log = file_log(Path.sched_log)
    
    umitdb_ng = Path.umitdb_ng

    if os.name == "posix":
        signal.signal(signal.SIGHUP, safe_shutdown)
        
    signal.signal(signal.SIGTERM, safe_shutdown)
    signal.signal(signal.SIGINT, safe_shutdown)

    cmds = { "start": start }

    cmds[sys.argv[2]]()

