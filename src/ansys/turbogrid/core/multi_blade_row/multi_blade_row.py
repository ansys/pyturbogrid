# Copyright (c) 2024 ANSYS, Inc. All rights reserved
#
# A multi_blade_row (MBR) instance represents a single rotating machine.
# MBR will spawn a single_blade_row (SBR) for each blade that is being considered.
# MBR job dispatch has two concepts. Jobs may be dispatched to a single row,
# or multiple rows in parallel.

import os
import ansys.turbogrid.core.ndf_parser.ndf_parser as ndf_parser

from ansys.turbogrid.core.launcher.launcher import launch_turbogrid
from ansys.turbogrid.core.multi_blade_row.single_blade_row import single_blade_row
from ansys.turbogrid.api import pyturbogrid_core
from pathlib import Path
from functools import partial
import concurrent.futures
import json


class multi_blade_row:
    initialized: bool = False
    init_file_path: Path
    all_blade_rows: dict
    all_blade_row_keys: list
    base_gsf: dict[str, float]

    # Consider passing in the filename (whether ndf or tginit) as initializing as raii
    def __init__(self):
        pass

    def __del__(self):
        for tg_worker_name, tg_worker in self.tg_worker_instances.items():
            tg_worker.pytg.quit()
        pass

    # a A TGInit parser would need to be written for this to work
    # def init_from_tginit(self, tginit_path: str):
    #     pass

    def init_from_ndf(self, ndf_path: str):
        self.all_blade_rows = ndf_parser.NDFParser(ndf_path).get_blade_row_blades()
        self.all_blade_row_keys = list(self.all_blade_rows.keys())
        print(f"Blade Rows to mesh: {self.all_blade_rows}")
        ndf_name = os.path.basename(ndf_path)
        ndf_file_name, ndf_file_extension = os.path.splitext(ndf_name)
        print(f"{ndf_name=}")
        # pyturbogrid_instance = launch_turbogrid(
        #     log_level=pyturbogrid_core.PyTurboGrid.TurboGridLogLevel.DEBUG,
        #     log_filename_suffix="_" + ndf_name,
        # )
        # pyturbogrid_instance.read_ndf(
        #     ndffilename=ndf_path,
        #     cadfilename=ndf_file_name + ".x_b",
        #     bladerow=self.all_blade_row_keys[0],
        # )
        # pyturbogrid_instance.quit()
        self.tg_worker_instances = {key: single_blade_row() for key in self.all_blade_row_keys}
        self.base_gsf = {key: 1.0 for key in self.all_blade_row_keys}
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(self.tg_worker_instances)
        ) as executor:
            job = partial(self.__launch_instances__, ndf_file_name)
            futures = [
                executor.submit(job, key, val) for key, val in self.tg_worker_instances.items()
            ]
            concurrent.futures.wait(futures)

    def init_from_tgmachine(self, tgmachine_path: str):
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
                self.__launch_instances_inf__, os.path.split(tgmachine_path)[0], self.neighbor_dict
            )
            futures = [
                executor.submit(job, key, val) for key, val in self.tg_worker_instances.items()
            ]
            concurrent.futures.wait(futures)

    def get_average_background_face_areas(self) -> dict:
        return {
            tg_worker_name: tg_worker_instance.pytg.query_average_background_face_area()
            for tg_worker_name, tg_worker_instance in self.tg_worker_instances.items()
        }

    def get_average_base_face_areas(self) -> dict:
        return {
            tg_worker_name: tg_worker_instance.pytg.query_average_base_face_area()
            for tg_worker_name, tg_worker_instance in self.tg_worker_instances.items()
        }

    def get_element_counts(self) -> dict:
        return {
            tg_worker_name: self.__get_ec__(tg_worker_instance)
            for tg_worker_name, tg_worker_instance in self.tg_worker_instances.items()
        }

    def get_spanwise_element_counts(self) -> dict:
        return {
            tg_worker_name: int(tg_worker_instance.pytg.query_number_of_spanwise_elements())
            for tg_worker_name, tg_worker_instance in self.tg_worker_instances.items()
        }

    def get_local_gsf(self) -> dict:
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
        if blade_row_name not in self.tg_worker_instances:
            raise Exception(
                f"No blade row with name {blade_row_name}. Available names: {self.all_blade_row_keys}"
            )
        self.tg_worker_instances[blade_row_name].pytg.set_global_size_factor(size_factor)

    def set_number_of_blade_sets(self, blade_row_name: str, number_of_blade_sets: int):
        if blade_row_name not in self.tg_worker_instances:
            raise Exception(
                f"No blade row with name {blade_row_name}. Available names: {self.all_blade_row_keys}"
            )
        self.tg_worker_instances[blade_row_name].pytg.set_obj_param(
            object="/GEOMETRY/MACHINE DATA",
            param_val_pairs=f"Bladeset Count = {number_of_blade_sets}",
        )

    def set_machine_base_size_factors(self, size_factors: dict[str, float]):
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
        print(f"save_meshes")
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(self.tg_worker_instances)
        ) as executor:
            futures = [
                executor.submit(self.__sve_mesh__, key, val)
                for key, val in self.tg_worker_instances.items()
            ]
            concurrent.futures.wait(futures)

    def __launch_instances__(self, ndf_file_name, tg_worker_name, tg_worker_instance):
        tg_worker_instance.pytg = launch_turbogrid(
            log_level=pyturbogrid_core.PyTurboGrid.TurboGridLogLevel.DEBUG,
            log_filename_suffix=f"_{ndf_file_name}_{tg_worker_name}",
            additional_kw_args={"local-root": "C:/ANSYSDev/gitSRC/CFX/CFXUE/src"},
        )
        tg_worker_instance.pytg.block_each_message = True
        tg_worker_instance.pytg.read_tginit(path=ndf_file_name + ".tginit", bladerow=tg_worker_name)
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

    def __launch_instances_inf__(
        self,
        base_dir,
        neighbor_dict: dict[str, str | None],
        tg_worker_name,
        tg_worker_instance,
    ):
        tg_worker_instance.pytg = launch_turbogrid(
            log_level=pyturbogrid_core.PyTurboGrid.TurboGridLogLevel.DEBUG,
            log_filename_suffix=f"_{tg_worker_name}",
            additional_kw_args={"local-root": "C:/ANSYSDev/gitSRC/CFX/CFXUE/src"},
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

    def __set_gsf__(self, size_factor, tg_worker_name, tg_worker_instance):
        tg_worker_instance.pytg.set_global_size_factor(self.base_gsf[tg_worker_name] * size_factor)

    def __set_tnc__(self, target_node_count, tg_worker_name, tg_worker_instance):
        tg_worker_instance.pytg.set_obj_param(
            object="/MESH DATA",
            param_val_pairs=f"Mesh Size Specification Mode = Target Total Node Count, "
            f"Target Mesh Granularity = Specify, "
            f"Target Mesh Node Count = {int(target_node_count)}",
        )

    def __get_ec__(self, tg_worker_instance) -> int:
        ec = 0
        try:
            ec = int(tg_worker_instance.pytg.query_mesh_statistics()["Elements"]["Count"])
        except:
            pass
        return ec

    def __sve_mesh__(self, tg_worker_name, tg_worker_instance):
        tg_worker_instance.pytg.save_mesh(tg_worker_name + ".def")
