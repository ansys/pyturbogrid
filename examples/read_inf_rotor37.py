"""
.. _read_inf_rotor37:

Read Inf Example
----------------

This example demonstrates how to launch a PyTurboGrid instance and use it to load a blade model into the associated TurboGrid instance by reading an inf file. Further this will also show how to queery mesh statistics from the session.

"""
import json
import os.path as ospath

#################################################################################
# At present the launcher is in ansys internal ansy-api-turbogrid repo.
# It is assumed that ansys-api-turbogrid has been installed.
# This may change in the future when launcher moves into pyturbogrid repo.
from ansys.api.turbogrid.launcher import get_turbogrid_exe_path, launch_turbogrid

#################################################################################
# Launch turbogrid in the most basic way
turbogrid = launch_turbogrid()

#################################################################################
# We want to access the examples folder in the TurboGrid installation that will be used
# Find the examples folder based on the path to cfxtg found by below call to get_turbogrid_exe_path
# If launch_turbogrid call above is given some input like turbogrid_path or product_version,
# the same should be sent to the below call
exec_path = get_turbogrid_exe_path()
turbogrid_install_location = "/".join(exec_path.parts[:-2])
turbogrid_install_location = turbogrid_install_location.replace("\\", "")
examples_path_str = turbogrid_install_location + "/examples"

#################################################################################
# For sanity, ensure the examples folder exists
if not ospath.isdir(examples_path_str):
    print("examples folder not found in the TurboGrid installation")
    exit()

#################################################################################
# Read inf for rotor37 example
turbogrid.read_inf(examples_path_str + "/rotor37/BladeGen.inf")

#################################################################################
# Generate mesh with the default settings
turbogrid.unsuspend(object="/TOPOLOGY SET")

#################################################################################
# Get the mesh statistics from the current session
stats = turbogrid.query_mesh_statistics()

#################################################################################
# Print out the mesh statistics in a formatting suitable to read
# json serializer can print nested dictionary content with nice indentation and formatting
print("Mesh statistics:", json.dumps(stats, indent=2))

#################################################################################
# quit the turbogrid session
turbogrid.quit()
