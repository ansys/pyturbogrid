.. _pyturbogrid_core:

pyturbogrid_core
================
  
.. py:function:: quit(self) -> None:
   
    Quit the PyTurboGrid instance.

.. py:function:: end_session(self) -> None:
    
    End the connected TurboGrid session.

.. py:function:: read_inf(self, filename: str) -> None:
    
    Read blade model from an inf file

    :param filename: Name of the inf file with relative path
    :type filename: str
    

.. py:function:: read_ndf(self, ndffilename: str, cadfilename: str, flowpath: str, bladerow: str, bladename: str) -> None:

    read ndf file

    :param ndffilename: Name of the NDF file
    :type ndffilename: str
    :param cadfilename: Name of the CAD file to be written
    :type cadfilename: str
    :param flowpath: Name of the flowpath to use
    :type flowpath: str
    :param bladerow: Name of the blade row to select
    :type bladerow: str
    :param bladename: Name of the blade to input
    :type bladename: str


.. py:function:: read_session(self, filename: str) -> None:

    Read a session file and repeat a previous session

    :param filename: Name of the session file
    :type filename: str


.. py:function:: read_state(self, filename: str) -> None:

    Restore a previous state from a saved state file

    :param filename: Name of the state file
    :type filename: str


.. py:function:: save_mesh(self, filename: str, onefile: str, onedomain: str) -> None:

    Save generated mesh to a file

    :param filename: Name of the mesh file to save
    :type filename: str
    :param onefile: String to indicate if onefile is preferred
    :type onefile: str
    :param onedomain: String to indicate if onedomain is preferred
    :type onedomain: str


.. py:function:: save_state(self, filename: str) -> None:

    Save TurboGrid state into a file

    :param filename: Name of the file to save
    :type filename: str


.. py:function:: set_global_size_factor(self, global_size_factor: str) -> None:

    Set global size factor

    :param global_size_factor: Value to use as size factor
    :type global_size_factor: str

