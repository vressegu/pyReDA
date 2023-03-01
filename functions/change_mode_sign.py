# -*- coding: utf-8 -*-
"""
Created on mar. 05 juil. 2022 14:29:25 CEST

@author: laurence.wallian
"""
import numpy as np

def change_mode_sign_ILCpchol(nb_modes_str,num_mode_str,I_sto,L_sto,C_sto,I_deter,L_deter,C_deter,pchol_cov_noises):
    
#    Change the sign of spatial mode for mode=num_mode
#    The sizes of the inputs are :
#    - I : m
#    - L : m x m
#    - C : m x m x m
#    - pschol_cov_noises : (m x (m+1)) x (m x (m+1))
    nb_modes=int(nb_modes_str)
    num_mode=int(num_mode_str)
    
    nx=nb_modes; ny=1;
    for i in range(nx):
        if (i-(num_mode-1)) == 0:
            I_sto[i] = -I_sto[i]
            I_deter[i] = -I_deter[i]
            
    nx=nb_modes; ny=nx;     
    for i in range(nx):
        for j in range(ny):
            if (i-(num_mode-1)) == 0:
                L_sto[i][j] = -L_sto[i][j]               
                L_deter[i][j] = - L_deter[i][j]
            if (j-(num_mode-1)) == 0:
                L_sto[i][j] = -L_sto[i][j]               
                L_deter[i][j] = - L_deter[i][j]
                
    nx=nb_modes; ny=nx; nz=nx;
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                if (i-(num_mode-1)) == 0:
                    C_deter[i][j][k] = -C_deter[i][j][k]
                    C_sto[i][j][k] = -C_sto[i][j][k]
                if (j-(num_mode-1)) == 0:
                    C_deter[i][j][k] = -C_deter[i][j][k]
                    C_sto[i][j][k] = -C_sto[i][j][k]
                if (k-(num_mode-1)) == 0:
                    C_deter[i][j][k] = -C_deter[i][j][k]
                    C_sto[i][j][k] = -C_sto[i][j][k]
            
    nx=nb_modes; nz=nx*(nx+1);    
    for i in range(nx):
        for k in range(nz):
            if (i-(num_mode-1)) == 0:
                pchol_cov_noises[i][k]=-pchol_cov_noises[i][k]
                
    nx=nb_modes; ny=nx; nz=ny*(nx+1); 
    for j in range(ny):
        for i in range(nx):
            for k in range(nz):
                if (i-(num_mode-1)) == 0:
                    pchol_cov_noises[i+nx*(j+1)][k]=-pchol_cov_noises[i+nx*(j+1)][k]
                if (j-(num_mode-1)) == 0:
                    pchol_cov_noises[i+nx*(j+1)][k]=-pchol_cov_noises[i+nx*(j+1)][k]
    
    return I_sto,L_sto,C_sto,I_deter,L_deter,C_deter,pchol_cov_noises
    

def change_mode_sign_bt_tot(nb_modes_str,num_mode_str,bt_tot):
    
#    Change the sign of spatial mode for mode=num_mode
#    The sizes of the inputs are :
#    - bt_tot : (...) x nb_modes
    nb_modes=int(nb_modes_str)
    num_mode=int(num_mode_str)
    
    print("---------> bt_tot : nx="+str(len(bt_tot)) + " ny="+str(len(bt_tot[0])))
    nx=len(bt_tot); 
    ny=len(bt_tot[0]); # =nb_modes
    j=(num_mode-1)
    for i in range(nx):
        bt_tot[i][j] = -bt_tot[i][j]
                
    return bt_tot

def change_mode_sign_bt_tot_OK(nb_modes_str,num_mode_str,bt_tot):
    
#    Change the sign of spatial mode for mode=num_mode
#    The sizes of the inputs are :
#    - bt_tot : (...) x nb_modes
    nb_modes=int(nb_modes_str)
    num_mode=int(num_mode_str)
    
    print("---------> bt_tot : nx="+str(len(bt_tot)) + " ny="+str(len(bt_tot[0])))
    nx=len(bt_tot); 
    ny=len(bt_tot[0]); # =nb_modes
    for i in range(nx):
        for j in range(ny):
            if (j-(num_mode-1)) == 0: # col=num_mode
                bt_tot[i][j] = -bt_tot[i][j]
                
    return bt_tot
 
def change_mode_sign_HPivK(nb_modes_str,num_mode_str,Hpiv_Topos,K):
    
#    Change the sign of spatial mode for mode=num_mode
#    The sizes of the inputs are :
#    - Hpiv_Topos : (nb_points*nb_dim) x (nb_modes+1)
#    - K : (nb_points*nb_dim) x (nb_modes+1)
    nb_modes=int(nb_modes_str)
    num_mode=int(num_mode_str)

    nx=len(Hpiv_Topos); 
    ny=len(Hpiv_Topos[0]); # =nb_modes
    i=(num_mode-1) # row=num_mode
    for j in range(ny):
        Hpiv_Topos[i][j] = -Hpiv_Topos[i][j]
    j=(num_mode-1)
    for i in range(nx):
        Hpiv_Topos[i][j] = -Hpiv_Topos[i][j]

    nx=len(K); 
    ny=len(K[0]); # =nb_modes
    j=(num_mode-1)
    for i in range(nx):
        K[i][j] = -K[i][j]
    
    return Hpiv_Topos,K
   
 
def change_mode_sign_HPivK_OK(nb_modes_str,num_mode_str,Hpiv_Topos,K):
    
#    Change the sign of spatial mode for mode=num_mode
#    The sizes of the inputs are :
#    - Hpiv_Topos : (nb_points*nb_dim) x (nb_modes+1)
#    - K : (nb_points*nb_dim) x (nb_modes+1)
    nb_modes=int(nb_modes_str)
    num_mode=int(num_mode_str)

    nx=len(Hpiv_Topos); 
    ny=len(Hpiv_Topos[0]); # =nb_modes
    for i in range(nx):
        for j in range(ny):
            if (i-(num_mode-1)) == 0:
                Hpiv_Topos[i][j] = -Hpiv_Topos[i][j]
            if (j-(num_mode-1)) == 0: # col=num_mode
                Hpiv_Topos[i][j] = -Hpiv_Topos[i][j]

    nx=len(K); 
    ny=len(K[0]); # =nb_modes
    for i in range(nx):
        for j in range(ny): # col=num_mode
            if (j-(num_mode-1)) == 0:
                K[i][j] = -K[i][j]
    
    return Hpiv_Topos,K
    
    
    
    
    
