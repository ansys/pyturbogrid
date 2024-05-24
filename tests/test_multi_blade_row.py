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


import json
import pathlib

from ansys.turbogrid.api.pyturbogrid_core import PyTurboGrid
import pytest

from ansys.turbogrid.core.multi_blade_row.multi_blade_row import multi_blade_row as MBR

# To run these tests, navigate your terminal to the root of this project (pyturbogrid)
# and use the command pytest -v. -s can be added as well to see all of the console output.
from conftest import TestExecutionMode

install_path = pathlib.PurePath(__file__).parent.parent.as_posix()


def test_multi_blade_row_basic(pytestconfig):
    machine = MBR()

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
    machine.init_from_ndf(
        ndf_path=f"{install_path}/tests/ndf/AxialFanMultiRow.ndf",
        turbogrid_path=pytestconfig.getoption("local_cfxtg_path"),
        turbogrid_location_type=pytest.turbogrid_install_type,
        tg_container_launch_settings=tg_container_launch_settings,
        tg_kw_args=json.loads(pytestconfig.getoption("tg_kw_args")),
        # use_existing_tginit_cad=True,
    )

    # This is a planned point-data initialization file format
    # machine.init_from_tgmachine(f"{dir_path}/~.TGMachine")
    # blade_rows = machine.get_blade_row_names()
    print(f"Average Face Area Before: {machine.get_average_base_face_areas()}")
    before_cannonical = {"bladerow1": 0.007804461, "bladerow2": 0.004956871}
    assert machine.get_average_base_face_areas() == before_cannonical
    machine.set_machine_sizing_strategy(MBR.MachineSizingStrategy.MIN_FACE_AREA)
    print(f"Average Face Area After: {machine.get_average_base_face_areas()}")
    after_cannonical = {"bladerow1": 0.005001607, "bladerow2": 0.004956871}
    assert machine.get_average_base_face_areas() == after_cannonical
