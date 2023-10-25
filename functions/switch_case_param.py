# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 07:51:46 2022 : from original [main_from_existing_ROM.py] file

@author: laurence.wallian
"""

# VAR DEFINED

# A) With [switch_case] :
#    
#  1) subsampling_PIV_grid_factor_gl :
#      Subsampling constant that will be applied in the observed data, 
#      (i.e if 3 we will take 1 point in 3)

#  2) nbPoints_x_gl :
#      Number of points that we will take in account in the observed grid. 
#      Therefore, with this two parameters we can select any possible subgrid 
#      inside the original PIV/DNS grid to observe.
#      Example : if nbPoints_x_gl=70, 
#                then nbPoints_x <= (202 - x0_index) /subsampling_PIV_grid_factor

#  3) nbPoints_y_gl :
#      Number of points that we will take in account in the observed grid. 
#      Therefore, with this two parameters we can select any possible subgrid 
#      inside the original PIV/DNS grid to observe.
#      Example : if nbPoints_y_gl=30, 
#                then nbPoints_y <= (74 - y0_index) /subsampling_PIV_grid_factor

#  4) assimilation_period :
#      Example : if  assimilation_period=float(5/10),
#                then factor_of_PIV_time_subsampling_gl = int(5/10 / dt_PIV)

# B) With [default_param] : Cf. matlab parameters file
#  
  
import numpy as np

##################################################################################################
# defining case
def switch_case(case_number):
  
  # default values :
  subsampling_PIV_grid_factor_gl = 3
  nbPoints_x_gl = 1
  nbPoints_y_gl = 1 
  assimilation_period = float(5/10)
    
  if case_number == 1 or \
     case_number == 3 or \
     case_number == 4 or \
     case_number == 5 or \
     case_number == 6 :
    subsampling_PIV_grid_factor_gl = 3
    nbPoints_x_gl = 1
    nbPoints_y_gl = 1
    assimilation_period = float(5/10)
    
  #if case_number == 7:
  if case_number == 2:
    subsampling_PIV_grid_factor_gl = 30
    nbPoints_x_gl = 3
    nbPoints_y_gl = 3
    assimilation_period = float(5/10)
    
  if case_number == 102:
    subsampling_PIV_grid_factor_gl = 3
    nbPoints_x_gl = 3
    nbPoints_y_gl = 3
    assimilation_period = float(5)
    
  #if case_number=10 = case_number=3:
    
  if case_number == 103:
    subsampling_PIV_grid_factor_gl = 10
    nbPoints_x_gl = 3
    nbPoints_y_gl = 3
    assimilation_period = float(5/10)
    
  #if case_number=8 = case_number=4
    
  if case_number == 104:
    subsampling_PIV_grid_factor_gl = 10
    nbPoints_x_gl = 3
    nbPoints_y_gl = 3
    assimilation_period = float(5/20)
    
  #if case_number=9 = case_number=5
    
  if case_number == 105:
    subsampling_PIV_grid_factor_gl = 3
    nbPoints_x_gl = 10
    nbPoints_y_gl = 10
    assimilation_period = float(5/10)
    
  if case_number == 11:
    subsampling_PIV_grid_factor_gl = 10
    nbPoints_x_gl = 7
    nbPoints_y_gl = 7
    assimilation_period = float(5/10)
    
  if case_number == "Case_Full":
    subsampling_PIV_grid_factor_gl = 3
    nbPoints_x_gl = 67
    nbPoints_y_gl = 24
    assimilation_period = float(5/10)
    
  if case_number == "Case_MegaFull":
    subsampling_PIV_grid_factor_gl = 1
    nbPoints_x_gl = 202
    nbPoints_y_gl = 74
    assimilation_period = float(5/10)
    
##factor_of_PIV_time_subsampling_gl = int(5 / 0.080833)
   
  print("\nCase = "+str(case_number)+":\n") 
  print("  subsampling_PIV_grid_factor_gl="+str(subsampling_PIV_grid_factor_gl))
  print("  nbPoints_x_gl="+str(nbPoints_x_gl))
  print("  nbPoints_y_gl="+str(nbPoints_y_gl))
  print("  assimilation_period="+str(assimilation_period))
  print('\n')
 
  return subsampling_PIV_grid_factor_gl, nbPoints_x_gl, nbPoints_y_gl, assimilation_period

##################################################################################################
# defining default param like in matlab parameter file
def default_param ( code ):
  
  param_dict = {}
  
  # param_dict['a_time_dependant'] = False
  # param_dict['adv_corrected'] = 1.0
  # param_dict['big_data'] = True
  # param_dict['C_deter_residu'] = np.zeros((2,2))
  # param_dict['coef_correctif_estim'] = {'learn_coef_a':False}
  # param_dict['d'] = 3.0
  # param_dict['d'] = 3
  
  # param_dict['data_in_blocks'] = {
  #   "bool":True,
  #   "len_blocks":16.0,
  #   "nb_blocks":80.0,
  #   "type_data2":'nan',
  #   "type_whole_data":'DNS300_inc3d_3D_2017_04_02_NOT_BLURRED_blocks_truncated'
  # }

  param_dict['decor_by_subsampl'] = {}
  # param_dict['decor_by_subsampl'] = {
  #   "bool":True,
  #   "choice_n_subsample":'htgen2',
  #   "meth":'bt_decor',
  #   "n_subsampl_decor":3.0,
  #   "no_subampl_in_forecast":False,
  #   "spectrum_threshold":'nan',
  #   "tau_corr":3.277349411005344,
  #   "test_fct":'b'
  # }
  
  # param_dict['dt'] = 0.75 
  # param_dict['dX'] = (0.0416667,0.0416667,0.0413158)  
  # param_dict['eq_proj_div_free'] = 2.0
  # param_dict['estim_rmv_fv'] = True
  # param_dict['folder_data'] = 'F:\MATLAB\RedLUM/data/'
  # param_dict['folder_file_U_temp'] = 'F:\MATLAB\RedLUM/data/folder_file_temp_DNS300_inc3d_3D_2017_04_02_NOT_BLURRED_blocks_truncated_2_modes__a_cst__decor_by_subsampl_bt_decor_choice_htgen2_threshold_NaNfct_test_b/'
  # param_dict['folder_results'] = 'F:\MATLAB\RedLUM\Gitlab_SCALIAN/resultats/current_results/'
  # param_dict['grid'] = np.zeros(3,)
  # param_dict['igrida'] = False
  # param_dict['lambda'] = (8.94353,8.57639)
  # param_dict['M'] = 3110984.0
  # param_dict['modified_Re'] = False
  # param_dict['MX'] = np.zeros(3,)
  # param_dict['N_test'] = 426.0
  # param_dict['N_tot'] = 427.0
  # param_dict['name_file_1st_result'] = 'F:\MATLAB\RedLUM\Gitlab_SCALIAN/resultats/current_results/1stresult_DNS300_inc3d_3D_2017_04_02_NOT_BLURRED_blocks_truncated_2_modes_htgen2b_fullsto/_integ_Ito_estim_rmv_fv_DFSPN.mat'
  # param_dict['name_file_diffusion_mode'] = 'F:\MATLAB\RedLUM/data/diffusion_mode_DNS300_inc3d_3D_2017_04_02_NOT_BLURRED_blocks_truncated_2_modes_a_cst_meth_htgen2.mat'
  # param_dict['name_file_mode'] = 'F:\MATLAB\RedLUM/data/mode_DNS300_inc3d_3D_2017_04_02_NOT_BLURRED_blocks_truncated_2_modes.mat'
  # param_dict['name_file_noise_cov'] = 'F:\MATLAB\RedLUM/data/noise_cov_DNS300_inc3d_3D_2017_04_02_NOT_BLURRED_blocks_truncated_2_modesmeth_htgen2_estim_rmv_fv_DFSPN.mat'
  # param_dict['name_file_pre_c_blurred'] = 'D:\/data/DNS300_inc3d_3D_2017_04_02_NOT_BLURRED_blocks_truncated_pre_c'
  # param_dict['name_file_U_centered'] = np.zeros(80,)
  # param_dict['name_file_U_temp'] = np.zeros(80,)
  # param_dict['nb_modes'] = 2.0
  # param_dict['normalized'] = True
  # param_dict['rho0'] = 1000.0
  # param_dict['save_all_bi'] = False
  # param_dict['save_before_subsampling'] = True
  # param_dict['type_data'] = 'DNS300_inc3d_3D_2017_04_02_NOT_BLURRED_blocks_truncated'
  # param_dict['visosity'] = 0.0033333333333333335
  
  return param_dict.copy()

##################################################################################################
#  (left,top) observation point position just below (xObs,yObs)*Dcyl (with (0,0)=cylinder center)
def Left_Top_PtObs( xObs, yObs, coordinates_x_PIV, coordinates_y_PIV ):
    x0_index = 0
    dx_min = xObs
    y0_index = 0
    dy_max = yObs
        
    dx = 0.
    while dx<dx_min:
        x0_index=x0_index+1
        dx=coordinates_x_PIV[x0_index]
        dx=np.sqrt(dx*dx) 
    x0_index=x0_index-1
    
    dy = 1000.
    while dy>dy_max:
        y0_index=y0_index+1
        dy=coordinates_y_PIV[y0_index]
        dy=np.sqrt(dy*dy)
    y0_index=y0_index
    
    print("Indexes of Left Top OBS point near P("+str(xObs)+","+str(yObs)+") are ("+str(x0_index)+","+str(y0_index)+")")
    print("   (You can change the value of xObs and yObs in [run_info.txt] to choose another point)\n")
  
    return x0_index, y0_index
