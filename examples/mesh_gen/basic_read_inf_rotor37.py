# Copyright (c) 2023 ANSYS, Inc. All rights reserved
"""
.. _read_inf_rotor37:

Basic mesh generation
---------------------

This basic example shows how to launch PyTurboGrid, load a blade model
by reading an INF file, and generate a mesh.

This image shows a model overview:
"""
#########################################################
# Workflow:
# .. image:: ../../_static/rotor37_overview.png
#  :width: 400
#  :alt: Model overview.
#
#########################################################

#########################################################
# Perform required imports
# ~~~~~~~~~~~~~~~~~~~~~~~~
# Perform the required imports.

import json
import os.path as ospath

from ansys.turbogrid.core.launcher.launcher import get_turbogrid_exe_path, launch_turbogrid

#################################################################################
# Get path for TurboGrid executable file
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# It is assumed that the ``ansys-turbogrid-core`` package has been installed.
# Get the path for the TurboGrid executable file.


#################################################################################
# Launch a TurboGrid instance
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Launch a TurboGrid instance in the most basic way.

turbogrid = launch_turbogrid()

#################################################################################
# Find the TurboGrid examples
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Find the ``examples`` folder for TurboGrid based on the path to its executable
# file. Calling the ``get_turbogrid_exe_path()`` method ensures that the ``examples``
# folder from the current TurboGrid installation is used.

exec_path = get_turbogrid_exe_path()
turbogrid_install_location = "/".join(exec_path.parts[:-2])
turbogrid_install_location = turbogrid_install_location.replace("\\", "")
examples_path_str = turbogrid_install_location + "/examples"

#################################################################################
# Ensure ``examples`` folder exists
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Ensure that the ``examples`` folder exits.

if not ospath.isdir(examples_path_str):
    print("examples folder not found in the TurboGrid installation")
    exit()

#################################################################################
# Read the file for the rotor37 example
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Read the BladeGen INF file for the rotor37 example.

turbogrid.read_inf(examples_path_str + "/rotor37/BladeGen.inf")

#################################################################################
# Generate a mesh
# ~~~~~~~~~~~~~~~
# Generate a mesh with the default settings.

turbogrid.unsuspend(object="/TOPOLOGY SET")

#################################################################################
# Get mesh statistics
# ~~~~~~~~~~~~~~~~~~~
# Get the mesh statistics from the current session.

stats = turbogrid.query_mesh_statistics()

#################################################################################
# Print mesh statistics
# ~~~~~~~~~~~~~~~~~~~~~
# Print the mesh statistics in a format suitable for reading.
# The JSON serializer can print nested dictionary content with indentation
# and formatting.

print("Mesh statistics:", json.dumps(stats, indent=2))

#################################################################################
# Save mesh
# ~~~~~~~~~
# Save the mesh

turbogrid.save_mesh(filename="rotor37.gtm")

#################################################################################
# Quit session
# ~~~~~~~~~~~~~
# Quit the TurboGrid session.

turbogrid.quit()
