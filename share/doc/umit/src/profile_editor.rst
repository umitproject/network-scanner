Profile Editor
==============

.. sectionauthor:: Adriano Monteiro Marques
.. sectionauthor:: Luís A. Bastião Silva

.. warning::

   This documentation is not finished! Part or all of it's content may be
   missing or inaccurate. As Umit is under constant development and
   improvement, expect changes in this documentation at upcoming releases.


Introduction
------------

Using Umit it's normal to use the same arguments or make repeated scans and
sometimes it's not easy to search for the same options of nmap again.

Profile Editor is able to create profiles. With it you should
be able to save the nmap arguments and run scans with some paramenters in the
future. 

Since Umit Network Scanner 1.0 it was included a manager of Profiles called ProfileManager.

What does it do?
^^^^^^^^^^^^^^^^

The customization advantage: It's easy to call a Profile.
In the tab scan you only choose the target, and select a Profile. It
will define automatically the Nmap parameters.


The profile editor modes
------------------------

* New profile: It's easy to create a new profile, you can define all Nmap
  parameters and save you a suggestive name.

* Edit profile: If you sometimes want to change the paramenters of profile,
  you should be use edit of profiles and add, or remove the parameters,
  checking it on the boxes.


Creating a simple scan profile
------------------------------

   .. image:: static/profile_editor_1.png
      :align: center

The screenshot above shows the Profile Editor.

1. **Use the key-stroke**

   * The key-stroke that creates a new Profile is CTRL + P

2. **Access from the Main Menu**

   * Go to the *Main Menu* (the one on the top of the application),
     Profile->New Profile.

3. **Access from the ProfileManager**
    
     1. Go to the *Profile Manager* (Profile>Profile Manager)
     
     2. Press in *New* button




The profile descriptions (name, hint, description, etc.)
There are some fields to fill about a Profile. It's mandatory fill the
name.

   +-------------+----------------------------------------------------------+
   | Field       | Description                                              |
   +=============+==========================================================+
   | Name        | It is the name that appears on combo box of **Scan Tab** |
   +-------------+----------------------------------------------------------+
   | Hint        | A tooltip.                                               |
   +-------------+----------------------------------------------------------+
   | Description | Tells what this profile does.                            |
   +-------------+----------------------------------------------------------+

You can browse on the tabs and apply option that you wish to build
a profile that you intend.

Just press Ok and you save the profile
How to use the recently created profile?
You can find recently profile created on Combo box in Scan tab. So just fill
the target, select profile and press scan. The option of your new profile are
running on the scan.


Editing a profile
-----------------

1. **Use the key-stroke**

   * The key-stroke Edit Profile is CTRL + E

2. **Access from the Main Menu**

   * Go to the *Main Menu* (the one on the top of the application),
     Profile->Edit Profile.

3. **Access from ProfileManager**

    1. Go to the *Profile Manager* (Profile>Profile Manager)
     
    2. Select profile you intend to change 

    3. Press in *Edit* button


Creating a new profile based on an old one
------------------------------------------

This option is like copy a profile. If you have a Profile and you can create
a similar Profile, use it.

1. **Use the key-stroke**

   * In combo Box of Scan Tab select a profile. The key-stroke create
     Profile is CTRL + R

2. **Acces from the Main Menu**

   * Select Profile in combo box of Scan tab and go to the *Main Menu*
     (the one on the top of the application), Profile->New Profile with Selected

3. **Access from the Profile Manager**
   
    1.  Go to the *Profile Manager* (Profile>Profile Manager)

    2. Select profile intended to copy

    3. Press in *Copy* button. 

    4. It will ask to another name. Then you are able to edit the copy's profile.



Deleting Profiles
-----------------

If you want delete a Profile by some reason it is possible. Follow one of the
procedures below.

1. **Acces from the Main Menu**

   * Select Profile in combo box of Scan tab and go to the *Main Menu*
     (the one on the top of the application), Profile->Delete Profile

2. **Using ProfileManager**

    1.  Go to the *Profile Manager* (Profile>Profile Manager)

    2. Select profile intended to remove

    3. Press the *Delete* button


Profile Manager
-----------------------------

The *Profile Manager* is able to create, edit and delete new profiles as we explain above.

   .. image:: static/profile_manager.png
      :align: center



The profile editor structure
-----------------------------

Where are the options saved? See :ref:`UMIT_CFG_DIR` for the place
where all configuration files are stored. The files related to the profile
editor are options.xml and profile_editor.xml.

The widgets available for options is combo box, checkbox and text
entry. We have the box with numbers (for example, number of ports) to
use as parameter.


