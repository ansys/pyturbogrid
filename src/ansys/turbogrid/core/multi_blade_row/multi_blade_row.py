# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-FileCopyrightText: 2023 ANSYS, Inc. All rights reserved
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# A multi_blade_row (MBR) instance represents a single rotating machine.
# MBR will spawn a single_blade_row (SBR) for each blade that is being considered.
# MBR job dispatch has two concepts. Jobs may be dispatched to a single row,
# or multiple rows in parallel.
"""Module for working on a multi blade row turbomachinery case using PyTurboGrid instances in parallel."""

import concurrent.futures
from enum import IntEnum
from functools import partial
import json
import math
import os
from pathlib import Path, PurePath
import queue
import traceback
from typing import Optional

from ansys.turbogrid.api.pyturbogrid_core import PyTurboGrid

from ansys.turbogrid.core.launcher.container_helpers import container_helpers
from ansys.turbogrid.core.launcher.launcher import launch_turbogrid, launch_turbogrid_container
from ansys.turbogrid.core.multi_blade_row.single_blade_row import single_blade_row
import ansys.turbogrid.core.ndf_parser.ndf_parser as ndf_parser


class multi_blade_row:
    """This class spawns multiple TG instances and can initialize and control an entire blade row at once."""

    initialized: bool = False
    init_file_path: Path
    all_blade_rows: dict
    all_blade_row_keys: list
    base_gsf: dict[str, float]
    turbogrid_location_type: PyTurboGrid.TurboGridLocationType
    tg_container_launch_settings: dict[str, str]
    turbogrid_path: str
    ndf_base_path: str
    ndf_file_name: str
    ndf_file_extension: str
    tg_kw_args = {}

    class MachineSizingStrategy(IntEnum):
        """
        These are machine sizing strategies that can be optionally applied using set_machine_sizing_strategy.

        Description
        -----------
        MIN_FACE_AREA
            This strategy attempts to size each blade row so that the element sizes are all equal,
            by using the blade row with the smallest face area as the target.
            This is the most robust strategy, although can result in many elements for the larger blade rows,
            and if the blade row is too large, the sizing may be huge.
        """

        MIN_FACE_AREA = 1

    # Consider passing in the filename (whether ndf or tginit) as initializing as raii
    def __init__(self):
        """Empty initializer."""
        pass

    def __del__(self):
        """This method will quit all TG instances."""
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(self.tg_worker_instances)
        ) as executor:
            futures = [
                executor.submit(self.__quit__, val) for key, val in self.tg_worker_instances.items()
            ]
            concurrent.futures.wait(futures)

    def init_from_ndf(
        self,
        ndf_path: str,
        use_existing_tginit_cad: bool = False,
        tg_log_level: PyTurboGrid.TurboGridLogLevel = PyTurboGrid.TurboGridLogLevel.INFO,
        turbogrid_path: str = None,
        turbogrid_location_type=PyTurboGrid.TurboGridLocationType.TURBOGRID_INSTALL,
        tg_container_launch_settings: dict[str, str] = {},
        tg_kw_args={},
    ):
        """
        Initialize the MBR representation with an ndf file.
        The file must be compatible with TurboGrid import ndf.

        Parameters
        ----------
        ndf_path : str
            The full absolute path and file name for the ndf file.
        use_existing_tginit_cad : bool, default: ``False``
            If true, a .tginit and .x_b file with the same name as the ndf_path will be used.
            If false, TG will (re)generate these files.
        tg_log_level : PyTurboGrid.TurboGridLogLevel, default: ``INFO``
            Logging settings for the underlying TG instances.
            The log_filename_suffix will be the ndf file name, and the flowpath for the worker instances.
        turbogrid_path : str, default: ``None``
            Optional specifying for cfxtg path. Otherwise, launcher will attempt to find it automatically.
        turbogrid_location_type : PyTurboGrid.TurboGridLocationType, default: ``TURBOGRID_INSTALL``
            For container/cloud operation, this can be changed. Generally only used by devs/github.
        tg_container_launch_settings : dict[str, str], default: ``{}``
            For dev usage.
        """
        self.tg_kw_args = tg_kw_args
        self.turbogrid_path = turbogrid_path
        self.turbogrid_location_type = turbogrid_location_type
        self.tg_container_launch_settings = tg_container_launch_settings
        self.all_blade_rows = ndf_parser.NDFParser(ndf_path).get_blade_row_blades()
        self.all_blade_row_keys = list(self.all_blade_rows.keys())
        print(f"Blade Rows to mesh: {self.all_blade_rows}")
        ndf_name = os.path.basename(ndf_path)
        self.ndf_base_path = PurePath(ndf_path).parent.as_posix()
        self.ndf_file_name, self.ndf_file_extension = os.path.splitext(ndf_name)
        print(f"{ndf_name=}")

        if use_existing_tginit_cad == False:
            tg_port = None
            tg_execution_control = None
            if (
                self.turbogrid_location_type
                == PyTurboGrid.TurboGridLocationType.TURBOGRID_RUNNING_CONTAINER
            ):
                tg_execution_control = launch_turbogrid_container(
                    self.tg_container_launch_settings["cfxtg_command_name"],
                    self.tg_container_launch_settings["image_name"],
                    self.tg_container_launch_settings["container_name"],
                    self.tg_container_launch_settings["cfx_version"],
                    self.tg_container_launch_settings["license_file"],
                    self.tg_container_launch_settings["keep_stopped_containers"],
                    self.tg_container_launch_settings["container_env_dict"],
                )
                tg_port = tg_execution_control.socket_port
            pyturbogrid_instance = launch_turbogrid(
                log_level=tg_log_level,
                log_filename_suffix="_" + ndf_name,
                turbogrid_path=self.turbogrid_path,
                turbogrid_location_type=self.turbogrid_location_type,
                port=tg_port,
            )
            if (
                self.turbogrid_location_type
                == PyTurboGrid.TurboGridLocationType.TURBOGRID_RUNNING_CONTAINER
            ):
                pyturbogrid_instance.block_each_message = True
                print(
                    f"get_container_connection {tg_execution_control.ftp_port} {self.tg_container_launch_settings['ssh_key_filename']}"
                )
                container = container_helpers.get_container_connection(
                    tg_execution_control.ftp_port,
                    self.tg_container_launch_settings["ssh_key_filename"],
                )
                print(f"transfer files to container {ndf_path}")
                container_helpers.transfer_files_to_container(
                    container,
                    self.ndf_base_path,
                    [ndf_name],
                )
                print(f"files transferred")
                # full path and file name in the container
                ndf_path = "/" + ndf_name

            pyturbogrid_instance.read_ndf(
                ndffilename=ndf_path,
                cadfilename=self.ndf_file_name + ".x_b",
                bladerow=self.all_blade_row_keys[0],
            )

            if (
                turbogrid_location_type
                == PyTurboGrid.TurboGridLocationType.TURBOGRID_RUNNING_CONTAINER
            ):
                print(f"Get file from container")
                container_helpers.transfer_files_from_container(
                    container,
                    self.ndf_base_path,
                    [self.ndf_file_name + ".x_b", self.ndf_file_name + ".tginit"],
                )
                print(f"file transferred")
            pyturbogrid_instance.quit()
            if tg_execution_control:
                del tg_execution_control

        self.tg_worker_instances = {key: single_blade_row() for key in self.all_blade_row_keys}
        self.base_gsf = {key: 1.0 for key in self.all_blade_row_keys}
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(self.tg_worker_instances)
        ) as executor:
            job = partial(self.__launch_instances__, self.ndf_file_name, tg_log_level)
            futures = [
                executor.submit(job, key, val) for key, val in self.tg_worker_instances.items()
            ]
            concurrent.futures.wait(futures)

    def init_from_tgmachine(self, tgmachine_path: str, tg_log_level):
        """
        Initialize the MBR representation with a TGMachine file.
        Still under development
        """
        print(f"init_from_tgmachine tgmachine_path = {tgmachine_path}")
        tgmachine_file = open(tgmachine_path, "r")
        machine_info = json.load(tgmachine_file)
        n_rows: int = machine_info["Number of Blade Rows"]
        interface_method: str = machine_info["Interface Method"]
        print(f"   n_rows = {n_rows}")
        self.all_blade_row_keys = machine_info["Blade Rows"]
        self.neighbor_dict = {}
        for i in range(len(self.all_blade_row_keys)):
            if interface_method == "Fully Extend":
                left_neighbor = None
                right_neighbor = None
            elif interface_method == "Neighbors":
                left_neighbor = self.all_blade_row_keys[i - 1] if i > 0 else None
                right_neighbor = (
                    self.all_blade_row_keys[i + 1] if i < len(self.all_blade_row_keys) - 1 else None
                )
                # since the neighbors are inf, extract the file name only, and append .crv
                if left_neighbor:
                    left_neighbor = os.path.splitext(left_neighbor)[0] + ".crv"
                if right_neighbor:
                    right_neighbor = os.path.splitext(right_neighbor)[0] + ".crv"
            self.neighbor_dict[self.all_blade_row_keys[i]] = [left_neighbor, right_neighbor]
        print(f"   {self.neighbor_dict=}")
        self.tg_worker_instances = {key: single_blade_row() for key in self.all_blade_row_keys}
        self.base_gsf = {key: 1.0 for key in self.all_blade_row_keys}
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(self.tg_worker_instances)
        ) as executor:
            job = partial(
                self.__launch_instances_inf__,
                tg_log_level,
                os.path.split(tgmachine_path)[0],
                self.neighbor_dict,
            )
            futures = [
                executor.submit(job, key, val) for key, val in self.tg_worker_instances.items()
            ]
            concurrent.futures.wait(futures)

    def get_average_background_face_areas(self) -> dict:
        """
        Query the background topology face areas for each blade row.
        This is TurboGrid specific information.
        """
        return {
            tg_worker_name: tg_worker_instance.pytg.query_average_background_face_area()
            for tg_worker_name, tg_worker_instance in self.tg_worker_instances.items()
        }

    def get_average_base_face_areas(self) -> dict:
        """
        Query the base topology face areas for each blade row.
        This is TurboGrid specific information.
        """
        return {
            tg_worker_name: tg_worker_instance.pytg.query_average_base_face_area()
            for tg_worker_name, tg_worker_instance in self.tg_worker_instances.items()
        }

    def get_element_counts(self) -> dict:
        """
        Query the element count for each blade row.
        """
        return {
            tg_worker_name: self.__get_ec__(tg_worker_instance)
            for tg_worker_name, tg_worker_instance in self.tg_worker_instances.items()
        }

    def get_spanwise_element_counts(self) -> dict:
        """
        Query the number of spanwise elements for each blade row.
        """
        return {
            tg_worker_name: int(tg_worker_instance.pytg.query_number_of_spanwise_elements())
            for tg_worker_name, tg_worker_instance in self.tg_worker_instances.items()
        }

    def get_local_gsf(self) -> dict:
        """
        Query the blade-row-local global size factor for each blade row.
        """
        return {
            tg_worker_name: float(
                tg_worker_instance.pytg.get_object_param(
                    object="/MESH DATA", param="Global Size Factor"
                )
            )
            for tg_worker_name, tg_worker_instance in self.tg_worker_instances.items()
        }

    def get_blade_row_names(self) -> list:
        return self.all_blade_row_keys

    def set_global_size_factor(self, blade_row_name: str, size_factor: float):
        """
        Set the blade-row-local global size factor for blade_row_name.
        """
        if blade_row_name not in self.tg_worker_instances:
            raise Exception(
                f"No blade row with name {blade_row_name}. Available names: {self.all_blade_row_keys}"
            )
        self.tg_worker_instances[blade_row_name].pytg.set_global_size_factor(size_factor)

    def set_number_of_blade_sets(self, blade_row_name: str, number_of_blade_sets: int):
        """
        Set the number of blade sets for blade_row_name.
        """
        if blade_row_name not in self.tg_worker_instances:
            raise Exception(
                f"No blade row with name {blade_row_name}. Available names: {self.all_blade_row_keys}"
            )
        self.tg_worker_instances[blade_row_name].pytg.set_obj_param(
            object="/GEOMETRY/MACHINE DATA",
            param_val_pairs=f"Bladeset Count = {number_of_blade_sets}",
        )

    def set_machine_sizing_strategy(self, strategy: MachineSizingStrategy):
        """
        Set the automatic machine sizing strategy for this machine.
        The machine simulation must be initialized already.

        """
        # When 3.9 is dropped, we can use match/case
        if strategy == self.MachineSizingStrategy.MIN_FACE_AREA:
            original_face_areas = self.get_average_base_face_areas()
            target_face_area = min(original_face_areas.values())
            base_gsf = {
                key: math.sqrt(original_face_area / target_face_area)
                for key, original_face_area in original_face_areas.items()
            }
            self.set_machine_base_size_factors(base_gsf)
        else:
            raise Exception(f"MachineSizingStrategy {strategy.name} not supported")

    def set_machine_base_size_factors(self, size_factors: dict[str, float]):
        """
        Manual setting for per-blade-row sizings, and set the machine size factor to 1.0.

        """
        # print(f"set_machine_base_size_factors {size_factors}")
        # Check sizes here!
        self.base_gsf = size_factors
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(self.tg_worker_instances)
        ) as executor:
            job = partial(self.__set_gsf__, 1.0)
            futures = [
                executor.submit(job, key, val) for key, val in self.tg_worker_instances.items()
            ]
            concurrent.futures.wait(futures)

    def set_machine_size_factor(self, size_factor: float):
        """
        Set the entire machine's size factor. Higher means more (and smaller) elements.

        """
        # print(f"set_machine_size_factor base {self.base_gsf} factor {size_factor}")
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(self.tg_worker_instances)
        ) as executor:
            job = partial(self.__set_gsf__, size_factor)
            futures = [
                executor.submit(job, key, val) for key, val in self.tg_worker_instances.items()
            ]
            concurrent.futures.wait(futures)

    def set_machine_target_node_count(self, target_node_count: int):
        """
        Instead of size factors, a target node count can be specified.
        Less robust but more predictable than using a size factor.
        Count must be over 50,000, and a count too high may be problematic.

        """
        print(f"set_machine_target_node_count target_node_count {target_node_count}")
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(self.tg_worker_instances)
        ) as executor:
            job = partial(self.__set_tnc__, target_node_count)
            futures = [
                executor.submit(job, key, val) for key, val in self.tg_worker_instances.items()
            ]
            concurrent.futures.wait(futures)

    def save_meshes(self):
        """
        Write out the .def files representing the entire blade row.
        Blade rows that threw errors will not write meshes (check the logs.)
        The assembly can be opened directly in CFX-Pre (Meshes contain some topology.)

        """
        print(f"save_meshes")
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(self.tg_worker_instances)
        ) as executor:
            futures = [
                executor.submit(self.__save_mesh__, key, val)
                for key, val in self.tg_worker_instances.items()
            ]
            concurrent.futures.wait(futures)

    def plot_machine(self):
        """
        Display the machine's mesh boundaries using pyvista.
        Experimental.

        """
        import random

        import pyvista as pv

        p = pv.Plotter()
        print("plot_machine")
        threadsafe_queue: queue.Queue = queue.Queue()
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(self.tg_worker_instances)
        ) as executor:
            job = partial(self.__write_boundary_polys__, threadsafe_queue)
            futures = [executor.submit(job, val) for key, val in self.tg_worker_instances.items()]
            concurrent.futures.wait(futures)

        # for tg_worker_name, tg_worker_instance in self.tg_worker_instances.items():
        #     print(f"  {tg_worker_name}")
        #     for b_m in tg_worker_instance.pytg.getBoundaryGeometry():
        #         p.add_mesh(b_m, color=[random.random(), random.random(), random.random()])
        print("add meshes")
        while threadsafe_queue.empty() == False:
            p.add_mesh(
                threadsafe_queue.get(), color=[random.random(), random.random(), random.random()]
            )
        print("show")
        p.show(jupyter_backend="client")

    def __launch_instances__(self, ndf_file_name, tg_log_level, tg_worker_name, tg_worker_instance):
        """
        :meta private:
        """
        try:

            tg_port = None
            if (
                self.turbogrid_location_type
                == PyTurboGrid.TurboGridLocationType.TURBOGRID_RUNNING_CONTAINER
            ):
                tg_worker_instance.tg_execution_control = launch_turbogrid_container(
                    self.tg_container_launch_settings["cfxtg_command_name"],
                    self.tg_container_launch_settings["image_name"],
                    self.tg_container_launch_settings["container_name"],
                    self.tg_container_launch_settings["cfx_version"],
                    self.tg_container_launch_settings["license_file"],
                    self.tg_container_launch_settings["keep_stopped_containers"],
                    self.tg_container_launch_settings["container_env_dict"],
                )
                tg_port = tg_worker_instance.tg_execution_control.socket_port
            tg_worker_instance.pytg = launch_turbogrid(
                log_level=tg_log_level,
                log_filename_suffix=f"_{ndf_file_name}_{tg_worker_name}",
                additional_kw_args=self.tg_kw_args,
                turbogrid_path=self.turbogrid_path,
                turbogrid_location_type=self.turbogrid_location_type,
                port=tg_port,
            )
            tg_worker_instance.pytg.block_each_message = True

            if (
                self.turbogrid_location_type
                == PyTurboGrid.TurboGridLocationType.TURBOGRID_RUNNING_CONTAINER
            ):
                print(
                    f"get_container_connection {tg_worker_instance.tg_execution_control.ftp_port} {self.tg_container_launch_settings['ssh_key_filename']}"
                )
                container = container_helpers.get_container_connection(
                    tg_worker_instance.tg_execution_control.ftp_port,
                    self.tg_container_launch_settings["ssh_key_filename"],
                )
                print(f"transfer files to container {ndf_file_name}")
                container_helpers.transfer_files_to_container(
                    container,
                    self.ndf_base_path,
                    [ndf_file_name + ".tginit", ndf_file_name + ".x_b"],
                )
                print(f"files transferred")

            tg_worker_instance.pytg.read_tginit(
                path=ndf_file_name + ".tginit", bladerow=tg_worker_name
            )
            tg_worker_instance.pytg.set_obj_param(
                object="/GEOMETRY/INLET", param_val_pairs="Opening Mode = Fully extend"
            )
            tg_worker_instance.pytg.set_obj_param(
                object="/GEOMETRY/OUTLET", param_val_pairs="Opening Mode = Fully extend"
            )
            # tg_worker_instance.pytg.set_obj_param(
            #     object="/TOPOLOGY SET", param_val_pairs="ATM Stop After Main Layers=True"
            # )
            tg_worker_instance.pytg.unsuspend(object="/TOPOLOGY SET")
            # av_bg_face_area = tg_worker_instance.pytg.query_average_background_face_area()
            # print(f"{tg_worker_name=} {av_bg_face_area=}")
        except Exception as e:
            print(f"{tg_worker_instance} exception on __launch_instances__: {e}")
            print(f"{tg_worker_instance} traceback: {traceback.extract_tb(e.__traceback__)}")

    def __launch_instances_inf__(
        self,
        tg_log_level,
        base_dir,
        neighbor_dict: dict[str, Optional[str]],
        tg_worker_name,
        tg_worker_instance,
    ):
        """
        :meta private:
        """
        try:
            tg_worker_instance.pytg = launch_turbogrid(
                log_level=tg_log_level,
                log_filename_suffix=f"_{tg_worker_name}",
                additional_kw_args=self.tg_kw_args,
            )
            tg_worker_instance.pytg.block_each_message = True
            tg_worker_instance.pytg.read_inf(filename=os.path.join(base_dir, tg_worker_name))
            if neighbor_dict[tg_worker_name][0]:
                tg_worker_instance.pytg.set_obj_param(
                    object="/GEOMETRY/INLET",
                    param_val_pairs=f"Opening Mode = Adjacent blade, Input Filename = {os.path.join(base_dir, neighbor_dict[tg_worker_name][0])}",
                )
                tg_worker_instance.pytg.set_obj_param(
                    object="/MESH DATA",
                    param_val_pairs=f"Inlet Domain = Off",
                )
            else:
                tg_worker_instance.pytg.set_obj_param(
                    object="/GEOMETRY/INLET", param_val_pairs=f"Opening Mode = Fully extend"
                )
            if neighbor_dict[tg_worker_name][1]:
                tg_worker_instance.pytg.set_obj_param(
                    object="/GEOMETRY/OUTLET",
                    param_val_pairs=f"Opening Mode = Adjacent blade, Input Filename = {os.path.join(base_dir, neighbor_dict[tg_worker_name][1])}",
                )
                tg_worker_instance.pytg.set_obj_param(
                    object="/MESH DATA",
                    param_val_pairs=f"Outlet Domain = Off",
                )
            else:
                tg_worker_instance.pytg.set_obj_param(
                    object="/GEOMETRY/OUTLET", param_val_pairs=f"Opening Mode = Fully extend"
                )
            tg_worker_instance.pytg.unsuspend(object="/TOPOLOGY SET")
        except Exception as e:
            print(f"{tg_worker_instance} exception on __launch_instances_inf__: {e}")

    def __set_gsf__(self, size_factor, tg_worker_name, tg_worker_instance):
        """
        :meta private:
        """
        tg_worker_instance.pytg.set_global_size_factor(self.base_gsf[tg_worker_name] * size_factor)

    def __set_tnc__(self, target_node_count, tg_worker_name, tg_worker_instance):
        """
        :meta private:
        """
        tg_worker_instance.pytg.set_obj_param(
            object="/MESH DATA",
            param_val_pairs=f"Mesh Size Specification Mode = Target Total Node Count, "
            f"Target Mesh Granularity = Specify, "
            f"Target Mesh Node Count = {int(target_node_count)}",
        )

    def __get_ec__(self, tg_worker_instance) -> int:
        """
        :meta private:
        """
        ec = 0
        try:
            ec = int(tg_worker_instance.pytg.query_mesh_statistics()["Elements"]["Count"])
        except:
            pass
        return ec

    def __save_mesh__(self, tg_worker_name, tg_worker_instance):
        """
        :meta private:
        """
        tg_worker_instance.pytg.save_mesh(tg_worker_name + ".def")

    def __quit__(self, tg_worker_instance):
        """
        :meta private:
        """
        tg_worker_instance.pytg.quit()

    def __write_boundary_polys__(self, threadsafe_queue: queue.Queue, tg_worker_instance):
        """
        :meta private:
        """
        for b_m in tg_worker_instance.pytg.getBoundaryGeometry():
            threadsafe_queue.put(b_m)
