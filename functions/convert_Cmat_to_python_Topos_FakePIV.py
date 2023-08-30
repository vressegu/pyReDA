# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 07:51:46 2022 : DATA and ROM from C++

@author: laurence.wallian
"""

# VAR DEFINED

# A) convert_Cmat_to_python_Time :
#     truncated_error2=0
#     bt_tot

# B) convert_Cmat_to_python_Topos :
#     topos, Sigma_inverse
#     MX_PIV
#     coordinates_x_PIV
#     coordinates_y_PIV

# C) convert_Cmat_to_python_FakePIV :

import numpy as np
from pathlib import Path
import os

import re # for grep search in param file

##################################################################################################
# search "-v" sequencies in [redlumcpp_code_version] and keep last part of the word 
def recentROM ( redlumcpp_code_version, first_digit, second_digit ):
    
   ROM_name = redlumcpp_code_version
   ROM_name = re.sub('-v', ' ', ROM_name)
   ROM_split = ROM_name.split(' ')
   ROM_release = ROM_split[1]
   bool_recentROM = (len(ROM_release)>=2)
   if bool_recentROM:
       bool_recentROM = ( (ROM_release[0].isdigit()) 
                         & (ROM_release[2].isdigit()) )
   if bool_recentROM:
       bool_recentROM = ( (int(ROM_release[0])>=first_digit) 
                          & (int(ROM_release[2])>=second_digit) )    
   return bool_recentROM

##################################################################################################
# defining indexes for cropping (index_XY_PIV), coordinates_x_PIV, coordinates_y_PIV and MX_PIV
def convert_Cmat_to_python_cropZone(PARAM):
    
    PATH_DATA = PARAM.PATH_DATA
    PATH_ROM_PIV = PARAM.PATH_ROM_PIV
    x1_PIV = PARAM.x1_PIV
    x2_PIV = PARAM.x2_PIV
    x0_cyl = PARAM.x0_cyl
    y1_PIV = PARAM.y1_PIV
    y2_PIV = PARAM.y2_PIV
    y0_cyl = PARAM.y0_cyl
    diam_cyl = PARAM.diam_cyl

    # mean = mode 0    
    topos_file = PATH_ROM_PIV.joinpath(Path('mean/1/B0001_new.dat'))
    if topos_file.exists():
    #if Path(topos_modes_file).is_file():
        f_topos = open(topos_file,'r')
        nb_line = 0
        nb_y=1
        while True:
          line = f_topos.readline()
          if not line: 
            break
          else:   
            if nb_line > 3:
                a = np.fromstring(line, dtype=float, sep=' ')
                y = a[1]
                if nb_line==4:
                    y0 = y
                if y != y0:
                    nb_y=nb_y+1
                y0=y
            nb_line=nb_line+1    
        f_topos.close() 
        
        nb_x=int((nb_line-4)/nb_y)
        MX_PIV_all=(nb_x,nb_y)
        
        X_PIV=np.zeros(nb_x)
        Y_PIV=np.zeros(nb_y)
        
        f_topos = open(topos_file,'r')
        nb_line = 0
        n_X_PIV = int(0)
        index1_X_PIV = int(0) # first index for crop 
        index2_X_PIV = int(0) # last index for crop 
        code_x = 0
        i = 0
        while True:
          line = f_topos.readline()
          if not line: 
            break
          else:            
            if nb_line > 3 and nb_line<=nb_x+3:
                a = np.fromstring(line, dtype=float, sep=' ')
                dx = float(a[0]) -float(x0_cyl)/float(diam_cyl)
                if (dx-x1_PIV)*(dx-x2_PIV)<0.:
                    if code_x==0:
                        code_x=1
                        index1_X_PIV=n_X_PIV
                    if code_x==1:
                        index2_X_PIV=n_X_PIV
                n_X_PIV=n_X_PIV+1
            nb_line=nb_line+1    
        f_topos.close() 
        
        x_topos_modes=np.zeros(index2_X_PIV-index1_X_PIV+1)
        f_topos = open(topos_file,'r')
        nb_line = 0
        n_X_PIV = int(0)
        i=int(0)
        while True:
          line = f_topos.readline()
          if not line: 
            break
          else:            
            if nb_line > 3 and nb_line<=nb_x+3:
                a = np.fromstring(line, dtype=float, sep=' ')
                if (n_X_PIV-index1_X_PIV)*(n_X_PIV-index2_X_PIV)<=0:
                    x_topos_modes[i]=a[0]
                    i=i+1
                n_X_PIV=n_X_PIV+1
            nb_line=nb_line+1    
        f_topos.close() 
        
        n_X_PIV=index2_X_PIV-index1_X_PIV+1
        
        # y coordinate
        f_topos = open(topos_file,'r')
        nb_line = 0
        n_Y_PIV = int(0)
        index1_Y_PIV = int(0) # first index for crop 
        index2_Y_PIV = int(0) # last index for crop 
        code_y = 0
        while True:
          line = f_topos.readline()
          if not line: 
            break
          else:            
            if nb_line > 3 and (nb_line-4)%nb_x==0:
                a = np.fromstring(line, dtype=float, sep=' ')
                dy = float(a[1]) -float(y0_cyl)/float(diam_cyl)
                if (dy-y1_PIV)*(dy-y2_PIV)<0.:
                    if code_y==0:
                        code_y=1
                        index1_Y_PIV=n_Y_PIV
                    if code_y==1:
                        index2_Y_PIV=n_Y_PIV
                n_Y_PIV=n_Y_PIV+1
            nb_line=nb_line+1    
        f_topos.close()         
        
        y_topos_modes=np.zeros(index2_Y_PIV-index1_Y_PIV+1)
        f_topos = open(topos_file,'r')
        nb_line = 0
        n_Y_PIV = int(0)
        i=int(0)
        while True:
         line = f_topos.readline()
         if not line: 
           break
         else:            
           if nb_line > 3 and (nb_line-4)%nb_x==0:
               a = np.fromstring(line, dtype=float, sep=' ')
               if (n_Y_PIV-index1_Y_PIV)*(n_Y_PIV-index2_Y_PIV)<=0:
                    y_topos_modes[i]=a[1]
                    i=i+1
               n_Y_PIV=n_Y_PIV+1
           nb_line=nb_line+1    
        f_topos.close() 
        
        n_Y_PIV=index2_Y_PIV-index1_Y_PIV+1

    # adim
    for i in range (n_X_PIV):
        x_topos_modes[i]=float(x_topos_modes[i]) -float(x0_cyl)/float(diam_cyl)
             
    for i in range (n_Y_PIV):
        y_topos_modes[i]=float(y_topos_modes[i]) -float(y0_cyl)/float(diam_cyl)
    
    # X and Y coordinates after crop
    coordinates_x_PIV = x_topos_modes     
    coordinates_y_PIV = y_topos_modes     
    
    # MX_PIV after crop = tuple
    MX_PIV=(n_X_PIV,n_Y_PIV)
    
    # crop indexes
    index_XY_PIV=(index1_X_PIV, index2_X_PIV, index1_Y_PIV, index2_Y_PIV)
                
    # print("file mean=mode0="+str(topos_file)+' => '+str(MX_PIV_all))
    
    # print("index_X=["+str(index1_X_PIV)+":"+str(index2_X_PIV)+"] index_Y=["+str(index1_Y_PIV)+":"+str(index2_Y_PIV)+"]")
    
    return MX_PIV_all, MX_PIV, index_XY_PIV, coordinates_x_PIV, coordinates_y_PIV

##################################################################################################
# defining lambda
def convert_Cmat_to_python_lambda(PARAM):
    
    nb_modes = PARAM.nb_modes
    PATH_ROM = PARAM.PATH_ROM
    t0_learningBase = PARAM.t0_learningBase
    t1_learningBase = PARAM.t1_learningBase
    dt_DNS = PARAM.dt_DNS
    redlumcpp_code_version = os.path.basename(os.path.normpath(PATH_ROM.parents[0]))
    # bool_npy = (len(redlumcpp_code_version)>=8) 
    # if bool_npy:
    #     bool_npy = ( (redlumcpp_code_version[5].isdigit()) 
    #                & (redlumcpp_code_version[7].isdigit()) )
    # if bool_npy:
    #     bool_npy = ( (int(redlumcpp_code_version[5])>=3) 
    #                  & (int(redlumcpp_code_version[7])>=1) )
    bool_npy = recentROM( redlumcpp_code_version, 3, 1 )
    if bool_npy:
        file_format = "npy"
    else:
        file_format = "txt"

    lambda_values = np.zeros(nb_modes)
    print("data=f(C++) => lambda=f(ITHACAoutput/temporalModes_*modes")
    # PATH_media = '/media/laurence.wallian/WD_Ressegui/Boulot/'
    # PATH_bt = PATH_media+'RedLUM/RedLum_from_OpenFoam/RedLum_D1_Lz1pi_Re'+str(int(Re))+'/'
    # print("PATH_bt="+str(PATH_bt))
    
    if (file_format=="npy"):
        N_t = int((t1_learningBase-t0_learningBase)/dt_DNS)+1
        bt_file = PATH_ROM.joinpath(Path('temporalModes_'+str(nb_modes)+'modes/U.npy'))
        bt = np.load(bt_file)
        for i in range(N_t):
            for j in range(nb_modes):
                lambda_values[j] = lambda_values[j] + bt[i,j]**2
        
    elif (file_format=="txt"):
        bt_file = PATH_ROM.joinpath(Path('temporalModes_'+str(nb_modes)+'modes/U_mat.txt'))
        
        print("bt_file="+str(bt_file))
        if bt_file.exists():
            f_bt = open(bt_file, 'r')
            N_t = 0
            t = t0_learningBase
            while True:
                line = f_bt.readline()
                if not line:
                    break
                else:
                    if t >= t0_learningBase and t < t1_learningBase:
                        a = np.fromstring(line, dtype=float, sep=' ')
                        for j in range(len(a)):
                            lambda_values[j] = lambda_values[j]+a[j]*a[j]
                        t = t+dt_DNS
                        N_t = N_t+1
            f_bt.close()
        else:
            print('ERROR: File does not exist ', str(bt_file))
            return 0
        
    else:
        print('ERROR: File format does not exist ', file_format)
        return 0    
    
    for n in range(nb_modes):
        lambda_values[n] = lambda_values[n]/float(N_t)

    return lambda_values

##################################################################################################
# defining bt_tot
def convert_Cmat_to_python_bt_tot(PARAM):
    
    nb_modes = PARAM.nb_modes
    PATH_ROM = PARAM.PATH_ROM
    t0_testBase = PARAM.t0_testBase
    t1_testBase = PARAM.t1_testBase
    dt_DNS = PARAM.dt_DNS
    redlumcpp_code_version = os.path.basename(os.path.normpath(PATH_ROM.parents[0]))
    # bool_npy = (len(redlumcpp_code_version)>=8) 
    # if bool_npy:
    #     bool_npy = ( (redlumcpp_code_version[5].isdigit()) 
    #                & (redlumcpp_code_version[7].isdigit()) )
    # if bool_npy:
    #     bool_npy = ( (int(redlumcpp_code_version[5])>=3) 
    #                  & (int(redlumcpp_code_version[7])>=1) )
    bool_npy = recentROM( redlumcpp_code_version, 3, 1 )    
    if bool_npy:
        file_format = "npy"
    else:
        file_format = "txt"

    bt_tot = np.zeros((int((t1_testBase-t0_testBase)/dt_DNS)+1, nb_modes))
    truncated_error2 = np.zeros((int((t1_testBase-t0_testBase)/dt_DNS)+1,1))
    print('bt_tot:'+str(bt_tot.shape))
    print("data=f(C++) => bt_tot=f(ITHACAoutput/temporalModesSimulation_*modes)")
    print("data=f(C++) => truncated_error=0")
    
    if (file_format=="npy"):
        bt_tot_file = PATH_ROM.joinpath(
            Path('temporalModesSimulation_'+str(nb_modes)+'modes/U.npy'))
        bt_tot = np.load(bt_tot_file)
    elif (file_format=="txt"):
        bt_tot_file = PATH_ROM.joinpath(
            Path('temporalModesSimulation_'+str(nb_modes)+'modes/U_mat.txt'))
        print("bt_tot_file="+str(bt_tot_file))
        if bt_tot_file.exists():
            f_bt_tot = open(bt_tot_file, 'r')
            i = 0
            while True:
                line = f_bt_tot.readline()
                if not line:
                    break
                else:
                    a = np.fromstring(line, dtype=float, sep=' ')
                    for j in range(len(a)):
                        bt_tot[i][j] = a[j]
                    i = i+1
            f_bt_tot.close()
        else:
            print('ERROR: File does not exist ', str(bt_tot_file))
            return 0
    else:
        print('ERROR: File format does not exist ', file_format)
        return 0

    return truncated_error2, bt_tot


##################################################################################################
# defining bt_MCMC
def convert_Cmat_to_python_bt_MCMC(PARAM, n_simu, n_particles,pathHilbertSpace, bool_PFD):
    
    nb_modes = PARAM.nb_modes
    PATH_ROM = PARAM.PATH_ROM
    print(PARAM.PATH_ROM)
    t0_testBase = PARAM.t0_testBase
    t1_testBase = PARAM.t1_testBase
    dt_DNS = PARAM.dt_DNS
    dt_run = PARAM.dt_DNS / n_simu
    redlumcpp_code_version = os.path.basename(os.path.normpath(PATH_ROM.parents[0])) 
    # bool_npy = (len(redlumcpp_code_version)>=8)     
    # if bool_npy:
    #     bool_npy = ( (redlumcpp_code_version[5].isdigit()) 
    #                & (redlumcpp_code_version[7].isdigit()) )
    # if bool_npy:
    #     bool_npy = ( (int(redlumcpp_code_version[5])>=3) 
    #                  & (int(redlumcpp_code_version[7])>=1) )
    bool_npy = recentROM( redlumcpp_code_version, 3, 1 )
    if bool_npy:
        file_format = "npy"
    else:
        file_format = "txt"
        
    bt_temp = np.zeros((int((t1_testBase-t0_testBase)/dt_DNS)+1, nb_modes))
    bt_MCMC = np.tile(bt_temp, (n_particles, 1, 1))
    bt_MCMC= np.transpose(bt_MCMC, (1, 2, 0))  
    # print('bt_MCMC:'+str(bt_MCMC.shape))

    file = 'Reduced_coeff_'+str(nb_modes)+'_'+str(dt_run)+ \
          '_'+str(int(n_particles))
    if (bool_PFD==True):
        file = file + '_fullOrderPressure'
    elif (bool_PFD==False):
        file = file + '_neglectedPressure'
    elif (bool_PFD==2):
        file = file + '_reducedOrderPressure'
    else:
        print('ERROR: unknown case: bool_PFD =', str(bool_PFD))
        return 0
    file = file + pathHilbertSpace
    if bool_npy:
        file = file + '_centered'
    file = file + '/approx_temporalModes_U_'
    for k in range(n_particles): 
        if (file_format=="npy"):
            bt_temp_file = PATH_ROM.joinpath(Path(file +str(k)+'.npy'))
            bt_temp = np.load(bt_temp_file)
            print("bt_temp_file="+str(bt_temp_file))
        elif (file_format=="txt"):
            bt_temp_file = PATH_ROM.joinpath(Path(file +str(k)+'_mat.txt'))
            print("bt_temp_file="+str(bt_temp_file))
            if bt_temp_file.exists():
                f_bt_temp = open(bt_temp_file, 'r')
                i = 0
                while True:
                    line = f_bt_temp.readline()
                    if not line:
                        break
                    else:
                        a = np.fromstring(line, dtype=float, sep=' ')
                        for j in range(len(a)):
                            bt_temp[i][j] = a[j]
                        i = i+1
                f_bt_temp.close()
            else:
                print('ERROR: File does not exist ', str(bt_temp_file))
                return 0
        else:
            print('ERROR: File format does not exist ', file_format)
            return 0
        bt_MCMC[:,:,k]=bt_temp

    return bt_MCMC



def convert_Cmat_to_python_Topos(MX_PIV_all, index_XY_PIV, data_assimilate_dim_str, PARAM):
     
    data_assimilate_dim=int(data_assimilate_dim_str)
    
    nb_modes = PARAM.nb_modes
    PATH_ROM = PARAM.PATH_ROM
    PATH_ROM_PIV = PARAM.PATH_ROM_PIV
    
    print("\n\ndata=f(C++) => mode0=f(ITHACAoutput/mean)")
    print("data=f(C++) => modei=f(ITHACAoutput/spatialModes_*modes)")
        
    # modes : mean=mode0, ...    
    
    n_xy_PIV_all=int(MX_PIV_all[0]*MX_PIV_all[1])
    #topos_modes_all = np.zeros(((n_xy_PIV_all, nb_modes+1, data_assimilate_dim)))
    topos_modes_all = np.zeros(((n_xy_PIV_all, nb_modes+1, 2)))
   
    n_xy_PIV=int((index_XY_PIV[1]-index_XY_PIV[0]+1)*(index_XY_PIV[3]-index_XY_PIV[2]+1))
   
    # mode 1, 2 ...
    for n in range (nb_modes):
        topos_modes_file = PATH_ROM_PIV.joinpath(Path('spatialModes_'+str(nb_modes)+'modes/'+str(n+1)+'/B0001_new.dat'))
        if topos_modes_file.exists():
            f_topos_modes = open(topos_modes_file,'r')
            i = 0
            nb_line = 0
            while True:
              line = f_topos_modes.readline()
              if not line: 
                break
              else:            
                if nb_line > 3:
                    a = np.fromstring(line, dtype=float, sep=' ')                  
                    topos_modes_all[i][n][0]=a[2]
                    topos_modes_all[i][n][1]=a[3]
                    i=i+1
                nb_line=nb_line+1    
            f_topos_modes.close() 
        
        else:
            print('ERROR: File does not exist ', str(topos_modes_file))
            return 0
        print("file mode"+str(n+1)+"="+str(topos_modes_file))
    # mode 0    
    #topos_modes_file = Path(PATH_topos_modes).joinpath(Path('mean/1/B0001_new.dat'))
    topos_modes_file = PATH_ROM_PIV.joinpath(Path('mean/1/B0001_new.dat'))
    if topos_modes_file.exists():
    #if Path(topos_modes_file).is_file():
        f_topos_modes = open(topos_modes_file,'r')
        i = 0
        nb_line = 0
        while True:
          line = f_topos_modes.readline()
          if not line: 
            break
          else:   
            if nb_line > 3:
                a = np.fromstring(line, dtype=float, sep=' ')  
                topos_modes_all[i][nb_modes][0]=a[2]
                topos_modes_all[i][nb_modes][1]=a[3]
                i=i+1
            nb_line=nb_line+1    
        f_topos_modes.close() 
    print("file mean=mode0="+str(topos_modes_file))
    print("\n\n")
            
    topos_modes_all2=np.reshape(topos_modes_all,(MX_PIV_all[1], MX_PIV_all[0], nb_modes+1, 2))
    topos_modes = topos_modes_all2[index_XY_PIV[2]:index_XY_PIV[3]+1,index_XY_PIV[0]:index_XY_PIV[1]+1,:,:]
    topos_modes2 = np.reshape(topos_modes,(n_xy_PIV, nb_modes+1, 2))  
    topos=topos_modes2
    
    print("\n\n")


    print("data=fake_real_data=f(C++) => inv(mat_covariance + mat_diag(0.06**2))")
    
    redlumcpp_code_version = os.path.basename(os.path.normpath(PATH_ROM.parents[0]))
    bool_res = recentROM( redlumcpp_code_version, 3, 3 )
    if bool_res:
        sigmaInv_file = PATH_ROM_PIV.joinpath(
            Path('residualSpeed_'+str(nb_modes)+'_U/Inv_COVxy.dat'))
    else:
        sigmaInv_file = PATH_ROM_PIV.joinpath(
            Path('residualSpeed_'+str(nb_modes)+'/Inv_COVxy.dat'))

    print("file sigma="+str(sigmaInv_file))
    #sigmaInv = np.zeros(((n_X_PIV*n_Y_PIV, 2, 2)))
    
    sigmaInv_all = np.zeros(((n_xy_PIV_all, 2, 2)))

    if sigmaInv_file.exists():
        f_sigmaInv = open(sigmaInv_file, 'r')
        i = 0
        nb_line = 0
        while True:
            line = f_sigmaInv.readline()
            if not line:
                break
            else:
                if nb_line > 1:
                    a = np.fromstring(line, dtype=float, sep=' ')
                    sigmaInv_all[i][0][0] = a[2]
                    sigmaInv_all[i][1][1] = a[3]
                    sigmaInv_all[i][0][1] = a[4]
                    sigmaInv_all[i][1][0] = a[4]
                    i = i+1
                nb_line = nb_line+1
        f_sigmaInv.close()
    else:
        print('ERROR: File does not exist ', str(sigmaInv_file)+"\n")
        
    sigmaInv_all2=np.reshape(sigmaInv_all,(MX_PIV_all[1],MX_PIV_all[0], 2, 2))
    sigmaInv = sigmaInv_all2[index_XY_PIV[2]:index_XY_PIV[3]+1,index_XY_PIV[0]:index_XY_PIV[1]+1,:,:]
    sigmaInv2 = np.reshape(sigmaInv,(n_xy_PIV, 2, 2))
    Sigma_inverse = sigmaInv2

# print ("\nBEFORE MASK")
# nb_col = len(Sigma_inverse.shape)
# for i in range ( len(Sigma_inverse.shape) ):
#     print("#### Sigma_inverse "+str(Sigma_inverse.shape)+"=> dim(col="+str(len(Sigma_inverse.shape)-i)+')='+\
#           str(Sigma_inverse.shape[len(Sigma_inverse.shape)-i-1]))
    
    return topos, Sigma_inverse


def convert_Cmat_to_python_FakePIV(MX_PIV_all, index_XY_PIV, PARAM):
     
    SECONDS_OF_SIMU = PARAM.SECONDS_OF_SIMU
    
    PATH_DATA= PARAM.PATH_DATA
    PIV_velocity = PARAM.PIV_velocity
    dt_PIV = PARAM.dt_PIV
    t0_testBase = PARAM.t0_testBase

    n_xy_PIV_all=int(MX_PIV_all[0]*MX_PIV_all[1])
    Wake_all = np.zeros(((n_xy_PIV_all, 2)))
    
    n_xy_PIV=int((index_XY_PIV[1]-index_XY_PIV[0]+1)*(index_XY_PIV[3]-index_XY_PIV[2]+1))
    
    
    print("\ndata=fake_real_data=f(C++) => wake+noise")
    # Normalizing  measured data
    # matrix_data_PIV_all_data = matrix_data_PIV_all_data / \
    #     u_inf_measured  # Normalizing the PIV data to compare with DNS

    # Cf. ../Boulot/RedLUM/RedLum_from_OpenFoam/RedLum_D1_Lz1pi_Re300/ROMDNS/system/ITHACAdict
    # Start of the learning set : InitialTime 100
    # End of the learning set, and start of the test set : FinalTime 600
    # End of the test set : FinalTimeSimulation 700
    # t_init = 100
    t_init = float(t0_testBase)
    n_file = int((SECONDS_OF_SIMU-SECONDS_OF_SIMU % dt_PIV)/dt_PIV)
    # t_final = t_init+n_file*dt_PIV
    # index_final = SECONDS_OF_SIMU/dt_PIV
    vector_of_assimilation_time = np.zeros(n_file, dtype=float)
    for i in range(n_file):
        vector_of_assimilation_time[i] = i*dt_PIV
        # vector_of_assimilation_time[i] = t_init +i*dt_PIV
        # vector_of_assimilation_time[i] = t_init +(i+1)*dt_PIV

    PATH_wake = PATH_DATA
    print("Path for Wake files :"+str(PATH_wake)+"\n")

    vector_flow = np.zeros(((n_file, n_xy_PIV, 2)))
    for n in range(n_file):
        t = t_init + n*dt_PIV
        if (t*10) % 10 == 0:
            Wake_file = Path(PATH_wake).joinpath(
                Path(str(int(t))+'/B0001_new.dat'))
        else:
            Wake_file = Path(PATH_wake).joinpath(
                Path(str(t)+'/B0001_new.dat'))

        #print("n="+str(n)+" t="+str(t)+" -> file wake="+str(Wake_file))

        if Wake_file.exists():
            f_Wake = open(Wake_file, 'r')
            i = 0
            nb_line = 0
            while True:
                line = f_Wake.readline()
                if not line:
                    break
                else:
                    if nb_line > 3:
                        a = np.fromstring(line, dtype=float, sep=' ')
                        Wake_all[i][0] = a[2]
                        Wake_all[i][1] = a[3]
                        i = i+1
                    nb_line = nb_line+1
            f_Wake.close()
    
        #print("index_X=["+str(index_XY_PIV[0])+":"+str(index_XY_PIV[1])+"] index_Y=["+str(index_XY_PIV[2])+":"+str(index_XY_PIV[3])+"]")

        Wake_all2=np.reshape(Wake_all,(MX_PIV_all[1],MX_PIV_all[0],2))
        Wake = Wake_all2[index_XY_PIV[2]:index_XY_PIV[3]+1,index_XY_PIV[0]:index_XY_PIV[1]+1,:]
        Wake2 = np.reshape(Wake,(n_xy_PIV,2))
        
        vector_flow[n, :, :] = Wake2[:, :]/PIV_velocity

        
    return vector_flow, vector_of_assimilation_time
