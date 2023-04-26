#!/bin/tcsh
#
# Laurence Wallian - ACTA - OPAALE - INRAE Rennes [Juin 2022 : Avril 2023]
#
# MORAANE project : Scalian - INRAE
#
#------------------------------------------------------------------------------
#
# MORAANE : movie including 3 figures
#   - left = IsoQ from DNS (directory openfoam_data/IsoQ)
#   - right up = FakePIV for ux (directory FakePIV_noise...)
#   - right down = FakePIV for uy (directory FakePIV_noise...)
#
#------------------------------------------------------------------------------
#
# USAGE : tcsh montage_IsoQ_FakePIV.csh arg1 arg2 arg3 arg4
# 
#  Input parameters :
#    - arg1 : DNS case folder (present folder)
#                (example : .../RedLUM/data_red_lum_cpp/DNS300-GeoLES3900)
#    - arg2 : FakePIV folder from (default FakePIV_noise2)
#    - arg3 : Start time (default : 600)
#    - arg4 : End time (default : 670)
#
#------------------------------------------------------------------------------

# current directory

set dir_ici = ` pwd `
alias lsd  ' ls -l | awk '\''{i=0; i=index($1,"d"); if (i==1) print $9 }'\'' '

# DIR0 folder :  for example .../RedLUM/data_red_lum_cpp/DNS300-GeoLES3900

# DIR0 folder : default value
set DIR0 = `pwd `

# DIR0 folder : input value
if ( $1 != "" ) set DIR0 = $1

# FakePIV folder : for example FakePIV_noise2

# DIR1 folder : default value
set DIR1 = FakePIV_noise2

# DIR1 folder : default value
if ( $2 != "" ) set DIR1 = $2

# first time for creating movie

# time first : default value
set t_first = 600

# time first : input value
if ( $3 != "" ) set t_first = $3

# last time for creating movie

# time last : default value
set t_last = 670

# time last : input value
if ( $4 != "" ) set t_last = $4

#------------------------------------------------------------------------------

set dir_montage = ${DIR0}/IsoQ_${DIR1}
if -e ${dir_montage} \rm -R ${dir_montage}; mkdir ${dir_montage}

set dir_FakePIV = ${DIR0}/${DIR1}

set dir_IsoQ = ${DIR0}/openfoam_data/IsoQ

if ((-e ${dir_IsoQ}) && (-e ${dir_FakePIV})) then

  cd ${dir_FakePIV}
  set All_t = ` lsd | grep -v '[a-Z;A-Z]' `
  cd ${dir_ici}
  set All_t = ` echo ${All_t} | awk -v t1=${t_first} -v t2=${t_last} '{ for (i=1;i<=NF; i++) { t=$i+0; if ((t>=t1+0.) && (t<=t2+0.)) print $i } }' `

  # PNG files
  
  echo ""; echo "creating PNG files for t=[${t_first}:${t_last}]"; echo ""
  
  foreach t ( ${All_t} )

    echo -n " ${t}"
    set t_IsoQ = ` echo ${t} | awk '{ printf("%5.0f",$1*100.) }' `

    convert -crop +0+30 -crop -0-30 ${dir_FakePIV}/${t}/PIV_new_Ux.png tmp1.png
    convert -crop +0+30 -crop -0-30 ${dir_FakePIV}/${t}/PIV_new_Uy.png tmp2.png
    montage tmp1.png tmp2.png -geometry +1+1 -tile 1x2 tmp.png
    montage \
      ${dir_IsoQ}/IsoQ2_Z15_t${t_IsoQ}.png \
      tmp.png \
      -geometry +1+1 -tile 2x1 ${dir_montage}/t${t_IsoQ}.png

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
  ffmpeg -r 18 -i ${dir_montage}/tmp_movie/%04d.png -crf 18 -vcodec libx264 -pix_fmt yuv420p  ${mp4_file}
  
  cd ${dir_ici}
  
  echo ""; echo "Cf. file ${mp4_file}\n (mplayer -speed 0.5 ${mp4_file}) "; echo ""
 
else

  echo "!\!\!\ ${dir_IsoQ} or ${dir_FakePIV} NOT FOUND \!\!\!"
  echo "!\!\!\ You should use script openfoamDNS_to_pseudoPIV_all.csh before !\!\!"
  echo ""

endif

#------------------------------------------------------------------------------
