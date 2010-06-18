Plugins
=================

.. sectionauthor:: Francesco Piccinno

.. warning::

   This documentation is not finished! Part or all of it's content may be
   missing or inaccurate. As Umit is under constant development and
   improvement, expect changes in this documentation at upcoming releases.

Introduction
------------

Plugins are useful to implement indipendent features that could help the user
to customize the UMIT experience.

From the Plugin Window you could manage UMIT plugins. The window is divided in
two sections the *Extensions* and *Path* view.

Extensions View
---------------

In the Extensions view you could see a list of available plugins.

   .. image:: static/plugins_extensionsview.png
      :align: center

Supported actions are:

   +-----------+-----------------------------------------------------------+
   | Action    | Requirement                                               |
   +===========+===========================================================+
   | Uninstall | This action requires write access to the plugin file and  |
   |           | respective directory.                                     |
   +-----------+-----------------------------------------------------------+
   | Update    | This action requires write access to the plugin file and  |
   |           | respective directory.                                     |
   +-----------+-----------------------------------------------------------+
   | Enable    | None                                                      |
   +-----------+-----------------------------------------------------------+
   | Disable   | None                                                      |
   +-----------+-----------------------------------------------------------+

Additional actions:

   +-------------+-----------------------------------------------------------+
   | Action      |                                                           |
   +=============+===========================================================+
   | Preferences | If a plugin provides a sort of configuration this action  |
   |             | will launch a preference window where you could change    |
   |             | the plugin behaviour.                                     |
   +-------------+-----------------------------------------------------------+
   | Visit       | Open a page in the default browser pointing to plugin     |
   | Homepage    | homepage.                                                 |
   +-------------+-----------------------------------------------------------+
   | About       | Shows an about dialog showing informations related to the |
   |             | selected plugin.                                          |
   +-------------+-----------------------------------------------------------+

Uninstall a plugin
^^^^^^^^^^^^^^^^^^

If you want to fully remove the plugin file from your hard disk than you could
choose the *Uninstall* action accessible from the context menu by right clicking
on the target plugin and by choosing *Uninstall* menu item.

In this case the ump file you have downloaded and placed in one of the Paths
enabled in the *Path View* will be deleted from your hard disk. Obviously you
need to have write access to that directory where the ump file is located.

Update a plugin
^^^^^^^^^^^^^^^

If a plugin provides an update field then UMIT plugin engine could check for
the presence of new versions of that plugin, and ask to the user if he wants to
update the plugin.

If you want to check for updates than you have to click to on *Find updates*
button on the bottom-right edge of the Plugin Manager window.

   .. image:: static/plugins_updatesnotfound.png
      :align: center

Enable a plugin
^^^^^^^^^^^^^^^

If you want to use a specific plugin that's on the list in the Plugin Manager
window than you have to click on the *Enable* button, or right click on it and
then choose *Enable* from the context menu.

Disable a plugin
^^^^^^^^^^^^^^^^

To disable a plugin like also enabling you have to click on the *Disable* button
or right click on the target plugin and then choose the *Disable* from the
context menu.


Paths View
----------

From Paths View you could add, remove, adjust paths were the UMIT plugins files
(!*.ump files) are located, so they will be presented in the Extensions View and
could be used.

   .. image:: static/plugins_pathview.png
      :align: center

Find and install new Plugins
----------------------------

You could take a look to the Plugin Index page accessible from 
http://trac.umitproject.org/wiki/Plugins

After having found your plugin you could download it and place under one of
Plugin Path directory, listed in the *Paths* View.

For example on *NIX system you could do::

   $ cd ~/.umit/plugins
   $ wget http://trac.umitproject.org/attachment/wiki/Plugins/throbberanimation.ump

And then you will see a ThrobberAnimation plugin in the *Extensions* View list.

Obviously you could simply place the the ump file in a directory and then add that
directory in the list of paths in the *Paths* View.
