# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 08:36:46 2023

@author: laurence.wallian
"""

# VAR DEFINED

# A) With [main_globalParam_from_info_txt_file] :
#    - type_data_C : Openfoam dataset 
#    - bool_PFD : True if the ROM correct for pressure
#    - code_DATA_from_matlab : test basis parameter
#      if True, MatLab data is used, else openfoam/C++ data is used 
#    - code_ROM_from_matlab : learning basis parameter
#      if True, MatLab result for ROM is used, else openfoam/C++ result is used      
#    - code_Assimilation : if True, test with assimilation 
#      if False, beta_2=0, beta_3=1, init_centred_on_ref=True and assimilation_period>=SECONDS_OF_SIMU-1
#    - code_load_run : if True, does not simulate but load existing (matlab or C++) run instead
#    - init_centred_on_ref : if True, INIT condition centered on real condition
#    - redlumcpp_code_version : Version of the code redlumcpp used (ROMDNS, ROMDNS-v1.0, ROMDNS-v1.1, ...)
#    - PATH_openfoam_data : upper PATH for subdirectories [ITHACAoutput], [ROM_PIV], [util] and [FakePIV_noise2]
#      example :  /media/laurence.wallian/Val4To/RedLUM/data_red_lum_cpp'
#    - beta_2 : parameter that controls the  noise in the initialization of the filter
#      if beta_2=0, there is NO noise added to INIT condition
#    - beta_3 : parameter that controls the impact in the model noise -> beta_3 * pchol_cov_noises
#      if beta_3=0, there is NO noise during simulation
#
# B) With [main_optionalParam_from_info_txt_file] :
#    - plot_debug : if True, mean(Ux) ... is plotted
#
# C) With [param_from_DNS_info_txt_file] :
#     - dt_DNS : DNS files saving period (>> DNS time step)
#     - t0_DNS : start time for DNS
#     - t1_DNS : end time for DNS
#
# D) With [param_from_PIV_info_txt_file] :
#     - PIV_velocity : reference velocity (=inlet velocity) in PIV (or FakePIV) files
#     - x0_cyl : cylinder center abciss in dimensionnal PIV (or FakePIV) files
#     - y0_cyl : cylinder center ordonnate in dimensionnal PIV (or FakePIV) files
#     - diam_cyl : cylinder diameter in dimensionnal PIV (or FakePIV) files 
#     - dt_PIV : time between two dimensionnal PIV (or FakePIV) files
#                !!! in FakePIV, it's adimensionnal time !!! 
#
# E) With [param_from_DNS_to_FakePIV_info_txt_file] :
#     - x1_PIV : min absciss for crop of dimensionnal PIV (or FakePIV) files
#     - y1_PIV : min ordinate for crop of dimensionnal PIV (or FakePIV) files
#     - x2_PIV : max absciss for crop of dimensionnal PIV (or FakePIV) files
#     - y2_PIV : max ordinate for crop of dimensionnal PIV (or FakePIV) files

import numpy as np

import re # for grep search in param file

##################################################################################################
# defining run parameters from [run_info.txt] file
def super_main_globalParam_from_info_txt_file ( param_file ):
    
    # 1) vect_nb_modes : for example [8,6,4,2]
    vect_nb_modes = None
    # 2) SECONDS_OF_SIMU : for example 10.
    # 3) type_data : for example 'DNS300_inc3d_3D_2017_04_02_NOT_BLURRED_blocks_truncated'
    # 4) EV : Eddy Viscosity model
    #         if EV=2 : Eddy Viscosity model with random IC only 
    #         if EV=1 : Eddy Viscosity model with noise and random IC 
    #         if EV=0 : no Eddy Viscosity model
    
    if param_file.exists():
        f_param = open(param_file, 'r')               
        while True:
            line = f_param.readline()
            line = line.replace(';','') # suppress COMMA
            line = line.replace('\t',' ') # replace TAB by one BLANK
            line = line.replace('\n',' ') # replace RETURN by one BLANK
            line = line.replace('#','# ') # add a BLANK behind a [#]
            line = line.replace(', ',',') # suppress COMMA
            line = line.replace(' ,',',') # suppress COMMA
            line = re.sub(' +', ' ', line) # replace multiple BLANKs by a single BLANK
            # => line is now a string with last character=BLANK
            a = line.split(' ')
            if not line:
                break
            else:
                # vect_nb_modes
                if re.search('vect_nb_modes', line):
                    if a[0] != '#':
                        N_list = a[1].split(',')
                        vect_nb_modes = list(map(int, N_list))
                # type_data
                if re.search('type_data', line):
                    if not re.search('type_data_C', line):
                        if a[0] != '#' :
                            type_data = str(a[1])
                # SECONDS_OF_SIMU
                if re.search('SECONDS_OF_SIMU', line):
                    if a[0] != '#':
                        SECONDS_OF_SIMU = float(str(a[1]))
                # EV
                if re.search('EV', line):
                    if a[0] != '#':
                        EV = int(str(a[1]))

    print("\nParameters defined in [run_file] :")       
    print(" - vect_nb_modes="+str(vect_nb_modes))
    print("    (list of nb_modes)") 
    print(" - type_data=["+str(type_data)+"]")
    print("    (Data set)")
    print(" - SECONDS_OF_SIMU=["+str(SECONDS_OF_SIMU)+"]")
    print("    (test duration in simulation base time : t_sim=t/t0=t*U0/L0)") 
    print(" - EV=["+str(EV)+"]")
    print("    (Eddy Viscosity model)") 
    print('\n')
                        
    return vect_nb_modes, type_data, SECONDS_OF_SIMU, EV

##################################################################################################
# defining run parameters from [run_info.txt] file
def main_globalParam_from_info_txt_file ( param_file ):
    
    # 1) type_data_C : Openfoam dataset : 
    #    for example, type_data_C = 'DNS300-D1_Lz1pi' 
    #
    # 2) bool_PFD : True if the ROM correct for pressure
    #    (using Leray projection : Proj. onto the space of Free Divergence functions)
    #    command redlumcpp-fullOrderPressure
    #    command redlumcpp-neglectedOrderPressure otherwise
    #
    # 3) code_DATA_from_matlab : if this test basis parameter is True, 
    #    MatLab data is used, else openfoam/C++ data is used
    #
    # 4) code_ROM_from_matlab : if this learning basis parameter is True, 
    #    MatLab result for ROM is used, else openfoam/C++ result is used
    #
    # 5) code_Assimilation : if True, test with assimilation 
    #    if False, beta_2=0, beta_3=1, init_centred_on_ref=True and assimilation_period>=SECONDS_OF_SIMU-1
    #
    # 6) code_load_run : if True, does not simulate but load existing (matlab or C++) run instead
    # 
    # 7) init_centred_on_ref : if True, INIT condition centered on real condition
    #
    # 8) redlumcpp_code_version : version of the code redlumcpp used 
    #    (ROMDNS, ROMDNS-v1.0, ROMDNS-v1.1, ...)   
    #     
    # 9) PATH_openfoam_data : upper PATH for subdirectories [ITHACAoutput], [ROM_PIV], [util] and [FakePIV_noise2]
    #    example :  /media/laurence.wallian/Val4To/RedLUM/data_red_lum_cpp'
    #
    # 10) beta_2 : parameter that controls the  noise in the initialization of the filter
    #     if beta_2=0, there is NO noise added to INIT condition
    #
    # 11) beta_3 : parameter that controls the impact in the model noise -> beta_3 * pchol_cov_noises
    #     if beta_3=0, there is NO noise during simulation
    #
    # 12) Left Top Obs observation point to cylinder center
    #     (Cf. Left_Top_PtObs in switch_case_param.py)
    
    if param_file.exists():
        f_param = open(param_file, 'r')               
        while True:
            line = f_param.readline()
            line = line.replace(';','') # suppress COMMA
            line = line.replace('\t',' ') # replace TAB by one BLANK
            line = line.replace('\n',' ') # replace RETURN by one BLANK
            line = line.replace('#','# ') # add a BLANK behind a [#]
            line = re.sub(' +', ' ', line) # replace multiple BLANKs by a single BLANK
            # => line is now a string with last character=BLANK
            a = line.split(' ')
            if not line:
                break
            else:
                # type_data_C : Openfoam dataset
                if re.search('type_data_C', line):
                    if a[0] != '#':
                        type_data_C = str(a[1])
                # bool_PFD : True if the ROM correct for pressure   
                if re.search('bool_PFD', line):
                    if str(a[0]) != '#':
                        if str(a[1]) == 'False':
                            bool_PFD = False
                        elif str(a[1]) == '2':
                            bool_PFD = 2
                        else:
                            bool_PFD = True
                # code_DATA_from_matlab : test basis parameter            
                if re.search('code_DATA_from_matlab', line):
                    if str(a[0]) != '#':
                        if str(a[1]) == 'False':
                            code_DATA_from_matlab = False
                        else:
                            code_DATA_from_matlab = True
                # code_ROM_from_matlab : learning basis parameter                        
                if re.search('code_ROM_from_matlab', line):
                    if str(a[0]) != '#':
                        if str(a[1]) == 'False':
                            code_ROM_from_matlab = False
                        else:
                            code_ROM_from_matlab = True
                # code_Assimilation : test with assimilation            
                if re.search('code_Assimilation', line):
                    if str(a[0]) != '#':
                        if str(a[1]) == 'False':
                            code_Assimilation = False
                        else:
                            code_Assimilation = True
                # code_load_run : if True, does not simulate but load existing (matlab or C++) run instead         
                if re.search('code_load_run', line):
                    if str(a[0]) != '#':
                        if str(a[1]) == 'False':
                            code_load_run = False
                        else:
                            code_load_run = True
                # init_centred_on_ref : if True, INIT condition centered on real condition
                if re.search('init_centred_on_ref', line):
                    if str(a[0]) != '#':
                        if str(a[1]) == 'False':
                            init_centred_on_ref = False
                        else:
                            init_centred_on_ref = True
                        
                # redlumcpp_code_version : version of the code redlumcpp used            
                if re.search('redlumcpp_code_version', line):
                    if a[0] != '#':
                        redlumcpp_code_version = str(a[1])
                # PATH_openfoam_data : upper PATH for subdirectories [ITHACAoutput], [ROM_PIV], [util] and [FakePIV_noise2]
                if re.search('PATH_openfoam_data', line):
                    if str(a[0]) != '#':
                        PATH_openfoam_data = str(a[1])
                        
                # beta_2 : if =0, NO noise added to INIT condition
                if re.search('beta_2', line):
                    if str(a[0]) != '#':
                        beta_2 = float(a[1])
                # beta_3 : if =0, NO noise added during simulation
                if re.search('beta_3', line):
                    if str(a[0]) != '#':
                        beta_3 = float(a[1])
                # x left observation point
                if re.search('xObs', line):
                    if a[0] != '#':
                        xObs = float(a[1])
                # y top observation point
                if re.search('yObs', line):
                    if a[0] != '#':
                        yObs = float(a[1])

    print("\nParameters defined in [run_file] :")       
    print(" - type_data_C=["+str(type_data_C)+"]")
    print("    (Openfoam dataset)") 
    print(" - bool_PFD=["+str(bool_PFD)+"]")
    print("    (True if the ROM correct for pressure)")
    print(" - code_DATA_from_matlab=["+str(code_DATA_from_matlab)+"]")
    print("    (test basis parameter; if True, MatLab data is used, else openfoam/C++ data is used)") 
    print(" - code_ROM_from_matlab=["+str(code_ROM_from_matlab)+"]")
    print("    (learning basis parameter; if True, MatLab result for ROM is used, else openfoam/C++ result is used)")      
    print(" - code_Assimilation=["+str(code_Assimilation)+"]")
    print("    (if True, test with assimilation") 
    print(" - code_load_run=["+str(code_load_run)+"]")
    print("    (if True, does not simulate but load existing (matlab or C++) run instead   ") 
    print(" - init_centred_on_ref=["+str(init_centred_on_ref)+"]")
    print("    (if True, INIT condition centered on real condition")   
    print(" - redlumcpp_code_version=["+str(redlumcpp_code_version)+"]")
    print("    (version of the code redlumcpp used)") 
    print(" - PATH_openfoam_data=["+str(PATH_openfoam_data)+"] :") 
    print("     (Upper PATH for subdirectories [ITHACAoutput], [ROM_PIV], [util] and [FakePIV_noise2])") 
    print(" - beta_2=["+str(beta_2)+"]")
    print("    (if =0, NO noise added to INIT condition)") 
    print(" - beta_3=["+str(beta_3)+"]")
    print("    (if =0, NO noise during simulation)") 
    print(" - xObs=["+str(xObs)+"] and yObs=["+str(yObs)+"]")
    print('    (Left Top observation point)')
        
    print('\n')
 
    return type_data_C, bool_PFD, code_DATA_from_matlab, code_ROM_from_matlab, \
    code_Assimilation, code_load_run, init_centred_on_ref, redlumcpp_code_version, PATH_openfoam_data, \
    beta_2, beta_3, xObs, yObs

##################################################################################################
# defining optional run parameters from [run_info.txt] file
def main_optionalParam_from_info_txt_file ( param_file ):
    
    # 1) plot_debug : if True, mean(Ux) ... is plotted
    
    if param_file.exists():
        f_param = open(param_file, 'r')               
        while True:
            line = f_param.readline()
            line = line.replace(';','') # suppress COMMA
            line = line.replace('\t',' ') # replace TAB by one BLANK
            line = line.replace('\n',' ') # replace RETURN by one BLANK
            line = line.replace('#','# ') # add a BLANK behind a [#]
            line = re.sub(' +', ' ', line) # replace multiple BLANKs by a single BLANK
            # => line is now a string with last character=BLANK
            a = line.split(' ')
            if not line:
                break
            else:
                # plot_debug           
                if re.search('plot_debug', line):
                    if str(a[0]) != '#':
                        if str(a[1]) == 'False':
                            plot_debug = False
                        else:
                            plot_debug = True
                        
    print("\nParameters defined in [run_file] :")       
    print(" - plot_debug=["+str(plot_debug)+"]")
    print("    (if True, mean(Ux) ... is plotted)")
    print('\n')
 
    return plot_debug

##################################################################################################
# defining parameters from [DNS_info.txt] file
def param_from_DNS_info_txt_file ( param_file ):

    # 1) dt_DNS : DNS files saving period (>> DNS time step)
    # 2) t0_DNS : start time for DNS
    # 3) t1_DNS : end time for DNS
    
    if param_file.exists():
        f_param = open(param_file, 'r')               
        while True:
          line = f_param.readline()
          if not line:
              break
          else:
            a = np.fromstring(line, dtype=float, sep=' ')
            if re.search('dt_DNS', line):
              dt_DNS = float(a[0])
            if re.search('t0_DNS', line):
              t0_DNS = float(a[0])
            if re.search('t1_DNS', line):
              t1_DNS = float(a[0])
              
    return dt_DNS, t0_DNS, t1_DNS

##################################################################################################
# defining nan parameters from [PIV_info.txt] file
def param_nan_PIV_info ( ):
    return float('Nan'), float('Nan'), float('Nan'), float('Nan'), float('Nan')

##################################################################################################
# defining parameters from [PIV_info.txt] file
def param_from_PIV_info_txt_file ( param_file ):

    # 1) PIV_velocity : reference velocity (=inlet velocity) in PIV (or FakePIV) files
    # 2) x0_cyl : cylinder center abciss in dimensionnal PIV (or FakePIV) files
    # 3) y0_cyl : cylinder center ordonnate in dimensionnal PIV (or FakePIV) files
    # 4) diam_cyl : cylinder diameter in dimensionnal PIV (or FakePIV) files 
    # 5) dt_PIV : time between two dimensionnal PIV (or FakePIV) files
    #             !!! in FakePIV, it's adimensionnal time !!! 
    
    if param_file.exists():
        f_param = open(param_file, 'r')               
        while True:
          line = f_param.readline()
          if not line:
              break
          else:
            a = np.fromstring(line, dtype=float, sep=' ')
            if re.search('PIV_Velocity', line):
              PIV_velocity = float(a[0])
            if re.search('PIV_xcyl', line):
              x0_cyl = float(a[0])
            if re.search('PIV_ycyl', line):
              y0_cyl = float(a[0])
            if re.search('PIV_Dcyl', line):
              diam_cyl = float(a[0])
            if re.search('dt_PIV', line):
              dt_PIV = float(a[0])

    return PIV_velocity, x0_cyl, y0_cyl, diam_cyl, dt_PIV

##################################################################################################
# defining nan parameters from [PIV_info.txt] file
def param_nan_DNS_to_FakePIV ( ):
    return float('Nan'), float('Nan'), float('Nan'), float('Nan')

##################################################################################################
# defining parameters from [DNS_to_FakePIV_info.txt] file, 
def param_from_DNS_to_FakePIV_info_txt_file ( param_file ):

    # 1) x1_PIV : min absciss for crop of dimensionnal PIV (or FakePIV) files
    # 2) y1_PIV : min ordinate for crop of dimensionnal PIV (or FakePIV) files
    # 3) x2_PIV : max absciss for crop of dimensionnal PIV (or FakePIV) files
    # 4) y2_PIV : max ordinate for crop of dimensionnal PIV (or FakePIV) files
    
    if param_file.exists():
        f_param = open(param_file, 'r')               
        while True:
          line = f_param.readline()
          if not line:
              break
          else:
            a = np.fromstring(line, dtype=float, sep=' ')
            if re.search('PIV_crop_x1', line):
              x1_PIV = float(a[0])
            if re.search('PIV_crop_y1', line):
              y1_PIV = float(a[0])
            if re.search('PIV_crop_x2', line):
              x2_PIV = float(a[0])
            if re.search('PIV_crop_y2', line):
              y2_PIV = float(a[0])           

    return x1_PIV, y1_PIV, x2_PIV, y2_PIV
