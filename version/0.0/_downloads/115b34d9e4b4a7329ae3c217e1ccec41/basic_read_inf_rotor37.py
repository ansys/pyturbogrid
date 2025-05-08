"""
.. _read_inf_rotor37:

Basic Mesh Generation
---------------------

This example demonstrates how to launch PyTurboGrid, load a blade model
by reading an inf file, and generate a mesh. The example also demonstrates how to
query mesh statistics for the mesh.

"""

# sphinx_gallery_thumbnail_path = '_static/rotor37_overview.png'

import json
import os.path as ospath

#################################################################################
# It is assumed that the ``ansys-turbogrid-core`` package has been installed.
from ansys.turbogrid.core.launcher.launcher import get_turbogrid_exe_path, launch_turbogrid

#################################################################################
# Launch a TurboGrid instance in the most basic way.
turbogrid = launch_turbogrid()

#################################################################################
# Find the examples folder based on the path to the TurboGrid executable found by the call below to ``get_turbogrid_exe_path``.
# This ensures that the examples folder from the current TurboGrid installation is used.
exec_path = get_turbogrid_exe_path()
turbogrid_install_location = "/".join(exec_path.parts[:-2])
turbogrid_install_location = turbogrid_install_location.replace("\\", "")
examples_path_str = turbogrid_install_location + "/examples"

#################################################################################
# Ensure the examples folder exists.
if not ospath.isdir(examples_path_str):
    print("examples folder not found in the TurboGrid installation")
    exit()

#################################################################################
# Read the BladeGen \*.inf file for the rotor37 example.
turbogrid.read_inf(examples_path_str + "/rotor37/BladeGen.inf")

#################################################################################
# Generate a mesh with the default settings.
turbogrid.unsuspend(object="/TOPOLOGY SET")

#################################################################################
# Get the mesh statistics from the current session.
stats = turbogrid.query_mesh_statistics()

#################################################################################
# Print out the mesh statistics in a format suitable for reading.
# json serializer can print nested dictionary content with indentation and formatting.
print("Mesh statistics:", json.dumps(stats, indent=2))

#################################################################################
# Save the mesh.
turbogrid.save_mesh(filename="rotor37.gtm")

#################################################################################
# Quit the TurboGrid session.
turbogrid.quit()
