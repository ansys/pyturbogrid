# Copyright (c) 2023 ANSYS, Inc. All rights reserved
"""Module for facilitating parsing on NDF file."""

import xml.etree.ElementTree as ET


class NDFParser:
    """
    Facilitates parsing of NDF file and finding various details about the blade rows.
    """

    _ndf_file_full_name = ""

    def __init__(self, ndf_file_full_name: str):
        self._ndf_file_full_name = ndf_file_full_name

    def get_blade_row_blades(self):
        tree = ET.parse(self._ndf_file_full_name)
        root = tree.getroot()
        blade_row_blades = []
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
            this_blade_row = [blade_row_name_to_use, []]
            for blade in br.iter("blade-name"):
                this_blade_row[1].append(blade.text)
            if len(this_blade_row[1]) != 1:
                print(
                    f"Blade row {this_blade_row[0]} with"
                    f" {len(this_blade_row[1])} blades not supported"
                )
                continue
            blade_row_blades.append(this_blade_row)
        return blade_row_blades
