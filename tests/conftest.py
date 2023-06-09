# Copyright (c) 2023 ANSYS, Inc. All rights reserved
import os
import sys

import pytest

pyturbogrid_root = os.getenv("PYTURBOGRID_ROOT")
if pyturbogrid_root:
    sys.path.append(f"{pyturbogrid_root}/src")
else:
    sys.path.append("./src")

# Note, internal ANSYS developers will have this available.
# External developers will need to have the most up-to-date ansys-turbogrid-api
# package installed in order to continue below.
pyturbogrid_api_root = os.getenv("PYTURBOGRID_API_ROOT")
if pyturbogrid_api_root:
    sys.path.append(f"{pyturbogrid_api_root}/src")


from ansys.turbogrid.api import pyturbogrid_core

from ansys.turbogrid.core.launcher.launcher import launch_turbogrid

pytest.socket_port = 5000


# Fixtures are set-up methods. The method is passed as an argument to the test method and will be
# run before the method definition.
@pytest.fixture
def pyturbogrid() -> pyturbogrid_core.PyTurboGrid:
    pytest.socket_port += 1
    is_debug = os.getenv("PYTURBOGRID_DEBUG")
    if is_debug == "1":
        additional_args = "-debug"
    else:
        additional_args = None

    tg_local_root = os.getenv("PYTURBOGRID_TURBOGRID_LOCAL_ROOT")
    if tg_local_root:
        additional_kw_args = {"local-root": tg_local_root}
    else:
        additional_kw_args = None

    pyturbogrid = launch_turbogrid(
        additional_args_str=additional_args,
        additional_kw_args=additional_kw_args,
        port=pytest.socket_port,
    )
    print("Success")
    return pyturbogrid
