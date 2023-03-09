# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 17:17:08 2019

@author: matheus.ladvig
"""

    
import json
from plot_bt_dB_MCMC_varying_error import plot_bt_dB_MCMC_varying_error_DA
import time as t_exe
from sklearn import linear_model
import scipy.sparse as sps
from scipy import interpolate
import matplotlib.pyplot as plt
from particle_filter import particle_filter
from evol_forward_bt_MCMC import evol_forward_bt_MCMC
import scipy.io as sio
import numpy as np
import hdf5storage
import sys
from pathlib import Path
from convert_mat_to_python_EV import convert_mat_to_python_EV

from convert_mat_to_python_param import convert_mat_to_python_param
from convert_mat_to_python_ILCpchol import convert_mat_to_python_ILCpchol
from convert_Cmat_to_python_ILCpchol import convert_Cmat_to_python_ILCpchol

from convert_Cmat_to_python_Topos_FakePIV import convert_Cmat_to_python_cropZone
from convert_Cmat_to_python_Topos_FakePIV import convert_Cmat_to_python_lambda
from convert_Cmat_to_python_Topos_FakePIV import convert_Cmat_to_python_bt_tot
from convert_Cmat_to_python_Topos_FakePIV import convert_Cmat_to_python_bt_MCMC
from convert_Cmat_to_python_Topos_FakePIV import convert_Cmat_to_python_Topos
from convert_Cmat_to_python_Topos_FakePIV import convert_Cmat_to_python_FakePIV

from switch_case_param import switch_case
from switch_case_param import default_param

from param_from_info_txt_file import main_globalParam_from_info_txt_file
from param_from_info_txt_file import main_optionalParam_from_info_txt_file
from param_from_info_txt_file import param_from_PIV_info_txt_file
from param_from_info_txt_file import param_from_DNS_to_FakePIV_info_txt_file
from param_from_info_txt_file import param_nan_PIV_info
from param_from_info_txt_file import param_nan_DNS_to_FakePIV

from param_from_Dict_file import param_from_controlDict_file
from param_from_Dict_file import param_from_ITHACADict_file

from plot_bt_dB_MCMC_varying_error_NoEV import plot_bt_dB_MCMC_varying_error_DA_NoEV

from change_mode_sign import change_mode_sign_ILCpchol
from change_mode_sign import change_mode_sign_bt_tot
from change_mode_sign import change_mode_sign_HPivK

from collections import namedtuple

import shutil
import os
import math

import re # for grep search in param file

# Parameters choice : not erased
param_ref = {}

### Parameters often modified which are defined in function [main_globalParam_from_info_txt_file]

# type_data_C : Openfoam dataset
#   example : type_data_C = 'type_data_C  DNS300-D1_Lz1pi' 

# redlumcpp_code_version : version of the code redlumcpp used (ROMDNS, ROMDNS-v1.0, ROMDNS-v1.1, ...)
#   example : redlumcpp_code_version = 'ROMDNS-v1'

# bool_PFD : True if the ROM correct for pressure
# (using Leray projection : Proj. onto the space of Free Divergence functions)
# command redlumcpp-fullOrderPressure
# command redlumcpp-neglectedOrderPressure otherwise
#   example : bool_PFD = True
    
# code_DATA_from_matlab : test basis parameter; if True, MatLab data is used, else openfoam/C++ data is used
#   example : code_DATA_from_matlab = False

# code_ROM_from_matlab : learning basis parameter; if True, MatLab result for ROM is used, else openfoam/C++ result is used
#   example : code_ROM_from_matlab = False

# PATH_openfoam_data : upper PATH for subdirectories [ITHACAoutput], [ROM_PIV], [util] and [FakePIV_noise2]
#   example : ../data_red_lum_cpp

# code_Assimilation : test with assimilation; if False, beta_2=0, beta_3=1, init_centred_on_ref=True and assimilation_period>=SECONDS_OF_SIMU-1
#   example : code_Assimilation = True

# code_load_run : if True, does not simulate but load existing (matlab or C++) run instead
#   example : code_load_run = False

# init_centred_on_ref : if True, INIT condition centered on real condition
#   example :  init_centred_on_ref = False

# beta_2 : parameter that controls the noise in the initialization of the filter
#          if beta_2=0, there is NO noise added to INIT condition
#   example : beta_2 = 1.
             
# beta_3 : the parameter that controls the impact in the model noise -> beta_3 * pchol_cov_noises
#          if beta_3=0, there is NO noise during simulation
#   example : beta_3 = 1.
    
MORAANE_PATH = Path(__file__).parents[2]

param_file = Path(MORAANE_PATH).joinpath('pyReDA/run_info.txt')

print("     Cf. run_file [", str(param_file)+"]")
type_data_C, bool_PFD, code_DATA_from_matlab, code_ROM_from_matlab, \
  code_Assimilation, code_load_run, init_centred_on_ref, \
  redlumcpp_code_version, PATH_openfoam_data, \
  beta_2, beta_3 = main_globalParam_from_info_txt_file(param_file)

if code_load_run:
    if code_Assimilation:
        print('ERROR: loading previous assimilation results is not code yet')
        sys.exit()
    else:
        if code_DATA_from_matlab:
            print('ERROR: loading previous matlab-test-basis results is not code yet')
            sys.exit()

# PATH_openfoam_data : upper PATH for subdirectories [ITHACAoutput], [ROM_PIV], [util] and [FakePIV_noise2]
PATH_openfoam_data = Path(PATH_openfoam_data)
if not PATH_openfoam_data.exists():
    print('\n!!! ERROR: openfoam_data directory ['+str(PATH_openfoam_data)+'] not found !!!')
    sys.exit()
    
# case without assimilation    
if not code_Assimilation:
    init_centred_on_ref = True
    beta_2 = 0.

# if ROM from Cpp and DATA form matlab: change the sign of spatial mode for mode=1
if type_data_C == 'DNS300-D1_Lz1pi':
    vect_num_mode_to_reverse = [1,2]
elif type_data_C == 'DNS300-GeoLES3900':
    vect_num_mode_to_reverse = [1]
elif type_data_C == 'LESRe100-openFoam2106-forYvhan-newSnap':
    vect_num_mode_to_reverse = []
elif type_data_C == 'StationnaryRegime_TestSeparated_Re300':
    vect_num_mode_to_reverse = [1]
elif type_data_C == 'DNS300-test1':
    vect_num_mode_to_reverse = [1,2]
elif type_data_C == 'DNS300-test2':
    vect_num_mode_to_reverse = [1]
elif type_data_C == 'LES100-test':
    vect_num_mode_to_reverse = []
else:
    if (not code_load_run):
        print('ERROR: unknown type_data_C')
if (not code_load_run) & (code_ROM_from_matlab == False):
    if code_DATA_from_matlab == True:
        # modif spatial mode sign for mode=num_mode_to_reverse => 2 choices
        #   1) change I,L,C and psckol_cov_noises matrix
        #   2) change bt_tot, Hpiv and K matrix
        code_change_mode_sign = True # default value
        if code_change_mode_sign == False:
            code_change_mode_sign_ILC = False # default value
            code_change_mode_sign_HpivK_bt_tot = False # default value
        else:
            # if True : change I,L,C and psckol_cov_noises matrix
            code_change_mode_sign_ILC = True
            if code_change_mode_sign_ILC == True:
                code_change_mode_sign_HpivK_bt_tot = False
            else:
                code_change_mode_sign_HpivK_bt_tot = True
    else:
        code_change_mode_sign = False  # default value
        code_change_mode_sign_ILC = False
        code_change_mode_sign_HpivK_bt_tot = False

else:
    code_change_mode_sign = False
    code_change_mode_sign_ILC = False
    code_change_mode_sign_HpivK_bt_tot = False

######################################----PARAMETERS TO CHOOSE----############################################

N_threshold = 40                        # Effective sample size in the particle filter
# Constant that constrol the balance in the new brownian and the old brownian in particle filter
pho = 0.998
linewidth_ = 3.

# The data that will be assimilated : 'real_data'  or 'fake_real_data'
assimilate = 'fake_real_data'


# In this experiments we assimilate 2D data, and in the case Reynolds=300, the vector flow in the z direction will be ignored.
data_assimilate_dim = 2

# We can choose not assimilate all possible moments(time constraints or filter performance constraints or benchmark constraints or decorraltion hypotheses). Hence, select True if subsampling necessary
sub_sampling_PIV_data_temporaly = True
if not code_Assimilation:
    sub_sampling_PIV_data_temporaly = False

# It can be chosen to plot chronos evolution in real time or only at the end of the simulation
plt_real_time = True
if code_load_run:
    plt_real_time = False
plot_period = 2 * float(5/10)/2
heavy_real_time_plot = True  # Compute confidence interval for real-time plots
# plot = orange part (or gray part)
fig_width = 9
fig_height = 4
plot_Q_crit = False
plot_ref_gl = True # plot = dotted black line

mask_obs = True      # True            # Activate spatial mask in the observed data

# Defining the case with 6 varaibles :
#  1) subsampling_PIV_grid_factor_gl :
#      Subsampling constant that will be applied in the observed data, 
#      (i.e if 3 we will take 1 point in 3)
#  2) x0_index_gl :
#      Parameter necessary to chose the grid that we will observe
#      (i.e if 6 we will start the select the start of the observed grid 
#       in the 6th x index, hence we will reduce the observed grid).
#  3) nbPoints_x_gl :
#      Number of points that we will take in account in the observed grid. 
#      Therefore, with this two parameters we can select any possible subgrid 
#      inside the original PIV/DNS grid to observe.
#      Example : if nbPoints_x_gl=70, 
#                then nbPoints_x <= (202 - x0_index) /subsampling_PIV_grid_factor
#  4) y0_index_gl :
#      Parameter necessary to chose the grid that we will observe
#      (i.e if 30 we will start the select the start of the observed grid 
#       in the 30th y index, hence we will reduce the observed grid).
#  5) nbPoints_y_gl :
#      Number of points that we will take in account in the observed grid. 
#      Therefore, with this two parameters we can select any possible subgrid 
#      inside the original PIV/DNS grid to observe.
#      Example : if nbPoints_y_gl=30, 
#                then nbPoints_y <= (74 - y0_index) /subsampling_PIV_grid_factor
#  6) assimilation_period_gl :
#      Example : if  assimilation_period=float(5/10),
#                then factor_of_PIV_time_subsampling_gl = int(5/10 / dt_PIV)

case_choice = 1
#case_choice = "Case_Full"
subsampling_PIV_grid_factor_gl, x0_index_gl, nbPoints_x_gl, \
 y0_index_gl, nbPoints_y_gl, assimilation_period_gl = switch_case(case_choice)


color_mean_EV_withoutNoise = 'b'
color_quantile_EV_withoutNoise = 'steelblue'
color_mean_EV = 'deepskyblue'
color_quantile_EV = 'paleturquoise'
color_mean_LU = 'orangered'
color_quantile_LU = 'sandybrown'

param_file = Path(MORAANE_PATH).joinpath('pyReDA/run_info.txt')
print("     Cf. run_file [", str(param_file)+"]")

#plot_debug = False
plot_debug = main_optionalParam_from_info_txt_file(param_file)

pos_Mes = -7

# #import matplotlib.pyplot as plt
path_functions = Path(__file__).parents[1].joinpath('functions')
sys.path.insert(0, str(path_functions))

#from scipy import sparse as svds

# writting INFO file

file_info = Path(MORAANE_PATH).joinpath('3rdresult').joinpath('test.info')

# print("\n---> Cf. INFO file = ", str(file_info), "------\n" ) 

f_info = open(file_info,'w')

f_info.write(str("\nTEST basis : ") ) 

if code_DATA_from_matlab == True:
    f_info.write("DATA=DATA(matlab)")
    f_info.write(str("\n") )    
else:
    f_info.write("DATA=DATA(C++)")
    f_info.write(str("\n") ) 

f_info.write(str("\nLEARNING basis : ") ) 

if code_ROM_from_matlab == True:
    f_info.write("ROM=ROM(matlab)")
    f_info.write(str("\n") )    
else:
    f_info.write("ROM=ROM(C++)")
    f_info.write(str("\n") )    

f_info.write(str("\n") ) 

if code_change_mode_sign == True:
    f_info.write("     mode"+str(vect_num_mode_to_reverse) +
                 " -> -mode"+str(vect_num_mode_to_reverse))
    f_info.write(str("\n"))
if code_change_mode_sign_ILC == True:
    f_info.write("     mode"+str(vect_num_mode_to_reverse)+" -> -mode" +
                 str(vect_num_mode_to_reverse)+" by modifying I,L,C and pschol_cov_noises")
    f_info.write(str("\n"))
if code_change_mode_sign_HpivK_bt_tot == True:
    f_info.write("     mode"+str(vect_num_mode_to_reverse)+" -> -mode" +
                 str(vect_num_mode_to_reverse)+" by modifying Hpiv,K and bt_tot")
    f_info.write(str("\n"))

f_info.write(str("\n") ) 

f_info.write("\nNOISE control parameter at INIT and during SIMULATION : \n\n" )
f_info.write("  - Noise control parameter at INIT : beta_2=" + str(beta_2) )
if beta_2 == 1:
    f_info.write(" ( -> NOISE is added to INIT condition)\n")
else:
    f_info.write(" ( -> NO noise added to INIT condition)\n")

f_info.write(
    "  - Noise control parameter during SIMULATION : beta_3=" + str(beta_3))
if beta_3 == 1:
    f_info.write(" ( -> NOISE is added during SIMULATION)\n")
else:
    f_info.write(" ( -> NO noise added during SIMULATION)\n")

if init_centred_on_ref:
    f_info.write(
        "\nINIT condition centered on real condition (Cf. [init_centred_on_ref] parameter)\n")
else:
    f_info.write(
        "\nINIT condition NOT centered on real condition (Cf. [init_centred_on_ref] parameter)\n")

f_info.write("\nParticle filter : \n\n")
f_info.write("  - Effective sample size in the particle filter : N_threshold=" +
             str(N_threshold) + "\n")
f_info.write(
    "  - Control constants for the balance in the new brownian and the old brownian in particle filter : \n")
f_info.write("    . pho=" + str(pho) + "\n")
f_info.write("    . linewidth_=" + str(linewidth_) + "\n")

f_info.write("\nAssimilated DATA type : assimilate=" + str(assimilate) + "\n")

f_info.write("\nDATA TYPE used to assimilate :\n")
f_info.write("  - Data Assimilation dim : data_assimilate_dim=" +
             str(data_assimilate_dim) + " ( -> " + str(data_assimilate_dim) + "D)\n")

f_info.write("\n  - PIV characteristics : \n")

f_info.write("\n  - DNS characteristics : \n")

if sub_sampling_PIV_data_temporaly:
    f_info.write(
        "\nSUB SAMPLING PIV data is applied (Cf. [sub_sampling_PIV_data_temporaly] parameter)\n\n")
else:
    f_info.write(
        "\nSUB SAMPLING PIV data is NOT applied (Cf. [sub_sampling_PIV_data_temporaly] parameter)\n\n")

f_info.write("\nPLOTTING parameters :\n" )
f_info.write("\n  - Plotting type and duration :\n\n" )

if plt_real_time:
    f_info.write(
        "    . plotting DURING simulation (Cf. [plt_real_time] parameter)\n")
else:
    f_info.write(
        "    . plotting AT END of simulation (Cf. [plt_real_time] parameter)\n")
f_info.write("    . plotting period : plot_period=" + str(plot_period) + "\n")

f_info.write("\n` - Plotted variables :\n\n" )
if heavy_real_time_plot:
    f_info.write(
        "    . Compute confidence interval for real-time is plotted in ORANGE part (Cf. [heavy_real_time_plot] parameter)\n")
else:
    f_info.write(
        "    . Compute confidence interval for real-time is NOT plotted (Cf. [heavy_real_time_plot] parameter)\n")

if plot_Q_crit:
    f_info.write(
        "    . Q criterion is plotted (Cf. [plot_Q_crit] parameter)\n")
else:
    f_info.write(
        "    . Q criterion is NOT plotted (Cf. [plot_Q_crit] parameter)\n")

if plot_ref_gl:
    f_info.write(
        "    . REFERENCE is plotted in DOTTED BLACK line (Cf. [plot_ref_gl] parameter)\n")
else:
    f_info.write(
        "    . REFERENCE is NOT plotted (Cf. [plot_ref_gl] parameter)\n")

if mask_obs:
    f_info.write(
        "    . Spatial mask is applied on observed data (Cf. [mask_obs] parameter)\n")
else:
    f_info.write(
        "    . Spatial mask is NOT applied on observed data (Cf. [mask_obs] parameter)\n")

if plot_debug:
    f_info.write("    . debug is plotted (Cf. [plot_debug] parameter)\n" )
else:
    f_info.write("    . debug is NOT plotted (Cf. [plot_debug] parameter)\n")

f_info.write("\n  - Other Variables colors :\n\n")
f_info.write("    . EV (Eddy Viscosity) variables :\n")
f_info.write("       Mean EV without noise     : color_mean_EV_withoutNoise=" +
             str(color_mean_EV_withoutNoise) + "\n")
f_info.write("       Quantile EV without noise : color_quantile_EV_withoutNoise=" +
             str(color_quantile_EV_withoutNoise) + "\n")
f_info.write("       Mean EV                   : color_mean_EV=" +
             str(color_mean_EV) + "\n")
f_info.write("       Quantile EV               : color_quantile_EV=" +
             str(color_quantile_EV) + "\n")
f_info.write("    . LU (Local Uncertainty) variables :\n")
f_info.write("       Mean LU                   : color_mean_LU=" +
             str(color_mean_LU) + "\n")
f_info.write("       Quantile LU               : color_quantile_LU=" +
             str(color_quantile_LU) + "\n")
f_info.write("\n  - Figure dimensions :\n\n")
f_info.write("    . Figure WIDTH  : fig_width=" + str(fig_width) + "\n")
f_info.write("    . Figure HEIGHT : fig_height=" + str(fig_height) + "\n")

if not code_Assimilation:
    f_info.write(
        "\n\n!!! WARNING : case without ASSIMILATION !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
    f_info.write(
        "!!!!! Change some of the following parameters to have ASSIMILATION !!!!!!!!!\n")
    f_info.write("    - beta_2 = " + str(beta_2) + " => beta_2 = 0\n")
    f_info.write("    - init_centred_on_ref = " +
                 str(init_centred_on_ref) + " => init_centred_on_ref = True\n")
    f_info.write("    - assimilation_period = " + str(assimilation_period_gl) +
                 " => assimilation_period = inf\n")
    f_info.write(
        "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")

f_info.write("\nASSIMILATION parameters :\n")

f_info.write("\n  - Temporal parameters (Observations time step) :\n\n")
f_info.write("    . Subsampling constant applied in the observed data : subsampling_PIV_grid_factor_gl=" + str(subsampling_PIV_grid_factor_gl) +
             "\n      ( -> 1 point selected every " + str(subsampling_PIV_grid_factor_gl) + " points)\n")
f_info.write("\n  - Spatial parameters (Observations OffSet and Number):\n\n")
f_info.write("    . X grid index OFFSET : x0_index_gl=" +
             str(x0_index_gl) + "\n")
f_info.write("    . Y grid index OFFSET : y0_index_gl=" +
             str(y0_index_gl) + "\n")
f_info.write("    . Number of points taken into account in X observed grid : nbPoints_x_gl=" + str(nbPoints_x_gl) +
             " ( =?= (202-" + str(x0_index_gl) + ")/" + str(subsampling_PIV_grid_factor_gl) + " points)\n")
f_info.write("    . Number of points taken into account in Y observed grid : nbPoints_y_gl=" + str(nbPoints_y_gl) +
             " ( =?= (74-" + str(y0_index_gl) + ")/" + str(subsampling_PIV_grid_factor_gl) + " points)\n")

f_info.write("\n  - assimilation_period = " + str(assimilation_period_gl) + "\n")

f_info.write("\nOTHER parameters :\n" )
f_info.write("\n  - pos_Mes= " + str(pos_Mes) + "\n")

f_info.write("  - path_functions= " + str(path_functions) + "\n")

# END writting INFO file

f_info.close()  


# %%                                          Begin the main_from_existing_ROM that constrols all the simulation

def main_from_existing_ROM(nb_modes, threshold, type_data, nb_period_test,
                           no_subampl_in_forecast, reconstruction,
                           adv_corrected, modal_dt, n_particles, test_fct, svd_pchol,
                           stochastic_integration,
                           estim_rmv_fv, eq_proj_div_free,
                           thrDtCorrect,
                           noBugSubsampl,
                           choice_n_subsample, EV,
                           nb_mutation_steps,
                           SECONDS_OF_SIMU):  # nb_modes,threshold,type_data,nb_period_test,no_subampl_in_forecast,reconstruction,adv_corrected,modal_dt):
    
    # learning basis
    if code_DATA_from_matlab == False:
        no_subampl_in_forecast = True

    # writting INFO file

    print("\n---> Cf. INFO file = ", str(file_info), "------\n")
    f_info = open(file_info, 'a+')

    f_info.write(
        "\n ------ INPUT parameters for [main_from_existing_ROM] function ------ \n\n")

    f_info.write("  - nb_modes               = " + str(nb_modes) + "\n")
    f_info.write("  - threshold              = " + str(threshold) + "\n")
    f_info.write("  - reconstruction         = " + str(reconstruction) + "\n")
    f_info.write("  - adv_corrected          = " + str(adv_corrected) + "\n")
    f_info.write("  - modal_dt               = " + str(modal_dt) + "\n")
    f_info.write("  - eq_proj_div_free       = " +
                 str(eq_proj_div_free) + "\n")
    f_info.write("  - nb_mutation_steps      = " +
                 str(nb_mutation_steps) + "\n")

    f_info.write("  - type_data              = " + str(type_data) + "\n")
    f_info.write("  - nb_period_test         = " + str(nb_period_test) + "\n")
    f_info.write("  - no_subampl_in_forecast = " +
                 str(no_subampl_in_forecast) + "\n")
    f_info.write("  - n_particle             = " + str(n_particles) + "\n")
    f_info.write("  - test_fct               = " + str(test_fct) + "\n")
    f_info.write("  - svd_pchol              = " + str(svd_pchol) + "\n")
    f_info.write("  - stochastic_integration = " +
                 str(stochastic_integration) + "\n")
    f_info.write("  - estim_rmv_fv           = " + str(estim_rmv_fv) + "\n")
    f_info.write("  - thrDtCorrect           = " + str(thrDtCorrect) + "\n")
    f_info.write("  - noBugSubsampl          = " + str(noBugSubsampl) + "\n")
    f_info.write("  - choice_n_subsample     = " +
                 str(choice_n_subsample) + "\n")
    f_info.write("  - EV                     = " + str(EV) + "\n")
    f_info.write("  - SECONDS_OF_SIMU        = " + str(SECONDS_OF_SIMU) + "\n")
    
    if not code_Assimilation:
        f_info.write(
            "\nASSIMILATION parameters modified since there is NO ASSIMILATION :\n")
        assimilation_period = np.inf
        f_info.write("  - assimilation_period    = " +
                     str(assimilation_period) + "\n")
        if beta_2 != 0 or beta_3 != 1 or not init_centred_on_ref or assimilation_period < np.inf:
            f_info.write(
                "\n  !!!!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            f_info.write(
                "  !!!!!!!!!!! Case without Assimilation !!!!!!!!!!!!!!!!!!!\n")
            f_info.write(
                "  !!!!!!!!!!! some parameters have bad values : !!!!!!!!!!!\n")
            f_info.write("    - beta_2 = " + str(beta_2) + " =?= 0\n")
            f_info.write("    - beta_3 = " + str(beta_3) + " =?= 1\n")
            f_info.write("    - init_centred_on_ref = " +
                         str(init_centred_on_ref) + " =?= True\n")
            f_info.write("    - assimilation_period = " + str(assimilation_period) +
                         " ?>= inf\n")
            f_info.write(
                "  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
    else:
        assimilation_period = assimilation_period_gl

    f_info.write(str("\n"))

    f_info.write(
        "\n ------ EXECUTING [main_from_existing_ROM] function ------ \n\n")

    if (EV == 2):
        LeastSquare = False
        EV_withoutNoise = True
        EV = True
    elif (EV == 1):
        LeastSquare = False
        EV_withoutNoise = True
        EV = True
    elif (EV == 3):
        LeastSquare = True
        EV_withoutNoise = False
        EV = True
    elif (EV == 0):
        LeastSquare = False
        EV_withoutNoise = False
        EV = False
    else:
        print('ERROR: unknow case for EV')
        return 0
    
    f_info.write("\nEddy Viscosity conditions :\n")   
    f_info.write("  - LeastSquare            = " + str(LeastSquare) + "\n")
    f_info.write("  - EV_withoutNoise        = " + str(EV_withoutNoise) + "\n")
    f_info.write("  - EV                     = " + str(EV) + "\n")
    f_info.write(str("\n"))   

    param_ref['N_particules'] = n_particles # Number of particles to select  
        
    if not mask_obs:   # If we must select a smaller grid inside the observed grid. 
        x0_index = 1.
        y0_index = 1.
        nbPoints_x = float('nan')
        nbPoints_y = float('nan')
        subsampling_PIV_grid_factor = 1
    else:
        x0_index = x0_index_gl
        y0_index = y0_index_gl
        nbPoints_x = nbPoints_x_gl
        nbPoints_y = nbPoints_y_gl
        subsampling_PIV_grid_factor = subsampling_PIV_grid_factor_gl
      
    f_info.write("\nSub sampling conditions :\n")   
    f_info.write("  - x0_index                    = " + str(x0_index) + "\n")
    f_info.write("  - y0_index                    = " + str(y0_index) + "\n")
    f_info.write("  - nbPoints_x                  = " + str(nbPoints_x) + "\n")
    f_info.write("  - nbPoints_y                  = " + str(nbPoints_y) + "\n")
    f_info.write("  - subsampling_PIV_grid_factor = " +
                 str(subsampling_PIV_grid_factor) + "\n")
    f_info.write(str("\n"))
    
    ###### default values ####################
    n_simu = 100 # Time step decreasing factor for ROM time integration
    # update param_ref
    param_ref['n_simu'] = n_simu
    ########################################

    switcher = {
        'DNS300_inc3d_3D_2017_04_02_NOT_BLURRED_blocks_truncated': 300,
        'DNS100_inc3d_2D_2018_11_16_blocks_truncated': 100
    }
    Re = switcher.get(type_data, [float('Nan')])

    f_info.write("\nReynolds Number :\n")   
    f_info.write("  - Re                          = " + str(Re) + "\n")
    f_info.write(str("\n"))   

    PATH_output = Path(MORAANE_PATH).joinpath('3rdresult')

    if assimilate == 'real_data':
        switcher = {
            'DNS300_inc3d_3D_2017_04_02_NOT_BLURRED_blocks_truncated': float(0.080833),
            'DNS100_inc3d_2D_2018_11_16_blocks_truncated': float(0.05625)
        }
        dt_PIV = switcher.get(type_data, [float('Nan')])
        if not sub_sampling_PIV_data_temporaly:
            factor_of_PIV_time_subsampling = 1
        else:
            factor_of_PIV_time_subsampling = int(assimilation_period/dt_PIV)
        plot_ref = plot_ref_gl
        # Number of PIV files to load
        number_of_PIV_files = int(SECONDS_OF_SIMU/dt_PIV) + 1
        # Construct the moments that can be assimilated.
        if code_Assimilation:
            vector_of_assimilation_time = np.arange(
                start=0, stop=number_of_PIV_files*dt_PIV, step=dt_PIV)
            # Using the factor to select the moments that we will take to assimilate
            vector_of_assimilation_time = vector_of_assimilation_time[::factor_of_PIV_time_subsampling]
        else:
            vector_of_assimilation_time = []
    elif assimilate == 'fake_real_data':
        plot_ref = plot_ref_gl                     # Plot bt_tot
               
        # input PATH = directory containing subdirectories [ITHACAoutput], [ROM_PIV], [util] and [FakePIV_noise2]
        PATH_input = PATH_openfoam_data.joinpath(type_data_C)
        
        if not PATH_input.exists():
            print('\n!!! ERROR: input directory ['+str(PATH_input)+'] not found !!!')
            sys.exit()        
        
        PATH_ROM = Path(PATH_input).joinpath(str(redlumcpp_code_version) + '/ITHACAoutput')
        PATH_util = Path(PATH_input).joinpath('util')
        PATH_ROM_PIV = Path(PATH_input).joinpath(str(redlumcpp_code_version) + '/ROM_PIV')
        PATH_DATA = Path(PATH_input).joinpath(Path('FakePIV_noise2'))
        
        param_file = Path(MORAANE_PATH).joinpath('pyReDA/run_info.txt')
        if not PATH_ROM.exists():
            print('\n!!! ERROR: directory ['+str(PATH_ROM)+'] not found !!!\n  => change values in ['+str(param_file)+'] file')
            sys.exit()
        if not PATH_util.exists():
            print('\n!!! ERROR: directory ['+str(PATH_util)+'] not found !!!\n  => change values in ['+str(param_file)+'] file')
            sys.exit()
        if code_Assimilation :
            if not PATH_ROM_PIV.exists():
                print('\n!!! ERROR: directory ['+str(PATH_ROM_PIV)+'] not found !!!\n  => change values in ['+str(param_file)+'] file')
                sys.exit()
            if not PATH_DATA.exists():
                print('\n!!! ERROR: directory ['+str(PATH_DATA)+'] not found !!!\n  => change values in ['+str(param_file)+'] file')
                sys.exit()
        
        if not code_DATA_from_matlab or not code_ROM_from_matlab:
       
            Cparam = namedtuple('Cparam', ['Re', 'nb_modes','SECONDS_OF_SIMU',
                                          'x1_PIV', 'x2_PIV',  'x0_cyl', 
                                          'y1_PIV', 'y2_PIV',  'y0_cyl',
                                          'diam_cyl', 'PIV_velocity', 'dt_PIV', 
                                          'dt_DNS', 't0_DNS', 't1_DNS',
                                          't0_learningBase', 't1_learningBase', 
                                          't0_testBase', 't1_testBase', 
                                          'PATH_input', 'PATH_DATA', 'PATH_ROM', 'PATH_ROM_PIV']) 
            
            print("\n\nDATA or ROM =f(C++) => param")
            
            if code_Assimilation :
                # parameters from info txt file
                param_file = PATH_util.joinpath(Path('PIV_info.txt'))
                print("param_PIV_file=", str(param_file)+"\n")
                PIV_velocity, x0_cyl, y0_cyl, diam_cyl, dt_PIV = param_from_PIV_info_txt_file ( param_file )

                param_file = PATH_util.joinpath(Path('DNS_to_FakePIV_info.txt'))
                print("param_DNS_to_FakePIV_file=", str(param_file)+"\n")
                x1_PIV, y1_PIV, x2_PIV, y2_PIV = param_from_DNS_to_FakePIV_info_txt_file ( param_file )
            else:
                PIV_velocity, x0_cyl, y0_cyl, diam_cyl, dt_PIV = param_nan_PIV_info ()
                x1_PIV, y1_PIV, x2_PIV, y2_PIV = param_nan_DNS_to_FakePIV ()

            # other parameters from openfoam Dict files 
            # in lines out of "{...}" sections
            param_file = PATH_ROM.joinpath(Path('../system/controlDict'))
            print("controlDict=", str(param_file)+"\n")
            dt_DNS, t0_DNS, t1_DNS = param_from_controlDict_file ( param_file )
            
            param_file = PATH_ROM.joinpath(Path('../system/ITHACAdict'))
            print("ITHACADict=", str(param_file)+"\n")
            t0_learningBase, t1_learningBase, t0_testBase, t1_testBase, n_simu = param_from_ITHACADict_file ( param_file )
            
            # update param_ref
            param_ref['n_simu'] = n_simu
            
            # other parameters
            nb_file_learning_basis = int((t1_learningBase-t0_learningBase)/dt_DNS)+1
            nb_snapshots_each_file = 1

            if (Re == 100):
                print("data=fake_real_data=f(C++) => nb_file_learning_basis unknown")
                print("data=fake_real_data=f(C++) => dt_PIV unknown")
                sys.exit()
      
            PARAM=Cparam(Re, nb_modes, SECONDS_OF_SIMU,
                         x1_PIV, x2_PIV, x0_cyl,
                         y1_PIV, y2_PIV, y0_cyl,
                         diam_cyl, PIV_velocity, dt_PIV,
                         dt_DNS, t0_DNS, t1_DNS,
                         t0_learningBase, t1_learningBase,
                         t0_testBase, t1_testBase,
                         PATH_input, PATH_DATA, PATH_ROM, PATH_ROM_PIV)
               
        if code_load_run:
            SECONDS_OF_SIMU = t1_testBase - t0_testBase
            
        if code_DATA_from_matlab:
            switcher = {
                'DNS300_inc3d_3D_2017_04_02_NOT_BLURRED_blocks_truncated': 80,
                'DNS100_inc3d_2D_2018_11_16_blocks_truncated': 14
            }
            nb_file_learning_basis = switcher.get(type_data, [float('Nan')])
            switcher = {
                'DNS300_inc3d_3D_2017_04_02_NOT_BLURRED_blocks_truncated': 0.25,
                'DNS100_inc3d_2D_2018_11_16_blocks_truncated': 0.05
            }
            dt_PIV = switcher.get(type_data, [float('Nan')])
        
        # defining first crop on PIV
        #    MX_PIV_all : all values found in file
        #    index_XY_PIV : index_X_1, index_X_2, index_Y_1, index_Y_2 for crop
        #    coordinates_x_PIV, coordinates_y_PIV : X,Y corrdinates corresponding to this crop
        
        MX_PIV_all=(1,1)
        MX_PIV=(1,1)
        index_XY_PIV = (0,1,0,1)
        coordinates_x_PIV = (0.,1.)
        coordinates_y_PIV = (0.,1.)
        
        if code_Assimilation and not code_DATA_from_matlab:
          MX_PIV_all, MX_PIV, index_XY_PIV, coordinates_x_PIV, coordinates_y_PIV = convert_Cmat_to_python_cropZone(PARAM)

        if not sub_sampling_PIV_data_temporaly:
            factor_of_PIV_time_subsampling = 1
        else:
            factor_of_PIV_time_subsampling = int(assimilation_period/dt_PIV)
    
    #%%  Initialize randm generator
    np.random.seed(0)      
    
    #%%  Parameters already chosen 
    
    f_info.write("\nFolders and Files (Re=" + str(Re) + ") : \n\n") 
    
# code_ROM_from_matlab = learning basis parameter : if True, MatLab result for ROM is used, else openfoam/C++ result is used
# code_DATA_from_matlab = test basis parameter : if True, MatLab data is used, else openfoam/C++ data is used

    folder_current_results = Path(MORAANE_PATH).joinpath('podfs2').joinpath('resultats').joinpath('current_results')   
    folder_current_results = str(folder_current_results)
    if code_ROM_from_matlab:
        folder_results = folder_current_results
    else:
        folder_results = PATH_ROM

    print('############ Folder Result (Re=' + str(Re) +
          ') : [' + str(folder_results) + "]\n")

    f_info.write("  - Result Folder (Re=" + str(Re)+") : \n    " +
                 str(folder_results) + str("\n\n"))

    if code_DATA_from_matlab:
        folder_nrj = folder_current_results
        folder_data = Path(MORAANE_PATH).joinpath('data')
    else:
        folder_nrj = 'Nan'
        #print("data=f(C++) => folder_data unknown")
        folder_data = PATH_DATA
        
    print('############ Folder Nrj   (Re=' +
          str(Re)+') : [' + str(folder_nrj) + "]\n")
    print('############ Folder Data   (Re=' +
          str(Re)+') : [' + str(folder_data) + "]\n")

    f_info.write("  - Data Folder (Re=" + str(Re)+") : \n    " +
                 str(folder_data) + str("\n\n"))

    param_ref['folder_results'] = str(
        folder_results)  # Stock folder results path
    param_ref['folder_data'] = str(folder_data)       # Stock folder data path
    if code_DATA_from_matlab:
        param_ref['folder_nrj'] = str(folder_nrj)       # Stock folder data path
    else:
        # sert à normaliser : inutilisé pour l'instant
        print("data=f(C++) => folder_nrj unknown\n")
       
    modal_dt_ref = modal_dt  # Define modal_dt_ref

    # %% Get data

    # Construct the path to select the model constants I,L,C,pchol and etc.

    # code_DATA_from_matlab = test basis parameter : if True, MatLab data is used, else openfoam/C++ data is used
    
    # parameters : case openfoam C++ -> matlab values copy
    param = default_param( 0 )
  
    print('############ Default Param (Re='+str(Re) +")\n")
    print("Cf. podfs2/python_scripts/mains/switch_case_param.py" + "\n")

    f_info.write("  - Param File (Re=" + str(Re)+") : any \n    parameters are defined by [switch_case_param.py]\n\n")
    
    # parameters : case matlab
    if code_DATA_from_matlab or code_ROM_from_matlab :
      
      file = '1stresult_' + type_data + '_' + str(nb_modes) + '_modes_'  \
          + choice_n_subsample
      if choice_n_subsample == 'auto_shanon':
          file = file + '_threshold_' + str(threshold)
      file = file + test_fct
      file = file + '_fullsto'  # File where the ROM coefficients are save
      file = file + '/'
      if not adv_corrected:
          file = file + '_no_correct_drift'
      if thrDtCorrect:
          file = file + '_thrDtCorrect'
      file = file + '_integ_' + stochastic_integration
      if estim_rmv_fv:
          file = file + '_estim_rmv_fv'
      if noBugSubsampl:
          file = file + '_noBugSubsampl'
      if eq_proj_div_free == 2:
          file = file + '_DFSPN'
      file = file + '.mat'
      
      folder_param = Path(MORAANE_PATH).joinpath('podfs2').joinpath('resultats').joinpath('current_results')

      file_param = folder_param / Path(file)

      param = convert_mat_to_python_param(str(file_param))
      print('############ File Param (Re='+str(Re) +
            ') : [' + str(file_param) + "]\n")
      print("Cf. podfs2/python_scripts/mains/convert_mat_to_python_param.py" + "\n")
  
      f_info.write("  - Param File (Re=" + str(Re)+") : \n    " +
                   str(file_param) + "\n\n")


    plot_bts = False
    # code_ROM_from_matlab = learning basis parameter : if True, MatLab result for ROM is used, else openfoam/C++ result is used
    if code_ROM_from_matlab:
        file_res = folder_results / Path(file)

        # The function creates a dictionary with the same structure as the Matlab Struct in the path file_res
        # Call the function and load the matlab data calculated before in matlab scripts.
        I_sto, L_sto, C_sto, I_deter, L_deter, C_deter, pchol_cov_noises = convert_mat_to_python_ILCpchol(
            str(file_res))

        print('############ File Result (Re='+str(Re)+') : [' + str(file_res))
        print("Cf. podfs2/python_scripts/mains/convert_mat_to_python_ILCpchol.py]\n\n")

        f_info.write("  - Result File (Re=" + str(Re) +
                     ") : \n    " + str(file_res) + "\n\n")
        f_info.write(
            "    (function used : podfs2/python_scripts/mains/convert_mat_to_python_ILCpchol.py)" + "]\n\n")

    if not code_ROM_from_matlab:
        svd_pchol = False
        I_sto, L_sto, C_sto, I_deter, L_deter, C_deter, pchol_cov_noises = convert_Cmat_to_python_ILCpchol(
            os.path.join(folder_results, 'Matrices'), str(Re), str(nb_modes), bool_PFD)

        # changing sign values for certain modes : value -> -values
        if code_change_mode_sign_ILC:
            for num_mode_to_reverse in vect_num_mode_to_reverse:
                change_mode_sign_ILCpchol(str(nb_modes), str(
                    num_mode_to_reverse), I_sto, L_sto, C_sto, I_deter, L_deter, C_deter, pchol_cov_noises)

        print('############ Files Result (Re='+str(Re) +
              ') : [' + os.path.join(folder_results, 'Matrices') + "/*_mat.txt]\n\n")
        print("Cf. podfs2/python_scripts/mains/convert_Cmat_to_python_ILCpchol.py]\n\n")

        f_info.write("  - Result Files (Re=" + str(Re)+") : \n    " +
                     os.path.join(folder_results, 'Matrices') + "/*_mat.txt\n\n")
        f_info.write(
            "    (function used : podfs2/python_scripts/mains/convert_Cmat_to_python_ILCpchol.py)" + "\n\n")

    if not code_DATA_from_matlab :
        param['dt'] = dt_DNS
        param['N_tot'] = int((t1_testBase-t0_testBase)/dt_DNS)+1
    else:
        #if code_DATA_from_matlab: Cf. podfs2/python_scripts/mains/convert_mat_to_python_param.py
        # Define the constant
        param['dt'] = float(param['dt'])
        param['decor_by_subsampl']['no_subampl_in_forecast'] = no_subampl_in_forecast
        
        # Remove subsampling effect
        param['dt'] = param['dt'] / param['decor_by_subsampl']['n_subsampl_decor']
        param['N_test'] = param['N_test'] * \
            param['decor_by_subsampl']['n_subsampl_decor']
        param['N_tot'] = param['N_test'] + 1
    param['decor_by_subsampl']['n_subsampl_decor'] = 1


    # code_ROM_from_matlab = learning basis parameter : if True, MatLab result for ROM is used, else openfoam/C++ result is used
    if code_ROM_from_matlab:
        if EV:
            file_EV = 'EV_result_' + type_data + '_' + str(nb_modes) + '_modes'
            file_EV = file_EV + '_noise.mat'
            file_EV_res = folder_results / Path(file_EV)
            # Call the function and load the matlab data calculated before in matlab scripts.
            ILC_EV = convert_mat_to_python_EV(str(file_EV_res))
        print("Cf. podfs2/python_scripts/mains/convert_mat_to_python_EV.py")

    else:
        print('############ [EV] UNDEFINED ################')

    # %% Redefined path to get acces to data
    folder_data = param_ref['folder_data']
    folder_results = param_ref['folder_results']
    big_data = False
    
    param['folder_data'] = str(folder_data)
    param['folder_results'] = str(folder_results)
    param['folder_nrj'] = folder_nrj
    param['big_data'] = big_data
    param['plots_bts'] = plot_bts

    param['folder_results'] = param_ref['folder_results']
    param['N_particules'] = param_ref['N_particules']
    n_simu = param_ref['n_simu']

    print("\nOther default parameters :")
    print("nb_period_test="+str(nb_period_test))
    print("plot_bts="+str(plot_bts))
    print("n_simu="+str(n_simu))
    

    if code_ROM_from_matlab:
        # Define the constant lambda (The integral in one period of the square temporal modes )
        lambda_values = param['lambda']
        print("\nDefault lambda_values="+str(lambda_values)+"\n")

    # Cf. data_red_lum_cpp/StationnaryRegime_TestSeparated_Re300/system/ITHACAdict
    # Cf. /media/laurence.wallian/WD_Ressegui/Boulot/RedLUM/RedLum_from_OpenFoam/RedLum_D1_Lz1pi_Re300/ROMDNS/system/ITHACAdict
    # if not code_DATA_from_matlab:
    if not code_ROM_from_matlab:
        lambda_values = convert_Cmat_to_python_lambda(PARAM)
        print("\nCf. podfs2/python_scripts/mains/convert_Cmat_to_python_lambda.py]\n\n")
        f_info.write("  - Lambda values (Re=" + str(Re)+") : \n    " +
                     os.path.join(folder_results, 'temporalModes_'+str(nb_modes)+'modes') + "/U_mat.txt\n\n")
        f_info.write(
            "    (function used : Cf. podfs2/python_scripts/mains/convert_Cmat_to_python_Topos_FakePIV.py)" + "\n\n")
    
    print("\nNew     lambda_values="+str(lambda_values)+"\n")
    
    print("svd_pchol="+str(svd_pchol))
    # %% Reduction of the noise matrix
    sq_lambda = np.sqrt(lambda_values)
    
    # figure limits
    lim_fig = [0] * len(sq_lambda)
    for i in range (len(sq_lambda)):
        lim_fig[i] = 4.*sq_lambda[i]
        
    if svd_pchol > 0:

        pchol_cov_noises_add = pchol_cov_noises[range(nb_modes), :]
        pchol_cov_noises = pchol_cov_noises[nb_modes:, :]
        pchol_cov_noises = np.reshape(pchol_cov_noises,
                                      (nb_modes, nb_modes, (nb_modes+1)*nb_modes), order='F')

        if svd_pchol == 1:
            for j in range(nb_modes):
                pchol_cov_noises_add[j, :] = (1/sq_lambda[j]) * \
                    pchol_cov_noises_add[j, :]
            for i in range(nb_modes):
                for j in range(nb_modes):
                    pchol_cov_noises[i, j, :] = (sq_lambda[i]/sq_lambda[j]) \
                        * pchol_cov_noises[i, j, :]
        elif svd_pchol == 2:
            for i in range(nb_modes):
                for j in range(nb_modes):
                    pchol_cov_noises[i, j, :] = (sq_lambda[i]) \
                        * pchol_cov_noises[i, j, :]

        pchol_cov_noises = np.reshape(pchol_cov_noises,
                                      (nb_modes*nb_modes, (nb_modes+1)*nb_modes), order='F')
        pchol_cov_noises = np.concatenate(
            (pchol_cov_noises_add, pchol_cov_noises), axis=0)

        U_cov_noises, S_cov_noises, _ = sps.linalg.svds(
            pchol_cov_noises, k=nb_modes)
        pchol_cov_noises = U_cov_noises @ np.diag(S_cov_noises)

        pchol_cov_noises_add = pchol_cov_noises[range(nb_modes), :]
        pchol_cov_noises = pchol_cov_noises[nb_modes:, :]
        pchol_cov_noises = np.reshape(pchol_cov_noises,
                                      (nb_modes, nb_modes, nb_modes), order='F')

        if svd_pchol == 1:
            for i in range(nb_modes):
                for j in range(nb_modes):
                    pchol_cov_noises[i, j, :] = (1/(sq_lambda[i]/sq_lambda[j])) \
                        * pchol_cov_noises[i, j, :]
            for j in range(nb_modes):
                pchol_cov_noises_add[j, :] = (1/(1/sq_lambda[j])) * \
                    pchol_cov_noises_add[j, :]
        elif svd_pchol == 2:
            for i in range(nb_modes):
                for j in range(nb_modes):
                    pchol_cov_noises[i, j, :] = (1/(sq_lambda[i])) \
                        * pchol_cov_noises[i, j, :]
        pchol_cov_noises = np.reshape(pchol_cov_noises,
                                      (nb_modes*nb_modes, nb_modes), order='F')
        pchol_cov_noises = np.concatenate(
            (pchol_cov_noises_add, pchol_cov_noises), axis=0)

#        if EV:
#            U_cov_noises_EV, S_cov_noises_EV, _ = \
#            sps.linalg.svds(ILC_EV['pchol_cov_noises'], k=nb_modes)
#            ILC_EV['pchol_cov_noises'] = U_cov_noises_EV @ np.diag(S_cov_noises_EV)

    #%% Folder to save data assimilation plot results
    plt.close('all')
    file_plots = '3rdresult/'
    if code_ROM_from_matlab and code_DATA_from_matlab:
        file_plots = file_plots + type_data
    else:
        file_plots = file_plots + type_data_C
    file_plots = file_plots + '_' + str(nb_modes) + '_modes'
    if not code_load_run :
        file_plots = file_plots + '_loaded'
    if not code_Assimilation :
        file_plots = file_plots + '_noDA'
    if not code_ROM_from_matlab :
        file_plots = file_plots + '_CppROM'
    if not code_DATA_from_matlab :
        file_plots = file_plots + '_Cpptestbasis'
    if not code_ROM_from_matlab or not code_DATA_from_matlab:
        file_plots = file_plots + '/' + type_data_C \
                     + '/' + redlumcpp_code_version + '/'
    else:
        file_plots = file_plots + '_' + choice_n_subsample 
        if choice_n_subsample == 'auto_shanon':
            file_plots = file_plots + '_threshold_' + str(threshold)
        file_plots = file_plots + test_fct + '/'
        if modal_dt:
            file_plots = file_plots + '_modal_dt'
        if not adv_corrected:
            file_plots = file_plots + '_no_correct_drift'
        if thrDtCorrect:
            file_plots = file_plots + '_thrDtCorrect'
        file_plots = file_plots + '_integ_' + stochastic_integration
        if estim_rmv_fv:
            file_plots = file_plots + '_estim_rmv_fv'
        if svd_pchol == 1:
            file_plots = file_plots + '_svd_pchol'
        elif svd_pchol == 2:
            file_plots = file_plots + '_svd_pchol2'
        if noBugSubsampl:
            file_plots = file_plots + '_noBugSubsampl'
        if eq_proj_div_free == 2:
            file_plots = file_plots + '_DFSPN'       
    file_plots = file_plots + '/' + assimilate + \
                              '/_DADuration_' + str(int(SECONDS_OF_SIMU)) + '_'
    if sub_sampling_PIV_data_temporaly:
        file_plots = file_plots + 'ObsSubt_' + \
            str(int(factor_of_PIV_time_subsampling)) + '_'
    if mask_obs:
        file_plots = file_plots + 'ObsMaskyy_sub_' + str(int(subsampling_PIV_grid_factor)) \
            + '_from_' + str(int(x0_index)) + '_to_' \
            + str(int(x0_index + nbPoints_x*subsampling_PIV_grid_factor)) \
            + '_from_' + str(int(y0_index)) + '_to_' \
            + str(int(y0_index+nbPoints_y*subsampling_PIV_grid_factor)) + '_'
    else:
        file_plots = file_plots + 'no_mask_'
    if init_centred_on_ref:
        file_plots = file_plots + 'initOnRef_'
    file_plots = file_plots + 'beta_2_' + str(int(beta_2))
    file_plots = file_plots + '_nSimu_' + str(int(n_simu))
    file_plots = file_plots + '_nMut_' + str(int(nb_mutation_steps))
    file_plots = file_plots + '_nPcl_' + str(int(n_particles))
    if EV_withoutNoise:
        file_plots = file_plots + '_EVnoNoise'
    if LeastSquare:
        file_plots = file_plots + '_LS'
    
    file_plots_res = os.path.join(MORAANE_PATH, file_plots)
    
    if not os.path.exists(file_plots_res):
        os.makedirs(file_plots_res)

    f_info.write("  - Plot Folder (Re=" + str(Re)+") : \n    " +
                 str(file_plots_res) + str("\n\n"))

    if plot_Q_crit:
        # File to save Q cirterion for real time 3D plots
        path_Q_crit = Path(MORAANE_PATH).joinpath('data_after_filtering').joinpath('Q_RedLUM')
        if os.path.exists(path_Q_crit):
            shutil.rmtree(path_Q_crit)
            plt.pause(1)
        os.makedirs(path_Q_crit)
        if EV:
            # File to save Q cirterion for real time 3D plots
            path_Q_crit_EV = Path(MORAANE_PATH).joinpath('data_after_filtering').joinpath('Q_EV')
            if not os.path.exists(path_Q_crit_EV):
                os.makedirs(path_Q_crit_EV)
        if plot_ref:
            # File to save Q cirterion for real time 3D plots
            path_Q_crit_ref = Path(MORAANE_PATH).joinpath('data_after_filtering').joinpath('Q_ref')
            if not os.path.exists(path_Q_crit_ref):
                os.makedirs(path_Q_crit_ref)

    # %% Parameters of the ODE of the b(t)

    modal_dt = modal_dt_ref

    tot = {'I': I_sto, 'L': L_sto, 'C': C_sto}

    I_sto = I_sto - I_deter
    L_sto = L_sto - L_deter
    C_sto = C_sto - C_deter

    deter = {'I': I_deter, 'L': L_deter, 'C': C_deter}

    sto = {'I': I_sto, 'L': L_sto, 'C': C_sto}

    ILC = {'deter': deter, 'sto': sto, 'tot': tot}

    ILC_a_cst = ILC.copy()   
    ILC_a_cst = ILC_a_cst['tot']
    
    #%% Do not temporally subsample, in order to prevent aliasing in the results
    N_tot_max = int(SECONDS_OF_SIMU/param['dt'])+1
    N_tot = param['N_tot']
    param['N_tot'] = N_tot
    param['N_test'] = param['N_tot'] - 1
    if N_tot > N_tot_max:
        N_tot = N_tot_max
    if not reconstruction:
        if assimilate == 'fake_real_data':
            # code_DATA_from_matlab = test basis parameter : if True, MatLab data is used, else openfoam/C++ data is used
            # code_ROM_from_matlab = learning basis parameter : if True, MatLab result for ROM is used, else openfoam/C++ result is used
            if code_DATA_from_matlab:
               name_file_data = Path(MORAANE_PATH).joinpath('data').\
                   joinpath(type_data + '_' + str(nb_modes) + '_modes' +
                            '_subsample_1_nb_period_test_NaN_Chronos_test_basis.mat')
               
               if name_file_data.exists():
                   mat = hdf5storage.loadmat(str(name_file_data))
                   bt_tot = mat['bt']
                   truncated_error2 = mat['truncated_error2']
               else:
                   print('ERROR: File does not exist ', str(name_file_data))
                   return 0

            if not code_DATA_from_matlab:
               # bt_tot = ITHACAoutput/temporalModesSimulation_*modes
               # truncated_error=0
               truncated_error2, bt_tot = convert_Cmat_to_python_bt_tot(PARAM)
               
               f_info.write("  - bt_tot (Re=" + str(Re)+") : \n    " +
                            os.path.join(folder_results, 'temporalModesSimulation_'+str(nb_modes)+'modes') + "/U_mat.txt\n\n")
               f_info.write(
                   "    (function used : Cf. podfs2/python_scripts/mains/convert_Cmat_to_python_Topos_FakePIV.py)" + "\n\n")
               if code_load_run:
                   bt_MCMC = convert_Cmat_to_python_bt_MCMC( \
                             PARAM, n_simu, n_particles, bool_PFD)
                
            param['truncated_error2'] = truncated_error2
            dt_bt_tot = param['dt'] / \
            param['decor_by_subsampl']['n_subsampl_decor']
            print("#### truncated_error2"+str(truncated_error2.shape))
            print("#### bt_tot"+str(bt_tot.shape))

            #    Change the sign of spatial mode for mode=num_mode_to_reverse
            # mode1 -> -mode1
            # num_mode = 1
            if code_change_mode_sign_HpivK_bt_tot == True:
                for num_mode_to_reverse in vect_num_mode_to_reverse:
                    change_mode_sign_bt_tot(
                        str(nb_modes), str(num_mode_to_reverse), bt_tot)

            if param['big_data'] == True:
                print('Test basis creation done')
            
            #Test basis creation
            
            param['N_tot'] = N_tot
            param['N_test'] = param['N_tot'] - 1
            bt_tot = bt_tot[:int(param['N_test']
                                 * param['decor_by_subsampl']['n_subsampl_decor'] + 1), :]                # Ref. Chronos in the DNS cas
            time_bt_tot = np.arange(0, bt_tot.shape[0], 1)*dt_bt_tot
            if len(time_bt_tot.shape) > 1:
                time_bt_tot = time_bt_tot[0, :]
            quantiles_PIV = np.zeros((2, bt_tot.shape[0], bt_tot.shape[1]))
        else:
            file = Path(MORAANE_PATH).joinpath('data_PIV').\
                joinpath('bt_tot_PIV_Re'+str(int(Re)) +
                         '_n'+str(nb_modes)+'.mat')
            print(file)
            dict_python = hdf5storage.loadmat(str(file))
            bt_tot = dict_python['bt_tot_PIV']
            quantiles_PIV = dict_python['quantiles_PIV']
            dt_PIV = dict_python['dt_PIV']
            N_tot_PIV_max = int(SECONDS_OF_SIMU/dt_PIV)+1
            if bt_tot.shape[0] > N_tot_PIV_max-1:
                bt_tot = bt_tot[:N_tot_PIV_max, :]
                quantiles_PIV = quantiles_PIV[:, :N_tot_PIV_max, :]
            time_bt_tot = np.arange(0, bt_tot.shape[0], 1)*dt_PIV
            time_bt_tot = time_bt_tot[0, :]
            truncated_error2 = np.zeros((bt_tot.shape[0], bt_tot.shape[1]))
            param['truncated_error2'] = truncated_error2
    
    #%% Time integration of the reconstructed Chronos b(t)
    
    # Define the initial condition as the reference
    bt_tronc = bt_tot[0, :][np.newaxis]

    # The simulation time step is dependent of the number of time evolution steps between the param['dt'],therefore the new param['dt'] is divided by the number of evolution steps
    param['dt'] = param['dt']/n_simu
    # Number of model integration steps is now the number of steps before times the number of integration steps between two old steps
    param['N_test'] = param['N_test'] * n_simu


#    Reconstruction in the stochastic case
    if not code_load_run:
        if init_centred_on_ref:
            # initializes the chronos of all particules equally
            bt_MCMC = np.tile(bt_tronc.T, (1, 1, param['N_particules']))
        else:
            bt_MCMC = np.zeros((1, nb_modes, param['N_particules']))
    
        bt_MCMC[:, :, :] = bt_MCMC + \
            beta_2*np.tile(np.sqrt(lambda_values)[..., np.newaxis], (1, 1, param['N_particules']))\
            * np.random.normal(0, 1, size=(1, nb_modes, param['N_particules']))  
    # Initialise the chronos particles randomly and dependent of the lambda values 

    # Define iii_realization that is necessary if any explosion in the simulation
    iii_realization = np.zeros((param['N_particules'], 1))
    if EV:
        bt_forecast_EV = bt_MCMC.copy()
        iii_realization_EV = iii_realization.copy()
    
        
   #%%  Loading matrices H_PivTopos calculated before, select the data in the new PIV grid and load sigma_inverse in the PIV space
    if code_Assimilation:
       
        # LOAD TOPOS
        print('\nLoading H_PIV @ Topos...')
    
        if code_DATA_from_matlab:
            path_topos = Path(folder_data).parents[0].joinpath('data_PIV').\
                joinpath('mode_'+type_data+'_'+str(nb_modes) +
                         '_modes_PIV')  # Topos path
            # Load topos
            topos_data = hdf5storage.loadmat(str(path_topos))
            topos = topos_data['phi_m_U']
            MX_PIV = topos_data['MX_PIV'].astype(int)
            MX_PIV = tuple(map(tuple, MX_PIV))[0]
            coordinates_x_PIV = topos_data['x_PIV_after_crop']
            coordinates_y_PIV = topos_data['y_PIV_after_crop']
            coordinates_x_PIV = np.reshape(coordinates_x_PIV, MX_PIV, order='F')
            coordinates_y_PIV = np.reshape(coordinates_y_PIV, MX_PIV, order='F')
            coordinates_x_PIV = np.transpose(coordinates_x_PIV[:, 0])
            # Select Topos
            coordinates_y_PIV = coordinates_y_PIV[0, :]
    
        if not code_DATA_from_matlab:
            # mode 0 = ITHACAoutput/mean
            # other modes = ITHACAoutput/spatialModes_*modes
            topos, Sigma_inverse = convert_Cmat_to_python_Topos(
                MX_PIV_all, index_XY_PIV, str(data_assimilate_dim), PARAM)
                    
            f_info.write("  - topos (Re=" + str(Re)+") : \n    " +
                         os.path.join(folder_results, 'spatialModes_'+str(nb_modes)+'modes') + "/*/B0001_new.dat\n\n")
            f_info.write("  - Sigma_inverse (Re=" + str(Re)+") : \n    " +
                         os.path.join(folder_results, 'residualSpeed_'+str(nb_modes)) + "/Inv_COVxy.dat\n\n")
            f_info.write(
                "    (function used : Cf. podfs2/python_scripts/mains/convert_Cmat_to_python_Topos_FakePIV.py)" + "\n\n")
    
        # Define the vectorial field dimension
        dim = topos.shape[-1]
        # Rearrange dimensions
        topos = np.transpose(topos, (0, 2, 1))
    
        # Define the DNS grid
        #grid = param['MX']
        # Define the spatial space between 2 samples in DNS grid
        #distance = param['dX']
        
        
        # LOAD Sigma_inverse
        '''
        The Sigma_inverse matrix was calculated before in the space H_piv, so we need just to load it.
        
            - The folder ''data_PIV'' contains all files related to measured data 
            - Therefore we need to search HSigSigH_PIV..... and load it here. It was calculated before in matlab.
            
                                             ---------------------------VERY IMPORTANT--------------------------------
                                             
                - THIS MATRIX IS DEPENDENT OF THE PIV MEASURED NOISE. THEREFORE THE MATRIX L. BEING SIGMA = [HSigSigH + LL]; 
                - THE VALUE USED HERE WAS ESTIMATED IN THE IRSTEA DATA AND REPRESENTS 6% OF THE AMPLITUDE.
                - THE NOISE IS UNCORRELATED IN TIME AND IN SPACE. SUBSAMPLING SPATIALLY AND TEMPORALLY CAN INCREASE THE POSSIBILITY OF BE TRUE.
        
        '''
    
        if code_DATA_from_matlab:
            path_Sigma_inverse = Path(MORAANE_PATH).joinpath('data_PIV').\
                joinpath('HSigSigH_PIV_'+type_data+'_'+str(nb_modes)
                         + '_modes_a_cst_threshold_NaN')  # Load Sigma_inverse
            Sigma_inverse_data = hdf5storage.loadmat(
                str(path_Sigma_inverse))  # Select Sigma_inverse
            Sigma_inverse = Sigma_inverse_data['inv_HSigSigH'][:, 0, :, :]
        else:
            print("\nSigma_inverse already defined with [convert_Cmat_to_python_Topos] function\n")
        topos_new_coordinates = np.reshape(topos,
                                           MX_PIV + tuple(np.array([data_assimilate_dim, (nb_modes+1)])), order='F')    
        
        # Plots for debug
        if plot_debug:
            matrix_H_plot = topos_new_coordinates.copy()
            fig = plt.figure(20)
            imgplot = plt.imshow(np.transpose(matrix_H_plot[:, :, 0, -1]),
                                 interpolation='none', extent=[coordinates_x_PIV[0], coordinates_x_PIV[-1],
                                                               coordinates_y_PIV[0], coordinates_y_PIV[-1]])
            plt.title("mean : Ux")
            fig.colorbar(imgplot, orientation="horizontal")
            plt.pause(1)
            plt.savefig(PATH_output.joinpath("mode0_Ux.png"),
                        dpi=100, transparent=False)
            plt.close()
    
            fig = plt.figure(21)
            imgplot = plt.imshow(np.transpose(matrix_H_plot[:, :, 1, -1]),
                                 interpolation='none', extent=[coordinates_x_PIV[0], coordinates_x_PIV[-1],
                                                               coordinates_y_PIV[0], coordinates_y_PIV[-1]])
            plt.title("mean : Uy")
            fig.colorbar(imgplot, orientation="horizontal")
            plt.pause(1)
            plt.savefig(PATH_output.joinpath("mode0_Uy.png"),
                        dpi=100, transparent=False)
            plt.close()
    
            for n in range(nb_modes):
    
                fig = plt.figure(int(20+n+1))
                imgplot = plt.imshow(np.transpose(matrix_H_plot[:, :, 0, n]),
                                     interpolation='none', extent=[coordinates_x_PIV[0], coordinates_x_PIV[-1],
                                                                   coordinates_y_PIV[0], coordinates_y_PIV[-1]])
                plt.title("mode "+str(n+1)+" : Ux")
                fig.colorbar(imgplot, orientation="horizontal")
                plt.pause(1)
                plt.savefig(PATH_output.joinpath("mode"+str(n+1) +
                            "_Ux.png"), dpi=100, transparent=False)
                plt.close()
    
                fig = plt.figure(int(21+n+1))
                imgplot = plt.imshow(np.transpose(matrix_H_plot[:, :, 1, n]),
                                     interpolation='none', extent=[coordinates_x_PIV[0], coordinates_x_PIV[-1],
                                                                   coordinates_y_PIV[0], coordinates_y_PIV[-1]])
                plt.title("mode "+str(n+1)+" : Uy")
                fig.colorbar(imgplot, orientation="horizontal")
                plt.pause(1)
                plt.savefig(PATH_output.joinpath("mode"+str(n+1) +
                            "_Uy.png"), dpi=100, transparent=False)
                plt.close()
    
        # The topos that we have estimated reshaped to posterior matrix multiplications
        Hpiv_Topos = np.reshape(topos_new_coordinates, (int(
            topos_new_coordinates.shape[0]*topos_new_coordinates.shape[1]*topos_new_coordinates.shape[2]), topos_new_coordinates.shape[3]), order='F')
    
        
        #%%  Define and apply mask in the observation
        '''
        In the lines below we define and apply the observation mask. 
        It allows define where we'll observe in the PIV grid and
        if necessary with smaller spatial grid. 
        
        Matrices that should receive M_mask:
            - Y_obs
            - H_piv_Topos
            - Sigma_inverse
        
        The information about the grid points in x and y spatially represented are stocked in 
        coordinates_x_PIV and coordinates_y_PIV, respectivelly.
        
        '''
        if mask_obs == True:   # If we must select a smaller grid inside the observed grid.
    
            # Define the last x index of the new grid
            xEnd_index = x0_index + nbPoints_x*subsampling_PIV_grid_factor
            # Define the last y new grid index
            yEnd_index = y0_index + nbPoints_y*subsampling_PIV_grid_factor
            # print(len(coordinates_y_PIV-1))
            # print(len(coordinates_x_PIV-1))
            # Checks if the points are inside the observed grid
            if (yEnd_index-subsampling_PIV_grid_factor) > (len(coordinates_y_PIV-1)) or (xEnd_index-subsampling_PIV_grid_factor) > (len(coordinates_x_PIV-1)):
                print('Error: grid selected is bigger than the observed')
                sys.exit()
    
            # Selecting the new grid
            coordinates_x_PIV_with_MASK = coordinates_x_PIV[x0_index:
                                                            xEnd_index:subsampling_PIV_grid_factor]
            # Selecting the new grid
            coordinates_y_PIV_with_MASK = coordinates_y_PIV[y0_index:
                                                            yEnd_index:subsampling_PIV_grid_factor]
    
            '''
            We need to construct the mask to select the coefficients in the matrices.
            '''
            Mask_x = np.zeros(len(coordinates_x_PIV),
                              dtype=np.int8)    # Construct the mask x
            # Define the points of the new grid as 1
            Mask_x[x0_index:xEnd_index:subsampling_PIV_grid_factor] = 1
    
            # Construct the mask y
            Mask_y = np.zeros(len(coordinates_y_PIV), dtype=np.int8)
            # Define the points of the new grid as 1
            Mask_y[y0_index:yEnd_index:subsampling_PIV_grid_factor] = 1
    
            ###############################--Begin the mask construction--#############
            # If the first collum dont  belongs to the grid
            if Mask_y[0] == 0:
                # Add a zeros to the mask
                Mask_final = np.zeros(len(Mask_x), dtype=np.int8)
            else:                                                  # If it belongs
                Mask_final = Mask_x.copy()                         # Add the Mask x
    
            # The process continues to y>1 until the last column
            for line in Mask_y[1:]:
                if line == 0:
                    Mask_final = np.concatenate(
                        (Mask_final, np.zeros(len(Mask_x), dtype=np.int8)))
                else:
                    Mask_final = np.concatenate((Mask_final, Mask_x.copy()))
    
    
            # print('The coordinates that will be observed: ')
            # print('The x coordinates: '+str(coordinates_x_PIV_with_MASK))
            # print('The y coordinates: '+str(coordinates_y_PIV_with_MASK))
        else:
            # Construct the mask
            Mask_final = np.ones(
                int(len(coordinates_x_PIV)*len(coordinates_y_PIV)), dtype=np.int8)
            coordinates_x_PIV_with_MASK = coordinates_x_PIV
            coordinates_y_PIV_with_MASK = coordinates_y_PIV
            xEnd_index = len(coordinates_x_PIV)
            yEnd_index = len(coordinates_y_PIV)
    
        # It must be concatenated with himself because we are working with 2 dimensions
        Mask_final = np.concatenate((Mask_final, Mask_final))
        # Transform the data inside in boolean. 1->True and 0->False
        Mask_final_bool = Mask_final.astype(bool)
    
        print('\nThe points that will be observed (with MASK): ')
        print('  The x coordinates : '+str(coordinates_x_PIV_with_MASK))
        print('  The y coordinates : '+str(coordinates_y_PIV_with_MASK))
        # %%   Calculate Sigma_inverse
    
        if code_DATA_from_matlab:
            print('Loading Sigma and multipling likelihood matrices')
            # Load Sigma inverse
            Sigma_inverse = Sigma_inverse_data['inv_HSigSigH'][:, 0, :, :]
    
        # SelectSigma inverse in the mask that we observe
        Sigma_inverse = Sigma_inverse[Mask_final_bool[:Sigma_inverse.shape[0]], :, :].copy(
        )
    
        # Transform this matrix in a square matrix
        # Number of points in the grid
        nb_points = Sigma_inverse.shape[0]
        # Dimension
        nb_dim = Sigma_inverse.shape[1]
    
        # Applying final mask after define observation window
        Hpiv_Topos = Hpiv_Topos[Mask_final_bool, :].copy()
    
        '''
        The sigma inversed must be transformed in a matrix.
        It contains the inversed matrix of correlations that is uncorrelated
        in space and in time. The correlation is between dimensions.     
        '''
        # We define K as the sigma inversed matrix times the Hpiv_Topos matrix
        # K = Sigma_inverse_squared @ Hpiv_Topos   
        # K = B in the JCP paper
    
        # Calculating necessary matrices
        
        K = np.zeros((int(nb_dim), int(nb_modes+1), int(nb_points)))
        Sigma_inverse = np.transpose(Sigma_inverse, (1, 2, 0))
        Hpiv_Topos = np.reshape(
            Hpiv_Topos, (int(nb_points), int(nb_dim), int(nb_modes+1)), order='F')
        Hpiv_Topos = np.transpose(Hpiv_Topos, (1, 2, 0))
        # To all spatial samples we create the first part of the matrix that contains the correlation of Vx
        for line in range(int(nb_points)):
            K[:, :, line] = Sigma_inverse[:, :, line] @ Hpiv_Topos[:, :, line]
        K = np.transpose(K, (2, 0, 1))  # ((nb_points),(nb_dim),(nb_modes+1),)
        K = np.reshape(K, (int(nb_points*nb_dim), int(nb_modes+1)), order='F')
        # ((nb_points),(nb_dim),(nb_modes+1),)
        Hpiv_Topos = np.transpose(Hpiv_Topos, (2, 0, 1))
        Hpiv_Topos = np.reshape(
            Hpiv_Topos, (int(nb_points*nb_dim), int(nb_modes+1)), order='F')
        # ((nb_points),(nb_dim),(nb_dim),)
        Sigma_inverse = np.transpose(Sigma_inverse, (2, 0, 1))
        
        #    Change the sign of spatial mode for mode=num_mode_to_reverse
        # mode1 -> -mode1
        # num_mode = 1
        if code_change_mode_sign_HpivK_bt_tot == True:
            for num_mode_to_reverse in vect_num_mode_to_reverse:
                change_mode_sign_HPivK(str(nb_modes), str(
                    num_mode_to_reverse), Hpiv_Topos, K)
    
        # The Hpiv_Topos times K is necessary too
        Hpiv_Topos_K = Hpiv_Topos.T @ K
    
        print('\nLikelihood matrices computed')
    
        print('  Hpiv_Topos:', str(Hpiv_Topos.shape))
        print('  Sigma_inverse:', str(Sigma_inverse.shape)+"\n")
        
        #%% LOAD PIV data 
        
        if assimilate == 'real_data':
    
            file = Path(MORAANE_PATH).joinpath('data_PIV').joinpath(
                'wake_Re'+str(Re)).joinpath('B'+str(1).zfill(4)+'.dat')   # The path to load PIV data
            # Open the PIV data
            data = open(str(file))
            # Reading the data
            datContent = [i.strip().split() for i in data.readlines()]
            # Getting the data PIV
            data = datContent[4:]
    
            nb_lines = len(data)                           # lines amount
            nb_collums = len(data[0][2:4])                 # Commumns amount
            # Creating matrix to stock data
            matrix = np.zeros(shape=(nb_lines, nb_collums))
    
            '''
            We will select the first data in 0.080833 and after we will load the files taking in account the factor of subsampling and the amount of files. 
            '''
            for i, line in enumerate(data):  # Select the data in the first PIV file
                for j, number in enumerate(line[2:4]):
                    matrix[i, j] = number
    
            # Select the PIV data in the first mask calculated (The mask inside PIV and DNS)
            matrix_data_PIV_all_data = matrix[Sigma_inverse_data['mask'][:, 0], :].copy()[
                np.newaxis, ...]
            print('Loading PIV data: '+str(number_of_PIV_files)+' files...')
    
            if number_of_PIV_files > 1:
                # Loading the other files as defined in the start of this function
                for nb_file in range(1, (number_of_PIV_files+1), factor_of_PIV_time_subsampling)[1:]:
                    print(nb_file)
                    file = Path(MORAANE_PATH).joinpath('data_PIV').joinpath(
                        'wake_Re'+str(Re)).joinpath('B'+str(nb_file).zfill(4)+'.dat')  # Path to file
                    # Open the file
                    data = open(str(file))
                    # Read the data
                    datContent = [i.strip().split() for i in data.readlines()]
                    # Getting the data PIV
                    data = datContent[4:]
    
                    # Define the matrix to stock the data
                    matrix = np.zeros(shape=(nb_lines, nb_collums))
                    # Decode the information and save it as a matrix
                    for i, line in enumerate(data):
                        for j, number in enumerate(line[2:4]):
                            matrix[i, j] = number
    
                    matrix_data_PIV_all_data = np.concatenate((matrix_data_PIV_all_data, matrix[Sigma_inverse_data['mask'][:, 0], :].copy()[
                                                              np.newaxis, ...]), axis=0)  # Save the matrix inside the matrix of all the PIV data
    
            # Normalizing  measured data
            matrix_data_PIV_all_data = matrix_data_PIV_all_data / \
                PIV_velocity  # Normalizing the PIV data to compare with DNS
            
            '''
            We need to apply the same observation mask on the observed data.
            Because the new mask is defined to control where we will observe inside the PIV window
            '''
            matrix_data_PIV_all_data = matrix_data_PIV_all_data[:,
                                                                Mask_final_bool[:matrix_data_PIV_all_data.shape[1]], :].copy()
    
        elif assimilate == 'fake_real_data':
            '''
            If the case of assimilate fake_real_data is choosen,
            we assimilate the DNS smoothed and with noise. 
            (fake PIV(real data)).
            '''
            start = t_exe.time()
            
            if code_DATA_from_matlab:
                i = 1
                file = Path(MORAANE_PATH).joinpath('data_PIV')\
                    .joinpath('wake_Re'+str(Re)+'_fake')\
                    .joinpath('strat'+str(nb_file_learning_basis+i)+'_U_temp_PIV')   # The path to load PIV data
                data = hdf5storage.loadmat(str(file))
                vector_of_assimilation_time = np.array(
                    data['interval_time_local'][0, :])
                dt_PIV = np.array(data['dt'][0, :])
                index_final = SECONDS_OF_SIMU/dt_PIV
                vector_flow = data['U'].copy()
                nb_snapshots_each_file = vector_flow.shape[1]
    
            time_per_file = (nb_snapshots_each_file)*dt_PIV
            if SECONDS_OF_SIMU % time_per_file == 0:
                number_of_FAKE_PIV_files = int(SECONDS_OF_SIMU/time_per_file)
            else:
                number_of_FAKE_PIV_files = int(SECONDS_OF_SIMU/time_per_file) + 1
    
            print('\nLoading Fake PIV data:' +
                  str(number_of_FAKE_PIV_files)+' files ...')
            
            if code_DATA_from_matlab:
    
                if number_of_FAKE_PIV_files > 1:
                    for i in range(1, number_of_FAKE_PIV_files+1, 1)[1:]:
                        file = Path(MORAANE_PATH).joinpath('data_PIV')\
                            .joinpath('wake_Re'+str(Re)+'_fake')\
                            .joinpath('strat'+str(nb_file_learning_basis+i)+'_U_temp_PIV')  # The path to load PIV data
    
                        print("##### file_data="+str(file))
    
                        data = hdf5storage.loadmat(str(file))
                        vector_flow = np.concatenate(
                            (vector_flow, data['U']), axis=1)
                        vector_of_assimilation_time = np.concatenate(
                            (vector_of_assimilation_time, np.array(data['interval_time_local'][0, :])))
    
                vector_flow = np.transpose(vector_flow, (1, 0, 2))
     
            if not code_DATA_from_matlab:
                # only space and time dimensional files like real PIV
                # ... time must be reviewed ...
                if (Re == 100):
                    print("\ndata=fake_real_data=f(C++) => fake_real_data unknown")
                    sys.exit()
                else:
                    vector_flow, vector_of_assimilation_time = convert_Cmat_to_python_FakePIV(MX_PIV_all, index_XY_PIV, PARAM)           
                    f_info.write("  - data (Re=" + str(Re)+") : \n    " +
                                 str(folder_data) + "/*/B0001_new.dat\n\n")
                    f_info.write(
                        "    (function used : Cf. podfs2/python_scripts/mains/convert_Cmat_to_python_Topos_FakePIV.py)" + "\n\n")
                
            end = t_exe.time()
            print('Time for loading '+str(number_of_FAKE_PIV_files)+' Fake PIV files : '+str(end -start)+'\n\n')
    
            # Plots for debug
            if plot_debug:
                mean_vector_flow = np.mean(vector_flow, axis=0)
                mean_vector_flow = np.reshape(mean_vector_flow, (len(
                    coordinates_x_PIV), len(coordinates_y_PIV), 2), order='F')
                mean_vector_flow.shape
    
                fig = plt.figure(10)
                imgplot = plt.imshow(np.transpose(mean_vector_flow[:, :, 0]), interpolation='none', extent=[
                    coordinates_x_PIV[0], coordinates_x_PIV[-1], coordinates_y_PIV[0], coordinates_y_PIV[-1]])
                plt.title("mean(WAKE) : Ux")
                fig.colorbar(imgplot, orientation="horizontal")
                plt.pause(1)
                plt.savefig(PATH_output.joinpath("mean_WAKE_Ux.png"),
                            dpi=100, transparent=False)
                # plt.close()
    
                fig = plt.figure(11)
                imgplot = plt.imshow(np.transpose(mean_vector_flow[:, :, 1]), interpolation='none', extent=[
                    coordinates_x_PIV[0], coordinates_x_PIV[-1], coordinates_y_PIV[0], coordinates_y_PIV[-1]])
                plt.title("mean(WAKE) : Uy")
                fig.colorbar(imgplot, orientation="horizontal")
                plt.pause(1)
                plt.savefig(PATH_output.joinpath("mean_WAKE_Uy.png"),
                            dpi=100, transparent=False)
                # plt.close()
    
                matrix_H_plot = topos_new_coordinates.copy()
                differ = mean_vector_flow[:, :, 0] - matrix_H_plot[:, :, 0, -1]
                fig = plt.figure(12)
                imgplot = plt.imshow(np.transpose(differ), interpolation='none', extent=[
                                     coordinates_x_PIV[0], coordinates_x_PIV[-1], coordinates_y_PIV[0], coordinates_y_PIV[-1]])
                plt.title("diff mean(WAKE)-mode0 : Ux")
                fig.colorbar(imgplot, orientation="horizontal")
                plt.pause(1)
                plt.savefig(PATH_output.joinpath(
                    "diff_mean_WAKE_mode0_Ux.png"), dpi=100, transparent=False)
                # plt.close()
    
                differ = mean_vector_flow[:, :, 1] - matrix_H_plot[:, :, 1, -1]
                fig = plt.figure(13)
                imgplot = plt.imshow(np.transpose(differ), interpolation='none', extent=[
                                     coordinates_x_PIV[0], coordinates_x_PIV[-1], coordinates_y_PIV[0], coordinates_y_PIV[-1]])
                plt.title("diff mean(WAKE)-mode0 : Uy")
                fig.colorbar(imgplot, orientation="horizontal")
                plt.pause(1)
                plt.savefig(PATH_output.joinpath(
                    "diff_mean_WAKE_mode0_Uy.png"), dpi=100, transparent=False)
                # plt.close()
    
            # reduce vector_flow to obs time range
            index_final = SECONDS_OF_SIMU/dt_PIV
            vector_flow = vector_flow[:int(
                index_final):factor_of_PIV_time_subsampling, :, :]
    
            # reshape using MASK
            vector_flow = vector_flow[:, Mask_final_bool[:vector_flow.shape[1]], :]
    
            matrix_data_PIV_all_data = vector_flow.copy()
            print("##### matrix_data_PIV_all_data=" +
                  str(matrix_data_PIV_all_data.shape))
    
            vector_of_assimilation_time = vector_of_assimilation_time[:int(
                index_final):factor_of_PIV_time_subsampling]
            print('##### vector_of_assimilation_time=' +
                  str(vector_of_assimilation_time)+"\n")
    
        else:
            print('Error: Data to assimilate is not known.')
            sys.exit()
        
        if len(vector_of_assimilation_time) > 0 and code_Assimilation:
            if vector_of_assimilation_time[0] == 0:
                matrix_data_PIV_all_data = matrix_data_PIV_all_data[1:, :, :]
                vector_of_assimilation_time = vector_of_assimilation_time[1:]
    else:
        vector_of_assimilation_time = np.full((1, 1), np.inf)
        
    #%% Pre-processing for plotting Q cirterion
    if plot_Q_crit:
        file = 'tensor_mode_' + type_data + '_'+str(nb_modes)+'_modes'
        name_file_data = Path(MORAANE_PATH).joinpath('data').joinpath(file)
        mat = hdf5storage.loadmat(str(name_file_data))
        Omega_phi_m_U = mat['Omega_phi_m_U']
        S_phi_m_U = mat['S_phi_m_U']
    
    #%% Begin propagation and assimilation
    # Cholesky de la matrix de covariance
    pchol_cov_noises = beta_3*pchol_cov_noises
    if LeastSquare:
        ILC_EV['pchol_cov_noises'] = np.zeros(ILC_EV['pchol_cov_noises'].shape)
        ILC_EV['I'] = np.zeros(ILC_EV['I'].shape)
        ILC_EV['L'] = np.zeros(ILC_EV['L'].shape)
        ILC_EV['C'] = np.zeros(ILC_EV['C'].shape)
        Hpiv_Topos_otimization = Hpiv_Topos[:, :-1].copy()
#            Hpiv_Topos_otimization[:,j] = Hpiv_Topos_otimization[:,j] / diag_reg[j]
    elif EV_withoutNoise:
        ILC_EV['pchol_cov_noises'] = np.zeros(ILC_EV['pchol_cov_noises'].shape)
    elif EV:
        ILC_EV['pchol_cov_noises'] = beta_3*ILC_EV['pchol_cov_noises']
    # Time simulation step
    original_dt_simu = param['dt']
    # Flag to control assimilation moments
    assimilate_PIV = False
    # Flag to count the assimilation steps
    nb_assim = 0
    # Control de next moment that a obs will be available
    next_time_of_assimilation = vector_of_assimilation_time[nb_assim]
    # Control de index of assimilation
    index_of_filtering = []
    # The time of assimilation
    time = [0]
    # Flag to control de noise in the past until now to mutation steps in Metropolis-Hastings
    index_pf = [0]
#    time_bt_tot = time_bt_tot + next_time_of_assimilation

    # Defining figure to plot if real data is True
    if plt_real_time == True:
        if bt_tot.shape[1] <= 2:
            fig_height_loc = int(float(fig_height)/2)
        else:
            fig_height_loc = fig_height
        plt.ion()
        fig = plt.figure(0, figsize=[fig_width, fig_height_loc])
        plt.rcParams['axes.grid'] = True

        if bt_tot.shape[1] <= 2:
            ax_1 = fig.add_subplot(1, 2, 1)
            ax_1.set_ylim([-lim_fig[0], lim_fig[0]])

            ax_2 = fig.add_subplot(1, 2, 2)
            ax_2.set_ylim([-lim_fig[1], lim_fig[1]])
        else:
            ax_1 = fig.add_subplot(2, 2, 1)
            ax_1.set_ylim([-lim_fig[0], lim_fig[0]])

            ax_2 = fig.add_subplot(2, 2, 2)
            ax_2.set_ylim([-lim_fig[1], lim_fig[1]])

            ax_3 = fig.add_subplot(2, 4, 5)
            ax_3.set_ylim([-lim_fig[2], lim_fig[2]])

            ax_4 = fig.add_subplot(2, 4, 6)
            ax_4.set_ylim([-lim_fig[3], lim_fig[3]])

            ax_5 = fig.add_subplot(2, 4, 7)
            ax_5.set_ylim([-lim_fig[4], lim_fig[4]])

            ax_6 = fig.add_subplot(2, 4, 8)
            ax_6.set_ylim([-lim_fig[5], lim_fig[5]])

        quantiles_now = np.quantile(
            bt_MCMC[-1, :, :], q=[0.025, 0.975], axis=1)
        particles_mean_now = np.mean(bt_MCMC[-1, :, :], axis=1)
        if EV:
            quantiles_now_EV = np.quantile(
                bt_forecast_EV[-1, :, :], q=[0.025, 0.975], axis=1)
            particles_mean_now_EV = np.mean(bt_forecast_EV[-1, :, :], axis=1)

        line11, = ax_1.plot(time[-1], particles_mean_now[0],
                            'b-', label='Red LUM particles mean')
        line12 = ax_1.fill_between(
            [0], quantiles_now[0:1, 0], quantiles_now[1:2, 0], color='gray')
        if EV:
            line11EV, = ax_1.plot(time[-1], particles_mean_now_EV[0], '-',
                                  color=color_mean_EV, label='EV particles mean')
            line12EV = ax_1.fill_between(
                [0], quantiles_now_EV[0:1, 0], quantiles_now[1:2, 0], color=color_quantile_EV)
        line13,  = ax_1.plot([0], [pos_Mes*1], 'r.', label='Assimilate True')

        line21, = ax_2.plot(time[-1], particles_mean_now[1],
                            'b-', label='Red LUM particles mean')
        if heavy_real_time_plot:
            line22 = ax_2.fill_between(
                [0], quantiles_now[0:1, 1], quantiles_now[1:2, 1], color='gray')
        if EV:
            line21EV, = ax_2.plot(time[-1], particles_mean_now_EV[1], '-',
                                  color=color_mean_EV, label='EV particles mean')
            if heavy_real_time_plot:
                line22EV = ax_2.fill_between(
                    [0], quantiles_now_EV[0:1, 1], quantiles_now[1:2, 1], color=color_quantile_EV)
        line23,  = ax_2.plot([0], [pos_Mes*1], 'r.', label='Assimilate True')

        if bt_tot.shape[1] > 2:
            line31, = ax_3.plot(
                time[-1], particles_mean_now[2], 'b-', label='Red LUM particles mean')
            if heavy_real_time_plot:
                line32 = ax_3.fill_between(
                    [0], quantiles_now[0:1, 2], quantiles_now[1:2, 2], color='gray')
            if EV:
                line31EV, = ax_3.plot(time[-1], particles_mean_now_EV[2], '-',
                                      color=color_mean_EV, label='EV particles mean')
                if heavy_real_time_plot:
                    line32EV = ax_3.fill_between(
                        [0], quantiles_now_EV[0:1, 2], quantiles_now[1:2, 2], color=color_quantile_EV)
            line33,  = ax_3.plot([0], [pos_Mes*1], 'r.',
                                 label='Assimilate True')

        if bt_tot.shape[1] > 3:
            line41, = ax_4.plot(
                time[-1], particles_mean_now[3], 'b-', label='Red LUM particles mean')
            if heavy_real_time_plot:
                line42 = ax_4.fill_between(
                    [0], quantiles_now[0:1, 3], quantiles_now[1:2, 3], color='gray')
            if EV:
                line41EV, = ax_4.plot(time[-1], particles_mean_now_EV[3], '-',
                                      color=color_mean_EV, label='EV particles mean')
                if heavy_real_time_plot:
                    line42EV = ax_4.fill_between(
                        [0], quantiles_now_EV[0:1, 3], quantiles_now[1:2, 3], color=color_quantile_EV)
            line43,  = ax_4.plot([0], [pos_Mes*1], 'r.',
                                 label='Assimilate True')

        if bt_tot.shape[1] > 4:
            line51, = ax_5.plot(
                time[-1], particles_mean_now[4], 'b-', label='Red LUM particles mean')
            if heavy_real_time_plot:
                line52 = ax_5.fill_between(
                    [0], quantiles_now[0:1, 4], quantiles_now[1:2, 4], color='gray')
            if EV:
                line51EV, = ax_5.plot(time[-1], particles_mean_now_EV[4], '-',
                                      color=color_mean_EV, label='EV particles mean')
                if heavy_real_time_plot:
                    line52EV = ax_5.fill_between(
                        [0], quantiles_now_EV[0:1, 4], quantiles_now[1:2, 4], color=color_quantile_EV)
            line53,  = ax_5.plot([0], [pos_Mes*1], 'r.',
                                 label='Assimilate True')

        if bt_tot.shape[1] > 5:
            line61, = ax_6.plot(
                time[-1], particles_mean_now[5], 'b-', label='Red LUM particles mean')
            if heavy_real_time_plot:
                line62 = ax_6.fill_between(
                    [0], quantiles_now[0:1, 5], quantiles_now[1:2, 5], color='gray')
            if EV:
                line61EV, = ax_6.plot(time[-1], particles_mean_now_EV[5], '-',
                                      color=color_mean_EV, label='EV particles mean')
                if heavy_real_time_plot:
                    line6EV2 = ax_6.fill_between(
                        [0], quantiles_now_EV[0:1, 5], quantiles_now[1:2, 5], color=color_quantile_EV)
            line63,  = ax_6.plot([0], [pos_Mes*1], 'r.',
                                 label='Assimilate True')

        if plot_ref == True:
            line14, =  ax_1.plot(
                time_bt_tot[-1], bt_tot[0, 0], 'k--', label='True state')
            line24, =  ax_2.plot(
                time_bt_tot[-1], bt_tot[0, 1], 'k--', label='True state')
            if bt_tot.shape[1] > 2:
                line34, =  ax_3.plot(
                    time_bt_tot[-1], bt_tot[0, 2], 'k--', label='True state')
            if bt_tot.shape[1] > 3:
                line44, =  ax_4.plot(
                    time_bt_tot[-1], bt_tot[0, 3], 'k--', label='True state')
            if bt_tot.shape[1] > 4:
                line54, =  ax_5.plot(
                    time_bt_tot[-1], bt_tot[0, 4], 'k--', label='True state')
            if bt_tot.shape[1] > 5:
                line64, =  ax_6.plot(
                    time_bt_tot[-1], bt_tot[0, 5], 'k--', label='True state')

        ax_1.set(xlabel="Time(sec)", ylabel='Chronos ' +
                 r'$b_'+str(1)+'$'+' amplitude')
        ax_1.legend()
        ax_2.set(xlabel="Time(sec)", ylabel='Chronos ' +
                 r'$b_'+str(2)+'$'+' amplitude')
        ax_2.legend()
        if bt_tot.shape[1] > 2:
            ax_3.set(xlabel="Time(sec)", ylabel='Chronos ' +
                     r'$b_'+str(3)+'$'+' amplitude')
            ax_3.legend()
        if bt_tot.shape[1] > 3:
            ax_4.set(xlabel="Time(sec)", ylabel='Chronos ' +
                     r'$b_'+str(4)+'$'+' amplitude')
            ax_4.legend()
        if bt_tot.shape[1] > 4:
            ax_5.set(xlabel="Time(sec)", ylabel='Chronos ' +
                     r'$b_'+str(5)+'$'+' amplitude')
            ax_5.legend()
        if bt_tot.shape[1] > 5:
            ax_6.set(xlabel="Time(sec)", ylabel='Chronos ' +
                     r'$b_'+str(6)+'$'+' amplitude')
            ax_6.legend()

    N_tot_max = int(SECONDS_OF_SIMU/param['dt'])+1
    N_tot = param['N_tot']*n_simu
    if N_tot > N_tot_max:
        N_tot = N_tot_max
    param['N_tot'] = N_tot
    param['N_test'] = param['N_tot'] - 1
    time_exe = 0
    if EV:
        time_exe_EV = 0
    n_frame_plots = int(plot_period/param['dt'])
                   
    ################################ Start temporal integration ###################################
    for index in range(param['N_test']*(not code_load_run)): # Set the number of integration steps

        ##### Model integration of all particles
        start = t_exe.time()
        val0, val1, val2, noises_centered = evol_forward_bt_MCMC(ILC_a_cst['I'],
                                                                 ILC_a_cst['L'],
                                                                 ILC_a_cst['C'],
                                                                 pchol_cov_noises, param['dt'],
                                                                 bt_MCMC[-1, :,
                                                                         :], float('Nan'),
                                                                 float('Nan'), mutation=False, noise_past=0, pho=0)
        end = t_exe.time()
        time_exe = time_exe + end - start
        if EV:
            start = t_exe.time()
            val0_EV, val1_EV, val2_EV, noises_centered_EV = evol_forward_bt_MCMC(ILC_EV['I'],
                                                                                 ILC_EV['L'],
                                                                                 ILC_EV['C'],
                                                                                 ILC_EV['pchol_cov_noises'], param['dt'],
                                                                                 bt_forecast_EV[-1, :, :], float(
                                                                                     'Nan'),
                                                                                 float('Nan'), mutation=False, noise_past=0, pho=0)
            end = t_exe.time()
            time_exe_EV = time_exe_EV + end - start
        
        if index == 0:
            # Set the noises
            noises = noises_centered[np.newaxis, ...]
            noises_EV = noises
        time.append(param['dt']+time[-1])
        #########################################----------------------#############################################
        #########################################--PARTICLE FILTERING--#############################################

#        if (index+1)%(int(period_in_samples*beta_4))== 0:
#            period = True
#            print('Index of activating filtering: '+str(index))
        
#        if ((index+1))%(int(factor*n_simu*beta_4)) == 0:
#            period = True
#            print('-----------------------------STARTING PARTICLE FILTERING---------------------------')
#            print('Index of activating filtering: '+str(index))
#        period = True

        # The Flag assimilate_PIV control the moments that we can assimilate data
        if (assimilate_PIV == True):
            # Stock the assimilation index
            index_of_filtering.append(index)
            print('Time : '+str(time[-1]))
            # Stock the assimilation index to control noise and past particles
            index_pf.append(index+1)
            
            # Define the obs and reshape it
            obs = np.reshape(matrix_data_PIV_all_data[nb_assim, :, :], (matrix_data_PIV_all_data[nb_assim,
                             :, :].shape[0]*matrix_data_PIV_all_data[nb_assim, :, :].shape[1]), order='F')[..., np.newaxis]

            # Define the particles now
            particles = val0[0, :, :]
            # Define the particles after the last filter step
            particles_past = bt_MCMC[index_pf[-2], ...]
            if EV:
                # Define the particles now
                particles_EV = val0_EV[0, :, :]
                # Define the particles after the last filter step
                particles_past_EV = bt_forecast_EV[index_pf[-2], ...]
            # Define the delta t as the number of integrations(IMPORTANT: In the case of real time assimilation the dt is variable.....)
            delta_t = index_pf[-1] - index_pf[-2]

            # Call particle filter
            print(' PF Red LUM')
            start = t_exe.time()
            particles = particle_filter(ILC_a_cst, obs, K, Hpiv_Topos_K, particles, N_threshold,
                                        np.concatenate((noises, noises_centered[np.newaxis, ...]), axis=0)[
                                            index_pf[-2]:index_pf[-1], ...],
                                        particles_past, nb_mutation_steps, original_dt_simu, param['dt'], pho, delta_t, pchol_cov_noises, time[-1])
            end = t_exe.time()
            time_exe = time_exe + end - start
            if EV:
                print(' PF EV+noise')
                start = t_exe.time()
                if LeastSquare:
                    '''                                                      
#                    Reshape Piv data in order to compare with topos
#                    '''
                    y_less_average = obs[:, 0] - Hpiv_Topos[..., -1].copy()
                    reg = linear_model.LinearRegression()
                    reg.fit(Hpiv_Topos_otimization, y_less_average.T)
                    particles_EV = np.tile(
                        reg.coef_[:, np.newaxis], (1, param['N_particules']))
                        
                else:
                    particles_EV = particle_filter(ILC_EV, obs, K, Hpiv_Topos_K, particles_EV, N_threshold,
                                                   np.concatenate((noises_EV, noises_centered_EV[np.newaxis, ...]), axis=0)[
                                                       index_pf[-2]:index_pf[-1], ...],
                                                   particles_past_EV, nb_mutation_steps, original_dt_simu, param['dt'], pho, delta_t, ILC_EV['pchol_cov_noises'], time[-1])
                end = t_exe.time()
                time_exe_EV = time_exe_EV + end - start

            # Define the particles
            val0 = particles[np.newaxis, ...]
            if EV:
                # Define the particles
                val0_EV = particles_EV[np.newaxis, ...]
            # Set the integration step as the original one
            param['dt'] = original_dt_simu
            # Set the next time of assimilation in the inf if there is no more data in the vecor
            if (nb_assim) == len(vector_of_assimilation_time)-1:
                next_time_of_assimilation = np.inf
            else:                                                                    # If there is data
                # Increments the Flag that controls the assimilation steps
                nb_assim += 1
                # Set the next time of assimilation
                next_time_of_assimilation = vector_of_assimilation_time[nb_assim]

            assimilate_PIV = False      # Set the control Flag to False

        ############################################################################################################
        #############################################################################################################
        # If the first time step integration
        if index == 0:
            # Set the noises
            noises = noises_centered[np.newaxis, ...]
        # If the next time of integration is not at inf, it saves the noise now
        elif (next_time_of_assimilation != np.inf):
            noises = np.concatenate(
                (noises, noises_centered[np.newaxis, ...]), axis=0)
        if EV:
            # If the first time step integration
            if index == 0:
                # Set the noises
                noises_EV = noises_centered_EV[np.newaxis, ...]
            # If the next time of integration is not at inf, it saves the noise now
            elif (next_time_of_assimilation != np.inf):
                noises_EV = np.concatenate(
                    (noises_EV, noises_centered_EV[np.newaxis, ...]), axis=0)

        # Concatenate the particles in this time step with the particles before
        bt_MCMC = np.concatenate((bt_MCMC, val0), axis=0)
        iii_realization = np.any(np.logical_or(np.isnan(bt_MCMC[index+1, :, :]), np.isinf(
            bt_MCMC[index+1, :, :])), axis=0)[..., np.newaxis]  # Control if any realization has explosed

        if EV:
            # Concatenate the particles in this time step with the particles before
            bt_forecast_EV = np.concatenate((bt_forecast_EV, val0_EV), axis=0)
            iii_realization_EV = np.any(np.logical_or(np.isnan(bt_forecast_EV[index+1, :, :]), np.isinf(
                bt_forecast_EV[index+1, :, :])), axis=0)[..., np.newaxis]  # Control if any realization has explosed

        # If the next time integration will end after the time of assimilation, hence we need to change the time step 'dt' to end exactly in the same time of the observation
        if (time[-1]+param['dt']) >= (next_time_of_assimilation):
            # Therefore, the next time integration step will be the difference between the future and the present.
            param['dt'] = next_time_of_assimilation - time[-1]
            assimilate_PIV = True                                # Set the Flag True

            # Solve possible explosions in the integration
        if np.any(iii_realization):
            if np.all(iii_realization):
                print('WARNING: All realization of the simulation have blown up.')
                
                if index < param['N_test']:
                    val_nan = np.full(
                        [int(param['N_test']-index), param['nb_modes'], param['N_particules']], np.nan)
                    bt_MCMC = np.concatenate((bt_MCMC, val_nan), axis=0)

                break

            nb_blown_up = np.sum(iii_realization)
            print('WARNING: ' + str(nb_blown_up) +
                  ' realizations have blown up and will be replaced.')
            good_indexes = np.where(
                (np.logical_not(iii_realization) == True))[0]
            bt_MCMC_good = bt_MCMC[-1, :, good_indexes].T

            bt_MCMC_good = bt_MCMC_good[np.newaxis, ...]

            rand_index = np.random.randint(
                0, param['N_particules'] - nb_blown_up, size=(nb_blown_up))
                
            bad_indexes = np.where((iii_realization == True))[0]
            bt_MCMC[-1, :, bad_indexes] = bt_MCMC_good[0, :, rand_index]
    
            del bt_MCMC_good 
            del rand_index 
            del nb_blown_up 
            del iii_realization     
        
        if EV:
            # Solve possible explosions in the integration
            if np.any(iii_realization_EV):
                if np.all(iii_realization_EV):
                    print('WARNING: All realization of the simulation have blown up.')
                    if index < param['N_test']:
                        val_nan_EV = np.full(
                            [int(param['N_test']-index), param['nb_modes'], param['N_particules']], np.nan)
                        bt_forecast_EV = np.concatenate(
                            (bt_forecast_EV, val_nan), axis=0)
                    break

                nb_blown_up_EV = np.sum(iii_realization_EV)
                print('WARNING: ' + str(nb_blown_up_EV) +
                      ' realizations have blown up and will be replaced.')
                good_indexes_EV = np.where(
                    (np.logical_not(iii_realization_EV) == True))[0]
                bt_forecast_EV_good = bt_forecast_EV[-1, :, good_indexes_EV].T

                bt_forecast_EV_good = bt_forecast_EV_good[np.newaxis, ...]

                rand_index_EV = np.random.randint(
                    0, param['N_particules'] - nb_blown_up_EV, size=(nb_blown_up_EV))
                    
                bad_indexes_EV = np.where((iii_realization_EV == True))[0]
                bt_forecast_EV_good[-1, :,
                                    bad_indexes_EV] = bt_forecast_EV_good[0, :, rand_index_EV]
        
                del bt_forecast_EV_good 
                del rand_index_EV 
                del nb_blown_up_EV 
                del iii_realization_EV   
    
        #%% Plots
        
        ######################### Testing real time plot #######################

        # Plot at each 20 time steps
        if (index % n_frame_plots) == 0 and ((plot_Q_crit == True) or (plt_real_time == True)):
            particles_mean = np.mean(bt_MCMC[:, :, :], axis=2)
            lim = np.where((time_bt_tot <= time[-1]))[0][-1] + 1

            if EV:
                particles_mean_EV = np.mean(bt_forecast_EV[:, :, :], axis=2)
                if (plt_real_time == True):
                    quantiles_EV = np.quantile(bt_forecast_EV[:, :, :], q=[
                                               0.025, 0.975], axis=2)

                ########################## Plotting Q cirterion ########################
                if plot_Q_crit:
                    particles_mean_ = np.hstack(
                        (particles_mean_EV, np.ones((particles_mean_EV.shape[0], 1))))[index, :]
                    particles_mean_ = np.tile(particles_mean_, ([
                                              Omega_phi_m_U.shape[0], Omega_phi_m_U.shape[2], Omega_phi_m_U.shape[3], 1]))
                    particles_mean_ = np.transpose(
                        particles_mean_, (0, 3, 1, 2))

                    Omega = np.multiply(particles_mean_, Omega_phi_m_U)
                    Omega = np.sum(Omega, axis=1)
                    Omega = np.sum(np.sum(np.power(Omega, 2), axis=2), axis=1)

                    S = np.multiply(particles_mean_, S_phi_m_U)
                    S = np.sum(S, axis=1)
                    S = np.sum(np.sum(np.power(S, 2), axis=2), axis=1)

                    Q = 0.5 * (Omega - S)
                    del Omega
                    del S
                    
                    MX = param['MX'].astype(int)
                    Q = np.reshape(Q, (MX))

                    time_CPU = time_exe_EV
                    time_phy = index*param['dt']
                    time_CPU_phy = np.array([time_CPU, time_phy])
                    
                    name_file_data_temp = path_Q_crit_EV.joinpath(
                        str(index)+'_temp.txt')
                    name_file_data = path_Q_crit_EV.joinpath(str(index)+'.txt')
                    
                    if os.path.exists(str(name_file_data)):
                        os.remove(str(name_file_data))
                    with open(str(name_file_data_temp), 'w') as f:
                        json.dump(time_CPU_phy.tolist(), f)
                        json.dump(Q.tolist(), f)
                    os.rename(r'' + str(name_file_data_temp),
                              r'' + str(name_file_data))
                    del Q
                
            if plot_ref:                
                ########################## Plotting Q cirterion ########################
                if plot_Q_crit:
                    bt_val_interp = np.zeros((1, bt_tot.shape[1]))
                    for j in range(bt_tot.shape[1]):
                        tck = interpolate.splrep(
                            time_bt_tot, bt_tot[:, j], s=0)
                        bt_val_interp[0, j] = interpolate.splev(
                            time[-1], tck, der=0)
                    particles_mean_ = np.hstack(
                        (bt_val_interp, np.ones((1, 1))))
                    particles_mean_ = np.tile(particles_mean_, ([
                                              Omega_phi_m_U.shape[0], Omega_phi_m_U.shape[2], Omega_phi_m_U.shape[3], 1]))
                    particles_mean_ = np.transpose(
                        particles_mean_, (0, 3, 1, 2))

                    Omega = np.multiply(particles_mean_, Omega_phi_m_U)
                    Omega = np.sum(Omega, axis=1)
                    Omega = np.sum(np.sum(np.power(Omega, 2), axis=2), axis=1)

                    S = np.multiply(particles_mean_, S_phi_m_U)
                    S = np.sum(S, axis=1)
                    S = np.sum(np.sum(np.power(S, 2), axis=2), axis=1)

                    Q = 0.5 * (Omega - S)
                    del Omega
                    del S
                    
                    MX = param['MX'].astype(int)
                    Q = np.reshape(Q, (MX))

                    time_CPU = 0
                    time_phy = index*param['dt']
                    time_CPU_phy = np.array([time_CPU, time_phy])
                    
                    name_file_data_temp = path_Q_crit_ref.joinpath(
                        str(index)+'_temp.txt')
                    name_file_data = path_Q_crit_ref.joinpath(
                        str(index)+'.txt')

                    if os.path.exists(str(name_file_data)):
                        os.remove(str(name_file_data))
                    with open(str(name_file_data_temp), 'w') as f:
                        json.dump(time_CPU_phy.tolist(), f)
                        json.dump(Q.tolist(), f)
                    os.rename(r'' + str(name_file_data_temp),
                              r'' + str(name_file_data))
                    del Q
            
            ########################## Plotting Q cirterion ########################
            if plot_Q_crit:
                particles_mean_ = np.hstack(
                    (particles_mean, np.ones((particles_mean.shape[0], 1))))[index, :]
                particles_mean_ = np.tile(particles_mean_, ([
                                          Omega_phi_m_U.shape[0], Omega_phi_m_U.shape[2], Omega_phi_m_U.shape[3], 1]))
                particles_mean_ = np.transpose(particles_mean_, (0, 3, 1, 2))

                Omega = np.multiply(particles_mean_, Omega_phi_m_U)
                Omega = np.sum(Omega, axis=1)
                Omega = np.sum(np.sum(np.power(Omega, 2), axis=2), axis=1)

                S = np.multiply(particles_mean_, S_phi_m_U)
                S = np.sum(S, axis=1)
                S = np.sum(np.sum(np.power(S, 2), axis=2), axis=1)

                Q = 0.5 * (Omega - S)
                del Omega
                del S
                
                MX = param['MX'].astype(int)
                Q = np.reshape(Q, (MX))

                time_CPU = time_exe
                time_phy = index*param['dt']
                time_CPU_phy = np.array([time_CPU, time_phy])
                
                name_file_data_temp = path_Q_crit.joinpath(
                    str(index)+'_temp.txt')
                name_file_data = path_Q_crit.joinpath(str(index)+'.txt')
                
                with open(str(name_file_data_temp), 'w') as f:
                    json.dump(time_CPU_phy.tolist(), f)
                    json.dump(Q.tolist(), f)
                os.rename(r'' + str(name_file_data_temp),
                          r'' + str(name_file_data))
                del Q

            if (plt_real_time == True):
                quantiles = np.quantile(bt_MCMC[:, :, :], q=[
                                        0.025, 0.975], axis=2)

                ax_1.set_xlim([0, time[-1]+10])
                ax_2.set_xlim([0, time[-1]+10])
                if bt_tot.shape[1] > 2:
                    ax_3.set_xlim([0, time[-1]+10])
                if bt_tot.shape[1] > 3:
                    ax_4.set_xlim([0, time[-1]+10])
                if bt_tot.shape[1] > 4:
                    ax_5.set_xlim([0, time[-1]+10])
                if bt_tot.shape[1] > 5:
                    ax_6.set_xlim([0, time[-1]+10])
                        
                ax_1.collections.clear()
                if EV:
                    line11EV.set_data(time, particles_mean_EV[:, 0])
    #                line11.set_data(time,particles_mean_EV[:,0], color=color_mean_EV)
                    ax_1.fill_between(
                        time, quantiles_EV[0, :, 0], quantiles_EV[1, :, 0], color=color_quantile_EV)
                line11.set_data(time, particles_mean[:, 0])
                ax_1.fill_between(
                    time, quantiles[0, :, 0], quantiles[1, :, 0], color='gray')
                line13.set_data(np.array(time)[np.array(index_pf)[
                                1:]], pos_Mes*np.ones((len(index_pf[1:]))))

                ax_2.collections.clear()
                if EV:
                    line21EV.set_data(time, particles_mean_EV[:, 1])
    #                line21EV.set_data(time,particles_mean_EV[:,1], color=color_mean_EV)
                    if heavy_real_time_plot:
                        ax_2.fill_between(
                            time, quantiles_EV[0, :, 1], quantiles_EV[1, :, 1], color=color_quantile_EV)
                line21.set_data(time, particles_mean[:, 1])
                if heavy_real_time_plot:
                    ax_2.fill_between(
                        time, quantiles[0, :, 1], quantiles[1, :, 1], color='gray')
                line23.set_data(np.array(time)[np.array(index_pf)[
                                1:]], pos_Mes*np.ones((len(index_pf[1:]))))

                if bt_tot.shape[1] > 2:
                    ax_3.collections.clear()
                    if EV:
                        line31EV.set_data(time, particles_mean_EV[:, 2])
        #                line31EV.set_data(time,particles_mean_EV[:,2], color=color_mean_EV)
                        if heavy_real_time_plot:
                            ax_3.fill_between(
                                time, quantiles_EV[0, :, 2], quantiles_EV[1, :, 2], color=color_quantile_EV)
                    line31.set_data(time, particles_mean[:, 2])
                    if heavy_real_time_plot:
                        ax_3.fill_between(
                            time, quantiles[0, :, 2], quantiles[1, :, 2], color='gray')
                    line33.set_data(np.array(time)[np.array(index_pf)[
                                    1:]], pos_Mes*np.ones((len(index_pf[1:]))))

                if bt_tot.shape[1] > 3:
                    ax_4.collections.clear()
                    if EV:
                        line41EV.set_data(time, particles_mean_EV[:, 3])
        #                line41EV.set_data(time,particles_mean_EV[:,3], color=color_mean_EV)
                        if heavy_real_time_plot:
                            ax_4.fill_between(
                                time, quantiles_EV[0, :, 3], quantiles_EV[1, :, 3], color=color_quantile_EV)
                    line41.set_data(time, particles_mean[:, 3])
                    if heavy_real_time_plot:
                        ax_4.fill_between(
                            time, quantiles[0, :, 3], quantiles[1, :, 3], color='gray')
                    line43.set_data(np.array(time)[np.array(index_pf)[
                                    1:]], pos_Mes*np.ones((len(index_pf[1:]))))

                if bt_tot.shape[1] > 4:
                    ax_5.collections.clear()
                    if EV:
                        line51EV.set_data(time, particles_mean_EV[:, 4])
        #                line51EV.set_data(time,particles_mean_EV[:,4], color=color_mean_EV)
                        if heavy_real_time_plot:
                            ax_5.fill_between(
                                time, quantiles_EV[0, :, 0], quantiles_EV[1, :, 4], color=color_quantile_EV)
                    line51.set_data(time, particles_mean[:, 4])
                    if heavy_real_time_plot:
                        ax_5.fill_between(
                            time, quantiles[0, :, 4], quantiles[1, :, 4], color='gray')
                    line53.set_data(np.array(time)[np.array(index_pf)[
                                    1:]], pos_Mes*np.ones((len(index_pf[1:]))))

                if bt_tot.shape[1] > 5:
                    ax_6.collections.clear()
                    if EV:
                        line61EV.set_data(time, particles_mean_EV[:, 5])
        #                line61EV.set_data(time,particles_mean_EV[:,5], color=color_mean_EV)
                        if heavy_real_time_plot:
                            ax_6.fill_between(
                                time, quantiles_EV[0, :, 5], quantiles_EV[1, :, 5], color=color_quantile_EV)
                    line61.set_data(time, particles_mean[:, 5])
                    if heavy_real_time_plot:
                        ax_6.fill_between(
                            time, quantiles[0, :, 5], quantiles[1, :, 5], color='gray')
                    line63.set_data(np.array(time)[np.array(index_pf)[
                                    1:]], pos_Mes*np.ones((len(index_pf[1:]))))

                if plot_ref == True:
                    line14.set_data(time_bt_tot[:lim], bt_tot[:lim, 0])
                    line24.set_data(time_bt_tot[:lim], bt_tot[:lim, 1])
                    if bt_tot.shape[1] > 2:
                        line34.set_data(time_bt_tot[:lim], bt_tot[:lim, 2])
                    if bt_tot.shape[1] > 3:
                        line44.set_data(time_bt_tot[:lim], bt_tot[:lim, 3])
                    if bt_tot.shape[1] > 4:
                        line54.set_data(time_bt_tot[:lim], bt_tot[:lim, 4])
                    if bt_tot.shape[1] > 5:
                        line64.set_data(time_bt_tot[:lim], bt_tot[:lim, 5])

                fig.canvas.draw()
                plt.pause(0.005)    
    
    
    del bt_tronc
    
    ##############################################################################################################
    #################################---TEST PLOTS---#############################################################

    plt.close('all')

    dt_tot = param['dt']
    N_test = param['N_test'] 
    if code_load_run:
        time = np.arange(bt_MCMC.shape[0])*float(dt_DNS)
        n_simu=1

    particles_mean = np.mean(bt_MCMC[:, :, :], axis=2)
    particles_median = np.median(bt_MCMC[:, :, :], axis=2)
    quantiles = np.quantile(bt_MCMC[:, :, :], q=[0.025, 0.975], axis=2)
    if EV:
        particles_mean_EV = np.mean(bt_forecast_EV[:, :, :], axis=2)
        particles_median_EV = np.median(bt_forecast_EV[:, :, :], axis=2)
        quantiles_EV = np.quantile(bt_forecast_EV[:, :, :], q=[
                                   0.025, 0.975], axis=2)
    n_particles = bt_MCMC.shape[-1]
#    particles_std_estimate = np.std(bt_MCMC[:,:,1:],axis=2)
#    erreur = np.abs(particles_mean-ref)

    for index in range(particles_mean.shape[1]):
        plt.figure(index, figsize=(12, 9))
        plt.ylim([-lim_fig[index], lim_fig[index]])
        if EV:
            plt.fill_between(
                time, quantiles_EV[0, :, index], quantiles_EV[1, :, index], color=color_quantile_EV)
            line1_EV = plt.plot(time, particles_mean_EV[:, index], '-',
                                color=color_mean_EV, label='EV particles mean', linewidth=linewidth_)
        plt.fill_between(
            time, quantiles[0, :, index], quantiles[1, :, index], color=color_quantile_LU)
        
        if plot_ref == True:
            if assimilate == 'real_data':
                plt.plot(time_bt_tot, quantiles_PIV[0, :, index],
                         'k--', label='True state', linewidth=linewidth_)
                plt.plot(time_bt_tot, quantiles_PIV[1, :, index],
                         'k--', label='True state', linewidth=linewidth_)
            else:
                plt.plot(time_bt_tot, bt_tot[:, index], 'k--',
                         label='True state', linewidth=linewidth_)

        line1 = plt.plot(time, particles_mean[:, index], '-', color=color_mean_LU,
                         label='Red LUM particles mean', linewidth=linewidth_)
     
        bt_diff = bt_tot.copy()
        bt_diff[:, index] = bt_diff[:, index]-particles_mean[::n_simu, index]
        #print ( "1) index="+str(index)+"=>"+str (bt_diff[:,index]))
        bt_diff[:, index] = np.power(np.power(bt_diff[:, index], 2.), 0.5)
        #print ( "2) index="+str(index)+"=>"+str (bt_diff[:,index]))
        plt.grid()
        plt.fill_between(time_bt_tot, bt_diff[:, index]-lim_fig[index], -lim_fig[index],
                         color='green', alpha=0.5, label='|Diff. bt_tot/particles_mean|')
        plt.grid()
        plt.ylabel('Chronos '+r'$b'+str(index+1)+'$'+' amplitude', fontsize=20)
        plt.xlabel('Time', fontsize=10)
        plt.legend(fontsize=10)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=10)
        path_img_name = Path(MORAANE_PATH)
        if code_ROM_from_matlab:
            plt.savefig(str(path_img_name)+"/diff_bt"+str(index+1) +
                        "_ROMmatlabA.png", dpi=200, transparent=False)
        else:
            plt.savefig(str(path_img_name)+"/diff_bt"+str(index+1) +
                        "_ROMcppA.png", dpi=200, transparent=False)
        plt.show()
        plt.grid()
        plt.plot(np.array(time)[np.array(index_pf)[1:]], pos_Mes *
                 np.ones((len(index_pf[1:]))), 'r.', linewidth=linewidth_)
        plt.grid()
        plt.ylabel('Chronos '+r'$b'+str(index+1)+'$'+' amplitude', fontsize=20)
        plt.xlabel('Time', fontsize=20)
        plt.legend(fontsize=20)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        file_res_mode = file_plots_res / Path(str(index+1) + '.pdf')
#            file_res_mode = file_plots_res / Path(str(index+1) + '.png')
#            file_res_mode = file_plots_res / Path(str(index+1) + '.jpg')
#            file_res_mode = file_plots_res / str(index) + '.png'
#            plt.savefig(file_res_mode)
        plt.savefig(file_res_mode, dpi=200)
#            plt.savefig(file_res_mode,dpi=500 )
#            plt.savefig(file_res_mode,quality = 95)

    if 'threshold_effect_on_tau_corrected' \
            in param['decor_by_subsampl']:
        param['decor_by_subsampl']['thrDtCorrect'] = \
            param['decor_by_subsampl']['threshold_effect_on_tau_corrected']
        del param['decor_by_subsampl']['threshold_effect_on_tau_corrected']
    else:
        param['decor_by_subsampl']['thrDtCorrect'] = False        
        
    dict_python = {}
    dict_python['param'] = param
    dict_python['time_bt_tot'] = time_bt_tot
    dict_python['bt_tot'] = bt_tot
    dict_python['quantiles_bt_tot'] = quantiles_PIV
    dict_python['dt_PIV'] = dt_PIV
    dict_python['index_pf'] = index_pf
    dict_python['time_DA'] = np.array(time)[np.array(index_pf)[1:]]
    dict_python['Re'] = Re
    dict_python['time'] = time
    dict_python['particles_mean'] = particles_mean
    dict_python['particles_median'] = particles_median
    dict_python['bt_MCMC'] = bt_MCMC
    dict_python['quantiles'] = quantiles
    if EV:
        dict_python['particles_mean_EV'] = particles_mean_EV
        dict_python['particles_median_EV'] = particles_median_EV
        dict_python['bt_forecast_EV'] = bt_forecast_EV
        dict_python['quantiles_EV'] = quantiles_EV
    file_res = file_plots_res / Path('chronos.mat')
    sio.savemat(file_res,dict_python)
    
    if EV:
        param['truncated_error2'] = param['truncated_error2'][0:(
            int(param['N_test']/n_simu)+1)]
        time = np.array(time)

        n_simu = 1
        N_ = particles_mean.shape[0]
        time = time[:N_:n_simu]
        index_time = (time <= time_bt_tot[-1])
        N_tot = np.sum(index_time)
        N_ = N_tot
        param['N_tot'] = N_tot
        param['N_test'] = N_tot-1

        struct_bt_MCMC = {}
        struct_bt_MCMC['mean'] = particles_mean\
            .copy()[:N_:n_simu]
        struct_bt_MCMC['var'] = np.var(bt_MCMC[:, :, :], axis=2)\
            .copy()[:N_:n_simu]
        struct_bt_MEV_noise = {}
        struct_bt_MEV_noise['mean'] = particles_mean_EV\
            .copy()[:N_:n_simu]
        struct_bt_MEV_noise['var'] = np.var(bt_forecast_EV[:, :, :], axis=2)\
            .copy()[:N_:n_simu]
        time = time[:N_:n_simu]
                
        bt_tot_interp = np.zeros(struct_bt_MCMC['mean'].shape)
        for index in range(bt_tot.shape[1]):
            interpolant_bt_tot_k = interpolate.interp1d(
                time_bt_tot, bt_tot[:, index])
            bt_tot_interp[:, index] = interpolant_bt_tot_k(time)
        interpolant_error = interpolate.interp1d(
            time_bt_tot, param['truncated_error2'][:, 0])
        param['truncated_error2'] = interpolant_error(time)
        param['truncated_error2'] = param['truncated_error2'][..., np.newaxis]

        plot_bt_dB_MCMC_varying_error_DA(file_plots_res,
                                         param, bt_tot_interp, struct_bt_MEV_noise, struct_bt_MCMC, time)

# diff using similar function as [plot_bt_dB_MCMC_varying_error_DA] without EV
# => Cf. [plot_bt_dB_MCMC_varying_error_DA_NoEV]
    if not EV:  # NULL value for [EV] part!              
        param['truncated_error2'] = param['truncated_error2'][0:(
            int(param['N_test']/n_simu)+1)]
        time = np.array(time)

        n_simu = 1
        N_ = particles_mean.shape[0]
        time = time[:N_:n_simu]
        index_time = (time <= time_bt_tot[-1])
        N_tot = np.sum(index_time)
        N_ = N_tot
        param['N_tot'] = N_tot
        param['N_test'] = N_tot-1

        struct_bt_MCMC = {}
        struct_bt_MCMC['mean'] = particles_mean\
            .copy()[:N_:n_simu]
        struct_bt_MCMC['var'] = np.var(bt_MCMC[:, :, :], axis=2)\
            .copy()[:N_:n_simu]
            
        time = time[:N_:n_simu]

        bt_tot_interp = np.zeros(struct_bt_MCMC['mean'].shape)
        for index in range(bt_tot.shape[1]):
            interpolant_bt_tot_k = interpolate.interp1d(
                time_bt_tot, bt_tot[:, index])
            bt_tot_interp[:, index] = interpolant_bt_tot_k(time)
 ##################### A CORRIGER ###########################
        if code_DATA_from_matlab:
            interpolant_error = interpolate.interp1d(
                time_bt_tot, param['truncated_error2'][:, 0])
            param['truncated_error2'] = interpolant_error(time)
            param['truncated_error2'] = param['truncated_error2'][..., np.newaxis]

            plot_bt_dB_MCMC_varying_error_DA_NoEV(file_plots_res,
                                                  param, bt_tot_interp, struct_bt_MCMC, time)
 ##################### A CORRIGER ###########################
        path_img_name = Path(MORAANE_PATH)
        if code_ROM_from_matlab:
            plt.savefig(str(path_img_name)+"/diff_bt_ROMmatlabB.png",
                        dpi=200, transparent=False)
        else:
            plt.savefig(str(path_img_name)+"/diff_bt_ROMcppB.png",
                        dpi=200, transparent=False)
        plt.show()
    
    # Time of execution
    print(choice_n_subsample)
    print('\n')
    print('Time of execution of PF & Red LUM for ' +
          str(SECONDS_OF_SIMU) + ' s of simulation:')
    print('\n')
    print(str(time_exe) + ' s')
    print('\n')
    if EV:
        print('Time of execution of PF & random EV for ' +
              str(SECONDS_OF_SIMU) + ' s of simulation:')
        print('\n')
        print(str(time_exe_EV) + ' s')
        print('\n')
        print('Ratio speed :')
        print('\n')
        print(str(100*time_exe_EV/time_exe) + ' %')
        print('\n')

    f_info.write(
        '\n------ RUN SUMMARY of [main_from_existing_ROM] function ------\n\n')
    f_info.write('\n  - Time of execution of PF & Red LUM for ' +
                 str(SECONDS_OF_SIMU) + 's of simulation : ' + str(time_exe) + ' s\n\n')
    if EV:
        f_info.write('  - Time of execution of PF & random EV for ' +
                     str(SECONDS_OF_SIMU) + 's of simulation : ' + str(time_exe_EV) + ' s\n')
        f_info.write('  - Ratio speed :\n' +
                     str(100*time_exe_EV/time_exe) + ' %\n\n')

    f_info.write('  - Files in Plot Folder : ' +
                 str(os.listdir(file_plots_res)) + ' \n\n')

    del C_deter
    del C_sto
    del L_deter
    del L_sto
    del I_deter
    del I_sto

    # closing INFO file
    
    f_info.close()

    # copying INFO file to file_plots_res
    file_info_copy = file_plots_res / Path('test.info')
    shutil.copyfile(str(file_info), str(file_info_copy))
    
    if plot_debug:
      for i in range(nb_modes+1):
        png_file = PATH_output / Path("mode"+str(i)+"_Ux.png")
        png_file_copy = file_plots_res / Path("mode"+str(i)+"_Ux.png")
        shutil.copyfile(str(png_file), str(png_file_copy))
        png_file = PATH_output / Path("mode"+str(i)+"_Uy.png")
        png_file_copy = file_plots_res / Path("mode"+str(i)+"_Uy.png")
        shutil.copyfile(str(png_file), str(png_file_copy))
      png_file = PATH_output / Path("mean_WAKE_Ux.png")
      png_file_copy = file_plots_res / Path("mean_WAKE_Ux.png")
      shutil.copyfile(str(png_file), str(png_file_copy))
      png_file = PATH_output / Path("mean_WAKE_Uy.png")
      png_file_copy = file_plots_res / Path("mean_WAKE_Uy.png")
      shutil.copyfile(str(png_file), str(png_file_copy))
      png_file = PATH_output / Path("diff_mean_WAKE_mode0_Ux.png")
      png_file_copy = file_plots_res / Path("diff_mean_WAKE_mode0_Ux.png")
      shutil.copyfile(str(png_file), str(png_file_copy))
      png_file = PATH_output / Path("diff_mean_WAKE_mode0_Uy.png")
      png_file_copy = file_plots_res / Path("diff_mean_WAKE_mode0_Uy.png")
      shutil.copyfile(str(png_file), str(png_file_copy))

    print('\n\nCf. files in directory : \n   ' + str(file_plots_res) + '\n\n')

    return 0  # var
