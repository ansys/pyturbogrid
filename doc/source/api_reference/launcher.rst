.. _launcher:

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

