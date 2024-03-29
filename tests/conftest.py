# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-FileCopyrightText: 2024 ANSYS, Inc. All rights reserved
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import ast
from enum import IntEnum
import os
import random
import socket
import sys
import time
from typing import Optional

from fabric import Connection
import pytest

from DeployTGContainer import deployed_tg_container, remote_tg_instance

pyturbogrid_root = os.getenv("PYTURBOGRID_ROOT")
if pyturbogrid_root:
    sys.path.append(f"{pyturbogrid_root}/src")
else:
    sys.path.append("./src")

# For now, this relies on the installed package because of github reasons.
# If you want to use a 'local' api module, you can use the following:
# pyturbogrid_api_root = os.getenv("PYTURBOGRID_API_ROOT")
# if pyturbogrid_api_root:
#     sys.path.append(f"{pyturbogrid_api_root}/src")
# else:
#     raise RuntimeError("PYTURBOGRID_API_ROOT must be defined")

from ansys.turbogrid.api import pyturbogrid_core

# from ansys.turbogrid.core.launcher.launcher import launch_turbogrid


class TestExecutionMode(IntEnum):
    __test__ = False
    DIRECT = 0
    REMOTE = 1
    CONTAINERIZED = 2


def pytest_addoption(parser):
    parser.addoption(
        "--cfx_version",
        action="store",
        default="232",
        help="Version of the base product to test",
    )
    parser.addoption(
        "--execution_mode",
        action="store",
        default="DIRECT",
        help="execution_mode can be either DIRECT, REMOTE or CONTAINERIZED",
        choices=("DIRECT", "REMOTE", "CONTAINERIZED"),
    )
    parser.addoption(
        "--license_file",
        action="store",
        help="License file is required when --execution-mode==CONTAINERIZED",
    )
    parser.addoption(
        "--image_name",
        action="store",
        help="The docker image name is required when --execution-mode==CONTAINERIZED",
    )
    parser.addoption(
        "--container_name",
        action="store",
        default="TGCONTAINER",
        help="The docker container name is required when --execution-mode==CONTAINERIZED",
    )
    parser.addoption(
        "--cfxtg_command_name",
        action="store",
        default="cfxtg",
        help="The optional command name to execute within the container when --execution-mode==CONTAINERIZED",
    )
    parser.addoption(
        "--ssh_key_filename",
        action="store",
        help=(
            "The location of the ssh key for connection to the TurboGrid container. "
            "Used when --execution-mode==CONTAINERIZED"
        ),
    )
    parser.addoption(
        "--container_env_dict",
        action="store",
        default="{}",
        help=(
            "A dictionary for additional environment variables to pass to the container. "
            "Used when --execution-mode==CONTAINERIZED"
        ),
    )
    parser.addoption(
        "--keep_stopped_containers",
        action="store_true",
        default=False,
        help=(
            "Whether or not to leave the stopped containers around without removing them. "
            "Used when --execution-mode==CONTAINERIZED"
        ),
    )
    parser.addoption(
        "--remote_command",
        action="store",
        help="A remote command is required when --execution-mode==REMOTE",
    )
    parser.addoption(
        "--local_cfxtg_path",
        action="store",
        help="The full path+filename to launch TurboGrid when --execution-mode==DIRECT",
    )
    parser.addoption(
        "--log_level",
        action="store",
        default="INFO",
        help="Sets the log level for the python client",
        choices=("CRITICAL", "ERROR", "WARNING", "INFO", "NETWORK_DEBUG", "DEBUG"),
    )


def get_additional_args(debug_env: str) -> str:
    is_debug = os.getenv(debug_env)
    if is_debug == "1":
        additional_args = "-debug"
    else:
        additional_args = None
    return additional_args


def get_path_to_engine(
    app_versions: list,
    relative_path: str,
    app_name: str,
) -> str:
    path_to_engine: str = ""
    for version in app_versions:
        awp_root = os.environ.get("AWP_ROOT" + version)
        if awp_root:
            path_to_engine = os.path.join(awp_root, relative_path)
            break
    if not path_to_engine:
        raise RuntimeError(f"Path to {app_name} could not be determined")
    return path_to_engine


def get_additional_kw_args(local_root_env: str) -> Optional[dict]:
    local_root = os.getenv(local_root_env)
    if local_root:
        additional_kw_args = {"local-root": local_root}
    else:
        additional_kw_args = None
    return additional_kw_args


def get_str_value_from_env(env_var_name: str, default_value: str, required: bool = False) -> str:
    value = os.getenv(env_var_name)
    if not value:
        if required:
            print(os.environ)
            raise Exception(f"{env_var_name} must be defined in the environment.")
        else:
            value = default_value
    return value


def get_int_value_from_env(env_var_name: str, default_value: str, required: bool = False) -> int:
    str_val: str = get_str_value_from_env(env_var_name, default_value, required)
    int_val: int = int(str_val)
    return int_val


def get_enum_value_from_env(
    env_var_name: str, enum_type, default_value, valid_values_str: str, required: bool = False
):
    enum_value = get_str_value_from_env(env_var_name, default_value.name, required)
    try:
        enum_value = enum_type[enum_value]
    except KeyError:
        raise RuntimeError(
            f"Environment variable {env_var_name} was set to an invalid value '{enum_value}'. "
            f"Valid values include {valid_values_str}."
        )
    return enum_value


def get_tg_container(pytestconfig, socket_port: int) -> deployed_tg_container:
    container_name: str = pytestconfig.getoption("container_name")
    # Generate a random integer with 10 digits
    random_number = random.randint(10**9, 10**10 - 1)
    container_name = container_name + str(random_number)
    image_name: str = pytestconfig.getoption("image_name")
    # The path to cfxtg_command is standardized by the container, so just replace the command name.
    # This allows image developers to write custom cfxtg commands.
    cfxtg_command: str = pytestconfig.getoption("cfxtg_command_name")
    cfxtg_command = (
        f"./v{pytestconfig.getoption('cfx_version')}/TurboGrid/bin/{cfxtg_command} "
        f"-py -control-port {socket_port}"
    )

    license_server: str = pytestconfig.getoption("license_file")
    pytest.ftp_port = get_open_port()

    tg_instance = deployed_tg_container(
        image_name,
        socket_port,
        pytest.ftp_port,
        cfxtg_command,
        license_server,
        container_name,
        pytestconfig.getoption("keep_stopped_containers"),
        ast.literal_eval(pytestconfig.getoption("container_env_dict")),
    )
    return tg_instance


def get_open_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # using '0' will tell the OS to pick a random port that is available.
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
        # Shutdown is not needed because the socket is not connected.
        # Also, this will throw and error in windows
        # s.shutdown(socket.SHUT_RDWR)
        s.close()
    # Wait a second to let the OS do things
    time.sleep(1)
    return port


class Helpers:
    pytestconfig: None

    def __init__(self, pytcfg):
        self.pytestconfig = pytcfg

    def get_container_connection(self, ftp_port: int, host_name="localhost"):
        container_connection = Connection(
            host=host_name,
            user="root",
            port=ftp_port,
            connect_kwargs={"key_filename": self.pytestconfig.getoption("ssh_key_filename")},
        )
        return container_connection

    @staticmethod
    def transfer_file_to_container(container_connection: Connection, local_filepath: str):
        print(f"To container-> {local_filepath}")
        container_connection.put(
            remote="/",
            local=local_filepath,
        )

    @staticmethod
    def transfer_files_to_container(
        container_connection: Connection, local_folder_path: str, local_filenames: list
    ):
        for filename in local_filenames:
            Helpers.transfer_file_to_container(
                container_connection, f"{local_folder_path}/{filename}"
            )

    @staticmethod
    def transfer_file_from_container(
        container_connection: Connection, remote_filename: str, local_path_only: str
    ):
        print(f"From container-> {local_path_only}/{remote_filename}")
        container_connection.get(
            remote=f"/{remote_filename}",
            local=f"{local_path_only}/{remote_filename}",
        )

    @staticmethod
    def transfer_files_from_container(
        container_connection: Connection, local_folder_path: str, remote_filenames: list
    ):
        for filename in remote_filenames:
            Helpers.transfer_file_from_container(container_connection, filename, local_folder_path)


@pytest.fixture
def helpers(pytestconfig):
    return Helpers(pytestconfig)


# Fixtures are set-up methods. The method is passed as an argument to the test method and will be
# run before the method definition.
@pytest.fixture
def pyturbogrid(pytestconfig, request) -> pyturbogrid_core.PyTurboGrid:
    pytest.socket_port = get_open_port()

    turbogrid_versions = ["241", "232"]

    pytest.turbogrid_log_level = pyturbogrid_core.PyTurboGrid.TurboGridLogLevel[
        pytestconfig.getoption("log_level")
    ]
    pytest.execution_mode = TestExecutionMode[pytestconfig.getoption("execution_mode")]
    # Regardless of this parameter, if we specified CONTAINERIZED above,
    # set this to the remote option

    pytest.turbogrid_install_type = (
        get_enum_value_from_env(
            "PYTURBOGRID_LOCATION_TYPE",
            pyturbogrid_core.PyTurboGrid.TurboGridLocationType,
            pyturbogrid_core.PyTurboGrid.TurboGridLocationType.TURBOGRID_INSTALL,
            "'TURBOGRID_INSTALL' and 'TURBOGRID_RUNNING_CONTAINER'",
        )
        if pytest.execution_mode == TestExecutionMode.DIRECT
        else pyturbogrid_core.PyTurboGrid.TurboGridLocationType.TURBOGRID_RUNNING_CONTAINER
    )

    if pytest.execution_mode != TestExecutionMode.REMOTE:
        print(f"Creating fixture on port {pytest.socket_port}")

    tg_execution_control: deployed_tg_container | remote_tg_instance | None = None
    if pytest.execution_mode == TestExecutionMode.CONTAINERIZED:
        tg_execution_control = get_tg_container(pytestconfig, pytest.socket_port)
    if pytest.execution_mode == TestExecutionMode.REMOTE:
        tg_execution_control = remote_tg_instance(
            pytest.socket_port,
            pytestconfig.getoption("remote_command"),
        )

    # path_to_cfxtg = (
    #     get_path_to_engine(turbogrid_versions, "TurboGrid/bin/cfxtg", "cfxtg")
    #     if pytest.execution_mode == TestExecutionMode.DIRECT
    #     else ""
    # )

    pytest.path_to_cfxtg = (
        pytestconfig.getoption("local_cfxtg_path")
        if pytest.execution_mode == TestExecutionMode.DIRECT
        else ""
    )

    pytest.additional_args = get_additional_args(debug_env="PYTURBOGRID_DEBUG")
    pytest.additional_kw_args = get_additional_kw_args(
        local_root_env="PYTURBOGRID_TURBOGRID_LOCAL_ROOT"
    )

    pyturbogrid = pyturbogrid_core.PyTurboGrid(
        socket_port=pytest.socket_port,
        turbogrid_location_type=pytest.turbogrid_install_type,
        cfxtg_location=pytest.path_to_cfxtg,
        log_level=pytest.turbogrid_log_level,
        additional_args_str=pytest.additional_args,
        additional_kw_args=pytest.additional_kw_args,
        log_filename_suffix=request.node.name,
    )

    # pyturbogrid = launch_turbogrid(
    #     additional_args_str=additional_args,
    #     additional_kw_args=additional_kw_args,
    #     port=pytest.socket_port,
    # )

    yield pyturbogrid
    # Because of conf-testy things, we can't rely on the proper lifetime management here
    pyturbogrid.quit()
    if tg_execution_control:
        del tg_execution_control
