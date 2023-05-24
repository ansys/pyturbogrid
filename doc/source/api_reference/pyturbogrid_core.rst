.. _pyturbogrid_core:

pyturbogrid_core
================

Module in the ansys-turbogrid-api package that is internally used by modules in pyturbogrid package for interactions with a running Ansys TurboGrid application.

.. py:class:: PyTurboGrid

    
    This class controls of the launching, interactions and quitting of TurboGrid.
    Refer :py:mod:`launcher` module to see how to create an instance of this class.

    .. py:method:: __init__( socket_port: int | None, turbogrid_location_type: TurboGridLocationType, cfxtg_location: str, log_level, additional_args_str: str | None, additional_kw_args: dict | None, )


    .. py:method:: read_inf(filename: str) -> None

        Read a blade model from a BladeGen \*.inf file..

        :param filename: Name or path for the Bladegen \*.inf file.
        :type filename: str

    .. py:method:: read_ndf( ndffilename: str, cadfilename: str, flowpath: str, bladerow: str, bladename: str ) -> None

        Read a blade model from an NDF \*.ndf file.
        TurboGrid uses the details in the NDF file to generate and import a CAD file containing the blade geometry.

        :param ndffilename: Name or path for the NDF \*.ndf file.
        :type ndffilename: str
        :param cadfilename: Name of the CAD \*.x_b file to be generated.
        :type cadfilename: str
        :param flowpath: Name of the flowpath to use.
        :type flowpath: str
        :param bladerow: Name of the blade row to select.
        :type bladerow: str
        :param bladename: Name of the blade to load.
        :type bladename: str

    .. py:method:: read_session(filename: str) -> None

        
        Read a session file to repeat a previous session.

        :param filename: Name of the session file.
        :type filename: str

    .. py:method:: read_state(filename: str) -> None

        
        Restore a previous state from a saved state file.

        :param filename: Name of the state file.
        :type filename: str

    .. py:method:: save_mesh(filename: str, onefile: str, onedomain: str) -> None

        
        Save generated mesh to a file.

        :param filename: Name of the mesh file to save.
        :type filename: str
        :param onefile: If enabled (true), write all of the available meshes to a single mesh file. The default is ``true``.
        :type onefile: str
        :param onedomain: If enabled (true), combine any inlet and outlet domain meshes with the passage domain,
            to form a single assembly. The default is ``true``.
        :type onedomain: str

    .. py:method:: save_state(filename: str) -> None

        Save TurboGrid state into a file.

        :param filename: Name of the file to save.
        :type filename: str

    .. py:method:: set_global_size_factor(global_size_factor: str) -> None

        
        Set global size factor.

        :param global_size_factor: Value to use as size factor in string format.
        :type global_size_factor: str

    .. py:method:: set_inlet_hub_position(parametric_hub_location: str) -> None

        
        Set the parametric position of the inlet line on the hub.

        :param parametric_hub_location: Value to be used as parametric location in string format.
        :type parametric_hub_location: str

    .. py:method:: set_inlet_shroud_position(parametric_shroud_location: str) -> None

        
        Set the parametric position of the inlet line on the shroud.

        :param parametric_shroud_location: Value to be used as parametric location in string format.
        :type parametric_shroud_location: str

    .. py:method:: set_obj_param(object: str, param_val_pairs: str) -> None

        
        Update the value for a CCL object parameter

        :param object: Name with full path for the CCL object
        :type object: str
        :param param_val_pairs: Name and value pair for the parameter to set
        :type param_val_pairs: str

    .. py:method:: set_outlet_hub_position(parametric_hub_location: str) -> None

        
        Set the parametric position of the outlet line on the hub.

        :param parametric_hub_location: Value to be used as parametric location in string format.
        :type parametric_hub_location: str

    .. py:method:: set_outlet_shroud_position(parametric_shroud_location: str) -> None

        
        Set the parametric position of the outlet line on the shroud.

        :param parametric_hub_location: Value to be used as parametric location in string format.
        :type parametric_hub_location: str

    .. py:method:: set_topology_choice(atm_topology_choice: str) -> None

        
        Set the topology method to be used for the topology set generation process.

        :param atm_topology_choice: Name of the topology method to be used.
        :type atm_topology_choice: str

        Example

        >>> turbogrid.set_topology_choice("Single Round Round Refined")


    .. py:method:: set_topology_list(atm_topology_list: str) -> None

        
        Set the list of topology pieces to be used for topology generation.

        :param atm_topology_list: The topology piece names concatenated using underscores.
        :type atm_topology_list: str

        Example

        >>> turbogrid.set_topology_list("LECircleHigh_TECircleLow")


    .. py:method:: start_session(filename: str) -> None

        
        Start recording a new TurboGrid session.

        :param filename: Name of the session file.
        :type filename: str

    .. py:method:: unsuspend(object: str) -> None

        
        Unsuspend an item in the TurboGrid objects tree.

        :param object: String specifying the name and type of the tree item to be unsuspended.
        :type object: str

        Example

        >>> turbogrid.unsuspend(object="/TOPOLOGY SET")


    .. py:method:: query_mesh_statistics(domain: str) -> dict

        
        Returns mesh quality measures from TurboGrid for the current session and specified domain.
        **Note**: It is suggested to use the :py:mod:`mesh_statistics` module instead of directly calling this.

        :param domain: Name of the domain to query measurements.
        :type domain: str
        :return: A dictionary form of the quality measurements.
        :rtype: dict


    .. py:method:: query_mesh_statistics_histogram_data( variable: str, domain: str, number_of_bins: int, upper_bound: float, lower_bound: float, bin_units: str, scale: str, use_absolute_values: bool, bin_divisions: list, ) -> dict

        
        Returns data that can be used to plot mesh statistics histograms.

        :param variable: Name of the quality measurement to query the statistics
        :type variable: str
        :param domain: Name of the domain to obtain the measuments from
        :type domain: str
        :param number_of_bins: Number of histogram columns to use
        :type number_of_bins: int
        :param upper_bound: The maximum limit for the horizontal axis
        :type upper_bound: float
        :param lower_bound: The minimum limit for the horizontal axis
        :type lower_bound: float
        :param bin_units: The unit to use for the horizontal ax1s
        :type bin_units: str
        :param scale: Scaling type for the horizontal axis, linear or logarithmic
        :type scale: str
        :param use_absolute_values: Choice to use absolute or percentage values on the vertical axis
        :type use_absolute_values: bool
        :param bin_divisions: User provided bin divisions
        :type bin_divisions: list
        :return: A dictionary form of the statistics for the requested quality measurement
        :rtype: dict

    .. py:method:: query_valid_topology_choices() -> list

        
        Returns the permitted topology methods for the blade geometry in the current session.

        :return: List of topology method names
        :rtype: list

    .. py:method:: quit() -> None

        Quit the PyTurboGrid instance.

    .. py:method:: end_session() -> None

        Stop recording a TurboGrid session file.

