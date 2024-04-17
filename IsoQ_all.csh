#!/bin/tcsh
#
# Laurence Wallian - ACTA - OPAALE - INRAE Rennes [Juin 2022 : Avril 2023]
#                                                                                  [February 2024]
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
# USAGE : tcsh IsoQ_all.csh arg1
# 
#  Input parameters :
#    - arg1 : DA duration (default=70)
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

# RedLUM directory -> run_info.txt

set dir_RedLUM = ` pwd `
set fic_run_info = ${dir_RedLUM}/run_info.txt

set dir_OpenFoam = ` cat ${fic_run_info} | sed s/"^ #"/"#"/g | grep -v "^#" | \
                                 grep "PATH_openfoam_data" | awk '{ print $2 }' | tail -1 `

set case_OpenFoam = ` cat ${fic_run_info} | sed s/"^ #"/"#"/g | grep -v "^#" | \
                                 grep "type_data_C" | awk '{ print $2 }' | tail -1 `
                                 
set redlumcpp_code_version = ` cat ${fic_run_info} | sed s/"^ #"/"#"/g | grep -v "^#" | \
                                 grep "redlumcpp_code_version" | awk '{ print $2 }' | tail -1 `
                                 
set type_data_C  = ` cat ${fic_run_info} | sed s/"^ #"/"#"/g | grep -v "^#" | \
                                 grep "type_data_C" | awk '{ print $2 }' | tail -1 `            

set DIR0 = ${dir_OpenFoam}/${case_OpenFoam}/${redlumcpp_code_version}
if (!( -e ${DIR0} )) then
  echo ""; echo "\!\!\! ${DIR0} NOT FOUND \!\!\!"; echo ""
  exit()
else
  echo ""; echo "OK, ${DIR0} FOUND"; echo ""
endif

set DIR1 =  ITHACAoutput
if (!( -e ${DIR0}/${DIR1} )) then
  echo ""; echo "\!\!\! ${DIR0}/${DIR1} NOT FOUND \!\!\!"; echo ""
  exit()
else
  echo ""; echo "OK, ${DIR0}/${DIR1} FOUND"; echo ""
endif

alias lsd  ' ls -l | awk '\''{i=0; i=index($1,"d"); if (i==1) print $9 }'\'' '

# 3rdresult directory
set rdresult_dir = ~/Bureau/MORAANE/3rdresult

# Dictionnary file
set fic_Dict = ${DIR0}/system/ITHACAdict

#------------------------------------------------------------------------------

# HilbertSpace
set mot_HilbertSpacea="_H1" 
set mot_HilbertSpaceb="H1" 
set code_HilbertSpacea=` echo ${redlumcpp_code_version} | grep L2 | wc -l `
if ( ${code_HilbertSpacea} == 0 ) then
  set mot_HilbertSpacea="_H1" 
  set mot_HilbertSpaceb="H1" 
else
  set mot_HilbertSpacea="" 
  set mot_HilbertSpaceb="L2" 
endif

# dt_run
set mot=writeInterval
set file=${DIR0}/system/controlDict
set writeInterval=`cat ${file} | grep "${mot} " | awk -v m=${mot} '{ if ($1==m) print $2 }' | sed s/";"//g | head -1 `
set mot=nSimu
set file=${DIR0}/system/ITHACADict
set nSimu=`cat ${file} | grep "${mot} " | awk -v m=${mot} '{ if ($1==m) print $2 }' | sed s/";"//g | head -1 `
set dt_run=` echo ${writeInterval} ${nSimu} | awk '{ print $1/$2 }' `

# number of particles
set nPart = 1000

# assimilation
set Assimilation = 1

set mot_DA="_DA"
if ( ${Assimilation} == 0 ) then
  set mot_DA=""
endif

# advection correction 
set advModifOrNot = 1
set mot_AdvC=""
if ( ${advModifOrNot} == 0 ) then
then
  set mot_AdvC="_noAdvC"
endif

# neglectedPressure (bool_PFD=0) or fullOrderPressure (bool_PFD=1)
set bool_PFD = 1
if ( ${bool_PFD} == 0 ) then
  set mot_redlum1=neglectedPressure
  set mot_redlum2=""
else
  set mot_redlum1=fullOrderPressure
  set mot_redlum2="-fullOrderP"
endif

# dir pyReDA  
if ( ${Assimilation} == 0 ) then
  set mot_DAa="_noDA"
  set mot_DAb="_initOnRef"
else
  set mot_DAa=""
  set mot_DAb=""
endif
        
set mot_AdvC=""
if ( ${advModifOrNot} == 0 ) then
then
  set mot_AdvC="_no_correct_drift"
endif

#------------------------------------------------------------------------------
# time first and max time last

set t_first = ` cat ${fic_Dict} | \
                          awk 'BEGIN{code=0}{if ($1=="{") code=code+1; if ($1=="}") code=code-1; if (code==0) print $0 }' | \
                          sed s/";"//g | awk '{ if ($1=="FinalTime") print  $2 }' `
set t_last_max = ` cat ${fic_Dict} | \
                          awk 'BEGIN{code=0}{if ($1=="{") code=code+1; if ($1=="}") code=code-1; if (code==0) print $0 }' | \
                          sed s/";"//g | awk '{ if ($1=="FinalTimeSimulation") print  $2 }' `
                          
# last time for creating movie : t_first+DADuration

# time last : default value for DADuration
set DADuration = 70

# time last : input value for DADuration
if ( $1 != "" ) set DADuration = $1

set t_last = ` echo ${t_first} ${DADuration} | awk '{ print $1+$2 }' `
                        
set code_t_last = ` echo ${t_last} ${t_last_max} | awk '{ if ($2>=$1) print 1; else print 0 }' `
if ( ${code_t_last} == 0 ) then
  echo ""; echo "\!\!\! OUPS !  time DA duration too long \!\!\!"; echo ""
else
  echo ""; echo "OK : Iso(Q) for t=[${t_first}:${t_last}]"; echo ""
endif
        
#------------------------------------------------------------------------------

# pyReDA folder result

set All_ROM_DATA = ( CppROM_Cpptestbasis CppROM )
set All_ROM_DATA = ( CppROM_Cpptestbasis )
foreach ROM_DATA ( ${All_ROM_DATA} )

  set All_nb_modes = ( 8 4 2 )
  set All_nb_modes = ( 8 )
  foreach nb_modes ( ${All_nb_modes} )

    set All_ObsCase = ( 1 2 3 )
    set All_ObsCase = ( 1 )
    foreach ObsCase ( ${All_ObsCase} )

      set All_correct_drift = ( 1 0 )
      set All_correct_drift = ( 1 )
      foreach correct_drift ( ${All_correct_drift} )

        # pyReDA folder result : default value
        
        set dir_redlum=ITHACAoutput/Reduced_coeff_${nb_modes}${mot_DA}${mot_AdvC}_${dt_run}_${nPart}_${mot_redlum1}${mot_HilbertSpacea}_centered

        set dir3_pyReDA_result = _DADuration_${DADuration}_ObsCase_${ObsCase}_beta_2_1_nSimu_100_nMut_-1_nPcl_100
        
        set dir1_pyReDA_result = ~/Bureau/MORAANE/3rdresult/${type_data_C}_${nb_modes}_modes_loaded${mot_DAa}_CppROM_Cpptestbasis/${redlumcpp_code_version}/${mot_AdvC}${mot_HilbertSpacea}${mot_redlum2}
        
        set dir1_pyReDA_result =  ${rdresult_dir}/${case_OpenFoam}_${nb_modes}_modes_loaded${mot_DAa}_${ROM_DATA}/${redlumcpp_code_version}/${mot_AdvC}${mot_HilbertSpacea}${mot_redlum2}
        
        if ( ${correct_drift} == 1 ) then 
          set dir2_pyReDA_result = fake_real_data        
        else
          set dir2_pyReDA_result = _no_correct_drift/fake_real_data
        endif
        
        if ( ${code_HilbertSpacea} == 0 ) then
          set dir3_pyReDA_result=_DADuration_${DADuration}_ObsCase_${ObsCase}${mot_DAb}_beta_2_${Assimilation}_nSimu_100_nMut_-1_nPcl_${nPart}
        else
          set dir3_pyReDA_result=_DADuration_${DADuration}_ObsCase_${ObsCase}${mot_DAb}_beta_2_${Assimilation}_nSimu_500_nMut_-1_nPcl_${nPart}
        endif
        
        set dir_pyReDA_result = ${dir1_pyReDA_result}/${dir2_pyReDA_result}/${dir3_pyReDA_result}
        
#         if ( ${correct_drift} == 1 ) then 
#             set dir_pyReDA_result = ${rdresult_dir}/${case_OpenFoam}_${nb_modes}_modes_${ROM_DATA}/${redlumcpp_code_version}/fake_real_data/${dir3_pyReDA_result}            
#         else
#             set dir_pyReDA_result = ${rdresult_dir}/${case_OpenFoam}_${nb_modes}_modes_${ROM_DATA}/${redlumcpp_code_version}/_no_correct_drift/fake_real_data/${dir3_pyReDA_result}
#         endif
        #------------------------------------------------------------------------------

        set dir_data_space = ${DIR0}/ITHACAoutput/spatialModes_${nb_modes}modes

        \cp util/extractU_from_ROM.csh .
        \cp util/IsoQ.csh .
        \cp util/montage_IsoQ_ROM.csh .
          
        ########### True State : created if not already exist
        
        set TrueState_base_dir = TrueState_${nb_modes}modes   
        if (!( -e ${DIR0}/${TrueState_base_dir} )) then

          set temporal_file = ${dir_pyReDA_result}/temporalModeSimulation.txt
         echo " tcsh extractU_from_ROM.csh ${t_first} ${t_last} ${dir_data_space} ${temporal_file}"
              
          tcsh extractU_from_ROM.csh ${t_first} ${t_last} ${dir_data_space} ${temporal_file}
              
          tcsh IsoQ.csh ${t_first} ${t_last} ${DIR0}/${TrueState_base_dir}
        
        else

          echo ""; echo "folder ${DIR0}/${TrueState_base_dir} already exist" ; echo ""

        endif
        
        ########### Assimilation State : created if not already exist
        
        set RedLumPart_base_dir = RedLumPart_${nb_modes}modes_${redlumcpp_code_version}${dir3_pyReDA_result}
        
        if (!( -e ${DIR0}/${RedLumPart_base_dir} )) then

          set temporal_file = ${dir_pyReDA_result}/temporalModeDAresult.txt
          \cp -R ${DIR0}/${dir_redlum}/U_reconstruct ${DIR0}/${RedLumPart_base_dir}
          \cp -R ${DIR0}/constant ${DIR0}/${RedLumPart_base_dir}
          \cp -R ${DIR0}/system ${DIR0}/${RedLumPart_base_dir}
          \cp -R util ${DIR0}/${RedLumPart_base_dir}    
            
          tcsh IsoQ.csh ${t_first} ${t_last} ${DIR0}/${RedLumPart_base_dir}
        
        else

          echo ""; echo "folder ${DIR0}/${RedLumPart_base_dir} already exist" ; echo ""

        endif

        ######### Movie 

        tcsh montage_IsoQ_ROM.csh ${DIR0} ${TrueState_base_dir} ${RedLumPart_base_dir} ${t_first} ${t_last}

      end

    end

  end

end

#------------------------------------------------------------------------------
