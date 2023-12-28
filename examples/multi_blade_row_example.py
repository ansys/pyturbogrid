# Copyright (c) 2023 ANSYS, Inc. All rights reserved
"""
.. _multi_blade_row_example:

Multi blade-row meshing example
-------------------------------
This basic example shows how to set up a multi blade-row meshing instance and execute it in parallel

"""

#################################################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform the required imports. It is assumed that the ``ansys-turbogrid-core``
# package has been installed.

import os
from ansys.turbogrid.core.multi_blade_row.multi_blade_row import MBR

# sphinx_gallery_thumbnail_path = '_static/multi_blade_row_example.png'

#################################################################################
# Create and use an MBR instance
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create an MBR instance, set it up for a multi-blade row case and execute.

if __name__ == "__main__":
    
    # Set working directory:
    working_directory = os.getcwd()
    
    # Set location for the NDF file
    case_folder = r"E:\AnsysDev\pyAnsys\S947493_concepts_nrec\turb_axial_4stage_geom"
    
    # Set name of the NDF file
    ndf_file_name = "turb_axial_4stage_geom.ndf"

    # Create MBR instance, set up meshing settings and execute
    mbr_instance = MBR(working_directory,
                       case_folder,
                       ndf_file_name)
    mbr_instance.set_spanwise_counts(56, 73)
    # mbr_instance.set_blade_rows_to_mesh(["segment4mainblade","segment6mainblade"])
    # mbr_instance.set_blade_row_gsfs(1.5)
    mbr_instance.set_blade_first_element_offsets(6e-6,{"segment4mainblade":1e-5})
    mbr_instance.execute()