"""
.. _read_inf_rotor37:

Basic Mesh Generation
---------------------

This example demonstrates how to launch a PyTurboGrid instance and use it to load a blade model
into the associated TurboGrid instance by reading an inf file. Further this will also show how to
query mesh statistics from the session.

"""

# sphinx_gallery_thumbnail_path = '_static/rotor37_overview.png'

import json
import os.path as ospath

#################################################################################
# At present the launcher is in ansys internal ansy-api-turbogrid repository.
# It is assumed that ansys-api-turbogrid has been installed.
# This may change in the future when launcher moves into pyturbogrid repository.
from ansys.turbogrid.api.launcher import get_turbogrid_exe_path, launch_turbogrid

#################################################################################
# Launch TurboGrid instance in the most basic way.
turbogrid = launch_turbogrid()

#################################################################################
# Find the examples folder based on the path to the TurboGrid executable found by below call to get_turbogrid_exe_path.
# We want to access the examples folder in the TurboGrid installation used. get_turbogrid_exe_path ensures that.
exec_path = get_turbogrid_exe_path()
turbogrid_install_location = "/".join(exec_path.parts[:-2])
turbogrid_install_location = turbogrid_install_location.replace("\\", "")
examples_path_str = turbogrid_install_location + "/examples"

#################################################################################
# For sanity, ensure the examples folder exists.
if not ospath.isdir(examples_path_str):
    print("examples folder not found in the TurboGrid installation")
    exit()

#################################################################################
# Read inf for rotor37 example.
turbogrid.read_inf(examples_path_str + "/rotor37/BladeGen.inf")

#################################################################################
# Generate mesh with the default settings.
turbogrid.unsuspend(object="/TOPOLOGY SET")

#################################################################################
# Get the mesh statistics from the current session.
stats = turbogrid.query_mesh_statistics()

#################################################################################
# Print out the mesh statistics in a formatting suitable to read.
# json serializer can print nested dictionary content with nice indentation and formatting.
print("Mesh statistics:", json.dumps(stats, indent=2))

#################################################################################
# Save the mesh.
turbogrid.save_mesh(filename="rotor37.gtm")

#################################################################################
# Quit the TurboGrid session.
turbogrid.quit()
