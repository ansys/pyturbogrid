.. _pyturbogrid_core:

pyturbogrid_core
==============================================================

.. py:function:: __init__(self,socket_port: int | None,turbogrid_location_type: TurboGridLocationType,cfxtg_location: str,log_level,additional_args_str: str | None,additional_kw_args: dict | None,): 



.. py:function:: read_inf(self, filename: str) -> None:

        Read blade model from an inf file

        :param filename: Name of the inf file with relative path
        :type filename: str


.. py:function:: read_ndf(self, ndffilename: str, cadfilename: str, flowpath: str, bladerow: str, bladename: str) -> None:

        Read blade model from an ndf file

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

        :param global_size_factor: Value to use as size factor sent in string format
        :type global_size_factor: str


.. py:function:: set_inlet_hub_position(self, parametric_hub_location: str) -> None:

        
        Set the parametric position of the inlet line on the hub

        :param parametric_hub_location: Value to be used as parametric location sent in string format
        :type parametric_hub_location: str


.. py:function:: set_inlet_shroud_position(self, parametric_shroud_location: str) -> None:

        
        Set the parametric position of the inlet line on the shroud

        :param parametric_shroud_location: Value to be used as parametric location sent in string format
        :type parametric_shroud_location: str


.. py:function:: set_obj_param(self, object: str, param_val_pairs: str) -> None: 



.. py:function:: set_outlet_hub_position(self, parametric_hub_location: str) -> None:

        
        Set the parametric position of the outlet line on the hub

        :param parametric_hub_location: Value to be used as parametric location sent in string format
        :type parametric_hub_location: str


.. py:function:: set_outlet_shroud_position(self, parametric_shroud_location: str) -> None:

        
        Set the parametric position of the outlet line on the shroud

        :param parametric_hub_location: Value to be used as parametric location sent in string format
        :type parametric_hub_location: str


.. py:function:: set_topology_choice(self, atm_topology_choice: str) -> None:

        
        Set the topology method to be used for the topology set generation process

        :param atm_topology_choice: Name of the topology method to be used sent as string.
        :type atm_topology_choice: str

        Example

        .. code-block:: pycon

            >>> turbogrid.set_topology_choice("Single Round Round Refined")



.. py:function:: set_topology_list(self, atm_topology_list: str) -> None:

        
        Set the list of topology pieces to be used for topology generation

        :param atm_topology_list: String input with the topology piece names concatenated using underscores
        :type atm_topology_list: str

        Example

        .. code-block:: pycon

            >>> turbogrid.set_topology_list("LECircleHigh_TECircleLow")



.. py:function:: start_session(self, filename: str) -> None:

        
        Start a new PyTurboGrid session

        :param filename: Name of the session file
        :type filename: str


.. py:function:: unsuspend(self, object: str) -> None:

        
        Unsuspend an item in the TurboGrid objects tree

        :param object: String specifying the name and type of the tree item to be unsuspended
        :type object: str

        Example

        .. code-block:: pycon

            >>> turbogrid.unsuspend(object="/TOPOLOGY SET")



.. py:function:: query_mesh_statistics(self, domain: str) -> dict:

        
        Returns mesh quality measures from TruboGrid for the current session and specified domain
        **Note**: It is suggested to use the mesh_statistics module instead of directly calling this.

        :param domain: Name of the domain to query measurements
        :type domain: str
        :return: A dictionary form of the quality measurements
        :rtype: dict



.. py:function:: query_mesh_statistics_histogram_data(self,variable: str,domain: str,number_of_bins: int,upper_bound: float,lower_bound: float,bin_units: str,scale: str,use_absolute_values: bool,bin_divisions: list,) -> dict:

        
        A low level query method internally used by mesh_statistics module


.. py:function:: query_valid_topology_choices(self) -> list:

        
        Returns the permitted topology methods for the blade geometry in the current session

        :return: List of topology method names
        :rtype: list


.. py:function:: quit(self) -> None:

        Quit the PyTurboGrid instance.


.. py:function:: end_session(self) -> None:

        End the connected TurboGrid session.


