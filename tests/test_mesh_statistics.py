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


# To run these tests, navigate your terminal to the root of this project (pyturbogrid)
# and use the command pytest -v. -s can be added as well to see all of the console output.

import os
from pathlib import Path

from ansys.turbogrid.api import pyturbogrid_core
import pytest

from ansys.turbogrid.core.launcher.container_helpers import container_helpers
from ansys.turbogrid.core.mesh_statistics import mesh_statistics
from conftest import TestExecutionMode

dir_path: str = os.path.dirname(os.path.realpath(__file__))


def test_get_mesh_statistics_basic(pyturbogrid: pyturbogrid_core.PyTurboGrid, pytestconfig):
    if pytest.execution_mode == TestExecutionMode.REMOTE:
        pyturbogrid.block_each_message = True

    if pytest.execution_mode == TestExecutionMode.CONTAINERIZED:
        pyturbogrid.block_each_message = True
        container = container_helpers.get_container_connection(
            pytest.ftp_port, pytestconfig.getoption("ssh_key_filename")
        )
        print(f"transfer files to container {dir_path}")
        container_helpers.transfer_files_to_container(
            container,
            f"{dir_path}/rotor37/",
            ["Rotor37State.tst", "BladeGen.inf", "hub.curve", "shroud.curve", "profile.curve"],
        )
        print(f"files transferred")

    tg_file_path: str = (
        f"{dir_path}/rotor37/" if pytest.execution_mode != TestExecutionMode.CONTAINERIZED else "/"
    )
    pyturbogrid.read_state(filename=f"{tg_file_path}/Rotor37State.tst")
    pyturbogrid.unsuspend(object="/TOPOLOGY SET")

    ms = mesh_statistics.MeshStatistics(pyturbogrid)
    print(ms)

    all_vars = ms.get_mesh_statistics()
    single_var = ms.get_mesh_statistics("Minimum Face Angle")
    pyturbogrid.quit()

    assert all_vars["Elements"]["Count"] > 5000
    assert all_vars["Edge Length Ratio"]["Maximum"] > 100

    assert single_var["Maximum"] > 0.01
    assert single_var["Limits Type"] == "Minimum"


def test_get_mesh_statistics_with_domain(pyturbogrid: pyturbogrid_core.PyTurboGrid, pytestconfig):
    if pytest.execution_mode == TestExecutionMode.REMOTE:
        pyturbogrid.block_each_message = True

    if pytest.execution_mode == TestExecutionMode.CONTAINERIZED:
        pyturbogrid.block_each_message = True
        container = container_helpers.get_container_connection(
            pytest.ftp_port, pytestconfig.getoption("ssh_key_filename")
        )
        print(f"transfer files to container {dir_path}")
        container_helpers.transfer_files_to_container(
            container,
            f"{dir_path}/rotor37/",
            ["Rotor37State.tst", "BladeGen.inf", "hub.curve", "shroud.curve", "profile.curve"],
        )
        print(f"files transferred")

    tg_file_path: str = (
        f"{dir_path}/rotor37/" if pytest.execution_mode != TestExecutionMode.CONTAINERIZED else "/"
    )
    pyturbogrid.read_state(filename=f"{tg_file_path}/Rotor37State.tst")
    pyturbogrid.unsuspend(object="/TOPOLOGY SET")

    ms = mesh_statistics.MeshStatistics(pyturbogrid)
    all_vars = ms.get_mesh_statistics()
    all_dom_count = all_vars["Elements"]["Count"]

    ms1 = mesh_statistics.MeshStatistics(pyturbogrid, domain="Passage")
    all_vars = ms1.get_mesh_statistics()
    passage_dom_count = all_vars["Elements"]["Count"]

    ms2 = mesh_statistics.MeshStatistics(pyturbogrid, domain="Inlet")
    all_vars = ms2.get_mesh_statistics()
    inlet_dom_count = all_vars["Elements"]["Count"]

    ms3 = mesh_statistics.MeshStatistics(pyturbogrid, domain="Outlet")
    all_vars = ms3.get_mesh_statistics()
    outlet_dom_count = all_vars["Elements"]["Count"]

    pyturbogrid.quit()

    assert all_dom_count > 0
    assert passage_dom_count > 0
    assert inlet_dom_count > 0
    assert outlet_dom_count > 0
    assert all_dom_count == passage_dom_count + inlet_dom_count + outlet_dom_count


def test_update_mesh_statistics(pyturbogrid: pyturbogrid_core.PyTurboGrid, pytestconfig):
    if pytest.execution_mode == TestExecutionMode.REMOTE:
        pyturbogrid.block_each_message = True

    if pytest.execution_mode == TestExecutionMode.CONTAINERIZED:
        pyturbogrid.block_each_message = True
        container = container_helpers.get_container_connection(
            pytest.ftp_port, pytestconfig.getoption("ssh_key_filename")
        )
        print(f"transfer files to container {dir_path}")
        container_helpers.transfer_files_to_container(
            container,
            f"{dir_path}/rotor37/",
            ["Rotor37State.tst", "BladeGen.inf", "hub.curve", "shroud.curve", "profile.curve"],
        )
        print(f"files transferred")

    tg_file_path: str = (
        f"{dir_path}/rotor37/" if pytest.execution_mode != TestExecutionMode.CONTAINERIZED else "/"
    )
    pyturbogrid.read_state(filename=f"{tg_file_path}/Rotor37State.tst")
    pyturbogrid.unsuspend(object="/TOPOLOGY SET")

    ms = mesh_statistics.MeshStatistics(pyturbogrid)
    old_dom_vars = ms.get_mesh_statistics()
    old_elem_count = old_dom_vars["Elements"]["Count"]

    pyturbogrid.set_global_size_factor(1.5)
    ms.update_mesh_statistics()
    new_dom_vars = ms.get_mesh_statistics()
    new_elem_count = new_dom_vars["Elements"]["Count"]

    pyturbogrid.quit()

    assert new_elem_count > old_elem_count


def test_create_histogram(pyturbogrid: pyturbogrid_core.PyTurboGrid, pytestconfig):
    if pytest.execution_mode == TestExecutionMode.REMOTE:
        pyturbogrid.block_each_message = True

    if pytest.execution_mode == TestExecutionMode.CONTAINERIZED:
        pyturbogrid.block_each_message = True
        container = container_helpers.get_container_connection(
            pytest.ftp_port, pytestconfig.getoption("ssh_key_filename")
        )
        print(f"transfer files to container {dir_path}")
        container_helpers.transfer_files_to_container(
            container,
            f"{dir_path}/rotor37/",
            ["Rotor37State.tst", "BladeGen.inf", "hub.curve", "shroud.curve", "profile.curve"],
        )
        print(f"files transferred")

    tg_file_path: str = (
        f"{dir_path}/rotor37/" if pytest.execution_mode != TestExecutionMode.CONTAINERIZED else "/"
    )
    pyturbogrid.read_state(filename=f"{tg_file_path}/Rotor37State.tst")
    pyturbogrid.unsuspend(object="/TOPOLOGY SET")

    ms = mesh_statistics.MeshStatistics(pyturbogrid)

    image_file = "basic_histogram.png"

    ms.create_histogram(
        variable="Maximum Face Angle", image_file=image_file, use_percentages=False, show=False
    )

    ms.create_histogram(variable="Minimum Face Angle", image_file=image_file, show=False)

    pyturbogrid.quit()

    path = Path(image_file)
    assert path.is_file()
    # Check for empty or near-empty file
    assert os.path.getsize(image_file) > 100

    # Remove it again not to pollute the unit test directory
    if os.path.exists(image_file):
        os.remove(image_file)


def test_write_table_to_csv(pyturbogrid: pyturbogrid_core.PyTurboGrid, pytestconfig):
    if pytest.execution_mode == TestExecutionMode.REMOTE:
        pyturbogrid.block_each_message = True

    if pytest.execution_mode == TestExecutionMode.CONTAINERIZED:
        pyturbogrid.block_each_message = True
        container = container_helpers.get_container_connection(
            pytest.ftp_port, pytestconfig.getoption("ssh_key_filename")
        )
        print(f"transfer files to container {dir_path}")
        container_helpers.transfer_files_to_container(
            container,
            f"{dir_path}/rotor37/",
            ["Rotor37State.tst", "BladeGen.inf", "hub.curve", "shroud.curve", "profile.curve"],
        )
        print(f"files transferred")

    tg_file_path: str = (
        f"{dir_path}/rotor37/" if pytest.execution_mode != TestExecutionMode.CONTAINERIZED else "/"
    )
    pyturbogrid.read_state(filename=f"{tg_file_path}/Rotor37State.tst")
    pyturbogrid.unsuspend(object="/TOPOLOGY SET")

    ms = mesh_statistics.MeshStatistics(pyturbogrid)

    csv_file = "stats.csv"
    ms.write_table_to_csv(csv_file)

    pyturbogrid.quit()

    path = Path(csv_file)
    assert path.is_file()

    file_size = os.path.getsize(csv_file)
    # Check that the file is approximately the right size
    assert file_size > 350
    assert file_size < 450

    # Remove it again not to pollute the unit test directory
    if os.path.exists(csv_file):
        os.remove(csv_file)


def test_get_table_as_text(pyturbogrid: pyturbogrid_core.PyTurboGrid, pytestconfig):
    if pytest.execution_mode == TestExecutionMode.REMOTE:
        pyturbogrid.block_each_message = True

    if pytest.execution_mode == TestExecutionMode.CONTAINERIZED:
        pyturbogrid.block_each_message = True
        container = container_helpers.get_container_connection(
            pytest.ftp_port, pytestconfig.getoption("ssh_key_filename")
        )
        print(f"transfer files to container {dir_path}")
        container_helpers.transfer_files_to_container(
            container,
            f"{dir_path}/rotor37/",
            ["Rotor37State.tst", "BladeGen.inf", "hub.curve", "shroud.curve", "profile.curve"],
        )
        print(f"files transferred")

    tg_file_path: str = (
        f"{dir_path}/rotor37/" if pytest.execution_mode != TestExecutionMode.CONTAINERIZED else "/"
    )
    pyturbogrid.read_state(filename=f"{tg_file_path}/Rotor37State.tst")
    pyturbogrid.unsuspend(object="/TOPOLOGY SET")

    ms = mesh_statistics.MeshStatistics(pyturbogrid, "Inlet")

    table_string = ms.get_table_as_text()

    pyturbogrid.quit()

    # Check that the string is approximately the right size (the exact contents might change
    # as the numbers might vary slightly)
    assert len(table_string) > 550
    assert len(table_string) < 750
    assert table_string.count("\n") == 12
