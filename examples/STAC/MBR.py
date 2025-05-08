
import json
import os
from ansys.turbogrid.core.launcher.launcher import get_turbogrid_exe_path, launch_turbogrid
from ansys.turbogrid.core.multi_blade_row.multi_blade_row import multi_blade_row as MBR
from ansys.turbogrid.core.multi_blade_row.single_blade_row import single_blade_row as SBR
from ansys.turbogrid.core.multi_blade_row.multi_blade_row import MachineSizingStrategy

def setting_spanwise_elements(turbogrid_instance, number_of_spanwise_elemenst,num_const_elements_spanwise ): 
    turbogrid_instance.set_obj_param(object='/MESH DATA',param_val_pairs='Spanwise Blade Distribution Option = Element Count and Size')
    turbogrid_instance.set_obj_param(object='/MESH DATA',param_val_pairs=f'Number Of Spanwise Blade Elements = {number_of_spanwise_elemenst}')
    turbogrid_instance.set_obj_param(object='/MESH DATA',param_val_pairs=f'Number Of Constant Spanwise Blade Elements = {num_const_elements_spanwise}')
    turbogrid_instance.unsuspend(object="/TOPOLOGY SET")


def set_inlet_outlet_through_axial_point(turbogrid_instance, inlet_param_value_shroud, inlet_param_value_hub, outlet_param_value_shroud , outlet_param_value_hub ): 
    
    if inlet_param_value_shroud is not None: 
        turbogrid_instance.set_obj_param(object='/GEOMETRY/INLET',param_val_pairs='Opening Mode = Parametric')
        turbogrid_instance.set_obj_param(object='/GEOMETRY/INLET',param_val_pairs=f'Parametric Hub Location = {inlet_param_value_hub}')
        turbogrid_instance.set_obj_param(object='/GEOMETRY/INLET',param_val_pairs=f'Parametric Shroud Location = {inlet_param_value_shroud}')
        #set inlet domain 
        turbogrid_instance.set_obj_param(object='/MESH DATA',param_val_pairs=f'Inlet Domain = On')
  

    else: 
        turbogrid_instance.set_obj_param(object='/GEOMETRY/INLET',param_val_pairs='Opening Mode = Fully extend')

    if outlet_param_value_shroud is not None: 
        turbogrid_instance.set_obj_param(object='/GEOMETRY/OUTLET',param_val_pairs='Opening Mode = Parametric')
        turbogrid_instance.set_obj_param(object='/GEOMETRY/OUTLET',param_val_pairs=f'Parametric Hub Location = {outlet_param_value_hub}')
        turbogrid_instance.set_obj_param(object='/GEOMETRY/OUTLET',param_val_pairs=f'Parametric Shroud Location = {outlet_param_value_shroud}')
        #set outlet domain
        turbogrid_instance.set_obj_param(object='/MESH DATA',param_val_pairs=f'Outlet Domain = On')

    else: 
        turbogrid_instance.set_obj_param(object='/GEOMETRY/OUTLET',param_val_pairs='Opening Mode = Fully extend')



#create turbogrid instance for each row seperately
s1 = launch_turbogrid()
s0 = launch_turbogrid()
r1 = launch_turbogrid()
r0 = launch_turbogrid()

#read curve files for all rows 
s1.read_inf("S1.inf")
s0.read_inf("S0.inf")
r1.read_inf("R1.inf")
r0.read_inf("R0.inf")


#for each row create single blade row object
#single blade row objects are assigned the respective turbogrid instances 

S1 = SBR()
S1.pytg = s1

S0 = SBR()
S0.pytg = s0

R1 = SBR()
R1.pytg = r1

R0 = SBR()
R0.pytg = r0

#create a multi blade row object - represents the entire turbine
machine = MBR()

#assign the single blade row intsances to the multi blade row object
machine.tg_worker_instances = {'S1':S1,'R1':R1,'S0':S0,'R0':R0}

#set the base global size factors for all rows
machine.base_gsf = {'S1':1.0,'R1':1.0,'S0':1.0,'R0':1.0}


#add shroud Tip for R1 and R0 
r1.set_obj_param(object = "/GEOMETRY/BLADE SET/SHROUD TIP", param_val_pairs = 'Option = Normal Distance' )
r1.set_obj_param(object = "/GEOMETRY/BLADE SET/SHROUD TIP", param_val_pairs = 'Tip Clearance = 0.0064 [m]' )

r0.set_obj_param(object = "/GEOMETRY/BLADE SET/SHROUD TIP", param_val_pairs = 'Option = Normal Distance' )
r0.set_obj_param(object = "/GEOMETRY/BLADE SET/SHROUD TIP", param_val_pairs = 'Tip Clearance = 0.0127 [m]' )

#unsuspend topology for all rows to edit mesh
s1.unsuspend(object="/TOPOLOGY SET")
r1.unsuspend(object="/TOPOLOGY SET")
s0.unsuspend(object="/TOPOLOGY SET")
r0.unsuspend(object="/TOPOLOGY SET")



#need to set number of blade sets for each row (info not taken from inf file)
machine.set_number_of_blade_sets('S1', 39)
machine.set_number_of_blade_sets('R1', 41)
machine.set_number_of_blade_sets('S0', 37)
machine.set_number_of_blade_sets('R0', 45)

machine.set_machine_sizing_strategy(MachineSizingStrategy.NONE)

#set spanwise count equally for all
num_elements_spanwise = 70 
num_const_elements_spanwise = 20

setting_spanwise_elements(s1,num_elements_spanwise,num_const_elements_spanwise)
setting_spanwise_elements(r1,num_elements_spanwise,num_const_elements_spanwise)
setting_spanwise_elements(s0,num_elements_spanwise,num_const_elements_spanwise)
setting_spanwise_elements(r0,num_elements_spanwise,num_const_elements_spanwise)

#set overall size factor
machine.set_machine_size_factor(2)
#machine.set_machine_target_node_count(4000000)

#setting inlet & outlet positions
set_inlet_outlet_through_axial_point(s1,None,None,None,None)
set_inlet_outlet_through_axial_point(r1,None,None,0.432829,0.504232)
set_inlet_outlet_through_axial_point(s0,0.438232,0.37711,None,None)
set_inlet_outlet_through_axial_point(r0,None,None,0.219331,0.152905)



#Mesh Information
element_num = machine.get_element_counts()
print(f"element numbers \n S1: {element_num['S1']} elements \n R1: {element_num['R1']} elements \n S0: {element_num['S0']} elements \n R0: {element_num['R0']} elements \n Total: {sum(element_num.values())} elements")


#save rows as def files 
machine.save_meshes()

machine.tg_worker_instances = None

s1.quit()
s0.quit()
r1.quit()
r0.quit()

