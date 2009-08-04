Plugins Architecture
====================

.. sectionauthor:: Francesco Piccinno

.. warning::

   This documentation is not finished! Part or all of it's content may be
   missing or inaccurate. As Umit is under constant development and
   improvement, expect changes in this documentation at upcoming releases.

Introduction
------------

This is an brief description of the UMIT Plugin System architecture.

Plugin Format
-------------

UMIT handles ``.ump`` plugins files. These are essentially zip files.

We have choose this approach to simplify the distribute phase and to avoid band overhead, and simplify the entire
installation process.

The UMIT plugin system supports python source code files (.py files),
precompiled python source code files (.pyo or .pyc files), c python modules
(.so or .pyd files).

A plugin have a simple directory tree structure containing:

- ``bin/`` containing the source files (``.py`` | ``.pyo`` | ``.pyc`` | ``.so`` | ``.pyd`` files). Required.
- ``lib/`` containing various libraries (``.py`` | ``.pyo`` | ``.pyc`` | ``.so`` | ``.pyd`` files) used by the plugin. This is optional.
- ``data/`` containing dist files like the logo image, default configurations files, etc. This is optional.
- ``locale/`` containing locale files (``.mo`` and related stuff). This is optional.

The plugin archive needs to provide also various files:

- a ``Manifest.xml`` on the root directory containing meta-informations. Required.
- a `data/logo.png`` file that's the image will be presented as logo for the plugin in the Plugin Manager window. This is optional.

.. _manifest-file:

Manifest File
-------------

The entire plugin system is based on the ``Manifest.xml`` file previously introduceed. This file is responsible to provide information to the Plugin Engine. These information are provided trough an xml file.

You could add you custom elements to the xml file but someone are reserved by UMIT Plugin system (Elements marked with * could compare several times in the Manifest file):

   +---------------------+---------------------------------------------------------------------+
   | /UmitPlugin         | Description                                                         |
   +=====================+=====================================================================+
   | ``<name>``          | A string representing the plugin name.                              |
   +---------------------+---------------------------------------------------------------------+
   | ``<version>``       | A string represetnting the plugin version.                          |
   +---------------------+---------------------------------------------------------------------+
   | ``<description>``   | A string containing a description of the plugin.                    |
   +---------------------+---------------------------------------------------------------------+
   | ``<url>``           | A URI string pointing to the target plugins homepage.               |
   +---------------------+---------------------------------------------------------------------+
   | ``<runtime>``       | Required.                                                           |
   +---------------------+---------------------------------------------------------------------+
   | ``<deptree>``       | Optional.                                                           |
   +---------------------+---------------------------------------------------------------------+
   | ``<credits>``       | Required.                                                           |
   +---------------------+---------------------------------------------------------------------+

``<runtime>`` description:

   +---------------------+---------------------------------------------------------------------+
   | /UmitPlugin/runtime | Description                                                         |
   +=====================+=====================================================================+
   | ``<start_file>``    | A string pointing to the main file in ``bin/`` directory.           |
   +---------------------+---------------------------------------------------------------------+
   | ``<update>`` *      | A URI string pointing to the target plugins update remote location. |
   |                     | In a manifest you could provide multiple ``<update>`` elements for  |
   |                     | mirroring reasons. Optional.                                        |
   +---------------------+---------------------------------------------------------------------+

``<deptree>`` description (all elements are optional here):

   +---------------------+---------------------------------------------------------------------+
   | /UmitPlugin/deptree | Description                                                         |
   +=====================+=====================================================================+
   | ``<provide>`` *     | A ``VersionString`` that describes what the target plugin provides  |
   |                     | to the others. Example ``=ftplib-1.0`` or ``=trayicon-2.0``.        |
   +---------------------+---------------------------------------------------------------------+
   | ``<need>`` *        | A ``VersionString`` of a needed virtual plugin that must be loaded  |
   |                     | in order to enable the target plugin.                               |
   +---------------------+---------------------------------------------------------------------+
   | ``<conflict>`` *    | A ``VersionString`` of a conflicting virtual plugin that must be    |
   |                     | **NOT** loaded in order to enable the target plugin.                |
   +---------------------+---------------------------------------------------------------------+

``credits`` description:

   +---------------------+---------------------------------------------------------------------+
   | /UmitPlugin/credits | Description                                                         |
   +=====================+=====================================================================+
   | ``<license>`` *     | A string representing the license used for the plugin.              |
   +---------------------+---------------------------------------------------------------------+
   | ``<copyright>`` *   | A string representing the copyright information for plugin.         |
   +---------------------+---------------------------------------------------------------------+
   | ``<author>`` *      | A string representing a plugin's author.                            |
   +---------------------+---------------------------------------------------------------------+
   | ``<contributor>`` * | A string representing a plugin's contributor. Optional.             |
   +---------------------+---------------------------------------------------------------------+
   | ``<translator>`` *  | A string representing a plugin's translator. Optional.              |
   +---------------------+---------------------------------------------------------------------+
   | ``<artist>`` *      | A string representing a plugin's artist. Optional.                  |
   +---------------------+---------------------------------------------------------------------+


UmitPlugin element could have also an attribute called type to indicate if the plugin is a UI addition or just a library. You could have respectively ``<UmitPlugin .. type="ui">`` or ``<UmitPlugin .. type="lib">``.

Following an example of a Manifest.xml::

    <?xml version="1.0" encoding="utf-8"?>
    <UmitPlugin xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.umitproject.org" xsi:schemaLocation="http://www.umitproject.org UmitPlugins.xsd" type="ui">
      <name>SystemInfo</name>
      <version>0.1</version>
      <description>A plugin that provides info about the system</description>
      <url>http://blog.archpwn.org</url>
      <runtime>
        <start_file>main</start_file>
        <update>http://localhost/mia/</update>
        <update>http://localhost/</update>
      </runtime>
      <deptree>
        <provide>&gt;=SystemInfo-1.0</provide>
      </deptree>
      <credits>
        <license>GPL</license>
        <copyright>(C) 2009 Adriano Monteiro Marques</copyright>
        <author>Francesco Piccinno</author>
      </credits>
    </UmitPlugin>

Version String
^^^^^^^^^^^^^^

Elements like ``<need>`` , ``<conflict>`` , ``<provide>`` are ``VersionString`` elements.

EBNF/regex form for op and *non-operator* ``VersionString`` is::

    Op version string := <operator><name><version>

    <operator> := '<' | '<=' | '>' | '>=' | '=' | '!'
    <name> := [a-zA-Z0-9]{1,}
    <version> := '-' (\d\.?){1,3}

    Non-op version string := <name><version>

    <name> := [a-zA-Z0-9]{1,}
    <version> := '-' (\d\.?){1,3}

Examples of ``VersionStrings`` are:

- >dummy-1.0
- <=woot-2.2.3

Examples of *non-operator* ``VersionStrings`` are:

- foobar-3.0
- foofoo-2.2.1


Web Update Process
------------------

If a plugin provides the ``<update>`` field UMIT will try to contact that URL to manage the update.

For example if we have a plugin with ``<update>`` element in Manifest.xml file setted to ``http://www.umitproject.org/plugins/dummy/`` then UMIT will try to get a ``latest.xml`` file from this location ``http://www.umitproject.org/plugins/dummy/latest.xml``.

The ``latest.xml`` file contains information regarding the update process. It's a plain XML file containing fixed elements:

   +--------------------+-------------------------------------------------------+
   | /UmitPluginUpdate  | Description                                           |
   +====================+=======================================================+
   | ``<version>``      | A *non-operative* ``VersionString`` like for Manifest.|
   +--------------------+-------------------------------------------------------+
   | ``<desciption>``   | A string representing a description of the update or  |
   |                    | a changelog. Optional.                                |
   +--------------------+-------------------------------------------------------+
   | ``<url>`` *        | A string (URL) pointing to the new version of the     |
   |                    | plugin.                                               |
   +--------------------+-------------------------------------------------------+
   | ``<integrity>`` *  | This element is optional and could compare several    |
   |                    | times. You have to set also ``<type>`` and            |
   |                    | ``value`` attribute. Example:                         |
   |                    | ``<integrity type="sha1" value="yourhexdigest"/>``    |
   +--------------------+-------------------------------------------------------+

An example of the ``latest.xml`` follows::

    <UmitPluginUpdate xmlns="http://www.umitproject.org" xsi:schemaLocation="http://www.umitproject.org UmitPlugins.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <update>
            <version>2.0</version>
            <description>Don't use this is only there for testing.</description>
            <url>http://localhost/test.ump</url>
        </update>
        <update>
            <version>0.1</version>
            <description>&lt;tt&gt;Changelog:
    &lt;b&gt;* Version 1.0&lt;/b&gt;:
    - Fixed blah
    - Fixed blah
    - Fixed blah
    - Fixed blah&lt;/tt&gt;</description>
            <url>http://localhost/system.ump</url>
            <integrity type="md5" value="d488cbec9b6a3de7de1502ab962a907a"/>
            <integrity type="sha1" value="1851a284568c2fa5fab81384559a3e945b1f2744"/>
        </update>
    </UmitPluginUpdate>

API Reference
=============

.. sectionauthor:: Francesco Piccinno

.. warning::

   This documentation is not finished! Part or all of it's content may be
   missing or inaccurate. As Umit is under constant development and
   improvement, expect changes in this documentation at upcoming releases.

Core Class
----------

.. class:: Core()

   The :class:`Core` object, is a singleton :class:`GObject` instance. It's accesible under ``umit/plugin/Core.py`` or with UmitConsole plugin:

      .. image:: static/plugins_dev_api_core_umitshell.png
         :align: center

   This is the central object that makes possible the communication with UMIT. It provides various signals, functions and getters.


:class:`Core` instance have the following signals:


.. method:: Core.connect("ScanNotebookPage-created", callback)

   This signal is emitted when a :class:`ScanNotebookPage` is created.
   
   This happens for example when the user click on the *New Scan* button in the toolbar.
   
   The callback should be in the form of:
   
   .. function:: callback(core, scannotebookpage)

.. method:: Core.connect("ScanResultNotebook-created", callback)

   This signal is emitted when a :class:`ScanResultNotebook` is created.
   
   This object is created in the :class:`ScanNotebookPage` constructor, and the signals emitted when the object construction is complete. Useful to add new custom tabs.
   
   The callback should be in the form of:
   
   .. function:: callback(core, scanresult)

.. method:: Core.connect("ScanHostsView-created", callback)

   This signal is emitted when a ScanHostView is created.
   
   This object, like the :class:`ScanResultNotebook` is created in the :class:`ScanNotebookPage` constructor, and the signals emitted when the object construction is complete.
   
   The callback should be in the form of:
   
   .. function:: callback(core, scanhostview)

To well understand the context take a look at this image:

   .. image:: static/plugins_dev_ui_structure.png
      :align: center


:class:`Core` instance have the following methods:


.. method:: Core.get_main_toolbar()

   That returns the :class:`gtk.Toolbar` of the UMIT's :class:`MainWindow`.

.. method:: Core.get_main_menu()

   That returns the :class:`gtk.Menu` of the UMIT's :class:`MainWindow`.

.. method:: Core.get_main_scan_notebook()

   That returns the :class:`ScanNotebook` of the UMIT's :class:`MainWindow`.

.. method:: Core.open_url(link)

   That opens the default browser at *link* location.

.. method:: Core.get_need(reader, needstr, [classname=None, need_module=False])

   That returns an instance of the class *classname* (optional) of the plugin that provides *needstr* or the respective module if *need_module* is True, or None on error.
   
   For example taking a look to the setup.py of Notifier plugin we could see that the autogenerated ``Manifest.xml`` will have the ``<need>`` element set to ``>=tray-2.0``. Assuming that we have already loaded the TrayPlugin that's taking care of providing ``=tray-2.0`` in his ``<provide>`` element in the Manifest file, we will have something like that::

        DEBUG - 2009-04-25 11:26:35,422 - >>> Core.get_need() -> [<main.TrayPlugin object at 0xa4c986c>] (module: False)
        DEBUG - 2009-04-25 11:26:35,422 - >>> Core.get_need(): No classname specified. Returning first instance

   This is due to that lines in the ``main.py`` ``start_file`` of the Notifier plugin::

        class Notifier(Plugin):
            def start(self, reader):
                self.reader = reader
                self.tray = Core().get_need(self.reader, 'tray')

   Now the :attr:`self.tray` attribute will be something like ``<main.TrayPlugin object at 0xa4c986c>``.
   This object is exported by the ``start_file`` of TrayPlugin with::
   
        class TrayPlugin(Plugin):
            ....
        __plugins__ = [TrayPlugin]
   
   and will be the instance of the :class:`TrayPlugin` class loaded by the plugin system.

PluginReader Class
------------------

.. class:: PluginReader()

:class:`PluginReader` instance have the following methods:

.. method:: PluginReader.get_logo([w=64, h=64])

   Return a :class:`gtk.gdk.Pixbuf` instance of the plugin logo.
   Use *w* to resize the width of the pixbuf, and *h* for the height.

.. method:: PluginReader.get_path()

   Return a string representing the full path to the ump plugin file.

.. method:: PluginReader.extract_dir(zip_path, [maxdepth=0])

   Extract the files contained in the directory passed with *zip_path* argument.
   Use *maxdepth* to limit the recursion limit of the extraction process (0 will do a fully recursive extraction).

   Return a list containing the full path of the files extracted. 

.. method:: PluginReader.extract_file(zip_path, [keep_path=False])

   Extract file accessible with *zip_path* in the ump file.
   Set *keep_path* to `True` if you want to mantain the original paths in the ump file also after the extraction.

   Return a string representing the full path of extracted file.

.. method:: PluginReader.bind_translation(modfile)

   Use this method if you have a localized plugin. This methods takes care to find the correct `.mo` *modfile* file
   inside `locale/` directory and returns a `gettext.GNUTranslations` instance that could be used to support i18n in your plugin.

   Take a look to :ref:`localized-plugin` section for additional information.


ScanNotebookPage Class
----------------------

.. class:: ScanNotebookPage()

:class:`ScanNotebookPage` instance have the following signals:

.. method:: ScanNotebookPage.connect("scan-finished", callback)

   This signal is emitted when a scan finish. The plugin have to check the status of the scan. It's not assured that the scans terminates correctly. To check the status of the scan see also :attr:`ScanNotebookPage.status`.
   
   The callback should be in the form of:
   
   .. function:: callback(core, scannotebookpage)

:class:`ScanNotebookPage` instance have the following methods:

.. method:: ScanNotebookPage.get_tab_label()

   Return the title of the current scan.

.. method:: ScanNotebookPage.set_tab_label(label)

   Set the title of the current scan to *label*.

.. method:: ScanNotebookPage.close_tab()

   Close the current scan.

:class:`ScanNotebookPage` instance have the following attributes:

.. attribute:: ScanNotebookPage.status

   :class:`PageStatus` instance representing the status of the scan.

.. attribute:: ScanNotebookPage.changes

   A :ctype:`bool` setted to True if the the current Scan has unsaved changes.

.. attribute:: ScanNotebookPage.comments

   A :ctype:`dict` object.

.. attribute:: ScanNotebookPage.hosts

   A :ctype:`dict` object.

.. attribute:: ScanNotebookPage.services

   A :ctype:`dict` object.

.. attribute:: ScanNotebookPage.parsed

   A :class:`NmapParser` instance.

.. attribute:: ScanNotebookPage.top_box

   A :class:`HIGVBox` instance.

.. attribute:: ScanNotebookPage.saved

   A :ctype:`bool` setted to True if the the current Scan is saved.

.. attribute:: ScanNotebookPage.saved_filename

   A :ctype:`str` setted representing the filename of the scan.

.. attribute:: ScanNotebookPage.scan_result

   A :class:`ScanResult` instance.

.. attribute:: ScanNotebookPage.host_view_selection

   The :class:`gtk.TreeSelection` of :attr:`ScanHostsView.host_view`.

.. attribute:: ScanNotebookPage.service_view_selection

   The :class:`gtk.TreeSelection` of :attr:`ScanHostsView.service_view`.

.. attribute:: ScanNotebookPage.toolbar

   A :class:`ScanToolbar` instance.

.. attribute:: ScanNotebookPage.empty_target

   A :ctype:`str` representing an empty target (The value could change because it's a gettext string. With ``LANG=C`` the value is ``<target>``).

.. attribute:: ScanNotebookPage.command_toolbar

   A :class:`ScanCommandToolbar` instance.

ScanResultNotebook Class
------------------------

ScanHostsView Class
-------------------

Tutorial
========

This is a short tutorial describing how to create a simple UMIT plugin.

First Tutorial
--------------

First we have to create a clean directory for our stuff. For simplicity we'll call ``helloworld``. So from console (or from your favourite file manager if you prefer) let's create our dir::

    $ pwd
    /home/stack/umit/source-plugins
    $ mkdir helloworld
    $ cd helloworld/

Directory Schema
^^^^^^^^^^^^^^^^

Now we have to think to our directory schema. We could assume the standard approach and store the sources files in the ``sources/`` directory while the data files in ``dist/`` directory::

    $ mkdir dist
    $ mkdir sources

The directory named ``dist/`` will contains also our logo.png file (a PNG file of 128x128 px). This will showed in the Umit Plugin window, so add there your favourite logo for your ``helloworld`` plugin.

Now let's code!

Start file
^^^^^^^^^^

We have to create a "start file" (see also ``<start-file>`` element in :ref:`manifest-file` section) that will be our main and called for plugin initialization. This file should contains at least one class that overloads the base Plugin class, and this class should be listed in ``__plugins__`` attribute::

    $ touch sources/main.py

Now let's edit our ``sources/main.py`` file with a text editor::

    from hello.italian import ciao, addio
    from umitPlugin.Engine import Plugin

    class HelloWorldPlugin(Plugin):
        def start(self, reader):
            print "Hello world!!!"
            ciao()

        def stop(self):
            print "Good bye world!"
            addio()
            
    __plugins__ = [HelloWorldPlugin]

This file simply create a class that overloads the Plugin base class (``umit.plugin.Engine.Plugin``) and export that with the ``__plugins__`` attribute. Of course we could have multiple plugins classes in a single ump file.

Let's explain the methods:

- The :meth:`start()` method is called on plugin initialization. It receives a :class:`PluginReader` instance for the *reader* argument. This object represent the ump file that contains the ``HelloWorldPlugin`` plugin, and permits various operation like the extraction of files, etc.


- The :meth:`stop()` method is called on plugin deinitialization and it's like a destructor.

Packages
^^^^^^^^

Now let's create our italian stuff::

    $ mkdir sources/hello/italian -p
    $ touch sources/hello/__init__.py
    $ touch sources/hello/italian.py

In ``italian.py`` file we'll have::

    def ciao(): print "Ciao mondo!"
    def addio(): print "Addio mondo crudele!"

Now we have to create the ``setup.py`` file that permits the creation of the ump file.

Setup.py file
^^^^^^^^^^^^^

The entire build process of ump file is dictated by the ``setup.py`` file. It's a `distutils <http://www.python.org/doc/2.5.2/lib/module-distutils.html>`_ like file that also adds various fields used to build a ``Manifest.xml`` file that contains various meta-informations that are interpreted by the Umit Plugin Engine (take a look to :ref:`manifest-file` for additional informations)::

    from umit.plugin.Containers import setup

    setup(
        name='helloworld',
        version='1.0',
        author=['Francesco Piccinno'],
        url='http://www.umitproject.org',
        #update=['http://localhost/~stack/plugins/dummywork'],
        license=['GPL'],
        copyright=['(C) 2009 Francesco Piccinno'],
        scripts=['sources/main.py'],
        start_file="main",
        data_files=[('data', ['dist/logo.png'])],
        provides='=helloworld-1.0',
        description='Say hello to world!',
        package_dir={'hello' : 'sources/hello'},
        packages=['hello'],
        output='helloworld.ump'
    )

Testing and Building
^^^^^^^^^^^^^^^^^^^^

Before packing your sources to ump file it's better to test the plugin::

    $ pwd
    /home/stack/umit
    $ UMIT_DEVELOPMENT=1 UMIT_PLUGINS="/home/stack/umit/source-plugins/helloworld/sources" bin/umit
    Hello world!!!
    Ciao mondo!

If everything works as excepted we could build the plugin by using the ``builder.py`` script::

    $ pwd
    /home/stack/umit/source-plugins
    $ python builder.py helloworld
    [*] Building helloworld plugin ...
    >> Running setup()
    running install
    running build
    running build_py
    running build_scripts
    running install_lib
    running install_scripts
    changing mode of output/bin/main.py to 755
    running install_data
    copying dist/logo.png -> output/data
    running install_egg_info
    >> Creating plugin
    Adding file bin main.py bin
    Adding file data logo.png data
    Adding file lib/hello italian.py lib
    Adding file lib/hello italian.pyc lib
    Adding file lib/hello __init__.pyc lib
    Adding file lib/hello __init__.py lib
    Manifest.xml created
    >> Plugin helloworld.ump created.
    >> Cleaning up
    $ ls /home/stack/.umit/plugins
    helloworld.ump

.. _localized-plugin:

Second Tutorial
---------------

In this tutorial you'll learn howto localize your plugin taking a look to ``Localized`` plugin.

Start file
^^^^^^^^^^

This is the content of ``main.py``, our ``start_file``::

    from umit.plugin.Core import Core
    from umit.plugin.Engine import Plugin
    from umit.plugin.Atoms import StringFile

    _ = str

    class Localize(Plugin):
        def start(self, reader):
            cat = reader.bind_translation("localizer")

            if cat:
                global _
                _ = cat.gettext

            print _("What the hell are you doing?")

        def stop(self):
            print _("Stopping localize ...")

    __plugins__ = [Localize]

Catalog file
^^^^^^^^^^^^

Now we have to create the catalog for our plugin. This is essentially a ``.pot`` file containing various string that should be translated. This is done by calling ``pygettext.py`` script::

    $ pygettext.py sources/*.py

This generates the ``messages.pot`` file. Now we have to create a ``.po`` file for our favorite language::

    $ LANG=it_IT msginit

Then use your favourite text editor and modify your ``it.po`` file and change::

    #: sources/main.py:37
    msgid "What the hell are you doing?"
    msgstr ""

    #: sources/main.py:40
    msgid "Stopping localize ..."
    msgstr ""

to::

    #: sources/main.py:37
    msgid "What the hell are you doing?"
    msgstr "Che diavolo stai facendo?"

    #: sources/main.py:40
    msgid "Stopping localize ..."
    msgstr "Disabilito localize ..."

Update your translation
^^^^^^^^^^^^^^^^^^^^^^^

If you have changed the code and you have introduced new gettext string is desiderable to regen your catalog (``messages.pot``), and then merge old translation with the new catalog with::

    $ msgmerge -U it.po messages.pot

Now you could update your ``it.po`` file and then pass to the next section.

Compile the ``.po`` file
^^^^^^^^^^^^^^^^^^^^^^^^

You could now compile ``it.po`` file to ``it.mo`` with::

    $ msgfmt it.po -o it.mo

And then rename your ``it.mo`` to ``localizer.mo`` (see also ``bind_translation()`` in ``main.py`` file), and then move under ``locale/it`` directory.

Now we are ready to pack everything inside a ``.ump`` file.

Setup.py
^^^^^^^^

This is the ``setup.py`` file::

    # ...

    mo_files = []
    for filepath in glob("locale/*/*.mo"):
        path = os.path.dirname(filepath)
        mo_files.append((path, [filepath]))

    setup(
        # ...
        data_files=[('data', ['dist/logo.png'])] + mo_files,
        # ...
    )
