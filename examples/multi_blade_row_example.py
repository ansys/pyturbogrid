import os
from ansys.turbogrid.core.multi_blade_row.multi_blade_row import MBR

if __name__ == "__main__":
    print("Here")
    mbr_instance = MBR(os.getcwd(),
                       r"E:\AnsysDev\pyAnsys\S947493_concepts_nrec\turb_axial_4stage_geom",
                       "turb_axial_4stage_geom.ndf")
    mbr_instance.set_spanwise_counts(56, 73)
    mbr_instance.set_blade_rows_to_mesh("segment2mainblade")
    #mbr_instance.set_blade_row_gsfs(1.5)
    #mbr_instance.set_blade_first_element_offsets(6e-6,{"segment4mainblade":1e-5})
    mbr_instance.execute()