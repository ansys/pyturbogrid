# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# Copyright (C) 2024 Concepts NREC, LLC.
# SPDX-FileCopyrightText: 2024 ANSYS, Inc. All rights reserved
# SPDX-FileCopyrightText: 2024 Concepts NREC, LLC All rights reserved
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
.. _multi_blade_row_batch_example:

Multi blade row meshing example
-------------------------------
This basic example shows how to set up a multi blade row meshing instance and execute it in parallel.

"""

#################################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform the required imports. It is assumed that the ``ansys-turbogrid-core``
# package has been installed.

import os
import pathlib

from ansys.turbogrid.core.multi_blade_row.multi_blade_row_batch import MultiBladeRow

#################################################################################
# Create and use a MultiBladeRow instance
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create a MultiBladeRow instance, set it up for a multi blade row case and execute.

if __name__ == "__main__":
    # Set working directory.
    working_directory = os.getcwd()

    # NDF file for this example.
    # Credits for the design go to: https://www.conceptsnrec.com/home
    # © Copyright 2024 Concepts NREC
    ndf_file_name = "AxialFanMultiRow.ndf"

    # Build the path to the test data folder
    test_data_path = pathlib.PurePath(__file__).parent.parent.as_posix()
    test_data_path = os.path.join(test_data_path, "tests")
    test_data_path = os.path.join(test_data_path, "ndf")

    # Create a MultiBladeRow instance.
    mbr_instance = MultiBladeRow(working_directory, test_data_path, ndf_file_name)

    # Set up some settings.
    mbr_instance.set_spanwise_counts(56, 73)
    mbr_instance.set_global_size_factor(1.5)
    mbr_instance.set_blade_boundary_layer_offsets(6e-6)

    # Call the execute method to perform the meshing.
    mbr_instance.execute()
