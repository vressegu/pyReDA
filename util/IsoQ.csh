#!/bin/tcsh
#
# Laurence Wallian - ACTA - OPAALE - INRAE Rennes [Juin 2022 : Avril 2023]
#                                                                                  [February 2024]
#
# MORAANE project : Scalian - INRAE
#
#  ------------------------------------------------------------------------------
#
# MORAANE : generating IsoQ PNG files
#
#------------------------------------------------------------------------------
#
# NOTE : for pseudo openfoam case (from ROM result), 
#              pyReDA must have been used before to generate
#              - temporalModeSimulation.txt : ROM result
#             OR
#              - temporalModeDAresult.txt : DA result
#
#------------------------------------------------------------------------------
#
# USAGE : tcsh IsoQ.csh arg1 arg2 arg3
# 
#  Input parameters :
#    - arg1 : openfoam data folder (default : present directory)
#                 NOTE : it can be 
#                              1) an exact openfoam result 
#                                  (.../RedLUM/data_red_lum_cpp/DNS.../openfoam_data)
#                              2) a pseudo openfoam case (obtained by extractU_from_ROM.csh)
#                                   2.a) reconstructed from ROM result (.../TrueState_...modes)
#                                   2.b) reconstructed from pyReDA result (.../RedLumPart_...modes...)
#    - arg2 : Start time (default : 600)
#    - arg3 : End time (default : 670)
#
#------------------------------------------------------------------------------

set dir_ici = `pwd`
set dir_ici_SED = `echo ${dir_ici} | sed s/"\/"/"\\\/"/g`

set dir_util = ${dir_ici}/util

#------------------------------------------------------------------------------

source /usr/lib/openfoam/openfoam2212/etc/cshrc
alias lsd  ' ls -l | awk '\''{i=0; i=index($1,"d"); if (i==1) print $9 }'\'' '

#------------------------------------------------------------------------------

# PATH for openfoam time directories :  for example .../RedLum_from_OpenFoam/D1_Lz*pi_Re*/openfoam_data

# dir_data folder : default value
set dir_data = `pwd `

# dir_data folder : input value
if ( $1 != "" ) set dir_data = $1

set dir_data_SED = ` echo ${dir_data} | sed s/"\/"/"\\\/"/g`

# first time for IsoQ picture

# time first : default value
set timeStart = 600

# time first : input value
if ( $2 != "" ) set timeStart = $2

# last time for IsoQ picture

# time last : default value
set timeEnd = 670

# time last : input value
if ( $3 != "" ) set timeEnd = $3

#  ------------------------------------------------------------------------------

cd ${dir_data}
if ( (!( -e constant)) || (!(-e system/controlDict)) ) then

  echo ""
  echo "OUPS \! NO Directory constant and/or file system/controlDict Found in ${dir_data} \!"
  echo "OUPS \! Q criterion can NOT be added to simulation results for t=[${timeStart}:${timeEnd}] \! "; echo ""
  echo ""
  
  cd ${dir_ici}
  
  exit()
  
else

  echo ""
  echo "OK, Directory constant and file system/controlDict Found in ${dir_data} "
  echo "Q criterion can be added to simulation results for t=[${timeStart}:${timeEnd}]"; echo ""
  echo ""
  
  set IsoQ_model = ${dir_util}/IsoQ_GEO_LES3900_model.py
  
  if ( -e ${IsoQ_model} ) then
  
    set code_GEO_LES390 = ` echo ${dir_data} | grep "GEO_LES3900" | wc -l `
    if (( ${code_GEO_LES390} == 0 ) && ( -e ${dir_util}/IsoQ_GEO_LES3900_model.py)) then
      echo ""
      echo "NOTE : paraFoam model used is adapted to GEO_LES3900 ... "
      echo ""
    endif
    
  else
  
    echo ""; echo "OUPS\! file ${IsoQ_model} NOT Found"; echo ""
    exit()
  
  endif
  
endif

#  ------------------------------------------------------------------------------

### Generating Q ###

set code = 1
if ( ${code} == 1 ) then

  echo ""; echo "Generating Q values for t=[${timeStart}:${timeEnd}]"; echo ""

  # code1 = 1 : OLD version : before openfoam 2212 ??? !!!

  set code1 = 0 # !!! no more necessary with openfoam 2212 !!!
  if ( ${code1} == 1 ) then
    
    set code2 = ` cat system/controlDict | grep Q_criterion | wc -l `
    if ( ${code2} == 0 ) then

      echo ""
      echo "Add the following lines to system/controlDict"
      echo ""
      cat system/Q_criterion_function.txt

    else

      set N1 = ` cat -n system/controlDict | grep Q_criterion | awk '{ print $1 }' `
      
      set N2 = ` awk -v N=${N1} 'BEGIN{c=0}{ if ((NR>N) && (NF!=0)) { if  ($1=="{") c=c+1; if ($1=="}") c=c-1; if ((c==1) && ($1=="timeStart")) print NR} }' system/controlDict `
      \mv system/controlDict tmp.txt
      awk -v N=${N2} '{ if (NR<N) print $0 }' tmp.txt > system/controlDict
      echo "timeStart ${timeStart};" >> system/controlDict
      awk -v N=${N2} '{ if (NR>N) print $0 }' tmp.txt >> system/controlDict
      
      set N2 = ` awk -v N=${N1} 'BEGIN{c=0}{ if ((NR>N) && (NF!=0)) { if  ($1=="{") c=c+1; if ($1=="}") c=c-1; if ((c==1) && ($1=="timeEnd")) print NR} }' system/controlDict `
      \mv system/controlDict tmp.txt
      awk -v N=${N2} '{ if (NR<N) print $0 }' tmp.txt > system/controlDict
      echo "timeEnd ${timeEnd};" >> system/controlDict
      awk -v N=${N2} '{ if (NR>N) print $0 }' tmp.txt >> system/controlDict

      postProcess -func Q
    
    endif
    
  else
    
      postProcess -func Q -time "${timeStart}:${timeEnd}"

  endif

endif

### Generating Q PNG view ###

set code = 1
if ( ${code} == 1 ) then

  echo ""; echo "Generating Q PNG files for t=[${timeStart}:${timeEnd}]"; echo ""

  set All_t_default = ` lsd | grep -v '[a-Z;A-Z]' | awk '{ printf("%.0f %s\n",1000.*($1+0.), $1) }' | sort -n | awk '{ print $2 }' `
  set All_t = ( ${All_t_default} )

  set fic_src = system/ITHACAdict
  set t_first = ` cat ${fic_src} | \
                            awk 'BEGIN{code=0}{if ($1=="{") code=code+1; if ($1=="}") code=code-1; if (code==0) print $0 }' | \
                            sed s/";"//g | awk '{ if ($1=="FinalTime") print  $2 }' `
  set t_last = ` cat ${fic_src} | \
                            awk 'BEGIN{code=0}{if ($1=="{") code=code+1; if ($1=="}") code=code-1; if (code==0) print $0 }' | \
                            sed s/";"//g | awk '{ if ($1=="FinalTimeSimulation") print  $2 }' `
  
  set t_first = ${timeStart}
  set t_last = ${timeEnd}
  
  set All_t = ` echo ${All_t} | \
                          awk -v t1=${t_first} -v t2=${t_last} '{ for (i=1;i<=NF; i++) { t=$i+0.; if ((t>=t1+0.) && (t<=t2+0.)) print $i } }' `

  set N_t = ` echo ${All_t} | awk '{ print NF }' `
  if ( ${N_t} == 0 ) set All_t = ( ${All_t_default} )
        
  set timeStart = ` echo ${All_t} | awk '{ print $1 }' `

  set Zplan = 1.5
  set IsoQ = 0.2
  
  if -e IsoQ \rm -R IsoQ; mkdir IsoQ
  set t = ${t_first}
  if -e IsoQ.py \rm IsoQ.py
  cat ${IsoQ_model} | \
    sed s/"PATH_to_DATA"/"${dir_data_SED}"/g | \
    sed s/"Q_VALUE"/"${IsoQ}"/g | \
    sed s/"Z_VALUE"/"${Zplan}"/g | \
    sed s/"TIME_VALUE"/"${t}"/g  | \
    sed s/"TIME_START_VALUE"/"${timeStart}"/g  | \
    sed s/"TIME_END_VALUE"/"${timeEnd}"/g > IsoQ.py
        
  pvbatch IsoQ.py

endif

cd ${dir_ici}

#  ------------------------------------------------------------------------------

echo ""
echo "Cf. PNG files in ${dir_data}/IsoQ"
echo ""

#  ------------------------------------------------------------------------------

