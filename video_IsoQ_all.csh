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
                                 
set dir_ROMDNS = ` cat ${fic_run_info} | sed s/"^ #"/"#"/g | grep -v "^#" | \
                                 grep "redlumcpp_code_version" | awk '{ print $2 }' | tail -1 `
                                 
set DIR0 = ${dir_OpenFoam}/${case_OpenFoam}/${dir_ROMDNS}
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
foreach ROM_DATA ( ${All_ROM_DATA} )

  set All_nb_modes = ( 8 4 2 )
  foreach nb_modes ( ${All_nb_modes} )

    set All_ObsCase = ( 1 2 3 )
    foreach ObsCase ( ${All_ObsCase} )

      set All_correct_drift = ( 1 0 )
      foreach correct_drift ( ${All_correct_drift} )

        # pyReDA folder result : default value
        
        set dirLast_pyReDA_result = _DADuration_${DADuration}_ObsCase_${ObsCase}_beta_2_1_nSimu_100_nMut_-1_nPcl_100
        
        if ( ${correct_drift} == 1 ) then 
            set dir_pyReDA_result = ${rdresult_dir}/${case_OpenFoam}_${nb_modes}_modes_${ROM_DATA}/${dir_ROMDNS}/fake_real_data/${dirLast_pyReDA_result}
        else
            set dir_pyReDA_result = ${rdresult_dir}/${case_OpenFoam}_${nb_modes}_modes_${ROM_DATA}/${dir_ROMDNS}/_no_correct_drift/fake_real_data/${dirLast_pyReDA_result}
        endif

        #------------------------------------------------------------------------------

        set dir_data_space = ${DIR0}/ITHACAoutput/spatialModes_${nb_modes}modes

        \cp util/extractU_from_ROM.csh .
        \cp util/IsoQ.csh .
        \cp util/montage_IsoQ_ROM.csh .
          
        ########### True State : creted if not already exist
        
        set TrueState_base_dir = TrueState_${nb_modes}modes  
        
        if (!( -e ${DIR0}/TrueState_${nb_modes}modes )) then

          set temporal_file = ${dir_pyReDA_result}/temporalModeSimulation.txt
#          tcsh extractU_from_ROM.csh ${t_first} ${t_last} ${dir_data_space} ${temporal_file}
              
#          tcsh IsoQ.csh ${t_first} ${t_last} ${DIR0}/${TrueState_base_dir}
        
        else

          echo ""; echo "folder ${DIR0}/TrueState_${nb_modes}modes already exist" ; echo ""

        endif

        ########## Particle Mean
        
        # with or without time shift when assimilation : default=0 => DO NOT USE time_shift=1 !!!!
        set time_shift=0
      # set time_shift=1 

        set temporal_file = ${dir_pyReDA_result}/temporalModeDAresult.txt
#        tcsh extractU_from_ROM.csh ${t_first} ${t_last} ${dir_data_space} ${temporal_file} ${time_shift}
        
        set RedLumPart_base_dir = RedLumPart_${nb_modes}modes_${ROM_DATA}${dirLast_pyReDA_result}

#         # definining time step
#         cd ${DIR0}/${RedLumPart_base_dir}
#         set All_t_default = ` lsd | grep -v '[a-Z;A-Z]' | awk '{ printf("%.0f %s\n",1000.*($1+0.), $1) }' | sort -n | awk '{ print $2 }' `
#         set dt = ` echo ${All_t_default} | awk '{ print $2-$1 }' | head -1 `
#         cd ${dir_ici}
 
#         # redefining first and last time
#         if ( ${time_shift} == 1 ) then
#           set t_last = ` echo ${t_last} ${dt} | awk '{ print $1+$2 }' `
#           set t_first = ` echo ${t_first} ${dt} | awk '{ print $1+$2 }' `        
#         else
#           set t_last = ` echo ${t_last} ${dt} | awk '{ print $1-$2 }' `
#         endif
#         
         set RedLumPart_new_dir = ${RedLumPart_base_dir}_correct_drift${correct_drift}
#         if -e ${DIR0}/${RedLumPart_new_dir} \rm -R ${DIR0}/${RedLumPart_new_dir}
#         \mv ${DIR0}/${RedLumPart_base_dir} ${DIR0}/${RedLumPart_new_dir} 
        
#        tcsh IsoQ.csh ${t_first} ${t_last} ${DIR0}/${RedLumPart_new_dir}

        ######### Movie 

#        tcsh montage_IsoQ_ROM.csh ${DIR0} ${TrueState_base_dir} ${RedLumPart_new_dir} ${t_first} ${t_last}

       set info = ` echo ${RedLumPart_new_dir} | awk -F'/' '{ print $NF }' | sed s/"RedLumPart_"//g `
       set dir_montage = ${DIR0}/IsoQ_${info}
       
        echo ""; echo "creating MP4 movie for t=[${t_first}:${t_last}]"; echo ""
        
        cd ${dir_montage}
        
        if -e tmp_movie \rm -R tmp_movie; mkdir tmp_movie

        set mp4_file = ${dir_montage}_t${t_first}_t${t_last}.mp4
        
        cd ${DIR0}/../openfoam_data
        set All_t = ` lsd | grep -v '[a-Z;A-Z]' `
        cd ${dir_ici}
        set All_t = ` echo ${All_t} | awk -v t1=${t_first} -v t2=${t_last} '{ for (i=1;i<=NF; i++) { t=$i+0; if ((t>=t1+0.) && (t<=t2+0.)) print $i } }' `

        set i = 1
        foreach t ( ${All_t} )

          set t_IsoQ = ` echo ${t} | awk '{ printf("%5.0f",$1*100.) }' `
          set png_file = t${t_IsoQ}.png
          set nom = `echo ${i} | awk '{ printf("%04d",$1) }' `
          \cp ${dir_montage}/${png_file} ${dir_montage}/tmp_movie/${nom}.png
          
          set i = ` echo ${i} | awk '{ print $1+1}' `
          
        end

        if -e ${mp4_file} \rm ${mp4_file}
        #ffmpeg -r 10 -i ${dir_montage}/tmp_movie/%04d.png ${mp4_file}
        
        ffmpeg -r 18 -i ${dir_montage}/tmp_movie/%04d.png -crf 18 -vcodec libx264 -pix_fmt yuv420p  ${mp4_file}
        
        cd ${dir_ici}
        
        echo ""; echo "Cf. file ${mp4_file}\n (mplayer -speed 0.5 ${mp4_file}) "; echo ""

      end

    end

  end

end

#------------------------------------------------------------------------------
