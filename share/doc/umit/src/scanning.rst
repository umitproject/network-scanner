Scanning
========

.. sectionauthor:: Adriano Monteiro Marques

.. warning::

   This documentation is not finished! Part or all of it's content may be
   missing or inaccurate. As Umit is under constant development and
   improvement, expect changes in this documentation at upcoming releases.


Introduction
------------

Umit was designed to accomodate and run more than one scan at time. Each scan
is executed and shown inside a *Scan Tab*, which has a title and organize
every information obtained in the scan result.

The *Scan Tab* tries to facilitate your life, by making the unformations
easier to navigate and search for a given information. Usually, if you wanted
to scan an entire network using Nmap, you would have to open up your favorite
terminal, type an entire Nmap command, like this one::

   nmap -A -F -n -T4 192.168.1.1-254

and when it finally finishes you'll end up with a bunch of lines in the
terminal that can hardly be searched and read. If your goal was to know
which of the 200 hosts found are serving ssh, what were you going to do?
Maybe it won't seen impossible for you, (and it's not) but surely it's
a boring task that gets worst when you have to do that more than once.

An answer to your problem is Umit, that can handle this task easily, with
just a couple of clicks.

So, if you're wondering if you should retire the command line, I would say
**NO!**. The Nmap's command interface is very useful when you want to scan a
few hosts, and skim the result quickly to make a decision. Every good network
administrator know how useful is it to simply call::

   nmap localhost

to know which services are up, for example. If you're at the command line,
you won't want to open a graphical application to do so, if you can quickly
pull off your doubt about what is up or down from were you stand.

Umit is intended to help you manage your network, by giving you a better
way to examine carefully your network peers. If your intention is to
*know* better your network, then Umit is what you need.


Starting a scan
---------------

To start a scan, you need an empty *Scan Tab*. At the time you start
Umit, a new *Scan Tab* is made available, and as soon as the main interface
is shown, you can start typing the target address. If you already used this
*Scan Tab*, you can create a new one, by doing one of the following:

   1. **Use the key-stroke**

      * The key-stroke that creates a new Scan Tab is CTRL + T.

   2. **Single click on the Create new Scan Tab button Icon in the Main
      Toolbar**

      * The Create new Scan Tab button is the 1st button in the Main Toolbar
        from left to right.

   3. **Acces from the Main Menu**

      * Go to the *Main Menu* (the one on the top of the application),
        File->New Scan.


Setting a Target
----------------

By the moment you start Umit, or create a new scan tab, you can start typing
the address of the target(s) that you want to scan. Every target inserted into
the Target field is recorded and remembered in case you need it in the future.
As this field features an auto-completation, it's going to be easy the reuse of
targets.


Conducting a scan
-----------------

A profile is a set of options that is going to be used during the scan
process against the target(s) specified. Profiles are customizable through the
*Profile Editor Window*. After specifying a target, select one of the profiles
in the profile list, and watch the command in the field get changed according
to the profile selected. This is awesome if you always have to run a scan with
the same set of options. If you are a newbie, this is awesome too, because you
can use one of the preset profiles according to your need.

Sometimes we need to fine tune a specific profile for a specific occasion
that is not likely to occour very often. In this case, it is not a good idea to
create a new profile, or to change an existing one. After selecting a target
and a profile, you can customize the command that will actually run, by
editing it directly in the command field.

.. warning::

   There is a known issue regarding changing the command manually and then
   trying to change the target using the target entry. If you try to do that,
   you'll end losing the changes you've done manually.

After Selecting the proper target, profile and making your manual tunning,
you're ready to click the scan button. As the scanning takes a considerable
time to finish, Umit will keep refreshing the scan output so you can follow
the scan execution and status.


Known issues
^^^^^^^^^^^^

*Non-root user:* If you're running Umit with a non-root user in a Unix like
operating system, you're likely to face some problems while trying to execute
the scan with options that require root privilege. In this case, Umit will
return a message saying that the scan failed because you have used a option
that requires root privileges.


Making Umit useful enough for your every-day scanning
-----------------------------------------------------

You may still be asking yourself "Why shoul I use Umit, instead of Nmap in the
command line". To put it simple: Because time is money. Umit's main goal is to
help you save your time. Here are some goodies that helps you save your time
while having to analyse a scan result and get useful informations from it.


The Hosts/Services View
^^^^^^^^^^^^^^^^^^^^^^^

After running finishing the execution of a scan, you'll see two buttons at
the left side of the window, right bellow the command field in your scan tab:
*"Hosts"* and *"Services"*. Those buttons change the way you order and view
the scan results, by listing either the hosts found or the services found.

If you're looking for hosts, and then want to see what kind of services
these hosts are providing, then you should use the *Hosts button*, which is
selected by *default*. This mode will show a list all hosts found, with an
icon representing the operating system of the host (if it was recognized) and
its hostname (if resolved, or its IP address). From that list, you can select
one or more hosts, and see what services they're providing at the
*Ports/Hosts* tab.

If what you need is to find what hosts are providing a given service,
like *SSH*, for example, then you should use the *Services button*, which will
show a list of all services found during scan execution. By clicking in a
service in that list, you'll see what hosts are providing the selected service
in the *Ports/Hosts* tab.

Ordering is quite simple. Click on the header of the column you want to have
the results ordered, and the ordering sequence will change accordingly. You're
also allowed to move columns arround and change their precedence in the
listing.


The Ports/Hosts Tab
^^^^^^^^^^^^^^^^^^^

This tab holds either a listing of found ports, for the selected host(s) or
a listsing of found hosts, for the selected service(s). It all depends on which
visualization mode you're in. While in *Hosts* mode, you'll see a list of what
ports the selected host(s) are providing. If you select more than one host,
the listing will change from list to tree view mode, and you'll be able
to compare easily the different ports and services open among the selected
hosts.

If you're in *Services* mode, then you'll see a list of hosts providing the
selected service(s). If you selected more than one service, the listing
will change for list to tree view, and you'll be able to compare what hosts
are providing the selected services easily.


Nmap Output Tab
^^^^^^^^^^^^^^^

For those who are terminal addicted, there is the *Nmap Output* tab, which
shows the regular nmap output almost like everyone is used to see:
unparsed and plain text, but with colored highlights! So, even if you really
prefer the regular output, you still have a reason to use Umit instead of the
command line.

If you want to disable the highlight, click the check box right bellow the
Nmap output result. If you want to change the colors, click the
*Preferences* button, and customize it according to your taste.


Scan Details Tab
^^^^^^^^^^^^^^^^

The *Scan Details* tab holds some informations regarding the scan that you
won't find on regular nmap outputs. There you can find the command that has
generated that result, the date and time that the scan has started and
finished, a list of all scanned ports, etc.


Host Details Tab
^^^^^^^^^^^^^^^^

This tab shows details regarding the host you have selected in the host list,
while in *Host Mode*. The *Host Details* tab works the same way the
*Ports/Hosts* page, letting you select one or more hosts at a time and having
their details show at the same time there.

If you're in *Services Mode*, this tab will show the details of the hosts
that are providing the selected service.

If you want to save any commentary for a given host, just click the
*Comments* expander, and write the commentary inside the text input that
will appear. If you save the scan result, the commentary will be saved as
well.

Two of the coolest features of Umit are the *Operating System Icon* and the
*Vulnerability Level Icon*.

If the scan has recognized the host's operating system, then an Icon
representing the operating system is shown inside the host's detail. This
helps you easily figure out what operating system is running in a given host
in a glance.

The *Vulnerability Level Icon* represents graphically the level of
vulnerability of a given host, based in the number of open ports it have.

*We, at Umit, know that the amount of open ports isn't an accure way to
grade a host's vulnerability level, but at this time Umit doesn't feature a
better and more accurate meaning for detecting the host's vulnerabilitty
level.*

There are five vulnerability levels, represented by the following icons ordered
by the less vulnerable to the more vulnerable level: the *vault*,
the *chest*, the *box*, the *swiss cheese* and the *bomb*.
