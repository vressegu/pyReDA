#!/bin/tcsh
#
# Laurence Wallian - ACTA - OPAALE - INRAE Rennes [Juin 2022 : Avril 2023]
#
# MORAANE project : Scalian - INRAE
#
#------------------------------------------------------------------------------
#
# MORAANE : this script 
#   1) generates IsoQ PNG files
#       - first, from ROM result : True State
#       - then, from DA result : RedLum Particle
#   2) creates a movie including this two types of figures
#       - left figure : True State
#       - right figure : RedLum Particle
#
#------------------------------------------------------------------------------
#
# NOTE : pyReDA must have been used before to generate
#              - temporalModeSimulation.txt : ROM result
#              - temporalModeDAresult.txt : DA result
#
#------------------------------------------------------------------------------
#
# USAGE : tcsh IsoQ_all.csh arg1 arg2 arg3
# 
#  Input parameters :
#    - arg1 : pyReDA folder result 
#                (default : 3rdresult/DNS300-GeoLES3900...)
#    - arg2 : Start time (default : 600)
#    - arg3 : End time (default : 670)
#
#------------------------------------------------------------------------------
#
# Scripts used :
#   - util/extractU_from_ROM.csh : generates pseudo OpenFoam time directories
#       from spatial and time modes
#   - util/IsoQ.csh : postprocess OpenFoam for IsoQ, and creates PNG files
#   - util/montage_IsoQ_ROM.csh : creates the movie
#
#------------------------------------------------------------------------------

# current directory

set dir_ici = ` pwd `
alias lsd  ' ls -l | awk '\''{i=0; i=index($1,"d"); if (i==1) print $9 }'\'' '

# pyReDA folder result

set ROM_version = ROM-v3.1.2

set nb_modes = 2
#set nb_modes = 4
#set nb_modes = 8

set ROM_DATA = CppROM_Cpptestbasis
set ROM_DATA = CppROM

set ObsCase = 3
set ObsCase = 1

# pyReDA folder result : default value

set dir_pyReDA_result = ~/Bureau/MORAANE/3rdresult/DNS300-GeoLES3900_${nb_modes}_modes_${ROM_DATA}/${ROM_version}/fake_real_data/_DADuration_70_ObsCase_${ObsCase}_beta_2_1_nSimu_100_nMut_-1_nPcl_100

# pyReDA folder result : input value
if ( $1 != "" ) set dir_pyReDA = $1

# nb_modes, ... : deduced from dir_pyReDA_result

set DNS = ` echo ${dir_pyReDA_result} | sed s/"\/"/"\n"/g | grep modes | awk -F'_' '{ print $1 }' `
set ROM = ` echo ${dir_pyReDA_result} | sed s/"\/"/"\n"/g | grep "ROM-" `
set nb_modes = ` echo ${dir_pyReDA_result} | sed s/"\/"/"\n"/g | grep "DNS" | awk -F'_' '{ print $2 }' `
set ROM_DATA = ` echo ${dir_pyReDA_result} | sed s/"\/"/"\n"/g | sed s/"_modes_"/"\n"/g | grep "ROM" | grep -v "ROM-" `
set dt = ` echo ${dir_pyReDA_result} | sed s/"\/"/"\n"/g | grep "_DADuration_" | awk -F'_' '{ print $3 }' `
set Other_info = ` echo ${dir_pyReDA_result} | awk -F'/' '{ print $NF }' `

set dir_ROM = /media/laurence.wallian/Val4To/RedLUM/data_red_lum_cpp/${DNS}/${ROM}

if (!( -e ${dir_ROM} )) then

  echo ""; echo "\!\!\! ${dir_ROM} NOT FOUND \!\!\!"; echo ""
  
else

  echo ""; echo "OK, ${dir_ROM} FOUND"; echo ""
  
endif

# first time for creating movie

# time first : default value
set t_first = 600

# time first : input value
if ( $2 != "" ) set t_first = $2

# last time for creating movie

# time last : default value
set t_last = ` echo ${t_first} ${dt} | awk '{ print $1+$2 }' `

# time last : input value
if ( $3 != "" ) set t_last = $3

#------------------------------------------------------------------------------

set dir_data_space = ${dir_ROM}/ITHACAoutput/spatialModes_${nb_modes}modes

\cp util/extractU_from_ROM.csh .
\cp util/IsoQ.csh .

########### True State : if not already exist

if (!( -e ${dir_ROM}/TrueState_${nb_modes}modes )) then

  set temporal_file = ${dir_pyReDA_result}/temporalModeSimulation.txt
  tcsh extractU_from_ROM.csh ${t_first} ${t_last} ${dir_data_space} ${temporal_file}
    
  tcsh IsoQ.csh ${t_first} ${t_last} ${dir_ROM}/TrueState_${nb_modes}modes
  
else

    echo ""; echo "folder ${dir_ROM}/TrueState_${nb_modes}modes already exist" ; echo ""

endif

########## Particle Mean

set temporal_file = ${dir_pyReDA_result}/temporalModeDAresult.txt
tcsh extractU_from_ROM.csh ${t_first} ${t_last} ${dir_data_space} ${temporal_file}
  
tcsh IsoQ.csh ${t_first} ${t_last} ${dir_ROM}/RedLumPart_${nb_modes}modes_${ROM_DATA}${Other_info}

######### Movie

tcsh montage_IsoQ_ROM.csh ${dir_ROM} TrueState_${nb_modes}modes RedLumPart_${nb_modes}modes_${ROM_DATA}${Other_info}

