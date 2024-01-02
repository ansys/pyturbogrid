# Copyright (c) 2023 ANSYS, Inc. All rights reserved
"""Module for working on a multi blade row turbomachinery case using PyTurboGrid instances in parallel."""

from collections import OrderedDict
from datetime import datetime as dt
from datetime import timedelta as td
import math
from multiprocessing import Manager, Pool, Process, cpu_count
import os
import threading
import time

from ansys.turbogrid.api import pyturbogrid_core
from ansys.turbogrid.api.CCL.ccl_object_db import CCLObjectDB
from fabric import Connection
from jinja2 import Environment, FileSystemLoader

from ansys.turbogrid.core.launcher.launcher import launch_turbogrid
from ansys.turbogrid.core.mesh_statistics import mesh_statistics
import ansys.turbogrid.core.ndf_parser.ndf_parser as ndfp


class MultiBladeRow:
    """
    Facilitates working on a multi blade row turbomachinery case using PyTurboGrid instances in parallel.
    """

    _working_dir: str = None
    _case_directory: str = None
    _case_ndf: str = None
    _ndf_file_full_path: str = None
    _results_directory: str = None
    _ndf_parser: ndfp.NDFParser = None

    _blade_rows_to_mesh: dict = None
    _multi_process_count: int = 0
    _blade_row_gsfs: dict = None
    _blade_boundary_layer_offsets: dict = None
    _blade_row_spanwise_counts: dict = None
    _custom_blade_settings: dict = None

    #: Number of decimal places to be used for values in the meshing reports
    report_stats_decimal_places = 3

    #: The unit to be used for the angles in the meshing reports.
    #: Use "rad" for angles in radian. "deg" for angles in degrees.
    report_stats_angle_unit = "deg"

    #: List of the quality measures to be reported for each blade row
    #: Permitted entries are:
    #: "Connectivity Number", "Edge Length Ratio", "Element Volume Ratio",
    #: "Maximum Face Angle", "Minimum Face Angle", "Minimum Volume",
    #: "Orthogonality Angle", "Skewness"
    report_mesh_quality_measures = [
        "Edge Length Ratio",
        "Minimum Face Angle",
        "Minimum Volume",
        "Orthogonality Angle",
    ]

    #: Set True to write tginit first before processing blade rows in parallel by reading the tginit
    #: instead of reading ndf in parallel and writing separate tginit for each blade row
    write_tginit_first = False

    #: When working in Ansys Labs, the number of retry to be made for file transfer from
    #: container to the local folder.
    max_file_transfer_attempts = 20

    #: When working in Ansys Labs, the name of the file containing the container key with full path.
    tg_container_key_file = ""

    def __init__(self, working_dir: str, case_directory: str, ndf_file_name: str):
        """
        Initialize the class using name with full path of an NDF file for the multi blade row case.

        Parameters
        ----------
        ndf_file_full_name : str
            Name with full path of the NDF file containing the blade rows for the multi blade row case.
        """
        self._set_working_directory(working_dir)
        self._set_case_directory_and_ndf(case_directory, ndf_file_name)
        self._ndf_parser = ndfp.NDFParser(self._ndf_file_full_path)
        self._assert_unique_blade_names()
        self.set_blade_rows_to_mesh([])

    def set_blade_rows_to_mesh(self, blades_to_mesh: list):
        """
        Set the blade rows to be meshed.

        Parameters
        ----------
        blades_to_mesh : list
            Names of the main blade from each blade row to be meshed in a list.
        """
        all_blade_rows = self._ndf_parser.get_blade_row_blades()
        blade_row_names_to_mesh = [
            x
            for x in all_blade_rows
            if (len(blades_to_mesh) == 0 or all_blade_rows[x][0] in blades_to_mesh)
        ]
        self._blade_rows_to_mesh = {}
        for blade_row in blade_row_names_to_mesh:
            self._blade_rows_to_mesh[blade_row] = all_blade_rows[blade_row]
        # print(f"Blade rows to mesh: {self._blade_rows_to_mesh.keys()}")
        # for blade_row in self._blade_rows_to_mesh:
        #    print(f"Blade row {blade_row} blades: {self._blade_rows_to_mesh[blade_row]}")

    def set_multi_process_count(self, multi_process_count: int):
        """
        Set number of processes to be used in parallel for meshing the selected blade rows.

        Parameters
        ----------
        multi_process_count : int
            The number of processes to be used in parallel.
        """
        num_rows_to_process = len(self._blade_rows_to_mesh)
        if num_rows_to_process == 0:
            self._multi_process_count = 0
            return
        max_producers = min(cpu_count(), num_rows_to_process)
        multi_process_count_clamped = min(max(0, multi_process_count), max_producers)
        num_producers = min(num_rows_to_process, multi_process_count_clamped)
        num_producers = num_producers if num_producers > 0 else max_producers
        # print(f"{cpu_count()=}")
        # print(f"{max_producers=}")
        # print(f"{multi_process_count_clamped=}")
        # print(f"{num_producers=}")
        self._multi_process_count = num_producers

    def set_global_size_factor(self, assembly_gsf: float):
        """
        Set the global size factor to be used for all the blade rows.

        Parameters
        ----------
        assembly_gsf : float
            The Global Size Factor to be used for each blade row.
            If not called the default size factor of 1 will be used.
        """
        self._blade_row_gsfs = self._get_blade_row_gsfs(assembly_gsf)
        # print(f"blade_row_gsfs {self._blade_row_gsfs}")

    def set_spanwise_counts(
        self,
        stator_spanwise_count: int,
        rotor_spanwise_count: int,
        rotor_blade_rows_blades: list = [],
    ):
        """
        Set the spanwise count of mesh elements for the different blade rows.

        Parameters
        ----------
        stator_spanwise_count : int
            The element count in the spanwise direction for stator blade rows.
        rotor_spanwise_count : int
            The element count in the spanwise direction for rotor blade rows.
        rotor_blade_rows : list, default: []
            List of main blade from each rotor blade row. If not provided,
            all even numbered rows will be taken as rotor with row numbering starting at 1.
        """
        self._blade_row_spanwise_counts = self._get_blade_row_spanwise_counts(
            stator_spanwise_count, rotor_spanwise_count, rotor_blade_rows_blades
        )

    def set_blade_boundary_layer_offsets(
        self, assembly_bl_offset: float, custom_blade_bl_offsets: dict = None
    ):
        """
        Set the boundary layer first element offset for the blades.

        Parameters
        ----------
        assembly_bl_offset : float
            The first element offset to be applied to all blade row blades.
        custom_blade_bl_offsets:dict, default: None
            Custom first element offset for particular blades given in the form of a
            dictionary: {'bladename' : offset,...}
        """
        self._blade_boundary_layer_offsets = self._get_blade_bl_offs(
            assembly_bl_offset, custom_blade_bl_offsets
        )
        # print(f"blade_boundary_layer_offsets {self._blade_boundary_layer_offsets}")

    def set_custom_blade_settings(self, custom_blade_settings: dict):
        """
        Set custom meshing settings for particular blade rows.

        Parameters
        ----------
        custom_blade_settings : dict
            Special settings for particular blade rows in a dictionary in the form:
            { blade_name : [("Full CCL Object Path", "Param Name=Value"), ... ], ... }

            Here each blade row has to be identified by the name of the main blade in the row.
        """
        self._custom_blade_settings = custom_blade_settings

    def execute(self):
        """
        Execute the multi blade row meshing process.
        """
        start_dt = dt.now()
        if self._blade_rows_to_mesh is None:
            self.set_blade_rows_to_mesh([])
        num_rows = len(self._blade_rows_to_mesh)
        if num_rows == 0:
            raise Exception("No blade rows found!!!")
        print(f"{num_rows} blade rows to mesh:")
        print(*[(x, [b for b in self._blade_rows_to_mesh[x]]) for x in self._blade_rows_to_mesh])

        if self._multi_process_count == 0:
            self.set_multi_process_count(0)
        num_producers = self._multi_process_count
        print(f"{num_producers} producers")
        if num_producers == 0:
            raise Exception("No meshing process created.")

        blade_row_settings = self._get_blade_row_settings()
        # print(f"blade row settings: {blade_row_settings}")

        original_dir = os.getcwd()
        os.chdir(self._results_directory)
        progress_updates_mgr = Manager()
        progress_updates_queue = progress_updates_mgr.Queue()
        reporter = threading.Thread(
            target=publish_progress_updates,
            args=(progress_updates_queue, num_rows, self._ndf_file_full_path),
        )
        reporter.start()
        if self.write_tginit_first:
            tginit_name = self._read_ndf(
                self._ndf_file_full_path,
                list(self._blade_rows_to_mesh.keys())[0],
                progress_updates_queue,
            )
            work_details = []
            for blade_row in self._blade_rows_to_mesh:
                blade = self._blade_rows_to_mesh[blade_row][0]
                work_details.append(
                    [
                        os.path.join(os.getcwd(), tginit_name),
                        blade_row,
                        blade,
                        blade_row_settings[blade_row],
                        progress_updates_queue,
                        self.report_stats_angle_unit,
                        self.report_stats_decimal_places,
                        self.report_mesh_quality_measures,
                    ]
                )
            with Pool(num_producers) as producers:
                producers.starmap(execute_tginit_bladerow, work_details)
            producers.close()
            producers.join()
        else:
            work_details = []
            for blade_row in self._blade_rows_to_mesh:
                blade = self._blade_rows_to_mesh[blade_row][0]
                work_details.append(
                    [
                        self._ndf_file_full_path,
                        blade_row,
                        blade,
                        blade_row_settings[blade_row],
                        progress_updates_queue,
                        self.report_stats_angle_unit,
                        self.report_stats_decimal_places,
                        self.report_mesh_quality_measures,
                    ]
                )
            with Pool(num_producers) as producers:
                producers.starmap(execute_ndf_bladerow, work_details)
            producers.close()
            producers.join()

        stop_dt = dt.now()
        print("Start time: ", start_dt)
        print("Stop time: ", stop_dt)
        delta_dt = stop_dt - start_dt
        delta_dt = td(seconds=int(delta_dt / td(seconds=1)))
        deldt_parts = str(delta_dt).split(":")
        print(f"Duration: {deldt_parts[0]} hours {deldt_parts[1]} minutes {deldt_parts[2]} seconds")
        progress_updates_queue.put(
            [
                "User Experience Time",
                f"Duration: {deldt_parts[0]} hours {deldt_parts[1]} minutes {deldt_parts[2]} seconds",
            ]
        )
        progress_updates_queue.put(["Main", "Done"])
        reporter.join()
        os.chdir(original_dir)

    def execute_in_ansys_labs(self):
        """
        Execute the multi blade row meshing process on Ansys Labs.
        """
        start_dt = dt.now()
        if self._blade_rows_to_mesh is None:
            self.set_blade_rows_to_mesh([])
        blade_rows_to_mesh = self._blade_rows_to_mesh
        num_rows = len(blade_rows_to_mesh)
        if num_rows == 0:
            raise Exception("No blade rows found!!!")
        print(f"{num_rows} blade rows to mesh:")
        print(*[(x, [b for b in blade_rows_to_mesh[x]]) for x in blade_rows_to_mesh])

        if self._multi_process_count == 0:
            self.set_multi_process_count(0)
        num_producers = self._multi_process_count
        print(f"{num_producers} producers")
        if num_producers == 0:
            raise Exception("No meshing process created.")

        blade_row_settings = self._get_blade_row_settings()
        # print(f"blade row settings: {blade_row_settings}")

        original_dir = os.getcwd()
        os.chdir(self._results_directory)
        progress_updates_mgr = Manager()
        progress_updates_queue = progress_updates_mgr.Queue()
        reporter = Process(
            target=publish_progress_updates,
            args=(progress_updates_queue, num_rows, self._ndf_file_full_path),
        )
        reporter.start()
        if self.write_tginit_first:
            tginit_name_list = progress_updates_mgr.list()
            ndf_reader_proc = Process(
                target=read_ndf_ansys_labs,
                args=(
                    self._ndf_file_full_path,
                    list(self._blade_rows_to_mesh.keys())[0],
                    progress_updates_queue,
                    self.max_file_transfer_attempts,
                    self.tg_container_key_file,
                    tginit_name_list,
                ),
            )
            ndf_reader_proc.start()
            ndf_reader_proc.join()
            if len(tginit_name_list) == 0:
                raise Exception("tginit not written")
            tginit_name = tginit_name_list[0]
            print("tginit is ", os.path.join(os.getcwd(), tginit_name))
            work_details = []
            for blade_row in blade_rows_to_mesh:
                blade = blade_rows_to_mesh[blade_row][0]
                work_details.append(
                    [
                        os.path.join(os.getcwd(), tginit_name),
                        blade_row,
                        blade,
                        blade_row_settings[blade_row],
                        progress_updates_queue,
                        self.report_stats_angle_unit,
                        self.report_stats_decimal_places,
                        self.report_mesh_quality_measures,
                        self.max_file_transfer_attempts,
                        self.tg_container_key_file,
                    ]
                )
            with Pool(num_producers) as producers:
                producers.starmap(execute_tginit_blade_row_ansys_labs, work_details)
            producers.close()
            producers.join()
        else:
            work_details = []
            for blade_row in blade_rows_to_mesh:
                blade = blade_rows_to_mesh[blade_row][0]
                work_details.append(
                    [
                        self._ndf_file_full_path,
                        blade_row,
                        blade,
                        blade_row_settings[blade_row],
                        progress_updates_queue,
                        self.report_stats_angle_unit,
                        self.report_stats_decimal_places,
                        self.report_mesh_quality_measures,
                        self.max_file_transfer_attempts,
                        self.tg_container_key_file,
                    ]
                )
            with Pool(num_producers) as producers:
                producers.starmap(execute_ndf_blade_row_ansys_labs, work_details)
            producers.close()
            producers.join()

        stop_dt = dt.now()
        print("Start time: ", start_dt)
        print("Stop time: ", stop_dt)
        delta_dt = stop_dt - start_dt
        delta_dt = td(seconds=int(delta_dt / td(seconds=1)))
        deldt_parts = str(delta_dt).split(":")
        print(f"Duration: {deldt_parts[0]} hours {deldt_parts[1]} minutes {deldt_parts[2]} seconds")
        progress_updates_queue.put(
            [
                "User Experience Time",
                f"Duration: {deldt_parts[0]} hours {deldt_parts[1]} minutes {deldt_parts[2]} seconds",
            ]
        )
        progress_updates_queue.put(["Main", "Done"])
        reporter.join()
        os.chdir(original_dir)

    ######################################
    # Private methods
    ######################################

    def _set_working_directory(self, working_dir: str):
        if not os.path.isdir(working_dir):
            raise (Exception(f"Folder {working_dir} does not exists."))
        self._working_dir = working_dir
        # print(f"Working directory set to: {self._working_dir}")

    def _set_case_directory_and_ndf(self, case_directory: str, ndf_file: str) -> str:
        if case_directory == "" or ndf_file == "":
            raise Exception(f"Case directory or NDF file name is empty.")
        if os.path.isabs(case_directory):
            self._case_directory = case_directory
        else:
            self._case_directory = os.path.join(self._working_dir, case_directory)
        if not os.path.isdir(self._case_directory):
            raise Exception(f"Case folder {self._case_directory} does not exists.")

        self._ndf_file_full_path = os.path.join(self._case_directory, ndf_file)
        print(f"NDF file full path set to: {self._ndf_file_full_path}")

        case_base_name = os.path.basename(os.path.normpath(self._case_directory))
        self._results_directory = os.path.join(self._working_dir, case_base_name + "_results")
        if not os.path.isdir(self._results_directory):
            print(f"Creating target folder {self._results_directory}.")
            os.mkdir(self._results_directory)
        print(f"Target location set to: {self._results_directory}")

    def _assert_unique_blade_names(self):
        all_blade_rows = self._ndf_parser.get_blade_row_blades()
        all_blade_names = []
        for blade_row in all_blade_rows:
            all_blade_names.extend(all_blade_rows[blade_row])
        unique_blade_names = sorted(set(all_blade_names))
        if len(unique_blade_names) != len(all_blade_names):
            print(*all_blade_names)
            print(*unique_blade_names)
            raise (Exception("Blade names in the the NDF are not unique"))

    def _get_blade_row_gsfs(self, assembly_gsf: float):
        blade_row_gsfs = {}
        for blade_row in self._blade_rows_to_mesh:
            blade_row_gsfs[blade_row] = assembly_gsf
        return blade_row_gsfs

    def _get_blade_bl_offs(self, assembly_bl_offset: float, custom_blade_bl_offsets: dict):
        blade_bl_offs = {}
        for blade_row in self._blade_rows_to_mesh:
            blade = self._blade_rows_to_mesh[blade_row][0]
            blade_bl_offs[blade] = assembly_bl_offset
            if custom_blade_bl_offsets is not None and blade in custom_blade_bl_offsets:
                blade_bl_offs[blade] = custom_blade_bl_offsets[blade]
        return blade_bl_offs

    def _get_blade_row_spanwise_counts(
        self, stator_spanwise_count, rotor_spanwise_count, rotor_blades
    ):
        blade_row_spanwise_counts = {}
        if len(rotor_blades) == 0:
            for i, blade_row in enumerate(self._blade_rows_to_mesh):
                if i % 2 == 0:
                    # stator
                    blade_row_spanwise_counts[blade_row] = stator_spanwise_count
                else:
                    # rotor
                    blade_row_spanwise_counts[blade_row] = rotor_spanwise_count
        else:
            for blade_row in self._blade_rows_to_mesh:
                blade = self._blade_rows_to_mesh[blade_row][0]
                if blade in rotor_blades:
                    blade_row_spanwise_counts[blade_row] = rotor_spanwise_count
                else:
                    blade_row_spanwise_counts[blade_row] = stator_spanwise_count
        return blade_row_spanwise_counts

    def _get_blade_row_settings(self):
        blade_row_settings = {}
        for blade_row in self._blade_rows_to_mesh:
            blade = self._blade_rows_to_mesh[blade_row][0]
            blade_row_settings[blade_row] = []
            if self._blade_row_gsfs is not None and blade_row in self._blade_row_gsfs:
                blade_row_settings[blade_row].append(
                    ("/MESH DATA", f"Global Size Factor={self._blade_row_gsfs[blade_row]}")
                )
            if (
                self._blade_row_spanwise_counts is not None
                and blade_row in self._blade_row_spanwise_counts
            ):
                blade_row_settings[blade_row].append(
                    ("/MESH DATA", f"Spanwise Blade Distribution Option=Element Count and Size")
                )
                blade_row_settings[blade_row].append(
                    (
                        "/MESH DATA",
                        f"Number Of Spanwise Blade Elements={self._blade_row_spanwise_counts[blade_row]}",
                    )
                )
            if (
                self._blade_boundary_layer_offsets is not None
                and blade in self._blade_boundary_layer_offsets
            ):
                this_bl_f_el_off = self._blade_boundary_layer_offsets[blade]
                blade_row_settings[blade_row].append(
                    (
                        "/MESH DATA",
                        f"Boundary Layer Specification Method=Target First Element Offset",
                    )
                )
                blade_row_settings[blade_row].append(
                    (
                        f"/MESH DATA/EDGE SPLIT CONTROL:{blade} Boundary Layer Control",
                        f"Target First Element Offset={this_bl_f_el_off} [m]",
                    )
                )
            if self._custom_blade_settings is not None and blade in self._custom_blade_settings:
                blade_row_settings[blade_row].extend(self._custom_blade_settings[blade])
        return blade_row_settings

    def _read_ndf(self, ndf_file, blade_row, progress_updates_queue):
        try:
            start_dt = dt.now()
            ndf_name = os.path.split(ndf_file)[1]
            ndf_name = ndf_name.split(".")[0]
            progress_updates_queue.put([ndf_name, f"Starting {ndf_name} ndf reader"])
            progress_updates_queue.put([ndf_name, f"Start time: {start_dt}"])

            pytg_instance = launch_turbogrid(
                product_version="24.1.0",
                log_level=pyturbogrid_core.PyTurboGrid.TurboGridLogLevel.CRITICAL,
                log_filename_suffix="_" + ndf_name,
            )
            progress_updates_queue.put([ndf_name, f"pytg_instance created"])

            progress_updates_queue.put([ndf_name, f"read_ndf:: {ndf_file}"])
            pytg_instance.read_ndf(
                ndffilename=ndf_file, cadfilename=ndf_name + ".x_b", bladerow=blade_row
            )
            pytg_instance.quit()
        except Exception as e:
            progress_updates_queue.put([ndf_name, f"Reader error {e}"])
        stop_dt = dt.now()
        delta_dt = stop_dt - start_dt
        delta_dt = td(seconds=int(delta_dt / td(seconds=1)))
        deldt_parts = str(delta_dt).split(":")
        progress_updates_queue.put([ndf_name, f"Stop time: {stop_dt}"])
        progress_updates_queue.put(
            [
                ndf_name,
                f"NDF Reader Duration: {deldt_parts[0]} hours {deldt_parts[1]} minutes {deldt_parts[2]} seconds",
            ]
        )
        return ndf_name + ".tginit"


#####################################
# Global methods in the module
#####################################


def execute_ndf_bladerow(
    ndf_file,
    bladerow,
    blade,
    settings,
    progress_updates_queue,
    report_stats_angle_unit,
    report_stats_decimal_places,
    report_mesh_quality_measures,
):
    start_dt = dt.now()
    progress_updates_queue.put([bladerow + "/" + blade, f"Starting {bladerow} producer"])
    progress_updates_queue.put([bladerow + "/" + blade, f"Start time: {start_dt}"])

    pytg_instance = launch_turbogrid(
        product_version="24.1.0",
        log_level=pyturbogrid_core.PyTurboGrid.TurboGridLogLevel.CRITICAL,
        log_filename_suffix="_" + blade,
    )
    progress_updates_queue.put([bladerow + "/" + blade, f"pytg_instance created"])

    progress_updates_queue.put([bladerow + "/" + blade, f"read_ndf:: {ndf_file}"])
    pytg_instance.read_ndf(ndffilename=ndf_file, cadfilename=blade + ".x_b", bladename=blade)

    progress_updates_queue.put([bladerow + "/" + blade, f"unsuspend"])
    pytg_instance.unsuspend(object="/TOPOLOGY SET")
    progress_updates_queue.put([bladerow + "/" + blade, f"Applying meshing settings"])
    for setting in settings:
        pytg_instance.set_obj_param(setting[0], setting[1])
    write_mesh_report(
        bladerow,
        blade,
        pytg_instance,
        progress_updates_queue,
        report_stats_angle_unit,
        report_mesh_quality_measures,
        report_stats_decimal_places,
    )
    pytg_instance.save_state(filename=blade + ".tst")
    pytg_instance.save_mesh(filename=blade + ".def")
    pytg_instance.quit()
    stop_dt = dt.now()
    delta_dt = stop_dt - start_dt
    delta_dt = td(seconds=int(delta_dt / td(seconds=1)))
    deldt_parts = str(delta_dt).split(":")
    progress_updates_queue.put([bladerow + "/" + blade, f"Stop time: {stop_dt}"])
    progress_updates_queue.put(
        [
            bladerow + "/" + blade,
            f"Duration: {deldt_parts[0]} hours {deldt_parts[1]} minutes {deldt_parts[2]} seconds",
        ]
    )
    progress_updates_queue.put([bladerow + "/" + blade, "Done"])


def execute_tginit_bladerow(
    tginit_file,
    blade_row,
    blade,
    settings,
    progress_updates_queue,
    report_stats_angle_unit,
    report_stats_decimal_places,
    report_mesh_quality_measures,
):
    start_dt = dt.now()
    progress_updates_queue.put([blade_row + "/" + blade, f"Starting {blade_row} producer"])
    progress_updates_queue.put([blade_row + "/" + blade, f"Start time: {start_dt}"])

    pytg_instance = launch_turbogrid(
        product_version="24.1.0",
        log_level=pyturbogrid_core.PyTurboGrid.TurboGridLogLevel.CRITICAL,
        log_filename_suffix="_" + blade,
    )
    progress_updates_queue.put([blade_row + "/" + blade, f"pytg_instance created"])

    progress_updates_queue.put([blade_row + "/" + blade, f"read_tginit:: {tginit_file}"])
    pytg_instance.read_tginit(path=tginit_file, bladerow=blade_row)

    progress_updates_queue.put([blade_row + "/" + blade, f"unsuspend"])
    pytg_instance.unsuspend(object="/TOPOLOGY SET")
    progress_updates_queue.put([blade_row + "/" + blade, f"Applying meshing settings"])
    for setting in settings:
        pytg_instance.set_obj_param(setting[0], setting[1])
    write_mesh_report(
        blade_row,
        blade,
        pytg_instance,
        progress_updates_queue,
        report_stats_angle_unit,
        report_mesh_quality_measures,
        report_stats_decimal_places,
    )
    pytg_instance.save_state(filename=blade + ".tst")
    pytg_instance.save_mesh(filename=blade + ".def")
    pytg_instance.quit()
    stop_dt = dt.now()
    delta_dt = stop_dt - start_dt
    delta_dt = td(seconds=int(delta_dt / td(seconds=1)))
    deldt_parts = str(delta_dt).split(":")
    progress_updates_queue.put([blade_row + "/" + blade, f"Stop time: {stop_dt}"])
    progress_updates_queue.put(
        [
            blade_row + "/" + blade,
            f"Duration: {deldt_parts[0]} hours {deldt_parts[1]} minutes {deldt_parts[2]} seconds",
        ]
    )
    progress_updates_queue.put([blade_row + "/" + blade, "Done"])


def execute_ndf_blade_row_ansys_labs(
    ndf_file,
    bladerow,
    blade,
    settings,
    progress_updates_queue,
    report_stats_angle_unit,
    report_stats_decimal_places,
    report_mesh_quality_measures,
    max_file_transfer_attempts,
    container_key_file,
):
    try:
        start_dt = dt.now()
        progress_updates_queue.put([bladerow + "/" + blade, f"Starting {bladerow} producer"])
        progress_updates_queue.put([bladerow + "/" + blade, f"Start time: {start_dt}"])

        pytg_instance = pyturbogrid_core.PyTurboGrid(
            0,
            pyturbogrid_core.PyTurboGrid.TurboGridLocationType.TURBOGRID_ANSYS_LABS,
            "",
            None,
            None,
            pyturbogrid_core.PyTurboGrid.TurboGridLogLevel.CRITICAL,
            "",
            "turbogrid",
            "241-ndf",
            "_" + blade,
        )
        progress_updates_queue.put([bladerow + "/" + blade, f"pytg_instance created"])
        pytg_instance.block_each_message = True
        progress_updates_queue.put([bladerow + "/" + blade, f"Connection"])
        container_connection = Connection(
            host=pytg_instance.ftp_ip,
            user="root",
            port=pytg_instance.ftp_port,
            connect_kwargs={"key_filename": container_key_file},
        )
        progress_updates_queue.put(
            [bladerow + "/" + blade, f"IP:{pytg_instance.ftp_ip} port:{pytg_instance.ftp_port}"]
        )

        local_filepath = ndf_file
        progress_updates_queue.put([bladerow + "/" + blade, f"To container->{local_filepath}"])
        container_connection.put(remote="/", local=local_filepath)

        progress_updates_queue.put([bladerow + "/" + blade, f"read_ndf:: {ndf_file}"])
        pytg_instance.read_ndf(
            ndffilename=os.path.split(ndf_file)[1], cadfilename=blade + ".x_b", bladename=blade
        )
        progress_updates_queue.put([bladerow + "/" + blade, f"unsuspend"])
        pytg_instance.unsuspend(object="/TOPOLOGY SET")
        progress_updates_queue.put([bladerow + "/" + blade, f"Applying meshing settings"])
        for setting in settings:
            pytg_instance.set_obj_param(setting[0], setting[1])
        write_mesh_report(
            bladerow,
            blade,
            pytg_instance,
            progress_updates_queue,
            report_stats_angle_unit,
            report_mesh_quality_measures,
            report_stats_decimal_places,
        )
        pytg_instance.save_state(filename=blade + ".tst")
        pytg_instance.save_mesh(filename=blade + ".def")
        attempts = 0
        while attempts == 0 or (
            os.path.isfile(f"{blade}.tst") is False and attempts <= max_file_transfer_attempts
        ):
            progress_updates_queue.put([bladerow + "/" + blade, f"Get state attempt {attempts}"])
            time.sleep(0.5)
            container_connection.get(remote=f"/{blade}.tst", local=f"{blade}.tst")
            attempts += 1
        attempts = 0
        while attempts == 0 or (
            os.path.isfile(f"{blade}.def") is False and attempts <= max_file_transfer_attempts
        ):
            progress_updates_queue.put([bladerow + "/" + blade, f"Get def attempt {attempts}"])
            time.sleep(0.5)
            container_connection.get(remote=f"/{blade}.def", local=f"{blade}.def")
            attempts += 1
        pytg_instance.quit()

    except Exception as e:
        progress_updates_queue.put([blade, f"Producer Error {e}"])

    stop_dt = dt.now()
    delta_dt = stop_dt - start_dt
    delta_dt = td(seconds=int(delta_dt / td(seconds=1)))
    deldt_parts = str(delta_dt).split(":")
    progress_updates_queue.put([bladerow + "/" + blade, f"Stop time: {stop_dt}"])
    progress_updates_queue.put(
        [
            bladerow + "/" + blade,
            f"Duration: {deldt_parts[0]} hours {deldt_parts[1]} minutes {deldt_parts[2]} seconds",
        ]
    )
    progress_updates_queue.put([bladerow + "/" + blade, "Done"])


def read_ndf_ansys_labs(
    ndf_file,
    blade_row,
    progress_updates_queue,
    max_file_transfer_attempts,
    container_key_file,
    tgint_file_list,
):
    try:
        start_dt = dt.now()
        ndf_name = os.path.split(ndf_file)[1]
        ndf_name = ndf_name.split(".")[0]
        progress_updates_queue.put([ndf_name, f"Starting ndf reader"])
        progress_updates_queue.put([ndf_name, f"Start time: {start_dt}"])

        pytg_instance = pyturbogrid_core.PyTurboGrid(
            0,
            pyturbogrid_core.PyTurboGrid.TurboGridLocationType.TURBOGRID_ANSYS_LABS,
            "",
            None,
            None,
            pyturbogrid_core.PyTurboGrid.TurboGridLogLevel.CRITICAL,
            "",
            "turbogrid",
            "241-ndf",
            "_" + ndf_name,
        )
        progress_updates_queue.put([ndf_name, f"pytg_instance created"])
        pytg_instance.block_each_message = True
        progress_updates_queue.put([ndf_name, f"Connection"])
        container_connection = Connection(
            host=pytg_instance.ftp_ip,
            user="root",
            port=pytg_instance.ftp_port,
            connect_kwargs={"key_filename": container_key_file},
        )
        progress_updates_queue.put(
            [ndf_name, f"IP:{pytg_instance.ftp_ip} port:{pytg_instance.ftp_port}"]
        )

        local_filepath = ndf_file
        progress_updates_queue.put([ndf_name, f"To container->{local_filepath}"])
        container_connection.put(remote="/", local=local_filepath)

        progress_updates_queue.put([ndf_name, f"read_ndf:: {ndf_file}"])
        pytg_instance.read_ndf(
            ndffilename=os.path.split(ndf_file)[1],
            cadfilename=ndf_name + ".x_b",
            bladerow=blade_row,
        )
        attempts = 0
        while attempts == 0 or (
            os.path.isfile(f"{ndf_name}.tginit") is False and attempts <= max_file_transfer_attempts
        ):
            progress_updates_queue.put([ndf_name, f"Get tginit attempt {attempts}"])
            time.sleep(0.5)
            container_connection.get(remote=f"/{ndf_name}.tginit", local=f"{ndf_name}.tginit")
            attempts += 1
        attempts = 0
        while attempts == 0 or (
            os.path.isfile(f"{ndf_name}.x_b") is False and attempts <= max_file_transfer_attempts
        ):
            progress_updates_queue.put([ndf_name, f"Get x_b attempt {attempts}"])
            time.sleep(0.5)
            container_connection.get(remote=f"/{ndf_name}.x_b", local=f"{ndf_name}.x_b")
            attempts += 1
        attempts = 0
        pytg_instance.quit()

    except Exception as e:
        progress_updates_queue.put([ndf_name, f"Reader error {e}"])

    stop_dt = dt.now()
    delta_dt = stop_dt - start_dt
    delta_dt = td(seconds=int(delta_dt / td(seconds=1)))
    deldt_parts = str(delta_dt).split(":")
    progress_updates_queue.put([ndf_name, f"Stop time: {stop_dt}"])
    progress_updates_queue.put(
        [
            ndf_name,
            f"NDF Reader Duration: {deldt_parts[0]} hours {deldt_parts[1]} minutes {deldt_parts[2]} seconds",
        ]
    )
    tgint_file_list.append(ndf_name + ".tginit")


def execute_tginit_blade_row_ansys_labs(
    tginit_file,
    blade_row,
    blade,
    settings,
    progress_updates_queue,
    report_stats_angle_unit,
    report_stats_decimal_places,
    report_mesh_quality_measures,
    max_file_transfer_attempts,
    container_key_file,
):
    try:
        start_dt = dt.now()
        progress_updates_queue.put([blade_row + "/" + blade, f"Starting {blade_row} producer"])
        progress_updates_queue.put([blade_row + "/" + blade, f"Start time: {start_dt}"])

        pytg_instance = pyturbogrid_core.PyTurboGrid(
            0,
            pyturbogrid_core.PyTurboGrid.TurboGridLocationType.TURBOGRID_ANSYS_LABS,
            "",
            None,
            None,
            pyturbogrid_core.PyTurboGrid.TurboGridLogLevel.CRITICAL,
            "",
            "turbogrid",
            "241-ndf",
            "_" + blade,
        )
        progress_updates_queue.put([blade_row + "/" + blade, f"pytg_instance created"])
        pytg_instance.block_each_message = True
        progress_updates_queue.put([blade_row + "/" + blade, f"Connection"])
        container_connection = Connection(
            host=pytg_instance.ftp_ip,
            user="root",
            port=pytg_instance.ftp_port,
            connect_kwargs={"key_filename": container_key_file},
        )
        progress_updates_queue.put(
            [blade_row + "/" + blade, f"IP:{pytg_instance.ftp_ip} port:{pytg_instance.ftp_port}"]
        )

        local_filepath = tginit_file
        progress_updates_queue.put([blade_row + "/" + blade, f"To container->{local_filepath}"])
        container_connection.put(remote="/", local=local_filepath)
        local_filepath = tginit_file[:-7] + ".x_b"
        progress_updates_queue.put([blade_row + "/" + blade, f"To container->{local_filepath}"])
        container_connection.put(remote="/", local=local_filepath)
        progress_updates_queue.put([blade_row + "/" + blade, f"read_tginit:: {tginit_file}"])
        pytg_instance.read_tginit(path=os.path.split(tginit_file)[1], bladerow=blade_row)
        progress_updates_queue.put([blade_row + "/" + blade, f"unsuspend"])
        pytg_instance.unsuspend(object="/TOPOLOGY SET")
        progress_updates_queue.put([blade_row + "/" + blade, f"Applying meshing settings"])
        for setting in settings:
            pytg_instance.set_obj_param(setting[0], setting[1])
        write_mesh_report(
            blade_row,
            blade,
            pytg_instance,
            progress_updates_queue,
            report_stats_angle_unit,
            report_mesh_quality_measures,
            report_stats_decimal_places,
        )
        pytg_instance.save_state(filename=blade + ".tst")
        pytg_instance.save_mesh(filename=blade + ".def")
        attempts = 0
        while attempts == 0 or (
            os.path.isfile(f"{blade}.tst") is False and attempts <= max_file_transfer_attempts
        ):
            progress_updates_queue.put([blade_row + "/" + blade, f"Get state attempt {attempts}"])
            time.sleep(0.5)
            container_connection.get(remote=f"/{blade}.tst", local=f"{blade}.tst")
            attempts += 1
        attempts = 0
        while attempts == 0 or (
            os.path.isfile(f"{blade}.def") is False and attempts <= max_file_transfer_attempts
        ):
            progress_updates_queue.put([blade_row + "/" + blade, f"Get def attempt {attempts}"])
            time.sleep(0.5)
            container_connection.get(remote=f"/{blade}.def", local=f"{blade}.def")
            attempts += 1
        pytg_instance.quit()

    except Exception as e:
        progress_updates_queue.put([blade, f"Producer Error {e}"])

    stop_dt = dt.now()
    delta_dt = stop_dt - start_dt
    delta_dt = td(seconds=int(delta_dt / td(seconds=1)))
    deldt_parts = str(delta_dt).split(":")
    progress_updates_queue.put([blade_row + "/" + blade, f"Stop time: {stop_dt}"])
    progress_updates_queue.put(
        [
            blade_row + "/" + blade,
            f"Duration: {deldt_parts[0]} hours {deldt_parts[1]} minutes {deldt_parts[2]} seconds",
        ]
    )
    progress_updates_queue.put([blade_row + "/" + blade, "Done"])


def write_mesh_report(
    blade_row,
    blade,
    pytg_instance,
    progress_updates_queue,
    report_stats_angle_unit,
    report_mesh_quality_measures,
    report_stats_decimal_places,
):
    ALL_DOMAINS = "ALL"
    progress_updates_queue.put([blade_row + "/" + blade, f"Getting CCLObjectDB"])
    ccl_db = CCLObjectDB(pytg_instance)
    domain_list = [obj.get_name() for obj in ccl_db.get_objects_by_type("DOMAIN")]
    domain_list.append(ALL_DOMAINS)
    case_info = OrderedDict()
    case_info["Case Name"] = blade
    case_info["Number of Bladesets"] = ccl_db.get_object_by_path(
        "/GEOMETRY/MACHINE DATA"
    ).get_value("Bladeset Count")
    case_info["Report Date"] = dt.today()
    ms = mesh_statistics.MeshStatistics(pytg_instance)
    domain_count = dict()
    progress_updates_queue.put([blade_row + "/" + blade, f"Getting mesh statistics"])
    for domain in domain_list:
        ms.update_mesh_statistics(domain)
        domain_count[ms.get_domain_label(domain)] = ms.get_mesh_statistics().copy()
    ms.update_mesh_statistics(ALL_DOMAINS)
    all_dom_stats = ms.get_mesh_statistics()
    stat_table_rows_raw = ms.get_table_rows()
    stat_table_rows = []
    convert_to_degree = report_stats_angle_unit.lower()[0:3] == "deg"
    for row in stat_table_rows_raw:
        if len(row) != 5 or row[0] == "Mesh Measure":
            stat_table_rows.append(row)
            continue
        if row[0] not in report_mesh_quality_measures:
            continue
        new_row = [row[0]]
        for i in range(1, 5):
            value_parts = row[i].split()
            value = float(value_parts[0])
            if len(value_parts) == 2:
                if convert_to_degree and "rad" in value_parts[1]:
                    value = value * 180.0 / math.pi
                    value_parts[1] = "[deg]"
                if new_row[0] != "Minimum Volume":
                    value = round(value, report_stats_decimal_places)
                new_row.append(str(value) + " " + value_parts[1])
            else:
                value = round(value, report_stats_decimal_places)
                new_row.append(str(value))
        stat_table_rows.append(new_row)
    hist_var_list = [
        "Connectivity Number",
        "Edge Length Ratio",
        "Element Volume Ratio",
        "Maximum Face Angle",
        "Minimum Face Angle",
        "Minimum Volume",
        "Orthogonality Angle",
        "Skewness",
    ]
    hist_var_list = [x for x in hist_var_list if x in report_mesh_quality_measures]
    hist_dict = dict()
    progress_updates_queue.put([blade_row + "/" + blade, f"Creating histograms statistics"])
    for var in hist_var_list:
        file_name = blade + "_tg_hist_" + var + ".png"
        var_units = all_dom_stats[var]["Units"]
        if var_units == "rad":
            var_units = "deg"
        ms.create_histogram(
            variable=var,
            use_percentages=True,
            bin_units=var_units,
            image_file=file_name,
            show=False,
        )
        hist_dict[var] = file_name
    environment = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))
    html_template = environment.get_template("report_template.html")
    html_context = {
        "case_info": case_info,
        "domain_count": domain_count,
        "stat_table_rows": stat_table_rows,
        "hist_dict": hist_dict,
    }
    progress_updates_queue.put([blade_row + "/" + blade, f"Writing report"])
    filename = f"{blade}_tg_report.html"
    content = html_template.render(html_context)
    with open(filename, mode="w", encoding="utf-8") as message:
        message.write(content)

    progress_updates_queue.put([blade_row + "/" + blade, f"Completed {blade} producer"])
    progress_updates_queue.put(
        [
            blade_row + "/" + blade,
            f"Total vertices: {domain_count[ms.get_domain_label(ALL_DOMAINS)]['Vertices']['Count']}",
        ]
    )
    progress_updates_queue.put(
        [
            blade_row + "/" + blade,
            f"Total elements: {domain_count[ms.get_domain_label(ALL_DOMAINS)]['Elements']['Count']}",
        ]
    )
    if domain_count[ms.get_domain_label(ALL_DOMAINS)]["Minimum Volume"]["Minimum"] < 0:
        progress_updates_queue.put([blade_row + "/" + blade, f"ERROR: Negative volume elements"])


def publish_progress_updates(progress_updates_queue, num_prods, ndf_file_name):
    print(f"Reporter: Running for {num_prods} rows", flush=True)
    # consume work
    num_prods_done = 0
    blade_time_infos = {}
    blade_count_infos = {}
    blade_errors = []
    total_verts = 0
    total_elems = 0
    while True:
        # get a unit of work
        item = progress_updates_queue.get()
        # check for stop
        if item[1] == "Done":
            num_prods_done += 1
        print(": ".join(item), flush=True)
        if ":" in item[1] and len(item_parts := item[1].split(":")) == 2:
            if (
                item[0] != "User Experience Time"
                and item_parts[0] != "NDF Reader Duration"
                and item[0] not in blade_count_infos
            ):
                blade_count_infos[item[0]] = {}
            if item_parts[0] == "Total vertices":
                blade_count_infos[item[0]]["verts"] = item_parts[1]
                total_verts += int(item_parts[1].strip())
            if item_parts[0] == "Total elements":
                blade_count_infos[item[0]]["elems"] = item_parts[1]
                total_elems += int(item_parts[1].strip())
            if item_parts[0] == "Duration":
                blade_time_infos[item[0]] = item_parts[1]
            if item_parts[0].lower() == "error":
                blade_errors.append(f"{item[0]}: {item_parts[1]}")
        if num_prods_done == num_prods + 1:
            break
    # all done
    blade_names = list(blade_count_infos.keys())
    if "Total" not in blade_count_infos:
        blade_count_infos["Total"] = {"verts": str(total_verts), "elems": str(total_elems)}
    if len(blade_errors) == 0:
        blade_errors.append(f"No errors reported.")
    environment = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))
    html_template = environment.get_template("summary_template.html")
    html_context = {
        "case_name": ndf_file_name,
        "case_time_infos": blade_time_infos,
        "blades": blade_names,
        "blade_count_infos": blade_count_infos,
        "blade_errors": blade_errors,
    }
    filename = f"{os.path.split(ndf_file_name)[1].split('.')[0]}_tg_mbr_summary.html"
    content = html_template.render(html_context)
    with open(filename, mode="w", encoding="utf-8") as message:
        print(f"Writing summary {filename}")
        message.write(content)
    print("Reporter: Done", flush=True)
