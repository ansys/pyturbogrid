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


class foo:
    a: int


class multi_blade_row:
    initialized: bool = False
    init_file_path: Path
    all_blade_rows: dict
    all_blade_row_keys: list

    # Consider passing in the filename (whether ndf or tginit) as initializing as raii
    def __init__(self):
        pass

    def __del__(self):
        for blade_row in self.all_blade_rows:
            self.tg_worker_instances[blade_row].pytg.quit()
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
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(self.tg_worker_instances)
        ) as executor:
            job = partial(self.__launch_instances__, ndf_file_name)
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

    def get_blade_row_names(self) -> list:
        return self.all_blade_row_keys

    def set_global_size_factor(self, blade_row_name: str, size_factor: float):
        if blade_row_name not in self.tg_worker_instances:
            raise Exception(
                f"No blade row with name {blade_row_name}. Available names: {self.all_blade_row_keys}"
            )
        self.tg_worker_instances[blade_row_name].pytg.set_global_size_factor(size_factor)

    def __launch_instances__(self, ndf_file_name, tg_worker_name, tg_worker_instance):
        tg_worker_instance.pytg = launch_turbogrid(
            log_level=pyturbogrid_core.PyTurboGrid.TurboGridLogLevel.DEBUG,
            log_filename_suffix=f"_{ndf_file_name}_{tg_worker_name}",
            additional_kw_args={"local-root": "C:/ANSYSDev/gitSRC/CFX/CFXUE/src"},
        )
        tg_worker_instance.pytg.block_each_message = True
        tg_worker_instance.pytg.read_tginit(path=ndf_file_name + ".tginit", bladerow=tg_worker_name)
        # tg_worker_instance.pytg.set_obj_param(
        #     object="/TOPOLOGY SET", param_val_pairs="ATM Stop After Main Layers=True"
        # )
        tg_worker_instance.pytg.unsuspend(object="/TOPOLOGY SET")
        av_bg_face_area = tg_worker_instance.pytg.query_average_background_face_area()
        print(f"{tg_worker_name=} {av_bg_face_area=}")
