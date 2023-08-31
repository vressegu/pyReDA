# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 16:13:50 2019

@author: matheus.ladvig, valentin resseguier
.


"""
import numpy as np
import math
import sys
from pathlib import Path

from param_from_info_txt_file import super_main_globalParam_from_info_txt_file

from main_from_existing_ROM import main_from_existing_ROM
    
def switch_type_data(argument):
    switcher = {
        'incompact3D_noisy2D_40dt_subsampl_truncated': [[1e-05],[False]],
        'DNS100_inc3d_2D_2018_11_16_blocks_truncated': [[1e-06],[True]], # BEST
        'turb2D_blocks_truncated': [[1e-05],[False,True]],
        'incompact3d_wake_episode3_cut_truncated': [[1e-06],[False]],
        'incompact3d_wake_episode3_cut': [[1e-06],[False]],
        'LES_3D_tot_sub_sample_blurred': [[1e-03],[True]],
        'inc3D_Re3900_blocks': [[1e-03],[True]],
        'inc3D_Re3900_blocks_truncated': [[1e-03],[True]],
        'DNS300_inc3d_3D_2017_04_02_NOT_BLURRED_blocks_truncated':[[1e-04],[True]] # BEST
       
    }
    return switcher.get(argument,[[0.0005],[False]])


if __name__ == '__main__':

    no_subampl_in_forecast = False 
    vect_reconstruction = [False] # for the super_main_from_existing_ROM
    #vect_adv_corrected = [False,True]
    vect_adv_corrected = [True]
    test_fct = 'b'
    svd_pchol = 2
    choice_n_subsample = 'htgen2'
    stochastic_integration = 'Ito'
    estim_rmv_fv = True
    vect_eq_proj_div_free = [2]
    
    thrDtCorrect = False
    noBugSubsampl = False
    
    vect_nb_mutation_steps = [-1]                # Number of mutation steps in particle filter 

    # temporalScheme = "euler"
    # temporalScheme = "adams-bashforth"

    n_particle = 100
    # HilbertSpace = "L2wBC"
    # HilbertSpace = "H1"
    HilbertSpace = "L2"
    freqBC = 100

    # parameters defined in [run_info.txt] file
    #
    # DATA SET examples :
    #   type_data = 'incompact3D_noisy2D_40dt_subsampl_truncated'  # dataset to debug
    #   type_data = 'DNS300_inc3d_3D_2017_04_02_NOT_BLURRED_blocks_truncated' # Reynolds 300
    #   type_data = 'DNS100_inc3d_2D_2018_11_16_blocks_truncated'  # Reynolds 100
    #
    # SECONDS_OF_SIMU :
    #   for example to have 331 seconds of real PIV data for reynolds=300 : we have 4103 files. --> 
    #   ( 4103*0.080833 = 331).....78 max in the case of fake_PIV : SECONDS_OF_SIMU <= 78
    #
    # vect_nb_modes :
    #   for example to test 4 nb_modes = 8,6,4 and 2], the [run_info.txt] file
    #   must have a line like "vect_nb_modes 8,6,4,2"
    #
    # EV : Eddy Viscosity model
    #   if EV=2 : Eddy Viscosity model with random IC only 
    #   if EV=1 : Eddy Viscosity model with noise and random IC 
    #   if EV=0 : no Eddy Viscosity model

    MORAANE_PATH = Path(__file__).parents[2]
    print("PATH="+str(MORAANE_PATH))
    
    param_file = Path(MORAANE_PATH).joinpath('pyReDA/run_info.txt')
    print("     Cf. run_file [", str(param_file)+"]")
    
    if not ('temporalScheme' in locals()):
        temporalScheme = "euler"
    vect_nb_modes, type_data, SECONDS_OF_SIMU, EV = super_main_globalParam_from_info_txt_file(param_file)
    
    if vect_nb_modes == None:
        print('\n!!! ERROR: vect_nb_modes undefined !!!\n  => change values in ['+str(param_file)+'] file')
        sys.exit()
    
    # Get threshold and modal_dt
    if choice_n_subsample == 'auto_shanon' :
        v_threshold,vect_modal_dt = switch_type_data(type_data)
    else:
         v_threshold = [float('nan')]
         vect_modal_dt = [False]
    
    nb_period_test = math.nan
    nb_modes_max = np.max(vect_nb_modes)
    
    # writting INFO file

    file_info = Path(MORAANE_PATH).joinpath('3rdresult/test_input.info')
  
    print("\n---> Cf. INFO file = ", str(file_info), "------\n" ) 
    f_info = open(file_info,'w')
    
    f_info.write("\n ------ INPUT parameters for [main_from_existing_ROM] function ------ \n\n" )
    
    f_info.write("  - vect_nb_modes          = " + str(vect_nb_modes) + "\n")
    f_info.write("  - v_threshold            = " + str(v_threshold) + "\n")
    f_info.write("  - vect_reconstruction    = " + str(vect_reconstruction) + "\n")
    f_info.write("  - vect_adv_corrected     = " + str(vect_adv_corrected) + "\n")
    f_info.write("  - vect_modal_dt          = " + str(vect_modal_dt) + "\n")
    f_info.write("  - vect_eq_proj_div_free  = " + str(vect_eq_proj_div_free) + "\n")
    f_info.write("  - vect_nb_mutation_steps = " + str(vect_nb_mutation_steps) + "\n")

    f_info.write("  - type_data              = " + str(type_data) + "\n")
    f_info.write("  - nb_period_test         = " + str(nb_period_test) + "\n")
    f_info.write("  - no_subampl_in_forecast = " + str(no_subampl_in_forecast) + "\n")
    f_info.write("  - n_particle             = " + str(n_particle) + "\n")
    f_info.write("  - temporalScheme             = " + str(temporalScheme) + "\n")
    f_info.write("  - HilbertSpace             = " + str(HilbertSpace) + "\n")
    f_info.write("  - test_fct               = " + str(test_fct) + "\n")
    f_info.write("  - svd_pchol              = " + str(svd_pchol) + "\n")
    f_info.write("  - stochastic_integration = " + str(stochastic_integration) + "\n")
    f_info.write("  - estim_rmv_fv           = " + str(estim_rmv_fv) + "\n")
    f_info.write("  - thrDtCorrect           = " + str(thrDtCorrect) + "\n")
    f_info.write("  - noBugSubsampl          = " + str(noBugSubsampl) + "\n")
    f_info.write("  - choice_n_subsample     = " + str(choice_n_subsample) + "\n")
    f_info.write("  - EV                     = " + str(EV) + "\n")
    f_info.write("  - SECONDS_OF_SIMU        = " + str(SECONDS_OF_SIMU) + "\n")

    f_info.write("\n")
 
    f_info.close()  
   
    for eq_proj_div_free in vect_eq_proj_div_free:
        for nb_mutation_steps in vect_nb_mutation_steps:
            for modal_dt in vect_modal_dt:
                for threshold in v_threshold:
                    for adv_corrected in vect_adv_corrected:
                        for reconstruction in vect_reconstruction:
                            for k in vect_nb_modes:
                                main_from_existing_ROM(k,threshold,type_data,nb_period_test,\
                                                       no_subampl_in_forecast,reconstruction,\
                                                       adv_corrected,modal_dt,n_particle,\
                                                       temporalScheme,HilbertSpace,freqBC,\
                                                       test_fct,svd_pchol,\
                                                       stochastic_integration,\
                                                       estim_rmv_fv,eq_proj_div_free,\
                                                       thrDtCorrect,\
                                                       noBugSubsampl,\
                                                       choice_n_subsample,EV,\
                                                       nb_mutation_steps,
                                                       SECONDS_OF_SIMU)
    

