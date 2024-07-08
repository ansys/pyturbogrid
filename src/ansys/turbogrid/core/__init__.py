# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-FileCopyrightText: 2023 ANSYS, Inc. All rights reserved
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

"""PyTurboGrid is a Python wrapper for Ansys TurboGrid."""

import os

# When this is defined, hardcode a tg container spinup for the purpose of auto documentation.
# Intended only for github CI runs.
socket_port = os.getenv("PYTURBOGRID_DOC_ENGINE_CONNECTION")
tg_container = None
if socket_port is not None:
    import atexit

    from ansys.turbogrid.core.launcher.deploy_tg_container import deployed_tg_container

    print("Running init for ansys turbogrid core")
    socket_port = int(socket_port)
    tg_version = os.environ.get("PYTURBOGRID_DOC_VERSION")
    cfxtg_command = f"./v{tg_version}/TurboGrid/bin/cfxtgpynoviewer -py -control-port {socket_port}"
    image_name = f"ghcr.io/ansys/ansys-api-turbogrid/tglin_reduced_ndf:{tg_version}"
    container_name = "TG_DOCBUILD_CONTAINER"
    license_server = os.environ.get("ANSYSLMD_LICENSE_FILE")
    tg_container = deployed_tg_container(
        image_name, socket_port, socket_port + 1, cfxtg_command, license_server, container_name
    )
    atexit.register(tg_container.__del__)

from ansys.turbogrid.core.launcher.launcher import launch_turbogrid

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:  # pragma: no cover
    import importlib_metadata

# Read from the pyproject.toml
# major, minor, patch
__version__ = "0.0.0"
try:
    __version__ = importlib_metadata.version("ansys-turbogrid-core")
except importlib_metadata.PackageNotFoundError:
    pass
