.. _functions:

Modules
#######

This documentation lists the modules and functions in pyturbogrid repository as well as in ansys-api-turbogrid repository if those module functions are directly accessible and are needed to be accessed to complement the functionalities defined in pyturbogrid repository.

launcher
========

A module in ansys-api-turbogrid that has the functions to create a running instance of TurboGrid application and returns a python interface to communicate with the instance.

launch_turbogrid
----------------

Create an instance of ``PyTurboGrid`` with an available port.
The PyTurboGrid object connects to your installation of TurboGrid application and initializes itself.

Parameters
^^^^^^^^^^
product_version : str, optional
    Version of TurboGrid to use in the numeric format (such as ``"23.2.0"``
    for 2023 R2). The default is ``None``, in which case the active version
    or latest installed version is used.
turbogrid_path : str, optional
    Path to the "cfxtg" command used to start TurboGrid. The default is ``None``.
    in which case the product_version is used instead.
port : int, optional
    Port to use for TurboGrid communications. The default is ``5000``.
additional_args_str : str, optional
    Additional arguments to send to TurboGrid. The default is ``None``.
additional_kw_args : dict, optional
    Additional arguments to send to TurboGrid. The default is ``None``.

Returns
^^^^^^^
pyturbogrid_core PyTurboGrid session.

Example:

.. code-block:: pycon

    >>> from ansys.api.turbogrid.launcher import launch_turbogrid
    >>> turbogrid = launch_turbogrid()

get_turbogrid_exe_path
----------------------

Returns Path object for the location of the TurboGrid executable that is used by launch_turbogrid function call.

pyturbogrid_core
================

read_inf
--------
.. code-block:: pycon

    >>> turbogrid.read_inf(path_to_inf_file)

read_session  
------------
.. code-block:: pycon

    >>> turbogrid.read_session(path_to_session_file)

read_state
---------
.. code-block:: pycon

    >>> turbogrid.read_state(path_to_state_file)

unsuspend
---------
Example:

.. code-block:: pycon

    >>> turbogrid.unsuspend(object="/TOPOLOGY SET")

save_state
---------
.. code-block:: pycon

    >>> turbogrid.save_state(path_to_new_state_file)

set_topology_choice
-----------------
.. code-block:: pycon

    >>> turbogrid.set_topology_choice(topology_choice_string)

set_topology_list
---------------
.. code-block:: pycon

    >>> turbogrid.set_topology_list(
    ...     topology_list_string
    ... )  # topology_list_string example: "LECircleHigh_TECircleLow"

set_global_size_factor
-------------------
Example:

.. code-block:: pycon

    >>> turbogrid.set_global_size_factor(2)

query_mesh_statistics
-------------------
.. code-block:: pycon

    >>> stats = turbogrid.query_mesh_statistics()

query_valid_topology_choices
-------------------------
.. code-block:: pycon

    >>> choices = turbogrid.query_valid_topology_choices()

quit
----
.. code-block:: pycon

    >>> turbogrid.quit()



.. toctree::
   :hidden:
   :maxdepth: 2
