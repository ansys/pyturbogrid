import os

from ansys.turbogrid.core.multi_blade_row.multi_blade_row import multi_blade_row as MBR

dir_path: str = os.path.dirname(os.path.realpath(__file__))


def test_multi_blade_row_basic():
    machine = MBR()
    machine.init_from_ndf(f"{dir_path}/ndf/AxiFan-01A-MultiRow.ndf")
    blade_rows = machine.get_blade_row_names()
    print(f"{machine.get_average_base_face_areas()=}")
    machine.set_global_size_factor(blade_rows[0], 2)
    print(f"{machine.get_average_base_face_areas()=}")
