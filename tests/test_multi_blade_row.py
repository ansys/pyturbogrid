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


# To run these tests, navigate your terminal to the root of this project (pyturbogrid)
# and use the command pytest -v. -s can be added as well to see all of the console output.
import pathlib

from ansys.turbogrid.core.multi_blade_row.multi_blade_row import multi_blade_row as MBR

install_path = pathlib.PurePath(__file__).parent.parent.as_posix()


def test_multi_blade_row_basic():
    machine = MBR()
    machine.init_from_ndf(f"{install_path}/tests/ndf/AxialFanMultiRow.ndf")
    # This is a planned point-data initialization file format
    # machine.init_from_tgmachine(f"{dir_path}/~.TGMachine")
    # blade_rows = machine.get_blade_row_names()
    print(f"Average Face Area Before: {machine.get_average_base_face_areas()}")
    before_cannonical = {"bladerow1": 0.007804461, "bladerow2": 0.004956871}
    assert machine.get_average_base_face_areas() == before_cannonical
    machine.set_machine_sizing_strategy(MBR.MachineSizingStrategy.MIN_FACE_AREA)
    print(f"Average Face Area After: {machine.get_average_base_face_areas()}")
    after_cannonical = {"bladerow1": 0.005001606, "bladerow2": 0.004956871}
    assert machine.get_average_base_face_areas() == after_cannonical
