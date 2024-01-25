# Copyright (c) 2024 ANSYS, Inc. All rights reserved
#
# A multi_blade_row (MBR) instance represents a single rotating machine.
# MBR will spawn a single_blade_row (SBR) for each blade that is being considered.
# MBR job dispatch has two concepts. Jobs may be dispatched to a single row,
# or multiple rows in parallel.

from pathlib import Path
import ansys.turbogrid.core.ndf_parser.ndf_parser as ndf_parser


class multi_blade_row:
    initialized: bool = False
    init_file_path: Path

    # Consider passing in the filename (whether ndf or tginit) as initializing as raii
    def __init__(self):
        pass

    # a A TGInit parser would need to be written for this to work
    # def init_from_tginit(self, tginit_path: str):
    #     pass

    def init_from_ndf(self, ndf_path: str):
        all_blade_rows = ndf_parser.NDFParser(ndf_path).get_blade_row_blades()
        print(f"Blade Rows to mesh: {all_blade_rows}")
