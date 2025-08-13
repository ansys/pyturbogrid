from ansys.turbogrid.core.multi_blade_row.multi_blade_row import multi_blade_row as MBR
from ansys.turbogrid.core.multi_blade_row.multi_blade_row import MachineSizingStrategy
import pathlib

install_path = pathlib.PurePath(__file__).parent.parent.as_posix()

# initialize a multblade row object
mbr= MBR()

# blade rows can be initialized from curve files using the init_from_tgmachine function 
# path to the tgmachine file needs to be provided 
# the tg machine file lists the inf files of all rows, must be in correct order --> within inf files path to curve files are given 
# define Interface Method in TGMachine file: 
    # shroud and hub curve for length of individual rows --> "Fully Extend" 
    # shroud and hub curve for entire length of all rows --> "Neighbors" 

tg_machine_path = f"{install_path}/tests/STAC/STAC.TGMachine"
print(f'path =  {tg_machine_path}')
mbr.init_from_tgmachine(tgmachine_path = tg_machine_path)

#------------SETTING SPECIFIC PARAMETERS  --------------------------------------------------------------------------------------------------------------------------
# To set specific parameters for the individual blade rows, the pyturbogrid instance of the row can be accessed via the mbr.tg_worker_instances dictionary
# to do so the set_obj_param function is used with the keywords from the command editor in TurboGrid 
# Example: "Number Of Outlet Elements = 5" in MESH DATA -->  set_obj_param(object='/MESH DATA',param_val_pairs='Number Of Outlet Elements = 5')

# if constant spanwise elements are wanted 
def setting_spanwise_elements(turbogrid_instance, number_of_spanwise_elemenst,num_const_elements_spanwise ): 
    """
    Function to set the spanwise elements for a given TurboGrid instance.
    """
    turbogrid_instance.set_obj_param(object='/MESH DATA',param_val_pairs='Spanwise Blade Distribution Option = Element Count and Size')
    turbogrid_instance.set_obj_param(object='/MESH DATA',param_val_pairs=f'Number Of Spanwise Blade Elements = {number_of_spanwise_elemenst}')
    turbogrid_instance.set_obj_param(object='/MESH DATA',param_val_pairs=f'Number Of Constant Spanwise Blade Elements = {num_const_elements_spanwise}')
    turbogrid_instance.unsuspend(object="/TOPOLOGY SET")

num_elements_spanwise = 70 
num_const_elements_spanwise = 20

setting_spanwise_elements(mbr.tg_worker_instances["S1.inf"].pytg,num_elements_spanwise,num_const_elements_spanwise)
setting_spanwise_elements(mbr.tg_worker_instances["R1.inf"].pytg,num_elements_spanwise,num_const_elements_spanwise)
setting_spanwise_elements(mbr.tg_worker_instances["S0.inf"].pytg,num_elements_spanwise,num_const_elements_spanwise)
setting_spanwise_elements(mbr.tg_worker_instances["R0.inf"].pytg,num_elements_spanwise,num_const_elements_spanwise)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# setting the meshing strategy: MIN_FACE_AREA --> attempts to size each blade row so that the element sizes are all equal 
# (allows for smooth mesh transition between the rows) 
# alternative MachineSizingStrategy is None
mbr.set_machine_sizing_strategy(MachineSizingStrategy.MIN_FACE_AREA)


# Set the entire machine's size factor
# In combination with MachineSizingStrategy.MIN_FACE_AREA this value will define the base size factor for the row 
# with the smallest face area
mbr.set_machine_size_factor(0.2)

# instead of machine size factor one can also specify the target number of elements each row should have
# mbr.set_machine_target_node_count(2000000)

# get an overview of element numbers
element_num = mbr.get_element_counts()
print(f"element numbers \n S1: {element_num['S1.inf']} elements \n R1: {element_num['R1.inf']} elements \n S0: {element_num['S0.inf']} elements \n R0: {element_num['R0.inf']} elements \n Total: {sum(element_num.values())} elements")


#save a def files for all balde rows, which can be opened in CFX pre
mbr.save_meshes()

#allowing shut down (should be mbr.quit() --> fix in next release )
mbr.tg_worker_instances = None
