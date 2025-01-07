# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 08:36:46 2023

@author: laurence.wallian
"""

# VAR DEFINED

# A) With [controlDict_file] :
#     - dt_DNS : DNS files saving period (>> DNS time step)
#     - t0_DNS : start time for DNS
#     - t1_DNS : end time for DNS
#
# B) With [ITHACADict_file] :
#     - t0_learningBase : initial time for learning basis
#     - t1_learningBase : Final time for learning basis
#     - t0_testBase : initial time for test basis
#     - t1_testBase : Final time for test basis

import numpy as np

import re # for grep search in param file


##################################################################################################
# defining parameters from [controlDict] file, 
def param_from_controlDict_file ( param_file ):

    # 1) dt_DNS : DNS files saving period (>> DNS time step)
    # 2) t0_DNS : start time for DNS
    # 3) t1_DNS : end time for DNS
    
    if param_file.exists():
        f_param = open(param_file, 'r')     
        N_bracket = 0
        while True:
          line = f_param.readline()
          if not line:
              break
          else:
            line = line.replace(';','') # suppress COMMA
            line = line.replace('\t',' ') # replace TAB by one BLANK
            line = line.replace('\n',' ') # replace RETURN by one BLANK
            line = re.sub(' +', ' ', line) # replace multiple BLANKs by a single BLANK
            line = re.sub(' {', '{', line) # brackets must be the first word
            line = re.sub(' }', '}', line) # brackets must be the first word
            # => line is now a string with last character=BLANK
            a = line.split('/'); line = a[0]; 
            a = line.split(' ')
            if a[0] == '{':
              N_bracket = N_bracket+1
            if a[0] == '}':
              N_bracket = N_bracket-1
            if N_bracket == 0:
              if re.search('writeInterval ', line):
                if str(a[0]) == 'writeInterval':
                    dt_DNS = float(a[-2])
              if re.search('startTime ', line):
                if str(a[0]) == 'startTime':
                    t0_DNS = float(a[-2])
              if re.search('endTime ', line):
                if str(a[0]) == 'endTime':
                    t1_DNS = float(a[-2])

    return dt_DNS, t0_DNS, t1_DNS

##################################################################################################
# defining parameters from [ITHACADict] file, 
def param_from_ITHACADict_file ( param_file ):

    # 1) t0_learningBase : initial time for learning basis
    # 2) t1_learningBase : Final time for learning basis
    # 3) t0_testBase : initial time for test basis
    # 4) t1_testBase : Final time for test basis
    # 5) n_simu : Time step decreasing factor for ROM time integration
    # 6) inflatNut : for case LES only
    # 7) interpFieldCenteredOrNot : for case LES only
    # 8) HypRedSto : for case LES only
    # 9) DEIMInterpolatedField : for case LES only
    
    if param_file.exists():
        inflatNut = ''
        interpFieldCenteredOrNot = ''
        HypRedSto = ''
        DEIMInterpolatedField = ''
        f_param = open(param_file, 'r')               
        N_bracket = 0
        while True:
          line = f_param.readline()
          if not line:
              break
          else:
            line = line.replace(';','') # suppress COMMA
            line = line.replace('"','') # suppress QUOTE
            line = line.replace('\t',' ') # replace TAB by one BLANK
            line = line.replace('\n',' ') # replace RETURN by one BLANK
            line = re.sub(' +', ' ', line) # replace multiple BLANKs by a single BLANK
            line = re.sub(' {', '{', line) # brackets must be the first word
            line = re.sub(' }', '}', line) # brackets must be the first word
            # => line is now a string with last character=BLANK
            a = line.split('/'); line = a[0]; 
            a = line.split(' ')
            if a[0] == '{':
              N_bracket = N_bracket+1
            if a[0] == '}':
              N_bracket = N_bracket-1
            if N_bracket == 0:
              if re.search('InitialTime ', line):
                if str(a[0]) == 'InitialTime': 
                    t0_learningBase = float(a[-2])
              if re.search('FinalTime ', line):
                if str(a[0]) == 'FinalTime': 
                    t1_learningBase = float(a[-2])
                    t0_testBase = t1_learningBase
              if re.search('FinalTimeSimulation ', line):
                if str(a[0]) == 'FinalTimeSimulation': 
                    t1_testBase = float(a[-2])
              if re.search('nSimu ', line):
                if str(a[0]) == 'nSimu': 
                    n_simu = int(a[-2])
              if re.search('inflatNut ', line):
                if str(a[0]) == 'inflatNut': 
                    inflatNut = int(a[-2])
              if re.search('interpFieldCenteredOrNot ', line):
                if str(a[0]) == 'interpFieldCenteredOrNot': 
                    interpFieldCenteredOrNot = int(a[-2])
              if re.search('HypRedSto ', line):
                if str(a[0]) == 'HypRedSto': 
                    HypRedSto = int(a[-2])
              if re.search('DEIMInterpolatedField ', line):
                if str(a[0]) == 'DEIMInterpolatedField': 
                    DEIMInterpolatedField = str(a[-2])
  
    return t0_learningBase, t1_learningBase, t0_testBase, t1_testBase, n_simu, inflatNut, interpFieldCenteredOrNot, HypRedSto, DEIMInterpolatedField
