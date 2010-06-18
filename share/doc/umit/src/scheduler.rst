UMIT Scheduler
==============

.. sectionauthor:: Guilherme Polo <ggpolo@gmail.com>


Introduction
------------

The *Scan Scheduler Editor* is the place where you will schedule
scans to run on background without noticing. You may save the scan
output to a file or send it to one or more emails. It is possible to
enable and disable the schedule, it can also be configured to auto-add
scan results to the Network Inventory by toggling the *Add to the Inventory*
option.


Setting up a Schedule
---------------------

To set up a new scan schedule you just need to define a name for the schedule,
a schedule profile and a command for it. The other options are optional, but
you may want to use them too.

The following table tells about all the fields you will find in the
*Scan Scheduler Editor*.

   +----------------------+---------------------------------------------------+
   | Field                | Meaning                                           |
   +======================+===================================================+
   | Schema name          | Defines an unique name for the Scan Schedule that |
   |                      | is being created, you may name it like            |
   |                      | "network scan", "local scan", etc.                |
   |                      | Note that if you choose to add this schedule      |
   |                      | to the Inventory, the Inventory's name will be    |
   |                      | the Schema name.                                  |
   +----------------------+---------------------------------------------------+
   | Scan Profile         | These profiles are the profiles you created in    |
   |                      | UMIT, they define scan options.                   |
   +----------------------+---------------------------------------------------+
   | Command              | Command is the scan command that will be used in  |
   |                      | this schedule.                                    |
   +----------------------+---------------------------------------------------+
   | Scheduling Profile   | You need to choose one of the available           |
   |                      | Scheduling Profiles.                              |
   |                      | This defines when the schema command will be      |
   |                      | executed. Clicking on "Edit Profiles" will open   |
   |                      | the Scheduling Profiles Editor.                   |
   +----------------------+---------------------------------------------------+
   | Save outputs to      | If you choose to save output, you will need to    |
   |                      | specify an output directory. A directory is       |
   |                      | required because a schedule is likely to be       |
   |                      | executed several times, so the file output is a   |
   |                      | combination of directory output, schema name      |
   |                      | and number of outputs for that schema.            |
   +----------------------+---------------------------------------------------+
   | Send output to email | If you choose to send output to a email, you      |
   |                      | will need to specify one or more recipients.      |
   |                      | Example: me@example.com or                        |
   |                      | me@example.com,her@example.com.                   |
   |                      | You also need to choose one of the available      |
   |                      | SMTP Schemas, if there is no SMTP Schema          |
   |                      | created yet you will need to open "SMTP Setup"    |
   |                      | window and create one so you can use it here.     |
   +----------------------+---------------------------------------------------+
   | Add to the Inventory | If you toggle on this option, the scan output     |
   |                      | will be added to the Network Inventory,           |
   |                      | according to the previous explanation given on    |
   |                      | "Schema Name".                                    |
   +----------------------+---------------------------------------------------+
   | Enabled              | If you toggle on "Enabled", this schema will      |
   |                      | run on the scheduled time if the Scheduler is     |
   |                      | running. Otherwise, it will just exist but will   |
   |                      | never be executed (you may come back later and    |
   |                      | Enable it).                                       |
   +----------------------+---------------------------------------------------+

After filling all the required fields, you may click on "Apply".
If no error dialog appears, your new Scan Schedule was created sucessfully.
Clicking on "OK" will do the same, but will close "Scan Scheduler Editor"
afterwards. Clicking on "Close" will discard the schema you were
creating and will close the window.


Creating a new Scheduling Profile
---------------------------------

To create a new scheduling profile you need to set an unique name for
it, and a cron time format. UMIT comes with some scheduling profiles
for those that aren't familiar with cron.

After filling all the required fields, you may click on "Apply".
If no error dialog appears, your new Scheduling Profile was created
sucessfully. Clicking on "OK" will do the same, but will close
"Scheduling Profiles Editor" afterwards. Clicking on "Close" will discard
the profile you were creating and will close the window.

.. seealso::

   `Crontab, some more info
   <http://www.opengroup.org/onlinepubs/009695399/utilities/crontab.html>`_


Starting Scheduler
------------------

When you see a "red ball" in UMIT interface, it means the Scheduler
is stopped. Clicking on it will start the Scheduler, or will display a Warning
telling some advice, or an error message.


Starting Scheduler as root
^^^^^^^^^^^^^^^^^^^^^^^^^^

To start the Scheduler as root you have some options, some will be described
here. First option, and not the best, would be running UMIT as root, so when
you start the Scheduler it will be started as root.

**If you run umit as root, it will use root's config files!** [*]_

The second option is "harder" to do, but better. You need to open a
terminal, and use sudo or any other tool that can preserve environment. The
command will be like this::

   sudo umit_scheduler.py start

And the Scheduler will start.

To stop it later, you may do::

   sudo umit_scheduler.py stop

umit_scheduler.py is installed in the same directory as umit, so
it should be on your path already.

.. [*] UMIT keeps config files for each user that runs it. If you always use
       it as a user called 'john', for example, your config files will be
       inside, for example, /home/john/.umit. So, when you run it as root, it
       uses /root/.umit, and 'john' doesn't see the changes in root
       files, neither root sees changes in john's files (usually).

If you want to start the Scheduler with root and tell it to use someone
else UMIT config files, you may do so. The final command will be like this::

   umit_scheduler.py start /home/john/.umit

   umit_scheduler.py stop /home/john/.umit

If you want to start Scheduler at system startup, you will have to write that
path you especified (/home/john/.umit) inside umit_scheduler.py in a var
called CONFIG_DIR.


Stopping Scheduler
------------------

When you see a "green ball" in UMIT interface, it means the Scheduler
is running. Clicking on it will stop Scheduler, except in the case you do not
have permission to stop it, then a Warning will be shown. If you are on
Windows, the possible cause for not being able to stop the Scheduler is
because you did not run UMIT as administrator.
