import math
import os
import pathlib
import sys
import time
import statistics

dir_path: str = os.path.dirname(os.path.realpath(__file__))
install_path = pathlib.PurePath(__file__).parent.parent.as_posix()
sys.path.append(os.path.join(install_path, "src"))

# API repo must be installed
from ansys.turbogrid.core.launcher.launcher import launch_turbogrid
from ansys.turbogrid.api import pyturbogrid_core
from ansys.turbogrid.core.multi_blade_row.multi_blade_row import multi_blade_row as MBR


def test_multi_blade_row_basic():
    machine = MBR()
    machine.init_from_tgmachine(f"{dir_path}/mbr/DTCG50Compressor/DTCG50.TGMachine")
    blade_rows = machine.get_blade_row_names()
    original_face_areas = machine.get_average_base_face_areas()
    target_face_area = min(original_face_areas.values())
    base_gsf = {
        key: math.sqrt(original_face_area / target_face_area)
        for key, original_face_area in original_face_areas.items()
    }
    machine.set_machine_base_size_factors(base_gsf)
    print(f"Average Face Area After: {machine.get_average_base_face_areas()}")
