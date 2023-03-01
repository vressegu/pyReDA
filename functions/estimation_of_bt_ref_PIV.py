# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 16:28:29 2019

@author: matheus.ladvig
"""

#
import numpy as np
from sklearn import linear_model
import matplotlib.pyplot as plt
import scipy.io as sio
from pathlib import Path
import hdf5storage
import os
from convert_mat_to_python import convert_mat_to_python
#from pathlib import Path

Plot_error_bar = True

#                           DATASET 
#    type_data = 'incompact3D_noisy2D_40dt_subsampl_truncated'  #dataset to debug
type_data = 'DNS300_inc3d_3D_2017_04_02_NOT_BLURRED_blocks_truncated' # Reynolds 300
#    type_data = 'DNS100_inc3d_2D_2018_11_16_blocks_truncated'  # Reynolds 100
#switcher = {
#    'incompact3D_noisy2D_40dt_subsampl_truncated': [[1e-05],[False]],
#    'DNS100_inc3d_2D_2018_11_16_blocks_truncated': [[1e-06],[True]], # BEST
#    'turb2D_blocks_truncated': [[1e-05],[False,True]],
#    'incompact3d_wake_episode3_cut_truncated': [[1e-06],[False]],
#    'incompact3d_wake_episode3_cut': [[1e-06],[False]],
#    'LES_3D_tot_sub_sample_blurred': [[1e-03],[True]],
#    'inc3D_Re3900_blocks': [[1e-03],[True]],
#    'inc3D_Re3900_blocks_truncated': [[1e-03],[True]],
#    'DNS300_inc3d_3D_2017_04_02_NOT_BLURRED_blocks_truncated':[[1e-04],[True]] # BEST
#   
#}
##switcher.get(argument,[[0.0005],[False]])
## Get threshold and modal_dt
#threshold,modal_dt = switcher.get(type_data)
#threshold=threshold[0]
#modal_dt=modal_dt[0]
threshold = float('NaN')
modal_dt = 0
no_subampl_in_forecast = False 
plot_debug = False
data_assimilate_dim = 2
nb_modes = 2
switcher = {
'DNS300_inc3d_3D_2017_04_02_NOT_BLURRED_blocks_truncated': float(0.080833),
'DNS100_inc3d_2D_2018_11_16_blocks_truncated' : float(0.05625)
}
dt_PIV = switcher.get(type_data,[float('Nan')])
switcher = {
'DNS300_inc3d_3D_2017_04_02_NOT_BLURRED_blocks_truncated': 300 ,
'DNS100_inc3d_2D_2018_11_16_blocks_truncated': 100  
}
Re = switcher.get(type_data,[float('Nan')])
test_fct = 'b'
#svd_pchol = True
adv_corrected = False
choice_n_subsample = 'htgen'
#    choice_n_subsample = 'auto_shanon'
stochastic_integration = 'Ito'
estim_rmv_fv = True
eq_proj_div_free = 2
#adv_corrected = [False]
u_inf_measured = 0.388 
#number_of_PIV_files = 300
number_of_PIV_files = 4082


current_pwd = Path(__file__).parents[1] # Select the path
folder_results = current_pwd.parents[0].joinpath('resultats').joinpath('current_results') # Select the current results path
folder_data = current_pwd.parents[0].joinpath('data') # Select the data path
#param_ref['folder_results'] = str(folder_results) # Stock folder results path
#param_ref['folder_data'] = str(folder_data)       # Stock folder data path
#modal_dt_ref = modal_dt # Define modal_dt_ref
 


#%% Get data

# On which function the Shanon ctriterion is used
#    test_fct = 'b'  # 'b' is better than db
a_t = '_a_cst_' 

############################ Construct the path to select the model constants I,L,C,pchol and etc.

file = '1stresult_' + type_data + '_' + str(nb_modes) + '_modes_'  \
          + choice_n_subsample
if choice_n_subsample == 'auto_shanon' :
    file = file + '_threshold_' + str(threshold)
file = file + test_fct   
file = file + '_fullsto' # File where the ROM coefficients are save
#        file = '1stresult_' + type_data + '_' + str(nb_modes) + '_modes_' + \
#            choice_n_subsample + '_threshold_' + str(threshold) + test_fct   
#        file = file_save
file = file + '/'
if not adv_corrected:
    file = file + '_no_correct_drift'
file = file + '_integ_' + stochastic_integration
if estim_rmv_fv:
    file = file + '_estim_rmv_fv'
if eq_proj_div_free == 2:
    file = file + '_DFSPN'            
#    file_save = file
file = file + '.mat'
file_res = folder_results / Path(file)
    
#file = '1stresult_' + type_data + '_' + str(nb_modes) + '_modes_' + \
#        a_t + '_decor_by_subsampl_bt_decor_choice_' + choice_n_subsample 
#if choice_n_subsample == 'auto_shanon' :
#    file = file + '_threshold_' + str(threshold)
#file = file +'fct_test_' + test_fct    
##    file = '1stresult_' + type_data + '_' + str(nb_modes) + '_modes_' + \
##            a_t + '_decor_by_subsampl_bt_decor_choice_auto_shanon_threshold_' + str(threshold) + \
##            'fct_test_' + test_fct    
##    var_exits =  'var' in locals() or 'var' in globals()
##    period_estim = 'period_estim' in locals() or 'period_estim' in globals()
##    if var_exits == True and period_estim == True:
##        file = file + '_p_estim_' + str(period_estim);
#file = file + '_fullsto' # File where the ROM coefficients are save
#print(file)
##    file_save = file
#if not adv_corrected:
#    file = file + '_no_correct_drift'
#file = file + '.mat'
#file_res = folder_results / Path(file)
#if not os.path.exists(file_res):
#    file = '1stresult_' + type_data + '_' + str(nb_modes) + '_modes_'  \
#              + choice_n_subsample
#    if choice_n_subsample == 'auto_shanon' :
#        file = file + '_threshold_' + str(threshold)
#    file = file + test_fct   
#    file = file + '_fullsto' # File where the ROM coefficients are save
##        file = '1stresult_' + type_data + '_' + str(nb_modes) + '_modes_' + \
##            choice_n_subsample + '_threshold_' + str(threshold) + test_fct   
##        file = file_save
#    if not adv_corrected:
#        file = file + '/_no_correct_drift'
#    file_save = file
#    file = file + '.mat'
#    file_res = folder_results / Path(file)
#    if not os.path.exists(file_res):
#        
#        file = file_save + '/'
#        if not adv_corrected:
#            file = file + '_no_correct_drift'
#        file = file_save + '_integ_Ito'
#        
##        file = file_save + '_integ_Ito'
#        file = file + '.mat'
#        file_res = folder_results / Path(file)
    

#file = '1stresult_' + type_data + '_' + str(nb_modes) + '_modes_' + \
#        a_t + '_decor_by_subsampl_bt_decor_choice_' + choice_n_subsample + \
#        '_threshold_' + str(threshold) + \
#        'fct_test_' + test_fct    
##    file = '1stresult_' + type_data + '_' + str(nb_modes) + '_modes_' + \
##            a_t + '_decor_by_subsampl_bt_decor_choice_auto_shanon_threshold_' + str(threshold) + \
##            'fct_test_' + test_fct    
##    var_exits =  'var' in locals() or 'var' in globals()
##    period_estim = 'period_estim' in locals() or 'period_estim' in globals()
##    if var_exits == True and period_estim == True:
##        file = file + '_p_estim_' + str(period_estim);
#file = file + '_fullsto' # File where the ROM coefficients are save
#print(file)
##    file_save = file
#if not adv_corrected:
#    file = file + '_no_correct_drift'
#file = file + '.mat'
#file_res = folder_results / Path(file)
#if not os.path.exists(file_res):
#    file = '1stresult_' + type_data + '_' + str(nb_modes) + '_modes_'  \
#              + choice_n_subsample
#    if choice_n_subsample == 'auto_shanon' :
#        file = file + '_threshold_' + str(threshold)
#    file = file + test_fct   
#    file = file + '_fullsto' # File where the ROM coefficients are save
##        file = '1stresult_' + type_data + '_' + str(nb_modes) + '_modes_' + \
##            choice_n_subsample + '_threshold_' + str(threshold) + test_fct   
##        file = file_save
#    if not adv_corrected:
#        file = file + '\\_no_correct_drift'
#    file = file + '.mat'
#    file_res = folder_results / Path(file)
#print(file)

# The function creates a dictionary with the same structure as the Matlab Struct in the path file_res
I_sto,L_sto,C_sto,I_deter,L_deter,C_deter,plot_bts,pchol_cov_noises,bt_tot,param = convert_mat_to_python(str(file_res)) # Call the function and load the matlab data calculated before in matlab scripts.
param['decor_by_subsampl']['no_subampl_in_forecast'] = no_subampl_in_forecast                                           # Define the constant
diag_reg = np.sqrt(param['lambda'])
diag_reg = np.ones((diag_reg.shape)) 
#diag_reg = np.ones((nb_modes,1)) / diag_reg_inv


'''
Load HpivTopos and PIV
'''
#Hpiv_Topos = np.load('Hpiv_Topos.npy')

#      LOAD TOPOS
print('Loading H_PIV @ Topos...')
path_topos = Path(folder_data).parents[1].joinpath('data_PIV').\
        joinpath('mode_'+type_data+'_'+str(nb_modes)+'_modes_PIV') # Topos path 
topos_data = hdf5storage.loadmat(str(path_topos))                                                                 # Load topos
Hpiv_Topos = topos_data['phi_m_U']  
#topos = topos_data['phi_m_U']   
MX_PIV = topos_data['MX_PIV'].astype(int)
MX_PIV = tuple(map(tuple,MX_PIV))[0]
M_PIV = MX_PIV[0]*MX_PIV[1]
coordinates_x_PIV= topos_data['x_PIV_after_crop']
coordinates_y_PIV= topos_data['y_PIV_after_crop']
coordinates_x_PIV= np.reshape(coordinates_x_PIV,MX_PIV,order='F') 
coordinates_y_PIV= np.reshape(coordinates_y_PIV,MX_PIV,order='F') 
coordinates_x_PIV =  np.transpose(coordinates_x_PIV[:,0])  
coordinates_y_PIV = coordinates_y_PIV[0,:]   
Hpiv_Topos = np.transpose(Hpiv_Topos,(0,2,1))
#Hpiv_Topos = np.reshape(Hpiv_Topos,\
#                MX_PIV + tuple(np.array([data_assimilate_dim,(nb_modes+1)])),\
#                order='F') 
Hpiv_Topos = np.reshape(Hpiv_Topos,\
                tuple(np.array([M_PIV*data_assimilate_dim,(nb_modes+1)])),\
                order='F') 
##topos_new_coordinates = np.reshape(topos,\
##                          MX_PIV + tuple(np.array([data_assimilate_dim,(nb_modes+1)])),order='F') 
#Hpiv_Topos = np.reshape(topos_new_coordinates,\
#            (int(topos_new_coordinates.shape[0]*topos_new_coordinates.shape[1]*topos_new_coordinates.shape[2]),\
#             topos_new_coordinates.shape[3]),order='F') # The topos that we have estimated reshaped to posterior matrix multiplications

##mU=topos[:,-1,:]
#plt.figure(48)
##plt.imshow((np.reshape(mU,(202,74,2),order='F')[:,:,0]).T)
#plt.imshow((np.reshape(Hpiv_Topos[:,-1],(202,74,2),order='F')[:,:,0]).T)
#plt.colorbar()

#%%   Calculate Sigma for LS variance estimation
#if Plot_error_bar:
print('Loading Sigma')
if choice_n_subsample == 'auto_shanon' :
    threshold_ = str(threshold).replace('.', '_',)
    path_Sigma_inverse = Path(__file__).parents[3].joinpath('data').\
    joinpath('diffusion_mode_PIV_'+type_data+'_'+str(int(param['nb_modes']))\
             +'_modes_a_cst_threshold_'+ threshold_)  # Load Sigma_inverse
else:
    path_Sigma_inverse = Path(__file__).parents[3].joinpath('data').\
    joinpath('diffusion_mode_PIV_'+type_data+'_'+str(int(param['nb_modes']))\
         +'_modes_a_cst_threshold_NaN')  # Load Sigma_inverse
##    path_Sigma_inverse = Path(__file__).parents[3].joinpath('data_PIV').joinpath('HSigSigH_PIV_'+type_data+'_'+str(param['nb_modes'])+'_modes_a_cst_threshold_0_'+str(threshold)[2:])  # Load Sigma_inverse
Sigma_data = hdf5storage.loadmat(str(path_Sigma_inverse)) # Select Sigma_inverse
Sigma = Sigma_data['z_on_tau'][:,0,:,:]                             # Load Sigma inverse 
##### Transform this matrix in a square matrix
nb_points = Sigma.shape[0]                                                      # Number of points in the grid
nb_dim = Sigma.shape[1]            

#%% Load PIV
    

file = (Path(__file__).parents[3]).joinpath('data_PIV').joinpath('wake_Re'+str(Re)).joinpath('B'+str(1).zfill(4)+'.dat')   # The path to load PIV data
data = open(str(file))                                                                                                     # Open the PIV data  
datContent = [i.strip().split() for i in data.readlines()]                                                                 # Reading the data 
data = datContent[4:]                                                                                                      # Getting the data PIV

nb_lines = len(data)                           # lines amount
nb_collums = len(data[0][2:4])                 # Commumns amount 
matrix = np.zeros(shape=(nb_lines,nb_collums)) # Creating matrix to stock data 

'''
We will select the first data in 0.080833 and after we will load the files taking in account the factor of subsampling and the amount of files. 
'''
for i,line in enumerate(data):  # Select the data in the first PIV file 
    for j,number in enumerate(line[2:4]):
        matrix[i,j] = number

matrix_data_PIV_all_data = matrix[Sigma_data['mask'][:,0],:].copy()[np.newaxis,...] # Select the PIV data in the first mask calculated (The mask inside PIV and DNS)    
print('Loading PIV data: '+str(number_of_PIV_files)+' files...')

if number_of_PIV_files>1:
    for nb_file in range(1,(number_of_PIV_files+1),1)[1:]:                                                    # Loading the other files as defined in the start of this function
        print(nb_file)
        file = (Path(__file__).parents[3]).joinpath('data_PIV').\
        joinpath('wake_Re'+str(Re)).joinpath('B'+str(nb_file).zfill(4)+'.dat') # Path to file
        data = open(str(file))                                                                                                         # Open the file       
        datContent = [i.strip().split() for i in data.readlines()]                                                                     # Read the data                                                                                                                                                                              
        data = datContent[4:]                                                                                                          # Getting the data PIV 
        
        matrix = np.zeros(shape=(nb_lines,nb_collums)) # Define the matrix to stock the data  
        for i,line in enumerate(data):                 # Decode the information and save it as a matrix
            for j,number in enumerate(line[2:4]):
                matrix[i,j] = number
        
        matrix_data_PIV_all_data = np.concatenate((matrix_data_PIV_all_data,\
            matrix[Sigma_data['mask'][:,0],:].copy()[np.newaxis,...]),\
            axis=0)  # Save the matrix inside the matrix of all the PIV data

    
#file = (Path(__file__).parents[3]).joinpath('data_PIV').joinpath('wake_Re'+str(Re)).joinpath('B'+str(1).zfill(4)+'.dat')   # The path to load PIV data
#data = open(str(file))                                                                                                     # Open the PIV data  
#datContent = [i.strip().split() for i in data.readlines()]                                                                 # Reading the data 
#data = datContent[4:]                                                                                                      # Getting the data PIV
#
#nb_lines = len(data)                           # lines amount
#nb_collums = len(data[0][2:4])                 # Commumns amount 
#matrix = np.zeros(shape=(nb_lines,nb_collums)) # Creating matrix to stock data 
#
#'''
#We will select the first data in 0.080833 and after we will load the files taking in account the factor of subsampling and the amount of files. 
#'''
#for i,line in enumerate(data):  # Select the data in the first PIV file 
#    for j,number in enumerate(line[2:4]):
#        matrix[i,j] = number
#
#matrix_data_PIV_all_data = matrix.copy()[np.newaxis,...] # Select the PIV data in the first mask calculated (The mask inside PIV and DNS)    
#print('Loading PIV data: '+str(number_of_PIV_files)+' files...')
#
#if number_of_PIV_files>1:
#    for nb_file in range(1,(number_of_PIV_files+1),1)[1:]:                                                    # Loading the other files as defined in the start of this function
#        print(nb_file)
#        file = (Path(__file__).parents[3]).joinpath('data_PIV').\
#        joinpath('wake_Re'+str(Re)).joinpath('B'+str(nb_file).zfill(4)+'.dat') # Path to file
#        data = open(str(file))                                                                                                         # Open the file       
#        datContent = [i.strip().split() for i in data.readlines()]                                                                     # Read the data                                                                                                                                                                              
#        data = datContent[4:]                                                                                                          # Getting the data PIV 
#        
#        
#        matrix = np.zeros(shape=(nb_lines,nb_collums)) # Define the matrix to stock the data  
#        for i,line in enumerate(data):                 # Decode the information and save it as a matrix
#            for j,number in enumerate(line[2:4]):
#                matrix[i,j] = number
#        
#    
#        matrix_data_PIV_all_data = np.concatenate((matrix_data_PIV_all_data,\
#                                                   matrix.copy()[np.newaxis,...]),\
#        axis=0)  # Save the matrix inside the matrix of all the PIV data


# Normalizing  measured data
matrix_data_PIV_all_data = matrix_data_PIV_all_data/u_inf_measured  # Normalizing the PIV data to compare with DNS 
np.save('Data_piv.npy',matrix_data_PIV_all_data)                   # If necessary to save(This will be saved as numpy array in this folder.)



y = matrix_data_PIV_all_data

'''
Load PIV
'''
#path_y = Path(folder_data).parents[1].joinpath('data_PIV').\
#        joinpath('Data_piv.npy')
#y = np.load(path_y)[:4082,:]

'''
Reshape Piv data in order to compare with topos
'''
y = np.reshape(y,(y.shape[0],int(y.shape[1]*y.shape[2])),order='F')


'''
get error from PIV with average velocity
'''
y_less_average = y.copy() - Hpiv_Topos[...,-1].copy()


'''
Get the topos with chronos different from 1

n -> n-1
'''
Hpiv_Topos_otimization = Hpiv_Topos[:,:-1].copy()
for j in range(int(nb_modes)): 
    Hpiv_Topos_otimization[:,j] = Hpiv_Topos_otimization[:,j] / diag_reg[j]


'''
Find the best chronos in all piv data in this inverse problem.
'''
valeurs = np.zeros((y_less_average.shape[0],Hpiv_Topos_otimization.shape[1]))
for time in range(y.shape[0]):
    print(time)
    reg = linear_model.LinearRegression()
#    reg = linear_model.RidgeCV()
#    reg = linear_model.RidgeCV(alphas=np.logspace(-2.5, 2.5, 30))
    reg.fit(Hpiv_Topos_otimization,y_less_average[time,...].T)       
#    reg.fit(Hpiv_Topos_otimization,y[time:time+1,...].T)       
    valeurs[time,:] = reg.coef_
for j in range(int(nb_modes)): 
    valeurs[:,j] = valeurs[:,j] * diag_reg[j]


#%%   Calculate Sigma for LS variance estimation
if Plot_error_bar:
    pinv_Hpiv = np.linalg.pinv(Hpiv_Topos_otimization.copy())
    cov = np.zeros((int(nb_modes),int(nb_modes)))
    # Calculating necessary matrices
    #K = np.zeros((int(nb_dim),int(nb_modes+1),int(nb_points)))
    Sigma = np.transpose(Sigma,(1,2,0))
    pinv_Hpiv = np.reshape(pinv_Hpiv,(int(nb_modes),int(nb_points),int(nb_dim)),order='F') 
    pinv_Hpiv = np.transpose(pinv_Hpiv,(0,2,1))
    for line in range(int(nb_points)):                                                  # To all spatial samples we create the first part of the matrix that contains the correlation of Vx
        cov = cov + \
            pinv_Hpiv[:,:,line] @ Sigma[:,:,line] @ pinv_Hpiv[:,:,line].T
    #K = np.transpose(K,(2,0,1)) # ((nb_points),(nb_dim),(nb_modes+1),)
    #K = np.reshape(K,(int(nb_points*nb_dim),int(nb_modes+1)),order='F') 
    #Hpiv_Topos = np.transpose(Hpiv_Topos,(2,0,1)) # ((nb_points),(nb_dim),(nb_modes+1),)
    #Hpiv_Topos = np.reshape(Hpiv_Topos,(int(nb_points*nb_dim),int(nb_modes+1)),order='F') 
    #Sigma_inverse = np.transpose(Sigma_inverse,(2,0,1))  # ((nb_points),(nb_dim),(nb_dim),)
    for i in range(int(nb_modes)): 
        for j in range(int(nb_modes)): 
            cov[i,j] = cov[i,j] * diag_reg[i] * diag_reg[j]
    estim_err = 1.96*np.sqrt(np.diag(cov))
    estim_err = np.tile( np.reshape(estim_err,(1,nb_modes)) ,(valeurs.shape[0],1 ))
    quantiles = np.zeros((2,valeurs.shape[0],valeurs.shape[1]))
    quantiles[0,:,:] = valeurs - estim_err
    quantiles[1,:,:] = valeurs + estim_err
    
for j in range(int(nb_modes)): 
    Hpiv_Topos_otimization[:,j] = Hpiv_Topos_otimization[:,j] * diag_reg[j]


'''
Plot the result for the chronos found
'''
t = np.arange(0,valeurs.shape[0]*dt_PIV,dt_PIV)
for i in range(valeurs.shape[1]):
    plt.figure()
    plt.plot(t,valeurs[:,i])
    if Plot_error_bar:
        plt.fill_between(t,quantiles[0,:,i],quantiles[1,:,i],color='gray')



'''
Compare the error in the time average PIV flow with the average topos(-> Hpiv[-1])
'''
average_time_value_PIV = np.mean(y,axis=0)
error = Hpiv_Topos[:,-1].copy() - average_time_value_PIV.copy()
error_reshaped = np.reshape(error,(202,74,2),order='F')

# PLOT


#Plot of the average flow for both
plt.figure(21)
plt.imshow((np.reshape(Hpiv_Topos[:,-1],(202,74,2),order='F')[:,:,0]).T)
plt.colorbar()
plt.figure(22)
plt.imshow((np.reshape(Hpiv_Topos[:,-1],(202,74,2),order='F')[:,:,1]).T)
plt.colorbar()
plt.figure(23)
plt.imshow((np.reshape(average_time_value_PIV,(202,74,2),order='F')[:,:,0]).T)
plt.colorbar()
plt.figure(24)
plt.imshow((np.reshape(average_time_value_PIV,(202,74,2),order='F')[:,:,1]).T)
plt.colorbar()


plt.figure(31)
plt.imshow(error_reshaped[:,:,0].T)
plt.colorbar()
plt.figure(32)
plt.imshow(error_reshaped[:,:,1].T)
plt.colorbar()

'''
The Chronos found here need to be saved and will be necessary to evaluate the particle filterning
'''


dict_python = {}
dict_python['Hpiv_Topos_x'] = np.reshape(Hpiv_Topos[:,-1],(202,74,2),order='F')[:,:,0]
dict_python['Hpiv_Topos_y'] = np.reshape(Hpiv_Topos[:,-1],(202,74,2),order='F')[:,:,1]
dict_python['average_time_value_PIV_x'] = np.reshape(average_time_value_PIV,(202,74,2),order='F')[:,:,0]
dict_python['average_time_value_PIV_y'] = np.reshape(average_time_value_PIV,(202,74,2),order='F')[:,:,1]
dict_python['bt_tot_PIV'] = valeurs
dict_python['dt_PIV'] = dt_PIV
dict_python['Re'] = Re
dict_python['quantiles_PIV'] = quantiles

file = (Path(__file__).parents[3]).joinpath('data_PIV').joinpath('bt_tot_PIV_Re'+str(dict_python['Re'])+'_n'+str(nb_modes)+'.mat')
#data = hdf5storage.loadmat(str(file))
sio.savemat(file,dict_python)




















