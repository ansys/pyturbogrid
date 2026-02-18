# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

"""Module for facilitating parsing on NDF file."""

import xml.etree.ElementTree as ET


class NDFParser:
    """
    Facilitates parsing of NDF file and finding various details about the blade rows.
    """

    _ndf_file_full_name = ""
    _tree = None

    def __init__(self, ndf_file_full_name: str):
        """
        Initialize the class using name with full path of an NDF file.

        Parameters
        ----------
        ndf_file_full_name : str
            Name with full path of the NDF file to be parsed.
        """
        self._ndf_file_full_name = ndf_file_full_name
        self._tree = ET.parse(self._ndf_file_full_name)

    def get_blade_row_blades(self) -> dict:
        """
        Get the name of the blade rows and blades in each row.

        Returns
        -------
        dict
            The names of the blade rows and blade in each row return in the form:
            { "bladerow1" : ["blade1", ], "bladerow2" : ["blade2", "splitter1", ], ... }

            If a blade row has no name in the NDF file, a name in the form "bladerowIndex"
            will be assigned where Index is the position of the row in the NDF file among the
            rows starting at position 1.
        """
        root = self._tree.getroot()
        blade_row_blades = {}
        blade_row_names = []
        blade_row_index = 1
        for br in root.iter("bladerow"):
            blade_row_name_in_ndf = br.text.strip(" \r\n")
            blade_row_name_to_use = (
                "bladerow" + str(blade_row_index)
                if blade_row_name_in_ndf == ""
                else blade_row_name_in_ndf
            )
            blade_row_index += 1
            if blade_row_name_to_use in blade_row_names:
                raise Exception(f"{blade_row_name_to_use} name is not unique~")
            this_blade_row_blades = []
            for blade in br.iter("blade-name"):
                this_blade_row_blades.append(blade.text)
            for blade in br.iter("splitter-name"):
                this_blade_row_blades.append(blade.text)
            blade_row_blades[blade_row_name_to_use] = this_blade_row_blades
        return blade_row_blades
