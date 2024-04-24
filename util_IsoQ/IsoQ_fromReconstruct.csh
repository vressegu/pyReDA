#!/bin/tcsh
#
# Laurence Wallian - ACTA - OPAALE - INRAE Rennes [February 2024]
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
# NOTE : U files have been obtained with option 
#                  onLineReconstruct=0
#              in system/ITHACAdict file
#              - directory from ROM result = U_reconstructSim
#              - directory from Assimilation = U_reconstruct 
#
#------------------------------------------------------------------------------
#
# USAGE : tcsh IsoQ_fromReconstruct.csh arg1
# 
#  Input parameters :
#    - arg1 : subdirectory of ITHACAoutput where are U_reconstructSim and U_reconstruct
#
#------------------------------------------------------------------------------
#
# Scripts used :
#   - util/IsoQ.csh : postprocess OpenFoam for IsoQ, and creates PNG files
#   - util/IsoQ_GEO_LES3900_model.py : model file for pvbatch
#
#------------------------------------------------------------------------------

set dir_ici = ` pwd `

# current directory : where are U_reconstructSim and U_reconstruct

# default value : current directory (for example .../data_red_lum_cpp/DNS300-GeoLES3900/ROMDNS-v3.3.2/ITHACAoutput/Reduced_coeff_...)
set DIR1 = `pwd `

# other value
if ( $1 != "" ) set DIR1 = $1

# ROM directory (for example .../data_red_lum_cpp/DNS300-GeoLES3900/ROMDNS-v3.3.2)
set DIR0 = ` echo ${DIR1} | awk -F'/' 'BEGIN{c=1}{ for (i=1;i<=NF;i++) { if ($i=="ITHACAoutput") c=0;  if (c==1) printf("/%s",$i); }}' `
set nModes = ` echo ${DIR1} | awk -F'/' 'BEGIN{c=0}{ for (i=1;i<=NF;i++) { if (c==1) print $i; if ($i=="ITHACAoutput") c=c+1; }}' | head -1 | \
awk -F'_' 'BEGIN{c=0}{ for (i=1;i<=NF;i++) { if (c==1) print $i; if ($i=="coeff") c=c+1; }}' | head -1 `

# spatial mode directory associated with nModes value
set dir_data_space = ${DIR0}/ITHACAoutput/spatialModes_${nModes}modes

#------------------------------------------------------------------------------
# directory util_IsoQ contains necessary files : IsoQ_fromReconstruct.csh, IsoQ.csh and IsoQ_GEO_LES3900_model.py
if ( -e ${DIR1}/util ) then
  \cp ~/Bureau/MORAANE/pyReDA/util_IsoQ/IsoQ_fromReconstruct.csh ${DIR1}/util
  \cp ~/Bureau/MORAANE/pyReDA/util_IsoQ/IsoQ.csh ${DIR1}/util
  \cp ~/Bureau/MORAANE/pyReDA/util_IsoQ/IsoQ_GEO_LES3900_model.py ${DIR1}/util
else
  \cp -R util_IsoQ ${DIR1}/util
endif

cd ${DIR1}

# time first and max time last

cd U_reconstructSim
set all_t = ` ls | sed s/'[a-z;A-Z;-;_]'//g | awk '{ if ($1!=".") print $1 }' ` 
set t_first = ` echo ${all_t} | awk '{ print $1 }' `
set t_first = ` echo ${all_t} | awk '{ if ($1 == 0) print $2; else print $1 }' `
set t_last = ` echo ${all_t} | awk '{ print $NF }' `
cd ..

\cp util/IsoQ.csh .
  
########### True State 
\cp -R ${DIR0}/constant U_reconstructSim
\cp -R ${DIR0}/system U_reconstructSim
\cp -R util U_reconstructSim
tcsh IsoQ.csh ${DIR1}/U_reconstructSim ${t_first} ${t_last}

########### Assimilation State
\cp -R ${DIR0}/constant U_reconstruct
\cp -R ${DIR0}/system U_reconstruct
\cp -R util U_reconstruct
tcsh IsoQ.csh ${DIR1}/U_reconstruct ${t_first} ${t_last}

######### Movie 
if -e image \rm -R image; mkdir image
foreach t ( ${all_t} )

  echo -n " ${t}"
  set t_IsoQ = ` echo ${t} | awk '{ printf("%6.0f",$1*100.) }' `
  montage \
    U_reconstructSim/IsoQ/IsoQ2_Z15_t${t_IsoQ}.png  \
    U_reconstruct/IsoQ/IsoQ2_Z15_t${t_IsoQ}.png \
    -geometry +1+1 -tile 2x1 image/t${t_IsoQ}.png

end

set mp4_file = IsoQ.mp4
if -e ${mp4_file} \rm ${mp4_file}
set code_ppt = 1 # if =1, readable in powerpoint and by VLC when Preference/Codec/Hardware-accelerated desactivated
if ( ${code_ppt} == 1 ) then
  #ffmpeg -r 18 -i tmp_movie/%04d.png -crf 18 -vcodec libx264 -pix_fmt yuv420p ${mp4_file}
  cat image/t*.png | ffmpeg -f image2pipe -i - -crf 18 -vcodec libx264 -pix_fmt yuv420p ${mp4_file}
else
  #ffmpeg -r 10 -i tmp_movie/%04d.png ${mp4_file}
  cat image/t*.png | ffmpeg -r 10 -f image2pipe -i - ${mp4_file}
endif

set mp4_copy = ` echo ${DIR1} | awk -F'/' '{ printf("%s.mp4", $NF) }' `
\cp ${mp4_file} ${dir_ici}/${mp4_copy}
#echo ""; echo "Cf. file ${mp4_file}\n (mplayer -speed 0.5 ${mp4_file}) "; echo ""

#------------------------------------------------------------------------------

cd ${dir_ici}
echo ""; echo "Cf. file ${mp4_copy}\n (mplayer -speed 0.5 ${mp4_copy}) "; echo ""

#------------------------------------------------------------------------------
