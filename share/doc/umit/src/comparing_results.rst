Comparing Results
=================

.. sectionauthor:: Adriano Monteiro Marques


Introduction
------------

The Compare Results Window, is a tool that allows you to compare two
distinct scan results, highlighting any difference that may occour between
one to another in a easy to read manner. This feature is intended to let you
compare two given scans, let's say one made in the morning and other made in
the evening, and not if in the mean time a given host has left the network,
or if a given host is still serving on the same port as in the morning,
for example. It can be really usefull for network administrators, as with
regular scans of it's network can be compared to show abnormalities.


Openning Instructions
---------------------

To reach the Compare Results Window, make sure that Umit Network Scanner is open, 
and then do one of  the following:

   1. **Use the key-stroke**

      * The key-stroke that shows the Compare Results Window is CTRL + D.

   2. **Access from the Main Menu**

      * Go to the *Main Menu* (the one on the top of the application),
        Tools->Compare Results.


Loaded/Loading Results
----------------------

To avoid too much user interaction, and usability problems, Umit Network Scanner
automatically make available at the *Compare Results Window* combo boxes,
the scan results currently loaded in the main interface. As you may have
already noted, scans are loaded separatedly inside scan tabs, that are
describe with a title that may be the scan result file name, a combination
of the Profile Name + Target used in the scan or something else. Thoose scan
tabs titles, are used as identifiers that loads the respective scan result for
comparison when selected at those combo boxes.

If one or both of the scan results that you wish to compare are not loaded in
Umit Network Scanner's main interface, you can compare then by loading then 
inside the *Compare Results Window* without the need of closing the window, 
loading the results into scan tabs, and then openning the 
*Compare Results Window* again. To load then directly, use the Open button 
that resides on the right of each combo box.

You may also want to compare results that are not saved into files, but inside
the Umit Network Scanner's search data base. To load those results, you'll 
have to load then into scan tabs first, and then open the *Compare Results Window* 
to compare them. It's a bit cumbersome, but loading then directly from the
*Compare Results Window* would implicate on creating more widgets inside
the window and making it more complex, thus lowing it's usability anyway.


Comparing Results
-----------------

To quickly start comparing two given resuls, simply select the results you
wish to compare at the *"Scan Result 1"* and *"Scan Result 2"* combo boxes.
The only thing you should pay attention while selecting the scan results, is
that the comparison is done by highlighting what has changed (or is not
present) in the second result when compared to the first one. So, if you
change the order of the scan results selection, you'll end up with a
different comparison result, that probably won't show what you're looking for.

If you just want to compare changes on your network, a simple rule that
won't let you get in trouble always select the older result first, and then
the newest one. By following this, you'll get a comparison that shows which
hosts has left your network in the mean time, or, which ports appeared or
disappeared, etc. By selecting the newest one first, you'll have a not so
usefull comparison.

Let's say that you have two different scans loaded in Umit Network Scanner, and 
you wish to compare then. The first one, called *"Quick Scan on 192.168.204.128"* 
is a scan result made 2 days ago, and the second one, called
*"Regular Scan on 192.168.204.128"* is a just finished scan result. The goal
is to verify if something has changed during this 2 days, like if a service
has been put up, or down in the mean while.

Having those scans already loaded, simply open the *Compare Results Window*,
by following `Opening Instructions` mentioned in the beginning. Doing so,
you'll end up with a window like this:

   .. image:: static/comparing_results1.png
      :align: center

The screenshot above shows the appearance of the *Compare Results Window*
running the *"Compare Mode"*  just after it's openning.

At *Scan Result 1* combo box, select *"Quick Scan on 192.168.204.128"*
and at *Scan Result 2* select *"Regular Scan on 192.168.204.128"*.
In the moment you finish the selection of the results you want to compare,
Umit Network Scanner detects your choices and generates automatically 
the comparison result.

   .. image:: static/comparing_results2.png
      :align: center

The *Compare Results Window* with selected results and the comparison
generated automatically by Umit Network Scanner.

   .. image:: static/comparing_results3.png
      :align: center

The same window, now showing the *"Text mode"* comparison result.


The Text Diff Mode
------------------

If you're an old Umit Network Scanner user, you won't be surprised with the text 
mode. But maybe, if you are a new user, you will probably be questionning why
there is a *"Text mode"*, if you've got the *"Compare mode"*, that is easier
to read and understand. Here goes the answer: The *"Text mode"* is the first
comparison mode, and it's quite useful in some situations. If you simply
want to visually compare two different scans, the *"Compare mode"* is just
what you need. But, if you need to report changes and save them for historical
purposes, the *"Text mode"* will generate for you a text diff that can be
copied and pasted anywhere. This mode is not so complete as the
*"Compare mode"*, but it's the only one that you can save for latter analysis.
In the future, Umit Network Scanner will feature a report generation tool, 
to ease this task.


Reading and Understanding
^^^^^^^^^^^^^^^^^^^^^^^^^

The text diff is basically the first result plus extra lines that describes
what is missing or what has changed in the second one. Those extra lines are
marked up with symbols that describes what happenned in that part of the text
result.

.. table:: Text diff symbols and their meanings

   +--------+--------------------------------------------------------------+
   | Symbol | Meaning                                                      |
   +========+==============================================================+
   | \+     | The line has appeared/changed in the second result.          |
   +--------+--------------------------------------------------------------+
   | \-     | The line was removed/changed from the first result.          |
   +--------+--------------------------------------------------------------+
   | ?      | Indicates that this line contains symbols that show what was |
   |        | modified in the line above.                                  |
   +--------+--------------------------------------------------------------+
   | ^      | Indicates what was modified in the line above.               |
   +--------+--------------------------------------------------------------+


Changing colors
^^^^^^^^^^^^^^^

If you like the colored highlight mode, you may want to change the colors to
those which you may feel better with, or that may show better in a given
situation. Doing so, is quite easy and every change is automatically saved,
so you'll won't have to worry about changing the colors everytime you use
this window.

Click once on the *Color Descriptions* button. The folowing dialog will show
up:

   .. image:: static/comparing_results4.png
      :align: center

If you're running the *"Text mode"*, there is only two colors that you may
want to change here (as this mode only uses two). Those colors are described
as *Property was Added* and *Property is Not Present*. Click once in the
button that holds the current color you want to change, and a color selection
dialog will be shown.

The colors will be automatically updated as soon as you leave the
*Color Descriptions* dialog.


The Comparison Mode
-------------------

Yet the best comparison mode for quick verification of changes betwen results,
this mode shows informations that doesn't exist in the regular nmap output.
Thus, this mode gives you more informations than the text one.


Reading and Understanding
^^^^^^^^^^^^^^^^^^^^^^^^^

Reading and understanding this mode is easy and intuitive, as it shows only one
information (or property) per line, and the symbol before each property
describes it's state in the second result. If you have the colored highlight
mode enabled, you'll have a more intuitive experience, as you won't have to
bother about understanding those symbols.

Here follows a list of symbols, followed by their meannings:

.. table:: Compare mode symbols and their meanings

   +--------+-----------------------------------------------------------+
   | Symbol | Meaning                                                   |
   +========+===========================================================+
   | U      | The property remained  *U* nchanged in the second result. |
   +--------+-----------------------------------------------------------+
   | A      | The property was  *A* dded in the second result.          |
   +--------+-----------------------------------------------------------+
   | M      | The property was *M* odified in the second result.        |
   +--------+-----------------------------------------------------------+
   | N      | The property is *N* ot present in the second result.      |
   +--------+-----------------------------------------------------------+


Changing colors
^^^^^^^^^^^^^^^

If you like the colored highlight mode, you may want to change the colors to
those which you may feel better with, or that may show better in a given
situation. Doing so, is quite easy and every change is automatically saved,
so you'll won't have to worry about changing the colors everytime you use this
window.

Click once on the *Color Descriptions* button. The folowing dialog will show
up:

   .. image:: static/comparing_results4.png
      :align: center

If you're running the *"Compare mode"*, you can change any color that you
feel like, by clicking in the button that holds the color you wish to change,
and they will be update as soon as you leave the *Color Descriptions* dialog.



Openning in Browser
-------------------

If you want to generate a quick HTML report of the generated diff, and view
in your default web browser, just click once in the *Open in Browser* button.
The HTML report holds another diff visualization mode, followed by the text
one. After openned in the browser, you can simply save it for latter view,
or historical purposes, if needed.


Known issues
^^^^^^^^^^^^

There's a bug that avoids the use of this feature when Umit Network Scanner is 
been executed with *sudo* in Linux.
