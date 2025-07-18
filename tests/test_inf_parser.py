# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

import pathlib

from ansys.turbogrid.core.inf_parser.inf_parser import INFParser

install_path = pathlib.PurePath(__file__).parent.parent.as_posix()


def test_inf_parser(pytestconfig):
    inf_path = f"{install_path}/tests/rotor37/BladeGen.inf"
    contents = INFParser.get_inf_contents(inf_path)
    assert contents == {
        "Axis of Rotation": "Z",
        "Number of Blade Sets": "36",
        "Geometry Units": "CM",
        "Hub Data File": "hub.curve",
        "Shroud Data File": "shroud.curve",
        "Profile Data File": "profile.curve",
    }
