# Copyright (c) 2023 ANSYS, Inc. All rights reserved
"""
.. _multi_blade_row_example:

Multi blade row meshing example
-------------------------------
This basic example shows how to set up a multi blade row meshing instance and execute it in parallel

"""

#################################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform the required imports. It is assumed that the ``ansys-turbogrid-core``
# package has been installed.

import os

from ansys.turbogrid.core.multi_blade_row.multi_blade_row import MultiBladeRow

#################################################################################
# Create and use an MultiBladeRow instance
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create an MultiBladeRow instance, set it up for a multi-blade row case and execute.

if __name__ == "__main__":
    # Set working directory.
    working_directory = os.getcwd()

    # Set location for the NDF file.
    case_folder = r"Full\Path\to\the\folder\having\the\NDF\file\for\the\case"

    # Set name of the NDF file.
    ndf_file_name = "Name_of_the_NDF_file_for_the_case.ndf"

    # Create MultiBladeRow instance, set up meshing settings and execute.
    mbr_instance = MultiBladeRow(working_directory, case_folder, ndf_file_name)
    mbr_instance.set_spanwise_counts(56, 73)
    # mbr_instance.set_blade_rows_to_mesh(["segment4mainblade","segment6mainblade"])
    # mbr_instance.set_global_size_factor(1.5)
    mbr_instance.set_blade_boundary_layer_offsets(6e-6, {"segment4mainblade": 1e-5})
    mbr_instance.write_tginit_first = True
    mbr_instance.execute()
