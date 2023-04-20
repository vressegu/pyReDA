# -*- coding: utf-8 -*-
"""
Created on Tuesday 21 10:53:30 2022 : from file [convert_mat_to_python.py] matheus.ladvig

@author: laurence.wallian
"""

# VAR DEFINED are  
#   I_sto,L_sto,C_sto
#   I_deter,L_deter,C_deter
#   pchol_cov_noises


import numpy as np
from pathlib import Path
import os


def convert_Cmat_to_python_ILCpchol(PATH_MAT,Re_str,nb_modes_str,bool_PFD=True,code_adv_cor=True):
 
    
    ############### FIRST PART ####################################
    ############### Cf. original file [convert_mat_to_python.py]
    
    Re=float(Re_str)
    nb_modes=int(nb_modes_str)
    redlumcpp_code_version = os.path.basename(os.path.normpath(
                                                Path(PATH_MAT).parents[1]))
    # Path completion if the ROM is Projected onto the space of Free Divergence functions
    if bool_PFD:
        path_PFD = '_PFD'
    else:
        path_PFD = ''
    PATH_MAT_test = str(Path(__file__).parents[3]) + '/data_red_lum_cpp/' + \
                                   'StationnaryRegime_TestSeparated_Re300/'
    bool_recentROM = (len(redlumcpp_code_version)>=8)
    if bool_recentROM:
        bool_recentROM = ( (redlumcpp_code_version[5].isdigit()) 
                         & (redlumcpp_code_version[7].isdigit()) )
    if bool_recentROM:
        bool_recentROM = ( (int(redlumcpp_code_version[5])>=3) 
                           & (int(redlumcpp_code_version[7])>=0) )
    if bool_recentROM or \
       PATH_MAT == PATH_MAT_test + \
                    'ROMDNS-branchCleanerDEIMtest/ITHACAoutput/Matrices' \
       or PATH_MAT == PATH_MAT_test + \
                        'ROMDNS-CommitCleanerDEIMTest/ITHACAoutput/Matrices' :
        add_0v = ''
        add_0m = '_0'
    else:
        add_0v = '_0'
        add_0m = ''

    
    ### Cf. functions_Cpp_to_matlab/read_Cpp_sto.m et functions_Cpp_to_matlab/read_Cpp_deter
    code_Cpp_to_mat = True
    
    ############### SECOND PART ####################################
    ############### Cf. l.436 of original file [main_from_existing_ROM.py]
    ############### link between 1) eq.52 Guillaume Le Pape report
    ############### and          2) eq.5 Valentin Resseguier report
        
    ### I_sto = L_PFD_1_vector_0_2_0 + S_PFD_1_vector_0_2_0 ###
    
    nx=nb_modes; ny=1;
    I_sto = np.zeros( (nx,ny), dtype=np.float64 ) 
    if code_adv_cor:
        file_name = PATH_MAT+'/L' + path_PFD + '_1_vector' + add_0v + '_' + nb_modes_str + '_0_mat.txt'
        coeff=1.
        f = open(file_name,'r')
        i = 0
        while True:
          line = f.readline()
          if not line: 
            break
          else:            
           a = np.fromstring(line, dtype=float, sep=' ')
           for j in range(len(a)):
               I_sto[i][j]=a[j]*coeff
           i=i+1
        f.close()    
    file_name = PATH_MAT+'/S' + path_PFD + '_1_vector' + add_0v + '_' + nb_modes_str + '_0_mat.txt'
    coeff=1.
    f = open(file_name,'r')
    i = 0
    while True:
      line = f.readline()
      if not line: 
        break
      else:            
       a = np.fromstring(line, dtype=float, sep=' ')
       for j in range(len(a)):
           I_sto[i][j]=I_sto[i][j]+a[j]*coeff
       i=i+1
    f.close()    
    #print(" -> I_sto="+str(I_sto))
    
    ### L_sto = L_PFD_2_0 + S_PFD_2_0 ###

    nx=nb_modes; ny=nx;
    L_sto = np.zeros( (nx,ny), dtype=np.float64 ) 
    if code_adv_cor:
        file_name = PATH_MAT+'/L' + path_PFD + add_0m + '_' + nb_modes_str + '_0_mat.txt'
        coeff=1.
        f = open(file_name,'r')
        i = 0
        while True:
          line = f.readline()
          if not line: 
            break
          else:            
           a = np.fromstring(line, dtype=float, sep=' ')
           for j in range(len(a)):
               L_sto[i][j]=a[j]*coeff
           i=i+1
        f.close()    
    file_name = PATH_MAT+'/S' + path_PFD + add_0m + '_' + nb_modes_str + '_0_mat.txt'
    coeff=1.
    f = open(file_name,'r')
    i = 0
    while True:
      line = f.readline()
      if not line: 
        break
      else:            
       a = np.fromstring(line, dtype=float, sep=' ')
       for j in range(len(a)):
          L_sto[i][j] = L_sto[i][j]+a[j]*coeff               
       i=i+1
    f.close()    
    #print(" -> L_sto="+str(L_sto))
    
    ### L_sto -> L_sto=Transpose(L_sto) (Cf. functions_Cpp_to_matlab/read_Cpp_sto.m)
    if code_Cpp_to_mat == True:
        tmp_sto = np.transpose(L_sto)
        L_sto = tmp_sto.copy()
    
    ### C_sto = NULL ###
    nx=nb_modes; ny=nx; nz=nx;
    C_sto = np.zeros( (nx,ny,nz), dtype=np.float64 ) 
    
    ### I_deter = -C_PFD_1_vector_2_0 + B_1_vector_0_2_0/Re ###
    nx=nb_modes; ny=1;
    I_deter = np.zeros( (nx,ny), dtype=np.float64 ) 
    file_name = PATH_MAT+'/C' + path_PFD + '_1_vector_' + nb_modes_str + '_0_mat.txt'
    coeff=-1.
    f = open(file_name,'r')
    i = 0
    while True:
      line = f.readline()
      if not line: 
        break
      else:            
       a = np.fromstring(line, dtype=float, sep=' ')
       for j in range(len(a)):
           I_deter[i][j]=a[j]*coeff
       i=i+1
    f.close()    
    file_name = PATH_MAT+'/B_1_vector_0_' + nb_modes_str + '_0_mat.txt'
    coeff=1./Re
    f = open(file_name,'r')
    i = 0
    while True:
      line = f.readline()
      if not line: 
        break
      else:            
       a = np.fromstring(line, dtype=float, sep=' ')
       for j in range(len(a)):
           I_deter[i][j]=I_deter[i][j]+a[j]*coeff
       i=i+1
    f.close()    
    #print(" -> I_deter="+str(I_deter))
    
    ### L_deter = -C_PFD_2_matrix_0_2_0 + B_0_2_0/Re ###
    nx=nb_modes; ny=nx;
    L_deter = np.zeros( (nx,ny), dtype=np.float64 ) 
    file_name = PATH_MAT+'/C' + path_PFD + '_2_matrix_0_' + nb_modes_str + '_0_mat.txt'
    coeff=-1.
    f = open(file_name,'r')
    i = 0
    while True:
      line = f.readline()
      if not line: 
        break
      else:            
       a = np.fromstring(line, dtype=float, sep=' ')
       for j in range(len(a)):
           L_deter[i][j]=a[j]*coeff
       i=i+1
    f.close()    
    file_name = PATH_MAT+'/B' + path_PFD + '_0_' + nb_modes_str + '_0_mat.txt'
    # file_name = PATH_MAT+'/B_0_' + nb_modes_str + '_0_mat.txt'
    coeff=1./Re
    f = open(file_name,'r')
    i = 0
    while True:
      line = f.readline()
      if not line: 
        break
      else:            
       a = np.fromstring(line, dtype=float, sep=' ')
       for j in range(len(a)):
           L_deter[i][j]= L_deter[i][j]+a[j]*coeff           
       i=i+1
    f.close()    
    
    ### L_deter -> L_deter=Transpose(L_deter) (Cf. functions_Cpp_to_matlab/read_Cpp_sto.m)
    if code_Cpp_to_mat == True:
        tmp_deter = np.transpose(L_deter)
        L_deter = tmp_deter.copy()
    
    ### C_deter = z0=C_PFD_0_2_0_t0 z1=-C_PFD_0_2_0_t1 ###
    nx=nb_modes; ny=nx; nz=nx;
    C_deter = np.zeros( (nx,ny,nz), dtype=np.float64 ) 
    file_name = PATH_MAT+'/C' + path_PFD + '_0_' + nb_modes_str + '_0/C0_mat.txt'
    coeff=-1.
    f = open(file_name,'r')
    i = 0
    while True:
      line = f.readline()
      if not line: 
        break
      else:            
       a = np.fromstring(line, dtype=float, sep=' ')
       for j in range(len(a)):
           C_deter[i][j][0]=a[j]*coeff
       i=i+1
    f.close()    
    file_name = PATH_MAT+'/C' + path_PFD + '_0_' + nb_modes_str + '_0/C1_mat.txt'
    coeff=-1.
    f = open(file_name,'r')
    i = 0
    while True:
      line = f.readline()
      if not line: 
        break
      else:            
       a = np.fromstring(line, dtype=float, sep=' ')
       for j in range(len(a)):
           C_deter[i][j][1]= a[j]*coeff
       i=i+1
    f.close()    
    #print(" -> C_deter="+str(C_deter))
    
    ### C_deter -> C_deter~Transpose(C_deter) (Cf. functions_Cpp_to_matlab/read_Cpp_deter.m)
    if code_Cpp_to_mat == True:
        tmp_deter = np.zeros( (nx,ny), dtype=np.float64 ) 
        for k in range(nz):
            tmp_deter =  np.transpose( C_deter[:,:,k] )
            C_deter[:,:,k] = tmp_deter.copy()
    
    #pchol_cov_noises = N_PFD_2x3_2x3
    nx=nb_modes*(nb_modes+1); ny=nx;
    pchol_cov_noises = np.zeros( (nx,ny), dtype=np.float64 ) 
    file_name = PATH_MAT+'/N' + path_PFD + '_' + \
                nb_modes_str + 'x' + str(nb_modes+1) + '_' + \
                nb_modes_str + 'x' + str(nb_modes+1) + '_mat.txt'
    coeff=1.
    f = open(file_name,'r')
    i = 0
    while True:
      line = f.readline()
      if not line: 
        break
      else:            
        a = np.fromstring(line, dtype=float, sep=' ')
        for j in range(len(a)):
            pchol_cov_noises[i][j]=a[j]*coeff
        i=i+1
    f.close()    
    #print(" -> pchol_cov_noises="+str(pchol_cov_noises))

    ############### FOURTH PART ####################################
    ############### Cf. l.650 of original file [main_from_existing_ROM.py]
    ############### Cf. part %% Parameters of the ODE of the b(t) : I_sto = I_sto - I_deter
    ############### link between 1) eq.52 Guillaume Le Pape report
    ############### and          2) eq.5 Valentin Resseguier report
    # _sto = -sum (_sto,_deter), _deter = - _deter
    
    I_sto = - ( I_sto + I_deter)
    L_sto = - ( L_sto + L_deter)
    C_sto = - ( C_sto + C_deter)
        
    I_deter = -I_deter
    L_deter = -L_deter
    C_deter = -C_deter 
     
    return I_sto, L_sto, C_sto, I_deter, L_deter, C_deter, pchol_cov_noises
 
    
    
