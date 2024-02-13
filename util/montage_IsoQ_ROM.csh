#!/bin/tcsh
#
# Laurence Wallian - ACTA - OPAALE - INRAE Rennes [Juin 2022 : Avril 2023]
#                                                                                  [February 2024]
#
# MORAANE project : Scalian - INRAE
#
#------------------------------------------------------------------------------
#
# MORAANE : movie including 2 figures
#   - left = IsoQ from ROM result : True State
#   - right = IsoQ from DA result : RedLum Particle
#
#------------------------------------------------------------------------------
#
# NOTE 1 : pyReDA must have been used before to generate
#                - temporalModeSimulation.txt : ROM result
#                - temporalModeDAresult.txt : DA result
#
# NOTE 2 : after using pyReDA, IsoQ must be created by
#                 IsoQ_all.csh script (which uses util/extractU_from_ROM.csh and util/IsoQ.csh)
#
#------------------------------------------------------------------------------
#
# USAGE : tcsh montage_IsoQ_ROM.csh arg1 arg2 arg3 arg4 arg5
# 
#  Input parameters :
#    - arg1 : ROM folder (present folder)
#                (example : .../RedLUM/data_red_lum_cpp/DNS300-GeoLES3900/ROM-v3.1.2)
#    - arg2 : reconstructed folder from ROM result (default TrueState_2modes)
#    - arg3 : reconstructed folder from pyReDA result (default RedLumPart_2modes...)
#    - arg4 : Start time (default : 600)
#    - arg5 : End time (default : 670)
#
#------------------------------------------------------------------------------

# current directory

set dir_ici = ` pwd `
alias lsd  ' ls -l | awk '\''{i=0; i=index($1,"d"); if (i==1) print $9 }'\'' '

# dir_ROM folder :  for example .../RedLum_from_OpenFoam/DNS300-GeoLES3900/ROM-v3.1.2

# dir_ROM folder : default value
set dir_ROM = `pwd`

# dir_ROM folder : input value
if ( $1 != "" ) set dir_ROM = $1

# TrueState folder

# TrueState folder : default value
set dir_TrueState = TrueState_2modes

# TrueState folder : input value
if ( $2 != "" ) set dir_TrueState = $2

# RedLumPart folder

# RedLumPart folder : default value
set dir_RedLumPart = RedLumPart_2modes_CppROM_Cpptestbasis_DADuration_70_ObsCase_1_beta_2_1_nSimu_100_nMut_-1_nPcl_100 

# RedLumPart folder : input value
if ( $3 != "" ) set dir_RedLumPart = $3

# first time for creating movie

# time first : default value
set t_first = 600

# time first : input value
if ( $4 != "" ) set t_first = $4

# last time for creating movie

# time last : default value
set t_last = 670

# time last : input value
if ( $5 != "" ) set t_last = $5

#------------------------------------------------------------------------------

set info = ` echo ${dir_RedLumPart} | awk -F'/' '{ print $NF }' | sed s/"RedLumPart_"//g `
set dir_montage = ${dir_ROM}/IsoQ_${info}
if -e ${dir_montage} \rm -R ${dir_montage}; mkdir ${dir_montage}

if ((-e ${dir_ROM}/${dir_TrueState}) && (-e ${dir_ROM}/${dir_RedLumPart})) then

  cd ${dir_ROM}/../openfoam_data
  set All_t = ` lsd | grep -v '[a-Z;A-Z]' `
  cd ${dir_ici}
  set All_t = ` echo ${All_t} | awk -v t1=${t_first} -v t2=${t_last} '{ for (i=1;i<=NF; i++) { t=$i+0; if ((t>=t1+0.) && (t<=t2+0.)) print $i } }' `
  
  # PNG files
  
  echo ""; echo "creating PNG files for t=[${t_first}:${t_last}]"; echo ""

  foreach t ( ${All_t} )
    
    echo -n " ${t}"
    set t_IsoQ = ` echo ${t} | awk '{ printf("%5.0f",$1*100.) }' `

    if ((-e ${dir_ROM}/${dir_TrueState}/IsoQ/IsoQ2_Z15_t${t_IsoQ}.png) && (-e ${dir_ROM}/${dir_RedLumPart}/IsoQ/IsoQ2_Z15_t${t_IsoQ}.png)) then
      montage \
        ${dir_ROM}/${dir_TrueState}/IsoQ/IsoQ2_Z15_t${t_IsoQ}.png  \
        ${dir_ROM}/${dir_RedLumPart}/IsoQ/IsoQ2_Z15_t${t_IsoQ}.png \
        -geometry +1+1 -tile 2x1 ${dir_montage}/t${t_IsoQ}.png
    endif
    
  end
  
  echo ""
  echo "";  echo "Cf. PNG files in ${dir_montage}"; echo ""
  
  # movie

  echo ""; echo "creating MP4 movie for t=[${t_first}:${t_last}]"; echo ""
  
  cd ${dir_montage}
  
  if -e tmp_movie \rm -R tmp_movie; mkdir tmp_movie

  set mp4_file = ${dir_montage}.mp4

  set i = 1
  foreach t ( ${All_t} )

    set t_IsoQ = ` echo ${t} | awk '{ printf("%5.0f",$1*100.) }' `
    set png_file = t${t_IsoQ}.png
    set nom = `echo ${i} | awk '{ printf("%04d",$1) }' `
    \cp ${dir_montage}/${png_file} tmp_movie/${nom}.png
    
    set i = ` echo ${i} | awk '{ print $1+1}' `
    
  end

  if -e ${mp4_file} \rm ${mp4_file}
  #ffmpeg -r 10 -i tmp_movie/%04d.png ${mp4_file}
  ffmpeg -r 18 -i tmp_movie/%04d.png -crf 18 -vcodec libx264 -pix_fmt yuv420p  ${mp4_file}
  
  cd ${dir_ici}
  
  echo ""; echo "Cf. file ${mp4_file}\n (mplayer -speed 0.5 ${mp4_file}) "; echo ""
 
else

  echo "\!\!\! ${dir_TrueState} or ${dir_RedLumPart} NOT FOUND \!\!\!"
  echo "\!\!\! You should use script IsoQ_all.csh before \!\!\!"
  echo ""

endif

#------------------------------------------------------------------------------
