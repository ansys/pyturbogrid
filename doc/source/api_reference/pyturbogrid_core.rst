.. _pyturbogrid_core:

pyturbogrid_core
================

.. py:function::__init__(
        self,
        socket_port: int | None,
        turbogrid_location_type,
        cfxtg_location,
        log_level,
        additional_args_str=None,
        additional_kw_args=None,
    )

    Creates the PyTurboGrid instance.

    :param socket_port: ``int``, ``optional``.
        Port at which PyTurbogrid should connect with TurboGrid application.
        If not provided, a random port available will be used.
    :param turbogrid_location_type: ``TurboGridLocationType``.
        Enum type input to indicate whether to use a locally installed TurboGrid application
        or a container installed application
    :param cfxtg_location: ``str``.
        Path to the ``cfxtg`` command used to start TurboGrid.
    :param log_level: ``TurboGridLogLevel``. 
        Level of details to be given in the log file and console output
    :param additional_args_str: ``str`` | ``None``.
        Additional arguments to send to TurboGrid. The default is ``None``
    :param additional_kw_args: ``dict`` | ``None``.
        Additional arguments to send to TurboGrid. The default is ``None``.
    
.. py:function::read_inf(self, filename: str)
    Reads a blade model from an inf file.

read_session  
------------
.. code-block:: pycon

    >>> turbogrid.read_session(path_to_session_file)

read_state
----------
.. code-block:: pycon

    >>> turbogrid.read_state(path_to_state_file)

unsuspend
---------
Example:

.. code-block:: pycon

    >>> turbogrid.unsuspend(object="/TOPOLOGY SET")

save_state
----------
.. code-block:: pycon

    >>> turbogrid.save_state(path_to_new_state_file)

set_topology_choice
-------------------
.. code-block:: pycon

    >>> turbogrid.set_topology_choice(topology_choice_string)

set_topology_list
-----------------
.. code-block:: pycon

    >>> turbogrid.set_topology_list(
    ...     topology_list_string
    ... )  # topology_list_string example: "LECircleHigh_TECircleLow"

set_global_size_factor
----------------------
Example:

.. code-block:: pycon

    >>> turbogrid.set_global_size_factor(2)

query_mesh_statistics
----------------------
.. code-block:: pycon

    >>> stats = turbogrid.query_mesh_statistics()

query_valid_topology_choices
----------------------------
.. code-block:: pycon

    >>> choices = turbogrid.query_valid_topology_choices()

quit
----
.. code-block:: pycon

    >>> turbogrid.quit()
