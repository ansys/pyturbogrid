import concurrent.futures
import math
import os
import pathlib
import sys
import time
import statistics

dir_path: str = os.path.dirname(os.path.realpath(__file__))
install_path = pathlib.PurePath(__file__).parent.parent.as_posix()
base_git_path = pathlib.PurePath(__file__).parent.parent.parent.as_posix()
sys.path.append(os.path.join(install_path, "src"))
sys.path.append(os.path.join(base_git_path, "ansys-api-turbogrid/src"))

# API repo must be installed
from ansys.turbogrid.core.launcher.launcher import launch_turbogrid
from ansys.turbogrid.api import pyturbogrid_core
from ansys.turbogrid.core.multi_blade_row.multi_blade_row import multi_blade_row as MBR

all_face_areas = {}
all_gsf = {}
all_element_counts = {}
all_spanwise_element_counts = {}


def run_mbr() -> list:
    machine = MBR()
    machine.init_from_ndf(f"{install_path}/tests/ndf/AxialFanMultiRow.ndf")
    machine.plot_machine()
    # machine.save_meshes()
    # return
    blade_rows = machine.get_blade_row_names()
    # original_face_areas = machine.get_average_base_face_areas()
    # # Get # elements in mesh as well
    # print(f"original_face_areas: {original_face_areas}")
    # target_face_area = sum(original_face_areas.values()) / float(len(original_face_areas))
    # target_face_area = min(original_face_areas.values())
    # print(f"target_face_area: {target_face_area}")
    # base_gsf = {
    #     key: math.sqrt(original_face_area / target_face_area)
    #     for key, original_face_area in original_face_areas.items()
    # }
    # print(f"New gsf: {[val for val in base_gsf.values()]}")
    # machine.set_machine_base_size_factors(base_gsf)
    # print(f"Average Face Area After: {machine.get_average_base_face_areas()}")
    # for factor in [0.75, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5]:
    # for factor in [0.75, 1, 1.25]:
    # for inlet_interface_position in [0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1, 0.08, 0.06, 0.04, 0.03, 0.02, 0.01]:
    # all_face_areas[inlet_interface_position] = []
    # all_element_counts[inlet_interface_position] = []
    # for factor in [0.1, 0.15, 0.25, 0.5, 0.75, 1]:
    # for target_node_count in [5e4]:
    # for target_node_count in [2.5e4, 5e4, 7.5e4, 10e4, 25e4, 50e4, 75e4, 100e4, 250e4, 500e4]:
    #     target_node_count = int(target_node_count)
    # print(f"    Machine GSF {factor}")
    #     print(f"    target_node_count {target_node_count}")
    # loop_start_time = time.time()
    #     machine.set_machine_target_node_count(target_node_count)
    # machine.set_machine_size_factor(factor)
    #     # print(f"GSF {factor} Av Face Area: {machine.get_average_base_face_areas()}")
    # all_face_areas[factor] = machine.get_average_base_face_areas()
    #     # print(f"GSF {factor} Element Count: {machine.get_element_counts()}")
    # all_element_counts[factor] = machine.get_element_counts()
    #     all_spanwise_element_counts[target_node_count] = machine.get_spanwise_element_counts()
    #     all_gsf[target_node_count] = machine.get_local_gsf()
    # loop_end_time = time.time()
    # print(f"        Duration: {(loop_end_time-loop_start_time)} seconds")

    return blade_rows


def stddev_percent(input_dict) -> float:
    as_list = [val for val in input_dict.values()]
    return statistics.stdev(as_list) / statistics.mean(as_list) * 100


if __name__ == "__main__":
    start_time = time.time()
    print(f"Start time: {time.asctime(time.localtime())}")

    brs = run_mbr()
    end_time = time.time()
    print(f"End time: {time.asctime(time.localtime())}")
    print(f"Duration: {(end_time-start_time)/60} minutes")
    # print(f"Average Base Face Sizes")
    # for inlet_pos, fas in all_face_areas.items():
    #     print(f"""inlet_pos {inlet_pos}: {', '.join([f"{value:.6e}" for value in fas])}""")
    # print(f"Element Counts")
    # for inlet_pos, ecs in all_element_counts.items():
    #     print(f"""inlet_pos {inlet_pos}: {', '.join([f"{value:.6e}" for value in ecs])}""")

    print(f"Average Base Face Sizes")
    print(f"Blade Rows: {', '.join(brs)}")
    for gsf, fas in all_face_areas.items():
        print(
            f"""machine gsf {gsf}: {', '.join([f"{value:.6e}" for value in fas.values()])}  """
            """std dev % {stddev_percent(fas)}"""
        )
    print(f"Element Counts")
    print(f"Blade Rows: {', '.join(brs)}")
    for gsf, ecs in all_element_counts.items():
        print(
            f"""machine gsf {gsf}: {', '.join(str(value) for value in ecs.values())}  """
            """std dev % {stddev_percent(ecs)}"""
        )

    # print(f"Spanwise Element Counts")
    # print(f"Blade Rows: {', '.join(brs)}")
    # for tnc, ecs in all_spanwise_element_counts.items():
    #     print(f"""tnc {tnc}: {', '.join(str(value) for value in ecs.values())}""")
    # print(f"Local Global Size Factors")
    # print(f"Blade Rows: {', '.join(brs)}")
    # for tnc, gsf in all_gsf.items():
    #     print(f"""tnc {tnc}: {', '.join(str(value) for value in gsf.values())}""")
