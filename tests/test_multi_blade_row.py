# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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


import json
import os
import pathlib

from ansys.turbogrid.api.pyturbogrid_core import PyTurboGrid
import pytest

from ansys.turbogrid.core.multi_blade_row.multi_blade_row import MachineSizingStrategy
from ansys.turbogrid.core.multi_blade_row.multi_blade_row import multi_blade_row as MBR

# To run these tests, navigate your terminal to the root of this project (pyturbogrid)
# and use the command pytest -v. -s can be added as well to see all of the console output.
from conftest import TestExecutionMode

install_path = pathlib.PurePath(__file__).parent.parent.as_posix()


def test_multi_blade_row_basic(pytestconfig):

    tg_container_launch_settings = {}

    pytest.turbogrid_install_type = PyTurboGrid.TurboGridLocationType.TURBOGRID_INSTALL
    pytest.execution_mode = TestExecutionMode[pytestconfig.getoption("execution_mode")]
    if pytest.execution_mode == TestExecutionMode.CONTAINERIZED:
        pytest.turbogrid_install_type = (
            PyTurboGrid.TurboGridLocationType.TURBOGRID_RUNNING_CONTAINER
        )
        tg_container_launch_settings = {
            "cfxtg_command_name": pytestconfig.getoption("cfxtg_command_name"),
            "image_name": pytestconfig.getoption("image_name"),
            "container_name": pytestconfig.getoption("container_name"),
            "cfx_version": pytestconfig.getoption("cfx_version"),
            "license_file": pytestconfig.getoption("license_file"),
            "keep_stopped_containers": pytestconfig.getoption("keep_stopped_containers"),
            "container_env_dict": pytestconfig.getoption("container_env_dict"),
            "ssh_key_filename": pytestconfig.getoption("ssh_key_filename"),
        }

    # Note that for non-containerized environments, turbogrid_location_type and tg_container_launch_settings are not needed
    # turbogrid_path can be None if you want the launcher to find your installation for you
    machine = MBR(
        turbogrid_location_type=pytest.turbogrid_install_type,
        tg_container_launch_settings=tg_container_launch_settings,
        turbogrid_path=pytestconfig.getoption("local_cfxtg_path"),
        tg_kw_args=json.loads(pytestconfig.getoption("tg_kw_args")),
    )

    machine.init_from_ndf(
        ndf_path=f"{install_path}/tests/ndf/AxialFanMultiRow.ndf",
        # use_existing_tginit_cad=True,
    )

    # This is a planned point-data initialization file format
    # machine.init_from_tgmachine(f"{dir_path}/~.TGMachine")
    # blade_rows = machine.get_blade_row_names()
    print(f"Average Face Area Before: {machine.get_average_base_face_areas()}")
    before_canonical = {"bladerow1": 0.007804461, "bladerow2": 0.004956871}
    before_canonical_2 = {"bladerow1": 0.007804943, "bladerow2": 0.004956871}
    before_canonical_252_container = {"bladerow1": 0.007804869, "bladerow2": 0.004956871}
    assert (
        machine.get_average_base_face_areas() == before_canonical
        or machine.get_average_base_face_areas() == before_canonical_2
        or machine.get_average_base_face_areas() == before_canonical_252_container
    )
    machine.set_machine_sizing_strategy(MachineSizingStrategy.MIN_FACE_AREA)
    print(f"Average Face Area After: {machine.get_average_base_face_areas()}")

    after_canonical_pre_252 = {"bladerow1": 0.005001607, "bladerow2": 0.004956871}
    after_canonical_252 = {"bladerow1": 0.005001606, "bladerow2": 0.004956871}
    after_canonical_post_252 = {"bladerow1": 0.005001909, "bladerow2": 0.004956871}
    after_canonical_252_container = {"bladerow1": 0.005001862, "bladerow2": 0.004956871}
    assert (
        machine.get_average_base_face_areas() == after_canonical_pre_252
        or machine.get_average_base_face_areas() == after_canonical_252
        or machine.get_average_base_face_areas() == after_canonical_post_252
        or machine.get_average_base_face_areas() == after_canonical_252_container
    )


def test_multi_blade_row_tgmachine(pytestconfig):
    tg_container_launch_settings = {}

    pytest.turbogrid_install_type = PyTurboGrid.TurboGridLocationType.TURBOGRID_INSTALL
    pytest.execution_mode = TestExecutionMode[pytestconfig.getoption("execution_mode")]
    if pytest.execution_mode == TestExecutionMode.CONTAINERIZED:
        pytest.turbogrid_install_type = (
            PyTurboGrid.TurboGridLocationType.TURBOGRID_RUNNING_CONTAINER
        )
        tg_container_launch_settings = {
            "cfxtg_command_name": pytestconfig.getoption("cfxtg_command_name"),
            "image_name": pytestconfig.getoption("image_name"),
            "container_name": pytestconfig.getoption("container_name"),
            "cfx_version": pytestconfig.getoption("cfx_version"),
            "license_file": pytestconfig.getoption("license_file"),
            "keep_stopped_containers": pytestconfig.getoption("keep_stopped_containers"),
            "container_env_dict": pytestconfig.getoption("container_env_dict"),
            "ssh_key_filename": pytestconfig.getoption("ssh_key_filename"),
        }

    # Note that for non-containerized environments, turbogrid_location_type and tg_container_launch_settings are not needed
    # turbogrid_path can be None if you want the launcher to find your installation for you
    machine = MBR(
        turbogrid_location_type=pytest.turbogrid_install_type,
        tg_container_launch_settings=tg_container_launch_settings,
        turbogrid_path=pytestconfig.getoption("local_cfxtg_path"),
        tg_kw_args=json.loads(pytestconfig.getoption("tg_kw_args")),
    )

    machine.init_from_tgmachine(
        tgmachine_path=f"{install_path}/tests/mbr/5_stage_hannover/5_stage_hannover.TGMachine",
        # disable_lma=True,
    )
    machine.disable_lma()
    print(f"Blade Rows: {machine.get_blade_row_names()}")
    print(f"Average Face Area: {machine.get_average_base_face_areas()}")
    print(f"Mesh Stats: {machine.get_mesh_statistics()}")
    assert all(
        br_face_area != 0.0
        for br_name, br_face_area in machine.get_average_base_face_areas().items()
    )
    # print(f"Blade Rows: {machine.get_blade_row_names()}")
    # print(f"Average Face Area: {machine.get_average_base_face_areas()}")
    # print(f"Mesh Stats: {machine.get_mesh_statistics()}")
    assert all(value != 0.0 for value in machine.get_average_base_face_areas())


def test_multi_blade_row_sfp(pytestconfig):
    tg_container_launch_settings = {}

    pytest.turbogrid_install_type = PyTurboGrid.TurboGridLocationType.TURBOGRID_INSTALL
    pytest.execution_mode = TestExecutionMode[pytestconfig.getoption("execution_mode")]
    if pytest.execution_mode == TestExecutionMode.CONTAINERIZED:
        pytest.turbogrid_install_type = (
            PyTurboGrid.TurboGridLocationType.TURBOGRID_RUNNING_CONTAINER
        )
        tg_container_launch_settings = {
            "cfxtg_command_name": pytestconfig.getoption("cfxtg_command_name"),
            "image_name": pytestconfig.getoption("image_name"),
            "container_name": pytestconfig.getoption("container_name"),
            "cfx_version": pytestconfig.getoption("cfx_version"),
            "license_file": pytestconfig.getoption("license_file"),
            "keep_stopped_containers": pytestconfig.getoption("keep_stopped_containers"),
            "container_env_dict": pytestconfig.getoption("container_env_dict"),
            "ssh_key_filename": pytestconfig.getoption("ssh_key_filename"),
        }

    machine = MBR(
        turbogrid_location_type=pytest.turbogrid_install_type,
        tg_container_launch_settings=tg_container_launch_settings,
        turbogrid_path=pytestconfig.getoption("local_cfxtg_path"),
        tg_kw_args=json.loads(pytestconfig.getoption("tg_kw_args")),
    )

    tginit_path = pathlib.PurePath(
        os.path.join(install_path, "tests", "sfp", "RadTurbine.tginit")
    ).as_posix()

    machine.init_from_tginit(
        tginit_path=tginit_path,
        blade_rows_to_mesh=machine.get_blade_row_names_from_tginit(tginit_path),
        tg_log_level=PyTurboGrid.TurboGridLogLevel[pytestconfig.getoption("client_log_level")],
    )

    # ----------- #

    # available_sfps = machine.get_secondary_flow_paths_from_tginit(tginit_path)
    # print(f"available_sfps: {available_sfps}")

    # for sfp_name in available_sfps:
    #     machine.add_secondary_flow_path_from_tginit(sfp_name=sfp_name, tginit_path=tginit_path)

    # available_theta_meshes = machine.get_available_secondary_flow_path_meshes()
    # print(f"available_theta_meshes: {available_theta_meshes}")

    # scene_graph: queue.Queue = machine.get_machine_boundary_surfaces()
    # assert scene_graph.qsize() == 24

    # ----------- #

    # from pprint import pprint

    # import pyvista as pv
    # import random

    # p = pv.Plotter()
    # while not scene_graph.empty():
    #     mesh = scene_graph.get()
    #     pprint(mesh)
    #     p.add_mesh(mesh, color=[random.random(), random.random(), random.random()])
    # p.show(None)


def test_multi_blade_row_save(pytestconfig):
    machine = MBR(
        turbogrid_location_type=PyTurboGrid.TurboGridLocationType.TURBOGRID_INSTALL,
        turbogrid_path=pytestconfig.getoption("local_cfxtg_path"),
        tg_kw_args=json.loads(pytestconfig.getoption("tg_kw_args")),
    )

    tginit_path = pathlib.PurePath(
        os.path.join(install_path, "tests", "sfp", "RadTurbine.tginit")
    ).as_posix()

    machine.init_from_tginit(
        tginit_path=tginit_path,
        blade_rows_to_mesh=machine.get_blade_row_names_from_tginit(tginit_path),
        tg_log_level=PyTurboGrid.TurboGridLogLevel[pytestconfig.getoption("client_log_level")],
    )

    for br_name, io_positions_dict in {
        "IGV": {"outlet": [0.5, 0.5]},
        "Main": {"outlet": [0.3, 0.3]},
    }.items():
        machine.set_inlet_outlet_parametric_positions(
            br_name,
            [],
            io_positions_dict["outlet"],
        )

    original_mesh_stats = machine.get_mesh_statistics()
    dict_result = machine.save_state()
    print(dict_result)
    save_path = os.path.join(install_path, "tests", "_testdata", "mbr_state.tst")
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(dict_result))
    machine.quit()

    machine2 = MBR(
        turbogrid_location_type=PyTurboGrid.TurboGridLocationType.TURBOGRID_INSTALL,
        turbogrid_path=pytestconfig.getoption("local_cfxtg_path"),
        tg_kw_args=json.loads(pytestconfig.getoption("tg_kw_args")),
    )

    machine2.init_from_state(str(save_path))
    from_state_mesh_stats = machine2.get_mesh_statistics()

    from pprint import pprint

    from deepdiff import DeepDiff

    print("original_mesh_stats")
    pprint(original_mesh_stats)
    print("from_state_mesh_stats")
    pprint(from_state_mesh_stats)
    diff = DeepDiff(original_mesh_stats, from_state_mesh_stats)
    print(diff)
    machine2.quit()
