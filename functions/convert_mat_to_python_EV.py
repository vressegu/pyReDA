# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 15:09:54 2019

@author: matheus.ladvig
"""

import hdf5storage # import the package resposible to convert


def convert_mat_to_python_EV(PATH_MAT_FILE):

    # Load the mat file of this path
    mat_EV = hdf5storage.loadmat(PATH_MAT_FILE)
    
    pchol_cov_noises = mat_EV['ILC_EV']['EV'][0][0]['pchol_cov_noises'][0][0]
    I = mat_EV['ILC_EV']['EV'][0][0]['I'][0][0]
    L = mat_EV['ILC_EV']['EV'][0][0]['L'][0][0]
    C = mat_EV['ILC_EV']['EV'][0][0]['C'][0][0]
    
    ILC_EV = {}
    ILC_EV['pchol_cov_noises']=pchol_cov_noises
    ILC_EV['I']=I
    ILC_EV['L']=L
    ILC_EV['C']=C
    
    del mat_EV
    
    
    return ILC_EV

if __name__ == '__main__':
    PATH_MAT_FILE = 'D:/python_scripts/resultats/current_results/1stresult_incompact3D_noisy2D_40dt_subsampl_truncated_2_modes__a_cst__decor_by_subsampl_bt_decor_choice_auto_shanon_threshold_1e-05fct_test_b_fullsto_no_correct_drift.mat'
    param_dict = convert_mat_to_python_EV(PATH_MAT_FILE)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    