# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 15:09:54 2019

@author: matheus.ladvig
"""

import hdf5storage # import the package resposible to convert
import numpy as np


def convert_mat_to_python(PATH_MAT_FILE):

    # Load the mat file of this path
    mat = hdf5storage.loadmat(PATH_MAT_FILE)
    
    
    # The param has the key 'param'
    param = mat['param']
    # Create the dictionary that will stock the data
    param_dict = {}
    
    param_dict = open_struct(param)
    
#    # Loop to run all the dtypes in the data
#    for name in param.dtype.names :
##        if name == 'lambda':
##            print(3)
#        
#        # If the dtype has only one information we take his name and create a key for this information
#        if param[0][name][0].dtype.names == None:
#            if param[0][name].shape[0] >1:
#                param_dict[name] = param[0][name]
#            elif param[0][name][0].shape == (1,1):
#                param_dict[name] = param[0][name][0][0,0]
#            elif param[0][name][0].shape == (1,):
#                param_dict[name] = param[0][name][0][0]
#            else:
#                param_dict[name] = param[0][name][0]
#        # If not, we need to create a dict that will be resposnsible to stock all fields of this structure
#        
#        else:
#            aux_dict = {}
#            for name2 in param[0][name][0].dtype.names:
##                if param[0][name][0][name2][0].shape == (1,1,1):
##                    aux_dict[name2] = param[0][name][0][name2][0,0,0]
##                else:
##                    aux_dict[name2] = param[0][name][0][name2][0]
#                if param[0][name][0][name2][0].shape == (1,1):
#                    aux_dict[name2] = param[0][name][0][name2][0][0][0]
#                elif param[0][name][0][name2][0].shape == (1,):
#                    aux_dict[name2] = param[0][name][0][name2][0][0]
#                else:
#                    aux_dict[name2] = param[0][name][0][name2][0]
##                aux_dict[name2] = param[0][name][0][name2][0][0][0]
##                if aux_dict[name2].shape == (1,):
##                    aux_dict[name2] = aux_dict[name2][0]
#                    
#                    
#            param_dict[name] = aux_dict
      
    
    I_sto = mat['I_sto']
    L_sto = mat['L_sto']
    C_sto = mat['C_sto']
    
    I_deter = mat['I_deter']
    L_deter = mat['L_deter']
    C_deter = mat['C_deter']
    
    plot_bts = mat['plot_bts']
    
    pchol_cov_noises = mat['pchol_cov_noises']
    
    bt_tot = mat['bt_tot']
    
    
    return I_sto,L_sto,C_sto,I_deter,L_deter,C_deter,plot_bts,pchol_cov_noises,bt_tot,param_dict.copy()
    

def open_struct(struct):
    
    
    struct_dict = {}
    # Loop to run all the dtypes in the data
    for name in struct.dtype.names :
#        struct_dict[name] = open_strcut_field(struct[0][name]) ???
#        if name == 'lambda':
#            print(name)
        struct_dict[name] = open_struct_field(struct[name])
        
    
    
#        if not (struct[0][name].dtype.names == None:):
#            struct_dict[name] = open_struct(struct[0][name][0])
#        elif 
#            
#        # If the dtype has only one information we take his name and create a key for this information
#        if struct[0][name].dtype.names == None:
#            
#            if struct[0][name][0].dtype.names == None:
#                if struct[0][name].shape[0] >1:
#                    if len(struct[0][name].shape) >1:
#                        if struct[0][name].shape[1] == 1:
#                            struct_dict[name] = struct[0][name][:,0]
#                        else:
#                            struct_dict[name] = struct[0][name]
#                    else:
#                        struct_dict[name] = struct[0][name]
#                elif len(struct[0][name].shape) >1:
#                    if struct[0][name].shape[1]>1:
#                        struct_dict[name] = struct[0][name][0,:]
#                    else:
#                        struct_dict[name] = struct[0][name][0,0]  
#                elif struct[0][name][0].shape[0] >1:
#                    if len(struct[0][name][0].shape) >1:
#                        if struct[0][name][0].shape[1] == 1:
#                            struct_dict[name] = struct[0][name][0][:,0]
#                        else:
#                            struct_dict[name] = struct[0][name][0]
#                    else:
#                        struct_dict[name] = struct[0][name][0]
#                elif len(struct[0][name][0].shape) >1:
#                    if struct[0][name][0].shape[1]>1:
#                        struct_dict[name] = struct[0][name][0][0,:]
#                    else:
#                        struct_dict[name] = struct[0][name][0][0,0]
#                elif struct[0][name][0].shape == (1,1):
#                    struct_dict[name] = struct[0][name][0][0,0]
#                elif struct[0][name][0].shape == (1,):
#                    struct_dict[name] = struct[0][name][0][0]
#                else:
#                    struct_dict[name] = struct[0][name][0]
#            # If not, we need to create a dict that will be resposnsible to stock all fields of this structure
#        
#        else:
#            struct_dict[name] = open_struct(struct[0][name][0])
##            aux_dict = {}
##            for name2 in struct[0][name][0].dtype.names:
##    #                if struct[0][name][0][name2][0].shape == (1,1,1):
##    #                    aux_dict[name2] = struct[0][name][0][name2][0,0,0]
##    #                else:
##    #                    aux_dict[name2] = struct[0][name][0][name2][0]
##                if struct[0][name][0][name2][0].shape == (1,1):
##                    aux_dict[name2] = struct[0][name][0][name2][0][0][0]
##                elif struct[0][name][0][name2][0].shape == (1,):
##                    aux_dict[name2] = struct[0][name][0][name2][0][0]
##                else:
##                    aux_dict[name2] = struct[0][name][0][name2][0]
##    #                aux_dict[name2] = struct[0][name][0][name2][0][0][0]
##    #                if aux_dict[name2].shape == (1,):
##    #                    aux_dict[name2] = aux_dict[name2][0]
                
    return struct_dict

#def open_strcut_field(struct_filed):
#    
#    if not (struct[0][name].dtype.names == None):
#        struct_dict[name] = open_struct(struct[0][name][0])
#    else:
#    
#        # If the dtype has only one information we take his name and create a key for this information
#        if struct[0][name][0].dtype.names == None:
#            if struct[0][name].shape[0] >1:
#                if len(struct[0][name].shape) >1:
#                    if struct[0][name].shape[1] == 1:
#                        struct_dict[name] = struct[0][name][:,0]
#                    else:
#                        struct_dict[name] = struct[0][name]
#                else:
#                    struct_dict[name] = struct[0][name]
#            elif len(struct[0][name].shape) >1:
#                if struct[0][name].shape[1]>1:
#                    struct_dict[name] = struct[0][name][0,:]
#                else:
#                    struct_dict[name] = struct[0][name][0,0]
#                    
#            elif struct[0][name][0].shape == (1,1):
#                struct_dict[name] = struct[0][name][0][0,0]
#            elif struct[0][name][0].shape == (1,):
#                struct_dict[name] = struct[0][name][0][0]
#            else:
#                struct_dict[name] = struct[0][name][0]
#        # If not, we need to create a dict that will be resposnsible to stock all fields of this structure
#        
#        else:
#            struct_dict[name] = open_struct(struct[0][name][0])
#            
#            
#    return field
    
    
def open_struct_field(struct_field):
    
    
        
    if ( (type(struct_field) is dict) or \
         (type(struct_field) is np.void)  ):
        field = open_struct(struct_field)
    elif (type(struct_field) is list):
        field = open_struct_field(struct_field[0])
#    elif ( (type(struct_field) is np.bool_) or \
#         (type(struct_field) is np.str_)  ):
#        field = struct_field
    elif (type(struct_field) is np.ndarray):
        if not (struct_field.dtype.names == None):
            field = open_struct(struct_field)
        elif struct_field.shape[0] >1:
            if len(struct_field.shape) >1:
                if struct_field.shape[1] == 1:
                    field = struct_field[:,0]
                else:
                    field = struct_field
            else:
                field = struct_field
        elif len(struct_field.shape) >1:
            if struct_field.shape[1]>1:
                field = open_struct_field(struct_field[0,:])
            else:
                field = open_struct_field(struct_field[0,0])
        elif struct_field.shape == (1,):
                field = struct_field[0]
        else:
            print(type(struct_field))
            print(struct_field.shape)
            assert False, 'Error'
    else:
        field = struct_field
#        print((struct_field))
#        print(type(struct_field))
#        assert False, 'Error'
            
    return field
    
    
if __name__ == '__main__':
    PATH_MAT_FILE = 'D:/python_scripts/resultats/current_results/1stresult_incompact3D_noisy2D_40dt_subsampl_truncated_2_modes__a_cst__decor_by_subsampl_bt_decor_choice_auto_shanon_threshold_1e-05fct_test_b_fullsto_no_correct_drift.mat'
    param_dict = convert_mat_to_python(PATH_MAT_FILE)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    