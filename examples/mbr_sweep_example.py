# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-FileCopyrightText: 2024 ANSYS, Inc. All rights reserved
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

"""
.. _multi_blade_row_example:

Multi blade row meshing example
-------------------------------
This basic example shows how to set up a multi blade row meshing instance and execute it in parallel.

"""

#################################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform the required imports. It is assumed that the ``ansys-turbogrid-core``
# package has been installed.


import pathlib
import time

install_path = pathlib.PurePath(__file__).parent.parent.as_posix()

from ansys.turbogrid.core.multi_blade_row.multi_blade_row import multi_blade_row as MBR

all_face_areas = {}
all_element_counts = {}


#################################################################################
# Create a multi_blade_row and initialize it
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Use the Concepts NREC sample provided

start_time = time.time()
print(f"Start time: {time.asctime(time.localtime())}")
machine = MBR()
machine.init_from_ndf(f"{install_path}/tests/ndf/AxialFanMultiRow.ndf")
# machine.plot_machine()
brs = machine.get_blade_row_names()
original_face_areas = machine.get_average_base_face_areas()
print(f"original_face_areas: {original_face_areas}")

#################################################################################
# Set the sizing strategy for the machine
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# If this is omitted, the defaults for TurboGrid will be used

machine.set_machine_sizing_strategy(MBR.MachineSizingStrategy.MIN_FACE_AREA)


#################################################################################
# Sweep a parameter
# ~~~~~~~~~~~~~~~~~
# In this case, increase the global size factor, and measure the (base) layer face areas, and the element counts.

for factor in [1, 1.5, 2]:
    all_face_areas[factor] = []
    all_element_counts[factor] = []
    machine.set_machine_size_factor(factor)
    all_face_areas[factor] = machine.get_average_base_face_areas()
    all_element_counts[factor] = machine.get_element_counts()

end_time = time.time()
print(f"End time: {time.asctime(time.localtime())}")
print(f"Duration: {(end_time-start_time)/60} minutes")
print(f"Average Base Face Sizes")
print(f"Blade Rows: {', '.join(brs)}")
for gsf, fas in all_face_areas.items():
    print(f"""machine gsf {gsf}: {', '.join([f"{value:.6e}" for value in fas.values()])}  """)
print(f"Element Counts")
print(f"Blade Rows: {', '.join(brs)}")
for gsf, ecs in all_element_counts.items():
    print(f"""machine gsf {gsf}: {', '.join(str(value) for value in ecs.values())}  """)
