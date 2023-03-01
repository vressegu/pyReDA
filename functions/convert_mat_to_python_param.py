# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 15:09:54 2019

@author: matheus.ladvig
"""

import hdf5storage # import the package resposible to convert
import numpy as np


def convert_mat_to_python_param(PATH_MAT_FILE):

    # Load the mat file of this path
    mat = hdf5storage.loadmat(PATH_MAT_FILE)
    
    # The param has the key 'param'
    param = mat['param']
    # Create the dictionary that will stock the data
    param_dict = {}
    
    param_dict = open_struct(param)
    
    return param_dict.copy()    

def open_struct(struct):
    
    
    struct_dict = {}
    # Loop to run all the dtypes in the data
    for name in struct.dtype.names :
        struct_dict[name] = open_struct_field(struct[name])
          
    return struct_dict

    
def open_struct_field(struct_field):
    
    if ( (type(struct_field) is dict) or \
         (type(struct_field) is np.void)  ):
        field = open_struct(struct_field)
    elif (type(struct_field) is list):
        field = open_struct_field(struct_field[0])
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
            
    return field
    
