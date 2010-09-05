Under Umit's Roof
=================

.. sectionauthor:: Adriano Monteiro Marques
.. sectionauthor:: Guilherme Polo <ggpolo@gmail.com>

.. warning::

   This documentation is not finished! Part or all of it's content may be
   missing or inaccurate. As Umit Network Scanner is under constant development
   and improvement, expect changes in this documentation at upcoming releases.


.. _UMIT_CFG_DIR:

Configuration Files
-------------------

Umit Network Scanner will always try to create a $HOME/.umit configuration 
directory if it doesn't exists yet, under UNIX. Under Windows it will try to a 
configuration directory named umit under user's local application data. 
We call this configuration directory as UMIT_CFG_DIR.

The steps bellow, describes how Umit Network Scanner is going to behave on every
startup in order to load the configuration files:

   1. Check if the location of the hardcoded paths does exist

   2. Check if UMIT_CFG_DIR does exist

   3. If UMIT_CFG_DIR does exist, than check the version of the files

   4. If the version of the files is older than the current Umit
      version, update the config files

   5. If UMIT_CFG_DIR doesn't exist, tries to create one

   6. If it is not possible to create the UMIT_CFG_DIR, then Umit will
      use the factory-made files


Checking out the Repository
---------------------------

Install the subversion client, and then run the command bellow::

   svn co https://umit.svn.sourceforge.net/svnroot/umit


Easter Eggs
-----------

Yes, there are easter eggs in Umit Network Scanner. Go find them!
