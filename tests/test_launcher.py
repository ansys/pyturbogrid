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
        "AWP_ROOT241": os.environ.get("AWP_ROOT241", None),
        "PYTURBOGRID_TURBOGRID_ROOT": os.environ.get("PYTURBOGRID_TURBOGRID_ROOT", None),
    }

    try:
        os.environ["AWP_ROOT232"] = "/myansys/v232"
        os.environ["AWP_ROOT241"] = "/myansys2/v241"

        latest_path = launcher.get_turbogrid_exe_path()
        version_path = launcher.get_turbogrid_exe_path(product_version="23.2")

        os.environ["PYTURBOGRID_TURBOGRID_ROOT"] = "/TGRoot/"
        pyturbogrid_env_path = launcher.get_turbogrid_exe_path(product_version="23.2")
        specified_path = launcher.get_turbogrid_exe_path(turbogrid_path="/MyPath/MyExe.exe")

        if platform.system() == "Windows":
            exe_suffix = ".exe"
        else:
            exe_suffix = ""

        assert str(latest_path) == str(Path(r"/myansys2/v241/TurboGrid/bin/cfxtg")) + exe_suffix
        assert str(version_path) == str(Path(r"/myansys/v232/TurboGrid/bin/cfxtg")) + exe_suffix
        assert str(pyturbogrid_env_path) == str(Path(r"/TGRoot/bin/cfxtg")) + exe_suffix
        assert str(specified_path) == str(Path(r"/MyPath/MyExe.exe"))

        del os.environ["AWP_ROOT232"]
        del os.environ["AWP_ROOT241"]

        with pytest.raises(RuntimeError, match="No Ansys version can be found."):
            print(launcher.get_latest_ansys_version())

    finally:
        for var, value in vars_to_restore.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]


def test_launch_turbogrid():
    # Error conditions only; successful usage is covered in other tests
    with pytest.raises(TypeError, match="got an unexpected keyword argument"):
        tg = launcher.launch_turbogrid(bad_arg="value")
