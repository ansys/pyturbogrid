.. _functions:

Functions
#########

Create an instance of ``PyTurboGrid`` with an available port.
The PyTurboGrid object connects to your installation of TurboGrid and initializes itselff.

.. code-block:: pycon

    >>> socketPort = 5000
    >>> PyTGInstance = PyTurboGrid(socketPort)

Initialization
==============
readsession
-----------    
.. code-block:: pycon

    >>> PyTGInstance.readsession(filename="session_filename.extension")

readinf
-------
.. code-block:: pycon

    >>> PyTGInstance.readinf(filename="inf_filename.extension")

readstate
---------
.. code-block:: pycon

    >>> PyTGInstance.readstate(filename="state_filename.extension")

Processing
==========
unsuspend
---------
.. code-block:: pycon

    >>> PyTGInstance.unsuspend(object="/TOPOLOGY SET")

savestate
---------
.. code-block:: pycon

    >>> PyTGInstance.savestate(filename="state_filename.extension")

setTopologyChoice
-----------------
.. code-block:: pycon

    >>> PyTGInstance.setTopologyChoice("Single Round Round Refined")

setTopologyList
---------------
.. code-block:: pycon

    >>> PyTGInstance.setTopologyList("LECircleHigh_TECircleLow")

setGlobalSizeFactor
-------------------
.. code-block:: pycon

    >>> PyTGInstance.setGlobalSizeFactor(2)

Queries
=======
queryMeshStatistics
-------------------
.. code-block:: pycon

    >>> PyTGInstance.queryMeshStatistics()

queryValidTopologyChoices
-------------------------
.. code-block:: pycon

    >>> PyTGInstance.queryValidTopologyChoices()

Shutting down
=============
quit
----
.. code-block:: pycon

    >>> PyTGInstance.quit()



.. toctree::
   :hidden:
   :maxdepth: 2