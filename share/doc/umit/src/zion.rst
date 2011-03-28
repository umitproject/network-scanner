Zion
====

.. sectionauthor:: João Paulo S. Medeiros

.. moduleauthor:: João Paulo S. Medeiros

.. warning::

   This documentation is not finished! Part or all of it's content may be
   missing or inaccurate. As Umit is under constant development and
   improvement, expect changes in this documentation at upcoming releases.


Introduction
------------

Zion [#zion]_ was introduced in Umit in Google Summer of Code 2009 [#gsoc]_.
Its goal is identify networks devices and systems in a remotely manner.
Some examples of these devices and systems are: SYN proxies, Honeyd, Firewalls
and Operating Systems in general.
Zion's current skills include:

    - OpenBSD PF [#pf]_ SYN proxy detection;
    - Honeyd 1.5c (and probably the old ones) detection;
    - Operating systems detection;
    - Basic port-scan (mainly used by other features);
    - Interface to sniff packets and select specific fields.

For instance, consider the testbed presented in :ref:`Zion testbed <testbed>`.

.. _testbed:
.. figure:: static/zion-testbed.png
   :align: center

   *Zion testbed*

Notes and references
--------------------

.. [#zion] The name Zion is an acronym which means *systematiZed Identification
   Over Network*, and is related to Matrix last human city on the planet Earth.

.. [#gsoc] Google Summer of Code: http://code.google.com/soc/.

.. [#pf] PF: The OpenBSD Packet Filter: http://www.openbsd.org/faq/pf/index.html.
