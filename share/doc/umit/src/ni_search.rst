UMIT Network Inventory - Search
===============================

.. sectionauthor:: Guilherme Polo <ggpolo@gmail.com>


Introduction
------------

The Network Inventory search system is designed to find devices
in Inventories. It searches based on Ports, Services, Changes that happened,
IP address, MAC, Hostname, OS Match, OS Classes and Fingerprint info.


Performing a search
-------------------

To search for something, just enter your search terms in the bar placed
on the top of Network Inventory and hit *Enter* or click on the
icon search. But note that in order to achieve better results it is important
to follow the rules described below.

To find devices based on port, your query should be similar to: port 80.
This will search for devices containing the port 80 in its results
(in any state). If you want to search for devices containing only ports
higher than 1024, you could do: port : 1024.
The port syntax allows you to the following operators: '>', '<', '==', '!=',
'>=', '<='. But at this point you can't use more than one at once.

To find devices based on service, the query should looks like this:
service apache. And will search for a service with that name.

To find devices based on some change, you should search for something
like this: change somechangetext.

To search based on things like hostname, ip, and others, just
type the text. Searching devices by a valid ip is the fastest way to find
them right now.

Bugs
----

As your scan number grows in your Inventories, you will feel the
pain when trying to search for devices. Also, you may get angry when
you notice the search system is not really smart.
