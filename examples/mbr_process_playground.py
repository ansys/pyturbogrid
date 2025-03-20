# Goal here is to create a process that uses MBR and secondary flow paths.
# Process will be hard-coded, and can be expanded to data-driven once the appropriate view framework is in place.
# Process will create the appropriate MBR steps and SFP steps, and create a data transfer link between them.
# Data transfer is a dummy for now until implemented in ThetaMesh
# Certain things still need to be added like 'rules' input for a step (like file name)

import os
import pathlib

from ansys.turbogrid.api import pyturbogrid_core
from ansys.turbogrid.api import turbo_process
from ansys.turbogrid.core.multi_blade_row.multi_blade_row import multi_blade_row as MBR

install_path = pathlib.PurePath(__file__).parent.parent.as_posix()


class mbr_endpoint:
    def __init__(self):
        pass

    def my_init(self, to_print: str, instance_info):
        print(to_print)
        # TODO: args as input dictionary
        self.app_id = self.__app_factory__.create_new_app_instance(
            MBR,
            arg_dict={
                "log_prefix": "_mbr",
                "tg_kw_args": {"local-root": "C:/ANSYSDev/gitSRC/CFX/CFXUE/src"},
            },
        )
        print("Finished", to_print)

    def get_mbr(self) -> MBR:
        return self.__app_factory__.get_app_instance(self.app_id)

    def do_work(self, work_id, consumed_data_dict, input_data_dict):
        print(
            f"Performing Instruction {work_id} with consumed data {consumed_data_dict} and input data {input_data_dict}"
        )
        match work_id:
            case "init_from_tginit":
                self.get_mbr().init_from_tginit(
                    tginit_path=input_data_dict["file_name"],
                    blade_rows_to_mesh=(
                        input_data_dict["blade_rows"] if "blade_rows" in input_data_dict else None
                    ),
                    tg_log_level=pyturbogrid_core.PyTurboGrid.TurboGridLogLevel.INFO,
                )
                if "set_inlet_outlet_parametric_positions" in input_data_dict:
                    for br_name, io_positions_dict in input_data_dict[
                        "set_inlet_outlet_parametric_positions"
                    ].items():
                        self.get_mbr().set_inlet_outlet_parametric_positions(
                            br_name,
                            (io_positions_dict["intlet"] if "intlet" in io_positions_dict else []),
                            (io_positions_dict["outlet"] if "outlet" in io_positions_dict else []),
                        )

            case "save_meshes":
                self.get_mbr().save_meshes("mbr_process_")

        print(
            f"Done performing Instruction {work_id} with consumed data {consumed_data_dict} and input data {input_data_dict}"
        )

    def query_data(self, data_id) -> any:
        print("processing query for data", data_id)
        # match data_id:
        #     case "a1_val":
        #         return self.__app_factory__.get_app_instance(self.app_id).val


class sfp_endpoint:
    def __init__(self):
        pass

    def my_init(self, to_print: str, instance_info):
        print(to_print, "with instance info", instance_info)
        # TODO: args as input dictionary
        log_prefix = instance_info["internal id"] if "internal id" in instance_info else ""

        self.app_id = self.__app_factory__.create_new_app_instance(
            pyturbogrid_core.PyTurboGrid,
            arg_dict={
                "socket_port": 0,
                "turbogrid_location_type": pyturbogrid_core.PyTurboGrid.TurboGridLocationType.TURBOGRID_INSTALL,
                "cfxtg_location": os.path.join(
                    os.environ["AWP_ROOT" + "252"], "TurboGrid/bin/cfxtg.exe"
                ),
                "log_level": pyturbogrid_core.PyTurboGrid.TurboGridLogLevel.INFO,
                "additional_kw_args": {"local-root": "C:/ANSYSDev/gitSRC/CFX/CFXUE/src"},
                "additional_args_str": "",
                "log_filename_suffix": f"_sfp_{log_prefix}_saas_mbr_process_playground",
            },
        )

        print("Finished", to_print)

    def get_pytg_saas(self) -> pyturbogrid_core.PyTurboGrid:
        return self.__app_factory__.get_app_instance(self.app_id)

    def do_work(self, work_id, consumed_data_dict, input_data_dict):
        print(
            f"Performing Instruction {work_id} with consumed data {consumed_data_dict} and input data {input_data_dict}"
        )
        # "sfp_name": "IGVHubCavity",

        match work_id:
            case "saas_mesh":
                tginit_contents = self.get_pytg_saas().getTGInitContents(
                    tginit_path=input_data_dict["file_name"]
                )

                if input_data_dict["sfp_name"] not in tginit_contents["secondary flow paths"]:
                    raise (
                        f"Secondary Flow Path {input_data_dict['sfp_name']} is not in the TGInit file {input_data_dict['file_name']}"
                    )

                sfp_family_types = tginit_contents["secondary flow paths"][
                    input_data_dict["sfp_name"]
                ]

                base, ext = os.path.splitext(input_data_dict["file_name"])
                cad_path = base + ".x_b"

                self.get_pytg_saas().generateThetaMesh(
                    name=input_data_dict["sfp_name"],
                    axis=tginit_contents["axis"],
                    units=tginit_contents["units"],
                    cad_path=cad_path,
                    wall_families=sfp_family_types["wall families"],
                    hubinterfacefamilies=sfp_family_types["hub families"],
                    shroudinterfacefamilies=sfp_family_types["shroud families"],
                    hubcurvefamily=tginit_contents["hub family"],
                    shroudcurvefamily=tginit_contents["shroud family"],
                )

                self.get_pytg_saas().write_theta_mesh(
                    name=input_data_dict["sfp_name"], filename_no_ext=input_data_dict["sfp_name"]
                )

        print(
            f"Done performing Instruction {work_id} with consumed data {consumed_data_dict} and input data {input_data_dict}"
        )

    def query_data(self, data_id) -> any:
        print("processing query for data", data_id)
        # match data_id:
        #     case "a1_val":
        #         return self.__app_factory__.get_app_instance(self.app_id).val


example_endpoint_dict = {
    "mbr_endpoint": {
        "instructions": {
            "init_from_tginit": {
                "_exec": lambda endpoint_instance, consumed_data_dict, input_data_dict: endpoint_instance.do_work(
                    work_id="init_from_tginit",
                    consumed_data_dict=consumed_data_dict,
                    input_data_dict=input_data_dict,
                ),
                "produces": ["blade row mesh"],
            },
            "save_meshes": {
                "_exec": lambda endpoint_instance, consumed_data_dict, input_data_dict: endpoint_instance.do_work(
                    work_id="save_meshes",
                    consumed_data_dict=consumed_data_dict,
                    input_data_dict=input_data_dict,
                ),
            },
        },
        "Init": lambda endpoint_instance, instance_info: endpoint_instance.my_init(
            to_print="Initializing mbr_endpoint", instance_info=instance_info
        ),
        "class": mbr_endpoint,
        "query": lambda endpoint_instance, data_id: endpoint_instance.query_data(data_id=data_id),
    },
    "sfp_endpoint": {
        "instructions": {
            "saas_mesh": {
                "_exec": lambda endpoint_instance, consumed_data_dict, input_data_dict: endpoint_instance.do_work(
                    "saas_mesh", consumed_data_dict, input_data_dict
                ),
            },
        },
        "Init": lambda endpoint_instance, instance_info: endpoint_instance.my_init(
            "Initializing sfp_endpoint", instance_info=instance_info
        ),
        "class": sfp_endpoint,
        "query": lambda endpoint_instance, data_id: endpoint_instance.query_data(data_id),
    },
}
step_type_info = {
    "MBR Init": {
        "endpoint": "mbr_endpoint",
        "instance": 1,
        "instruction": "init_from_tginit",
        "input data": {
            "file_name": f"{install_path}/tests/sfp/RadTurbine.tginit",
            "set_inlet_outlet_parametric_positions": {
                "IGV": {"outlet": [0.5, 0.5]},
                "Main": {"outlet": [0.3, 0.3]},
            },
        },
    },
    "MBR Save Mesh": {
        "endpoint": "mbr_endpoint",
        "instance": 1,
        "instruction": "save_meshes",
    },
    "IGVHubCavity": {
        "endpoint": "sfp_endpoint",
        "instance": 1,
        "instruction": "saas_mesh",
        "input data": {
            "file_name": f"{install_path}/tests/sfp/RadTurbine.tginit",
            "sfp_name": "IGVHubCavity",
        },
    },
    "ShrCavity": {
        "endpoint": "sfp_endpoint",
        "instance": 2,
        "instruction": "saas_mesh",
        "input data": {
            "file_name": f"{install_path}/tests/sfp/RadTurbine.tginit",
            "sfp_name": "ShrCavity",
        },
    },
}
instance_info = {
    "sfp_endpoint": {1: {"internal id": "IGVHubCavity"}, 2: {"internal id": "ShrCavity"}}
}
edges = [
    ("MBR Init", "MBR Save Mesh"),
    ("MBR Save Mesh", "IGVHubCavity"),
    ("MBR Save Mesh", "ShrCavity"),
]


turbogrid_version = "252"
path_to_localroot = "C:/ANSYSDev/gitSRC/CFX/CFXUE/src"

awp_root = os.environ["AWP_ROOT" + turbogrid_version]
path_to_cfxtg = os.path.join(awp_root, "TurboGrid/bin/cfxtg.exe")

turbogrid_install_type = pyturbogrid_core.PyTurboGrid.TurboGridLocationType.TURBOGRID_INSTALL
pyturbogrid = pyturbogrid_core.PyTurboGrid(
    socket_port=0,
    turbogrid_location_type=turbogrid_install_type,
    cfxtg_location=path_to_cfxtg,
    log_level=pyturbogrid_core.PyTurboGrid.TurboGridLogLevel.INFO,
    additional_args_str="",
    # additional_args_str="-debug",
    additional_kw_args={"local-root": path_to_localroot},
    log_filename_suffix="_mbr_process_playground",
)

tp = turbo_process.TurboProcess(pyturbogrid)

tp.register_endpoint_dict(endpoint_dict=example_endpoint_dict)
tp.register_instance_info(instance_info)
tp.create_graph_from_text(
    edges=edges,
    step_type_info=step_type_info,
)
import time

t0 = time.time()
tp.run_process(render_progress=True, sleep_between_steps=0.5)
t1 = time.time()
print("run process time: ", round(t1 - t0))
del tp
