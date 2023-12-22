# Copyright (c) 2023 ANSYS, Inc. All rights reserved
"""Module for working on a multi blade-row turoomachinery case using PyTurboGrid instances in parallel."""

import ndf_parser.ndf_parser as ndfp
import os


from multiprocessing import cpu_count

class MBR:
    """
    Facilitates working on a multi blade-row turoomachinery case using PyTurboGrid instances in parallel.
    """

    _working_dir:str = None
    _case_directory:str = None
    _case_ndf:str = None
    _ndf_file_full_path:str = None  
    _results_directory:str = None
    _ndf_parser:ndfp.NDFParser = None  

    _blade_rows_to_mesh:dict = None
    _multi_process_count:int = 0
    _blade_row_gsfs:dict = None
    _blade_first_element_offsets:dict = None
    _custom_blade_settings:dict = None

    def __init__(self, 
                 working_dir:str,
                 case_directory:str,
                 ndf_file_name:str):
        """
        Initialize the class using name with full path of an NDF file for the multi blade row case.

        Parameters
        ----------
        ndf_file_full_name : str
            Name with full path of the NDF file containing the blade rows for the multi blade row case.
        """
        self._set_working_directory(working_dir)
        self._results_directory = self._set_case_directory_and_ndf(case_directory,ndf_file_name)
        self._ndf_parser = ndfp.NDFParser(self._ndf_file_full_path)
        raise(Exception("Implement self._assert_all_rows_single_and_unique_bladed()"))
        self._assert_unique_blade_names()
    
    def set_blade_rows_to_mesh(self,
                               blades_to_mesh:list[str]):
        all_blade_rows = self._ndf_parser.get_blade_row_blades()
        blade_row_names_to_mesh = [x for x in all_blade_rows if (len(blades_to_mesh) == 0 or all_blade_rows[x][0] in blades_to_mesh)]
        for blade_row in blade_row_names_to_mesh:
            self._blade_rows_to_mesh[blade_row] = all_blade_rows[blade_row]
        print(f"Blade rows to mesh: {self._blade_rows_to_mesh.keys()}")
        for blade_row in self._blade_rows_to_mesh:
            print(f"Blade row {blade_row} blades: {self._blade_rows_to_mesh[blade_row]}")

    def set_multi_process_count(self, 
                                multi_process_count):
        num_rows_to_process = len(self._blade_rows_to_mesh)
        if num_rows_to_process == 0:
            self._multi_process_count = 0
            return
        max_producers = cpu_count()
        multi_process_count_clamped = min(max(0,multi_process_count), max_producers)
        num_producers = min(num_rows_to_process,multi_process_count_clamped)
        num_producers = num_producers if num_producers > 0 else max_producers
        # print(f"{cpu_count()=}")
        # print(f"{max_producers=}")
        # print(f"{multi_process_count_clamped=}")
        # print(f"{num_producers=}")
        self._multi_process_count = num_producers

    def set_blade_row_gsfs(self,
                           assembly_gsf):
        self._blade_row_gsfs = self._get_blade_row_gsfs(assembly_gsf)
        #print(f"blade_row_gsfs {blade_row_gsfs}")
        
    def set_spanwise_counts(self,
                            stator_spanwise_count,
                            rotor_spanwise_count,
                            rotor_blade_rows):
        self._blade_row_spanwise_counts = self._get_blade_row_spanwise_counts(self,
                                                                              stator_spanwise_count,
                                                                              rotor_spanwise_count,
                                                                              rotor_blade_rows)        
        #print(f"blade_row_spanwise_counts {blade_row_spanwise_counts}")
        
    def set_blade_first_element_offsets(self,
                                        assembly_f_el_offset,
                                        custom_blade_f_el_offsets):
        self._blade_first_element_offsets = self._get_blade_feloffs(assembly_f_el_offset,
                                                                    custom_blade_f_el_offsets)
        #print(f"blade_first_element_offsets {blade_first_element_offsets}")

    def set_custom_blade_settings(self,
                                  custom_blade_settings):
        self._custom_blade_settings = custom_blade_settings

    ######################################
    # Private methods
    ######################################
        
    def _set_working_directory(self, 
                               working_dir:str):
        if not os.path.isdir(working_dir):
            print(f"Folder {working_dir} does not exists.")
            exit()
        os.chdir(working_dir) 
        self._working_dir = working_dir
    
    def _set_case_directory_and_ndf(self, 
                                    case_directory:str,
                                    ndf_file:str) -> str:
        if os.path.isabs(case_directory):
            self._case_directory = case_directory
        else:
            self._case_directory = os.path.join(self._working_dir,case_directory)
        if not os.path.isdir(self._case_directory):
            print(f"Case folder {self._case_directory} does not exists.")
            exit()

        self._ndf_file_full_path = os.path.join(self._case_directory,ndf_file)
        
        case_base_name = os.path.basename(os.path.normpath(self._case_directory))        
        self._results_directory = os.path.join(self._working_dir,case_base_name+"_results")
        if not os.path.isdir(self._results_directory):
            print(f"Creating target folder {self._results_directory}.")
            os.mkdir(self._results_directory)
        os.chdir(self._results_directory)          
        print("Target location set to: ",os.getcwd())        
        
        return self._results_directory

    def _get_blade_row_gsfs(self, 
                            assembly_gsf):
        blade_row_gsfs = {}
        for blade_row in self._blade_rows_to_mesh:
            blade_row_gsfs[blade_row] = assembly_gsf
        return blade_row_gsfs

    def _get_blade_feloffs(self, 
                           assembly_f_el_offset, 
                           custom_blade_f_el_offsets):
        blade_feloffs = {}
        for blade_row in self._blade_rows_to_mesh:
            blade = self._blade_rows_to_mesh[blade_row][0]
            blade_feloffs[blade] = assembly_f_el_offset
            if blade in custom_blade_f_el_offsets:
                blade_feloffs[blade] = custom_blade_f_el_offsets[blade]
        return blade_feloffs

    def _get_blade_row_spanwise_counts(self, 
                                       stator_spanwise_count, 
                                       rotor_spanwise_count,
                                       rotor_blades):
        blade_row_spanwise_counts = {}
        if len(rotor_blades) == 0:
            for i, blade_row in enumerate(self._blade_rows_to_mesh):
                blade = blade_row[1][0]
                if i%2 == 0:
                    #stator
                    blade_row_spanwise_counts[blade_row] = stator_spanwise_count
                else:
                    #rotor
                    blade_row_spanwise_counts[blade_row] = rotor_spanwise_count
        else:
            for blade_row in self._blade_rows_to_mesh:
                blade = blade_row[1][0]
                if blade in rotor_blades:
                    blade_row_spanwise_counts[blade_row] = rotor_spanwise_count
                else:
                    blade_row_spanwise_counts[blade_row] = stator_spanwise_count
        return blade_row_spanwise_counts

    def _get_blade_row_settings(self):
        blade_row_settings = {}
        for blade_row in self._blade_rows_to_mesh:
            blade = blade_row[1][0]
            blade_row_settings[blade] = []
            if self._blade_row_gsfs is not None and blade_row in self._blade_row_gsfs:
                blade_row_settings[blade_row].append(("/MESH DATA",
                                                    f"Global Size Factor={self._blade_row_gsfs[blade_row]}"))
            if self._blade_row_spanwise_counts is not None and blade_row in self._blade_row_spanwise_counts:
                blade_row_settings[blade_row].append(("/MESH DATA",
                                                    f"Spanwise Blade Distribution Option=Element Count and Size"))
                blade_row_settings[blade_row].append(("/MESH DATA",
                                                    f"Number Of Spanwise Blade Elements={self._blade_row_spanwise_counts[blade_row]}"))
            if self._blade_first_element_offsets is not None and blade in self._blade_first_element_offsets:
                this_bl_f_el_off = self._blade_first_element_offsets[blade]
                blade_row_settings[blade_row].append(("/MESH DATA",
                                                      f"Boundary Layer Specification Method=Target First Element Offset"))
                blade_row_settings[blade_row].append((f"/MESH DATA/EDGE SPLIT CONTROL:{blade} Boundary Layer Control",
                                                      f"Target First Element Offset={this_bl_f_el_off} [m]"))
            if self._custom_blade_settings is not None and blade in self._custom_blade_settings:
                blade_row_settings[blade_row].extend(self._custom_blade_settings[blade])
        return blade_row_settings
