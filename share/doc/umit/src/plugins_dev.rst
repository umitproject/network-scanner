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

You could add you custom elements to the xml file but someone are reserved by UMIT Plugin system:

   +--------------------+-------------------------------------------------------+
   | Element            |                                                       |
   +====================+=======================================================+
   | ``<needs>``        | A list (``VersionString``) of needed virtual plugins  |
   |                    | that must be already loaded to enable the target      |
   |                    | plugin.                                               |
   +--------------------+-------------------------------------------------------+
   | ``<conflicts>``    | A list (``VersionString``) of conflicting virtual     |
   |                    | plugins that must be **NOT** present to load the      |
   |                    | target plugin.                                        |
   +--------------------+-------------------------------------------------------+
   | ``<provides>``     | A list (``VersionString``) of exported virtual names  |
   |                    | that the target plugin provides to the others.        |
   +--------------------+-------------------------------------------------------+
   | ``<start-file>``   | A string pointing to the main file in ``bin/``        |
   |                    | directory.                                            |
   +--------------------+-------------------------------------------------------+
   | ``<url>``          |A string (URL) pointing to the target plugins homepage.|
   +--------------------+-------------------------------------------------------+
   | ``<author>``       | A string representing the name of the plugin's author.|
   +--------------------+-------------------------------------------------------+
   | ``<license>``      | A string representing the license used for the plugin.|
   +--------------------+-------------------------------------------------------+
   | ``<name>``         | A *non-operator* ``VersionString`` describing the     |
   |                    | plugin.                                               |
   +--------------------+-------------------------------------------------------+
   | ``<update>``       | A string (URL) pointing to the target plugins update  |
   |                    | directory.                                            |
   +--------------------+-------------------------------------------------------+
   | ``<description>``  | A string containing a description of the plugin.      |
   +--------------------+-------------------------------------------------------+
   | ``<version>``      | A string represetnting the plugin version.            |
   +--------------------+-------------------------------------------------------+
   | ``<contributors>`` | A list of plugin's contributors.                      |
   +--------------------+-------------------------------------------------------+
   | ``<translators>``  | A list of plugin's translators.                       |
   +--------------------+-------------------------------------------------------+
   | ``<artists>``      | A list of plugin's artists.                           |
   +--------------------+-------------------------------------------------------+

Following an example of a Manifest.xml::

    <?xml version="1.0" ?>
    <UmitPlugin>
      <url>http://www.umitproject.org</url>
      <conflicts></conflicts>
      <provides>&gt;=SystemInfo-1.0</provides>
      <needs></needs><type></type>
      <start_file>main</start_file>
      <name>SystemInfo</name>
      <version>0.1</version>
      <description>A plugin that provides info about the system</description>
      <author>Francesco Piccinno</author>
      <license>GPL</license>
      <update>http://localhost/~stack/plugins/systeminfo</update>
    </UmitPlugin>

Version String
^^^^^^^^^^^^^^

Elements like ``<needs>`` , ``<conflicts>`` , ``<provides>`` and ``<name>`` are ``VersionString`` elements.

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
   | Element            |                                                       |
   +====================+=======================================================+
   | ``<update-uri>``   | A string (URL) pointing to the new version of the     |
   |                    | plugin.                                               |
   +--------------------+-------------------------------------------------------+
   | ``<version>``      | A *non-operative* ``VersionString`` like for Manifest.|
   +--------------------+-------------------------------------------------------+
   | ``<md5>``          | This element is optional and contains the MD5 hex     |
   |                    | digest string used for integrity check on the         |
   |                    | downloaded file (the ``<update-uri>`` file).          |
   +--------------------+-------------------------------------------------------+

An example of the ``latest.xml`` follows::

    <UmitPluginUpdate>
        <update-uri>http://localhost/~stack/plugins/systeminfo/SystemInfo.ump</update-uri>
        <version>2.0.0</version>
        <md5>c7487b08545f58999512f6155852050e</md5>
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
   
   For example taking a look to the setup.py of Notifier plugin we could see that the autogenerated ``Manifest.xml`` will have the ``<needs>`` element set to ``>=tray-2.0``. Assuming that we have already loaded the TrayPlugin that's taking care of providing ``=tray-2.0`` in his ``<provides>`` element in the Manifest file, we will have something like that::

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
        author='Francesco Piccinno',
        url='http://www.umitproject.org',
        #update='http://localhost/~stack/plugins/dummywork',
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
    Field url setted to http://www.umitproject.org
    Field conflicts setted to
    Field provides setted to =helloworld-1.0
    Field needs setted to
    Field type setted to
    Field start_file setted to main
    Field name setted to helloworld
    Field version setted to 1.0
    Field description setted to Say hello to world!
    Field author setted to Francesco Piccinno
    Field license setted to
    Field artist setted to
    Field copyright setted to
    Field update setted to
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

