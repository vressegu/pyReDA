#!/bin/tcsh
#
# Laurence Wallian - ACTA - OPAALE - INRAE Rennes [Juin 2022 : Avril 2023]
#
# MORAANE project : Scalian - INRAE
#
#  ------------------------------------------------------------------------------
#
# VELOCITY in test basis : from 
#    - True state (TrueState) 
#      (Cf. dashed black line in pyReDa result)
#   or 
#    - Red LUM particles mean (RedLumPart)
#      (Cf. red line in pyReDa result)
#
#------------------------------------------------------------------------------
#
# NOTE : pyReDA must have been used before to generate
#              - temporalModeSimulation.txt : ROM result
#             OR
#              - temporalModeDAresult.txt : DA result
#
#------------------------------------------------------------------------------
#
# USAGE : tcsh extractU_from_ROM.csh arg1 arg2 arg3 arg4
# 
#  Input parameters :
#    - arg1 : Start time (default : 600)
#    - arg2 : End time (default : 670)
#    - arg3 : spatial modes folder
#                (default : present directory)
#    - arg4 : temporal mode file created by pyReDA run
#                (default : arg3/temporalModesSimulation_...modes/U_mat.txt)
#
#------------------------------------------------------------------------------

set dir_ici = `pwd`
set dir_ici_SED = `echo ${dir_ici} | sed s/"\/"/"\\\/"/g`

#------------------------------------------------------------------------------

# first time for reconstructed velocity
set timeStart = 600
if ( $1 != "" ) set timeStart = $1

# last time for reconstructed velocity
set timeEnd = 670
if ( $2 != "" ) set timeEnd = $2

# PATH for ROM spatial mode directory (ex : .../ROM-.../ITHACAoutput/spatialModes_...modes)
# ex : /media/laurence.wallian/Val4To/RedLUM/data_red_lum_cpp/DNS300-GeoLES3900/ROM-v3.1.0/ITHACAoutput/spatialModes_2modes
set dir_data_space = ${dir_ici}
if ( $3 != "" ) set dir_data_space = $3
set dir_data_space_SED = ` echo ${dir_data_space} | sed s/"\/"/"\\\/"/g `

# number of modes
set nb_modes = ` echo ${dir_data_space} | awk -F'/' '{ print $NF }' | sed s/"spatialModes_"//g | sed s/"modes"//g `

# PATH for ROM temporal file (ex : .../ROM-.../ITHACAoutput/temporalModesSimulation_...modes/U_mat.txt)
# ex : /media/laurence.wallian/Val4To/RedLUM/data_red_lum_cpp/DNS300-GeoLES3900/ROM-v3.1.0/ITHACAoutput/temporalModesSimulation_2modes/U_mat.txt
set temporal_file = ${dir_data_space}/temporalModesSimulation_${nb_modes}modes/U_mat.txt
if ( $4 != "" ) set temporal_file = $4

set code = ` head -1 ${temporal_file} | awk -v nb_modes=${nb_modes} '{ if (NF==nb_modes) print 1; else print 0 }' `
if ( ${code} != 1 ) then

   echo ""
   echo "\! OUPS \! number of modes defined in spatial mode directory (=${nb_modes}) NOT equal to this used in temporal file \!"
   echo ""
   exit()
   
else

   echo ""
   echo "OK, number of modes defined in spatial mode directory (=${nb_modes})  equal to this used in temporal file"
   echo ""

endif

# vect_num_mode_to_reverse : for some modes, value must be reversed when ROM=C++ and DATA=matlab

set vect_num_mode_to_reverse = ()

set code_CppROM = ` echo ${temporal_file} | grep "_CppROM" | grep -v "_CppROM_Cpptestbasis" | wc -l `
if ( ${code_CppROM} == 1 ) then
    set test_info_file = ` echo ${temporal_file} | awk -F'/' '{ for (i=1;i<NF;i++) printf("%s/",$i); print "text.info" }' `
    if -e ${test_info_file} then
        set vect_num_mode_to_reverse = ` cat ${test_info_file} |  grep "\-mode" | head -1 | awk -F'[' '{ print $NF }' | sed s/"]"/" "/g | sed s/","/" "/g `
    endif
endif

# non inverse value
set vect_num_mode_to_reverse = ()

if -e vect_num_mode_to_reverse.txt \rm vect_num_mode_to_reverse.txt; touch vect_num_mode_to_reverse.txt
set n=0
while ( ${n} != 16 )
    set n = ` echo ${n} | awk '{ print 1+$1 }' `
    echo ${vect_num_mode_to_reverse} | \
    awk -v n=${n} '{ C=1; for (i=1;i<=NF;i++) {if ($i==n) C=-1}}END{ print n,C }'  >> vect_num_mode_to_reverse.txt
end

# dir_extractU = TrueState or RedLumPart

set N_time_step = 1
set code_dir  = ` echo ${temporal_file} | sed s/"\.txt"//g | grep "temporalModeSimulation" | wc -l `
if ( ${code_dir} == 1 ) then
    set dir_extractU = TrueState_${nb_modes}modes
else
    set ROM_DATA = ` echo ${temporal_file} | sed s/"\/"/"\n"/g | sed s/"_modes_"/"\n"/g | grep "ROM" | grep -v "ROM-" `
    set N_time_step = ` echo ${temporal_file} | sed s/"\/"/"\n"/g | sed s/"_nPcl_"/"\n_nPcl_"/g | grep "_nPcl_" | sed s/"_nPcl_"//g `
    set Other_info = ` echo ${temporal_file} | sed s/"\/temporalModeDAresult\.txt"//g | awk -F'/' '{ print $NF }' `
    set dir_extractU = RedLumPart_${nb_modes}modes_${ROM_DATA}${Other_info}
endif

set src_ROM_case = ${dir_data_space}/../..

set openfoam_path = ${src_ROM_case}/../openfoam_data
cd ${openfoam_path}
set All_t_default = ` lsd | grep -v '[a-Z;A-Z]' | awk '{ printf("%.0f %s\n",1000.*($1+0.), $1) }' | sort -n | awk '{ print $2 }' `
set All_t = ` echo ${All_t_default} | \
                      awk -v t1=${timeStart} -v t2=${timeEnd} '{ for (i=1;i<=NF; i++) { t=$i+0.; if ((t>=t1+0.) && (t<=t2+0.)) print $i } }' `
set N_t = ` echo ${All_t} | awk '{ print NF }' `
cd ${dir_ici}

#------------------------------------------------------------------------------

set path_extractU = ${src_ROM_case}/${dir_extractU}
if -e ${path_extractU} \rm -R ${path_extractU}; mkdir ${path_extractU}
cd ${path_extractU}
\cp -R ${src_ROM_case}/constant .
\cp -R ${src_ROM_case}/system .

if -e tmp_dir \rm -R tmp_dir; mkdir tmp_dir
cd tmp_dir

\cp -R ${dir_data_space}/* .
set All_mode = ` lsd | sed s/'[a-z;A-Z;-;_]'//g | awk '{ if (NF!=0) print $1 }' | sort -n `
set first_mode = ` echo ${All_mode} | awk '{ print $1 }' `
set last_mode = ` echo ${All_mode} | awk '{ print $NF }' `

# mean
set mode_mean = `echo ${last_mode} | awk '{ print 1+$1 }' `
set dir_mean = ${src_ROM_case}/ITHACAoutput/mean
if (!(-e ${mode_mean})) then
  mkdir ${mode_mean}
  \cp ${dir_mean}/1/*  ${mode_mean}
  \cp -R ${mode_mean} mean
endif

# temporal mode file
if -e temporal_mode_U_mat.txt \rm temporal_mode_U_mat.txt
if ( ${dir_extractU} == TrueState_${nb_modes}modes ) then
  awk -v N=${N_time_step} '{ if (NR%N == 0) print $0 }' ${temporal_file} > temporal_mode_U_mat.txt 
else
  awk -v N=${N_time_step} '{ if (NR%N == 1) print $0 }' ${temporal_file} > temporal_mode_U_mat.txt 
endif

#------------------------------------------------------------------------------

if ( !( -e SOS )) mkdir SOS

set All_mode = ( ${mode_mean} ${All_mode} )
foreach mode ( ${All_mode} )
  if (!(-e SOS/${mode})) then
    \mv ${mode} SOS
  else
    chmod -w -R ${mode}
    \rm -R ${mode}
  endif
end

set first_mode = ` echo ${All_mode} | awk '{ print $1 }' `
set last_mode = ` echo ${All_mode} | awk '{ print $NF-1 }' `

echo""; echo "MODES = [${first_mode}:${last_mode}] (= ${All_mode})"; echo ""

# ux_mean+ux_mode1*b1(t)+ux_mode2*b2(t)+...

set code = 1
if ( ${code} != 0 ) then

  set n_t = 1
  set n_t_max = ` echo ${N_t} | awk '{ print 1+$1 }' `
  
  while ( ${n_t} != ${n_t_max} )
  
    set t = ` echo ${All_t} | awk -v n=${n_t} '{ print $n }' `

    foreach mode ( ${All_mode} )
      
      if ( ${mode} == ${mode_mean} ) then
        set bt = 1.
      else
        set bt = `cat temporal_mode_U_mat.txt | awk -v n=${n_t} -v m=${mode} '{ if (NR==n) print $m }' `
      endif
 
      echo "--- mode ${mode} t=${t} -> bt(t=${t})*phi${mode} with bt=${bt} ---"

      if (!(-e SOS/${mode})) then
        \mv ${mode} SOS
      else
        if -e ${mode} \rm -R ${mode}
      endif
       
      set C = ` awk -v mode=${mode} '{ if ($1==mode) print $2 }' ${dir_ici}/vect_num_mode_to_reverse.txt `
      
      if (!( -e ${mode})) mkdir ${mode}
      cat SOS/${mode}/U | sed s/"("/"( "/g | sed s/")"/" )"/g | \
        awk -v C=${C} -v bt=${bt} '{ \
          if ((NF==5) && ($1="(")) { \
            x=$2+0.; y=$3+0.; z=$4+0.; printf("( %f %f %f )\n", C*bt*x ,C*bt*y, C*bt*z); \
          } else print $0 \
        }' > ${mode}/U
    end
  
    set dir_bt = `echo ${All_mode} | awk '{ for (i=1;i<=NF;i++) printf("%d",$i*10);  }' `
    if ( !(-e ${dir_bt})) mkdir ${dir_bt}
        
    foreach mode ( ${All_mode} )
 
      if ( ${mode} != ${mode_mean} ) then 
        echo "--- mode ${mode}     t=${t} -> mean+ bt(t=${t})*phi${mode}+... ---"
      else
        echo "--- mean value t=${t} -> mean+ bt(t=${t})*phi${mode}+... ---"
      endif
   
      if ( ${mode} == ${mode_mean} ) then
        \cp ${mode}/U ${dir_bt}
      else
        if -e U_tmp \rm U_tmp
        paste ${mode}/U ${dir_bt}/U | \
        awk '{ if ((NF==10) && ($1="(")) { \
            x=$2+$7+0.; y=$3+$8+0.; z=$4+$9+0.; printf("( %f %f %f )\n",x,y,z); \
          } else { for (i=1;i<=NF/2;i++) printf("%s ",$i); print ""; } \
        }' > U_tmp
        \mv U_tmp ${dir_bt}/U
      endif
      
      #paste ${dir_bt}/U ${mode}/U | head -25
      \rm -R ${mode}
      
    end
  
    # mv result and restore state
    \mv ${dir_bt} ../${t}
    \cp -R SOS/* .
    
    set n_t = `echo ${n_t} | awk '{ print 1+$1 }' `
     
  end

endif

#------------------------------------------------------------------------------

cd ${dir_ici}

#\cp -R ${dir_extractU} ${src_ROM_case}

echo ""
echo "Cf. time files in ${src_ROM_case}/${dir_extractU}"
echo ""

#------------------------------------------------------------------------------

