# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 15:09:54 2019

@author: matheus.ladvig
"""

import hdf5storage # import the package resposible to convert
import numpy as np

def convert_mat_to_python_ILCpchol(PATH_MAT_FILE):

    # Load the mat file of this path
    mat = hdf5storage.loadmat(PATH_MAT_FILE)
        
    I_sto = mat['I_sto']
    L_sto = mat['L_sto']
    C_sto = mat['C_sto']
    
    I_deter = mat['I_deter']
    L_deter = mat['L_deter']
    C_deter = mat['C_deter']
    
    pchol_cov_noises = mat['pchol_cov_noises']
    
    return I_sto,L_sto,C_sto,I_deter,L_deter,C_deter,pchol_cov_noises    

