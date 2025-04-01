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

    def my_save(self, to_print: str, instance_info) -> dict[str, any]:
        print(to_print)
        dict_result = self.get_mbr().save_state()
        return dict_result

    def get_mbr(self) -> MBR:
        return self.__app_factory__.get_app_instance(self.app_id)

    def save_meshes(self, prefix: str = ""):
        self.get_mbr().save_meshes(prefix)

    def get_mesh_geometry(self) -> any:
        import pyvista as pv

        q = self.get_mbr().get_machine_boundary_surfaces()
        return pv.merge([q.get() for _ in range(q.qsize())])

    def do_work(self, work_id, consumed_data_dict, input_data_dict):
        from pprint import pformat

        print(
            f"Performing Instruction {work_id} with consumed data {pformat(consumed_data_dict)} and input data {pformat(input_data_dict)}"
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
                self.save_meshes("mbr_process_")

        print(f"  Done performing Instruction {work_id}")

    def query_data(self, data_id) -> any:
        print("processing query for data", data_id)
        match data_id:
            case "save_mesh_interface":
                return self.save_meshes
            case "display_geometry_interface":
                return self.get_mesh_geometry

    def my_quit(self, to_print: str, instance_info):
        print(to_print)
        self.get_mbr().quit()


class sfp_endpoint:
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

    def my_save(self, to_print: str, instance_info) -> dict[str, any]:
        return {
            "last_used_input_data": self.last_used_input_data,
            "consumed_data_dict": self.consumed_data_dict,
        }

    def get_pytg_saas(self) -> pyturbogrid_core.PyTurboGrid:
        return self.__app_factory__.get_app_instance(self.app_id)

    def save_mesh(self, prefix: str = ""):
        self.get_pytg_saas().write_theta_mesh(
            name=self.sfp_name,
            filename_no_ext=prefix + self.sfp_name,
        )

    def get_mesh_geometry(self) -> any:
        import pyvista as pv

        return pv.MultiBlock(self.get_pytg_saas().getThetaMesh(self.sfp_name)).combine()

    def do_work(self, work_id, consumed_data_dict, input_data_dict):
        from pprint import pformat

        print(
            f"Performing Instruction {work_id} with consumed data {pformat(consumed_data_dict)} and input data {pformat(input_data_dict)}"
        )

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
                # Record this for future use
                self.sfp_name = input_data_dict["sfp_name"]
                # Since we have no real way to persist a theta mesh yet,
                # and generation takes so little time,
                # we'll just call this function again with this dict in order to restore the state.
                self.last_used_input_data = input_data_dict
                self.consumed_data_dict = consumed_data_dict
            case "save_meshes":
                self.save_mesh("mbr_process_")

        print(f"Done performing Instruction {work_id}")

    def query_data(self, data_id) -> any:
        print("processing query for data", data_id)
        match data_id:
            case "save_mesh_interface":
                return self.save_mesh
            case "display_geometry_interface":
                return self.get_mesh_geometry

    def my_quit(self, to_print: str, instance_info):
        print(to_print)
        self.get_pytg_saas().quit()


class save_mesh_endpoint:
    def my_init(self, to_print: str, instance_info):
        print(to_print, "with instance info", instance_info)
        print("Finished", to_print)
        pass

    def my_save(self, to_print: str, instance_info) -> dict[str, any]:
        return {}

    def do_work(self, work_id, consumed_data_dict, input_data_dict):
        from pprint import pformat

        print(
            f"Performing Instruction {work_id} with consumed data {pformat(consumed_data_dict)} and input data {pformat(input_data_dict)}"
        )

        match work_id:
            case "save_meshes":
                for smi in consumed_data_dict["save_mesh_interface"]:
                    smi("mbr_process_mesh_")
        print(f"Done performing Instruction {work_id}")

    def query_data(self, data_id) -> any:
        print("processing query for data", data_id)

    def my_quit(self, to_print: str, instance_info):
        print(to_print)


class show_pyvista_geometry_endpoint:
    def my_init(self, to_print: str, instance_info):
        print(to_print, "with instance info", instance_info)
        print("Finished", to_print)
        pass

    def my_save(self, to_print: str, instance_info) -> dict[str, any]:
        return {}

    def do_work(self, work_id, consumed_data_dict, input_data_dict):
        from pprint import pformat

        print(
            f"Performing Instruction {work_id} with consumed data {pformat(consumed_data_dict)} and input data {pformat(input_data_dict)}"
        )

        match work_id:
            case "show_pyvista_geometry":
                import pyvista as pv
                import random

                plotter = pv.Plotter()
                for dgi in consumed_data_dict["display_geometry_interface"]:
                    plotter.add_mesh(
                        dgi(), color=[random.random(), random.random(), random.random()]
                    )
                plotter.show_axes()
                plotter.background_color = (0, 0, 0)
                plotter.show()
        print(f"Done performing Instruction {work_id}")

    def query_data(self, data_id) -> any:
        print("processing query for data", data_id)

    def my_quit(self, to_print: str, instance_info):
        print(to_print)


class pause_endpoint:
    def my_init(self, to_print: str, instance_info):
        print(to_print, "with instance info", instance_info)
        print("Finished", to_print)

    def my_save(self, to_print: str, instance_info) -> dict[str, any]:
        return {}

    def do_work(self, work_id, consumed_data_dict, input_data_dict):
        from pprint import pformat

        print(
            f"Performing Instruction {work_id} with consumed data {pformat(consumed_data_dict)} and input data {pformat(input_data_dict)}"
        )

        print(f"Done performing Instruction {work_id}")
        return "pause"

    def query_data(self, data_id) -> any:
        print("processing query for data", data_id)

    def my_quit(self, to_print: str, instance_info):
        print(to_print)


example_endpoint_dict = {
    "mbr_endpoint": {
        "instructions": {
            "init_from_tginit": {
                "_exec": lambda endpoint_instance, consumed_data_dict, input_data_dict: endpoint_instance.do_work(
                    work_id="init_from_tginit",
                    consumed_data_dict=consumed_data_dict,
                    input_data_dict=input_data_dict,
                ),
                "produces": ["save_mesh_interface", "display_geometry_interface"],
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
        "Save": lambda endpoint_instance, instance_info: endpoint_instance.my_save(
            to_print="Saving mbr_endpoint", instance_info=instance_info
        ),
        "Quit": lambda endpoint_instance, instance_info: endpoint_instance.my_quit(
            to_print="Quitting mbr_endpoint", instance_info=instance_info
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
                "produces": ["save_mesh_interface", "display_geometry_interface"],
            },
        },
        "Init": lambda endpoint_instance, instance_info: endpoint_instance.my_init(
            "Initializing sfp_endpoint", instance_info=instance_info
        ),
        "Save": lambda endpoint_instance, instance_info: endpoint_instance.my_save(
            to_print="Saving sfp_endpoint", instance_info=instance_info
        ),
        "Quit": lambda endpoint_instance, instance_info: endpoint_instance.my_quit(
            to_print="Quitting sfp_endpoint", instance_info=instance_info
        ),
        "class": sfp_endpoint,
        "query": lambda endpoint_instance, data_id: endpoint_instance.query_data(data_id),
    },
    "save_mesh_endpoint": {
        "instructions": {
            "save_meshes": {
                "_exec": lambda endpoint_instance, consumed_data_dict, input_data_dict: endpoint_instance.do_work(
                    "save_meshes", consumed_data_dict, input_data_dict
                ),
                "consumes_all": ["save_mesh_interface"],
            },
        },
        "Init": lambda endpoint_instance, instance_info: endpoint_instance.my_init(
            "Initializing save_mesh_endpoint", instance_info=instance_info
        ),
        "Save": lambda endpoint_instance, instance_info: endpoint_instance.my_save(
            to_print="Saving save_mesh_endpoint", instance_info=instance_info
        ),
        "Quit": lambda endpoint_instance, instance_info: endpoint_instance.my_quit(
            to_print="Quitting save_mesh_endpoint", instance_info=instance_info
        ),
        "class": save_mesh_endpoint,
        "query": lambda endpoint_instance, data_id: endpoint_instance.query_data(data_id),
    },
    "show_pyvista_geometry_endpoint": {
        "instructions": {
            "show_pyvista_geometry": {
                "_exec": lambda endpoint_instance, consumed_data_dict, input_data_dict: endpoint_instance.do_work(
                    "show_pyvista_geometry", consumed_data_dict, input_data_dict
                ),
                "consumes_all": ["display_geometry_interface"],
            },
        },
        "Init": lambda endpoint_instance, instance_info: endpoint_instance.my_init(
            "Initializing show_pyvista_geometry_endpoint", instance_info=instance_info
        ),
        "Save": lambda endpoint_instance, instance_info: endpoint_instance.my_save(
            to_print="Saving show_pyvista_geometry_endpoint", instance_info=instance_info
        ),
        "Quit": lambda endpoint_instance, instance_info: endpoint_instance.my_quit(
            to_print="Quitting show_pyvista_geometry_endpoint", instance_info=instance_info
        ),
        "class": show_pyvista_geometry_endpoint,
        "query": lambda endpoint_instance, data_id: endpoint_instance.query_data(data_id),
    },
    "pause_endpoint": {
        "instructions": {
            "pause": {
                "_exec": lambda endpoint_instance, consumed_data_dict, input_data_dict: endpoint_instance.do_work(
                    "pause", consumed_data_dict, input_data_dict
                ),
            },
        },
        "Init": lambda endpoint_instance, instance_info: endpoint_instance.my_init(
            "Initializing pause_endpoint", instance_info=instance_info
        ),
        "Save": lambda endpoint_instance, instance_info: endpoint_instance.my_save(
            to_print="Saving pause_endpoint", instance_info=instance_info
        ),
        "Quit": lambda endpoint_instance, instance_info: endpoint_instance.my_quit(
            to_print="Quitting pause_endpoint", instance_info=instance_info
        ),
        "class": pause_endpoint,
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
    # "Save All Meshes": {
    #     "endpoint": "save_mesh_endpoint",
    #     "instance": 1,
    #     "instruction": "save_meshes",
    # },
    # "Show All Meshes": {
    #     "endpoint": "show_pyvista_geometry_endpoint",
    #     "instance": 1,
    #     "instruction": "show_pyvista_geometry",
    # },
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
    # "Pause": {
    #     "endpoint": "pause_endpoint",
    #     "instance": 1,
    #     "instruction": "pause",
    # },
    # "Pause2": {
    #     "endpoint": "pause_endpoint",
    #     "instance": 1,
    #     "instruction": "pause",
    # },
}
instance_info = {
    "sfp_endpoint": {1: {"internal id": "IGVHubCavity"}, 2: {"internal id": "ShrCavity"}}
}
# edges = [
#     ("MBR Init", "Pause"),
#     ("Pause", "IGVHubCavity"),
#     ("Pause", "ShrCavity"),
#     ("IGVHubCavity", "Pause2"),
#     ("ShrCavity", "Pause2"),
#     ("Pause2", "Save All Meshes"),
#     ("Save All Meshes", "Show All Meshes"),
# ]
edges = [
    ("MBR Init", "IGVHubCavity"),
    ("MBR Init", "ShrCavity"),
]
if __name__ == "__main__":
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

    # with open("yaml_dump.yaml", "w", encoding="utf-8") as f:
    #     f.write(tp.export_to_yaml())

    # tp.import_from_from_yaml(yaml_string=open("yaml_dump.yaml", "r", encoding="utf-8").read())
    # tp.visualize()
    import time

    t0 = time.time()
    tp.run_process(render_progress=True, sleep_between_steps=0.5)

    # while (
    #     status := tp.run_process(render_progress=True, sleep_between_steps=0.5)
    # ) == turbo_process.TurboProcess.ProcessStatus.PAUSED:
    #     print("resuming process")
    #     continue

    t1 = time.time()
    print("run process time: ", round(t1 - t0))

    t0 = time.time()
    save_dict = tp.save_process_state()
    t1 = time.time()
    print("save time: ", round(t1 - t0))

    from pprint import pprint

    pprint(save_dict)

    tp.quit()
