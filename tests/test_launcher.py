# Copyright (c) 2023 ANSYS, Inc. All rights reserved
# To run these tests, navigate your terminal to the root of this project (pyturbogrid)
# and use the command pytest -v. -s can be added as well to see all of the console output.

import os
from pathlib import Path
import platform

import pytest

from ansys.turbogrid.core.launcher import launcher


def test_turbogrid_version():

    assert launcher.TurboGridVersion(23.2) == launcher.TurboGridVersion.version_23R2
    assert launcher.TurboGridVersion("23.2") == launcher.TurboGridVersion.version_23R2
    assert launcher.TurboGridVersion("23.2.0") == launcher.TurboGridVersion.version_23R2

    with pytest.raises(RuntimeError, match="does not exist. Available version strings"):
        print(launcher.TurboGridVersion(22.2))

    with pytest.raises(RuntimeError, match="does not exist. Available version strings"):
        print(launcher.TurboGridVersion("bad value"))


def test_turbogrid_exe_paths():

    vars_to_restore = {
        "AWP_ROOT232": os.environ.get("AWP_ROOT232", None),
        "PYTURBOGRID_TURBOGRID_ROOT": os.environ.get("PYTURBOGRID_TURBOGRID_ROOT", None),
    }

    try:

        dummy_version = "23.2"
        os.environ["AWP_ROOT232"] = "/myansys/v232"

        latest_path = launcher.get_turbogrid_exe_path()
        version_path = launcher.get_turbogrid_exe_path(product_version="23.2")

        os.environ["PYTURBOGRID_TURBOGRID_ROOT"] = "/TGRoot/"
        pyturbogrid_env_path = launcher.get_turbogrid_exe_path(product_version="23.2")
        specified_path = launcher.get_turbogrid_exe_path(turbogrid_path="/MyPath/MyExe.exe")

        if platform.system() == "Windows":
            exe_suffix = ".exe"
        else:
            exe_suffix = ""

        assert str(latest_path) == str(Path(r"/myansys/v232/TurboGrid/bin/cfxtg")) + exe_suffix
        assert str(version_path) == str(Path(r"/myansys/v232/TurboGrid/bin/cfxtg")) + exe_suffix
        assert str(pyturbogrid_env_path) == str(Path(r"/TGRoot/bin/cfxtg")) + exe_suffix
        assert str(specified_path) == str(Path(r"/MyPath/MyExe.exe"))

        del os.environ["AWP_ROOT232"]
        with pytest.raises(RuntimeError, match="No Ansys version can be found."):
            print(launcher.get_latest_ansys_version())

    finally:
        for var, value in vars_to_restore.items():
            if value:
                os.environ[var] = value
            else:
                del os.environ[var]
        print("New:" + os.environ["AWP_ROOT232"])


def test_launch_turbogrid():
    # Error conditions only; successful usage is covered in other tests
    with pytest.raises(TypeError, match="got an unexpected keyword argument"):
        tg = launcher.launch_turbogrid(bad_arg="value")
