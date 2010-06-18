SMTP Setup
==========

.. sectionauthor:: Guilherme Polo <ggpolo@gmail.com>


Introduction
------------

The "SMTP Setup" window is the place where you set up SMTP Accounts
to be used within Scheduler.


Setting up a SMTP Accout
------------------------

When you open the "SMTP Setup" window, you will see some fields to be
filled. The fields are: Schema name, Server, Port, Mail from, Username and
Password. There are also two options: "Server requires authentication" and
"Use TLS Encryption".

.. table:: Fields explanation

   +-------------+------------------------------------------------------+
   | Field       | Meaning                                              |
   +=============+======================================================+
   | Schema name | Defines an unique name for the SMTP Account that is  |
   |             | being created, you may name it like "local server",  |
   |             | "someone smtp", and etc.                             |
   +-------------+------------------------------------------------------+
   | Server      | Defines the smtp server that will be used.           |
   +-------------+------------------------------------------------------+
   | Port        | Define what port the server uses, the standard smtp  |
   |             | port is 25.                                          |
   +-------------+------------------------------------------------------+
   | Mail from   | Defines from whom emails will be sent when using the |
   |             | SMTP schema in Scheduler.                            |
   +-------------+------------------------------------------------------+
   | Username    | Username to be used for server authentication.       |
   +-------------+------------------------------------------------------+
   | Password    | Password for username to be used for server          |
   |             | authentication.                                      |
   +-------------+------------------------------------------------------+

If your server requires authentication, you need to toggle the
"Server requires authentication" option, and, if your server requires
TLS Encryption (gmail for example) you need to toggle "Use TLS Encryption"
option.

After filling all the required fields, you may click on "Apply".
If no error dialog appears, your new SMTP schema is created and you
may use it in withing Scheduler now. Clicking on "OK" will do the same,
but will close "SMTP Account Editor" afterwards. Clicking on "Close" will
discard the schema you were creating and will close the window.
