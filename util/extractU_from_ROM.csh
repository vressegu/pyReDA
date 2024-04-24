#!/bin/tcsh
#
# Laurence Wallian - ACTA - OPAALE - INRAE Rennes [Juin 2022 : Avril 2023]
#                                                                                  [February 2024]
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
# USAGE : tcsh extractU_from_ROM.csh arg1 arg2 arg3 arg4 arg5
# 
#  Input parameters :
#    - arg1 : Start time (default : 600)
#    - arg2 : End time (default : 670)
#    - arg3 : spatial modes folder
#                (default : present directory)
#    - arg4 : temporal mode file created by pyReDA run
#                (default : arg3/temporalModesSimulation_...modes/U_mat.txt)
#    - arg5 : time step shift in case of assimilation
#                (default : 0)
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
set temporal_file = ${dir_data_space}/../temporalModesSimulation_${nb_modes}modes/U_mat.txt
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

# with or without time shift
set time_shift=0
if ( $5 != "" ) set time_shift = $5

# vect_num_mode_to_reverse : for some modes, value must be reversed when ROM=C++ and DATA=matlab

set vect_num_mode_to_reverse = ()

set code_CppROM = ` echo ${temporal_file} | grep "_CppROM" | grep -v "_CppROM_Cpptestbasis" | wc -l `
if ( ${code_CppROM} == 1 ) then
    set test_info_file = ` echo ${temporal_file} | awk -F'/' '{ for (i=1;i<NF;i++) printf("%s/",$i); print "test.info" }' `
    if -e ${test_info_file} then
        set vect_num_mode_to_reverse = ` cat ${test_info_file} |  grep "\-mode" | head -1 | awk -F'[' '{ print $NF }' | sed s/"]"/" "/g | sed s/","/" "/g `
    endif
endif

# non inverse value
#set vect_num_mode_to_reverse = ()

if -e ${dir_ici}/vect_num_mode_to_reverse.txt \rm ${dir_ici}/vect_num_mode_to_reverse.txt; touch ${dir_ici}/vect_num_mode_to_reverse.txt
set n=0
while ( ${n} != 16 )
    set n = ` echo ${n} | awk '{ print 1+$1 }' `
    echo ${vect_num_mode_to_reverse} | \
    awk -v n=${n} '{ C=1; for (i=1;i<=NF;i++) {if ($i==n) C=-1}}END{ print n,C }'  >> ${dir_ici}/vect_num_mode_to_reverse.txt
end

# dir_extractU = TrueState or RedLumPart

set Nb_time_step = 1
set code_dir  = ` echo ${temporal_file} | sed s/"\.txt"//g | grep "temporalModeSimulation" | wc -l `
if ( ${code_dir} == 1 ) then
    set dir_extractU = TrueState_${nb_modes}modes
else
    set ROM_DATA = ` echo ${temporal_file} | sed s/"\/"/"\n"/g | sed s/"_modes_"/"\n"/g | grep "ROM" | grep -v "ROM-" | tail -1 `
    set Nb_time_step = ` echo ${temporal_file} | sed s/"\/"/"\n"/g | sed s/"_nPcl_"/"\n_nPcl_"/g | grep "_nPcl_" | sed s/"_nPcl_"//g `
    set Other_info = ` echo ${temporal_file} | sed s/"\/temporalModeDAresult\.txt"//g | awk -F'/' '{ print $NF }' `
    set dir_extractU = RedLumPart_${nb_modes}modes_${ROM_DATA}${Other_info}
endif
set src_ROM_case = ${dir_data_space}/../..

set Nb_time_step = 1


set openfoam_path = ${src_ROM_case}/../openfoam_data
cd ${openfoam_path}
set All_t_default = ` lsd | grep -v '[a-Z;A-Z]' | awk '{ printf("%.0f %s\n",1000.*($1+0.), $1) }' | sort -n | awk '{ print $2 }' `
set All_t = ` echo ${All_t_default} | \
                      awk -v t1=${timeStart} -v t2=${timeEnd} '{ for (i=1;i<=NF; i++) { t=$i+0.; if ((t>=t1+0.) && (t<=t2+0.)) print $i } }' `
set n_t_last = ` echo ${All_t} | awk '{ print NF }' `
cd ${dir_ici}

set time_step = ` echo ${All_t} | awk '{ print  $2-$1 }' `

#------------------------------------------------------------------------------

set path_extractU = ${src_ROM_case}/${dir_extractU}
if -e ${path_extractU} \rm -R ${path_extractU}; mkdir ${path_extractU}
cd ${path_extractU}
\cp -R ${src_ROM_case}/constant .
\cp -R ${src_ROM_case}/system .

# mean : can be saved as init (time_shift=0) or last time (time_shift=1)
#             for assimilation case
if (!(-e mean)) mkdir mean
\cp ${src_ROM_case}/ITHACAoutput/mean/1/* mean

#------------------------------------------------------------------------------

if -e tmp_dir \rm -R tmp_dir; mkdir tmp_dir
cd tmp_dir

\cp -R ${dir_data_space}/* .
set All_mode = ` lsd | sed s/'[a-z;A-Z;-;_]'//g | awk '{ if (NF!=0) print $1 }' | sort -n `
set first_mode = ` echo ${All_mode} | awk '{ print $1 }' `
set last_mode = ` echo ${All_mode} | awk '{ print $NF }' `

# temporal mode file
if -e temporal_mode_U_mat.txt \rm temporal_mode_U_mat.txt
# if ( ${dir_extractU} == TrueState_${nb_modes}modes ) then
#   awk -v N=${Nb_time_step} '{ if (NR%N == 0) print $0 }' ${temporal_file} > temporal_mode_U_mat.txt 
# else
#   awk -v N=${Nb_time_step} '{ if (NR%N == 1) print $0 }' ${temporal_file} > temporal_mode_U_mat.txt 
# endif
awk -v N=${Nb_time_step} '{ if (NR%N == 0) print $0 }' ${temporal_file} > temporal_mode_U_mat.txt 

# new value for the number of defined times
set n_t_last = ` cat temporal_mode_U_mat.txt | wc -l | awk -v n=${n_t_last} '{ if ($1<n) print $1; else print n}' `
echo "value of extract times : $n_t_last"

#------------------------------------------------------------------------------

### ux_mean+ux_mode1*b1(t)+ux_mode2*b2(t)+... ###

# time : to measure how long it takes to reconstruct U
set t1 = `date +%s`

set mode_mean = 0
set All_mode = ( ${mode_mean} ${All_mode} )
set first_mode = ` echo ${All_mode} | awk '{ print $1 }' `
set last_mode = ` echo ${All_mode} | awk '{ print $NF }' `
echo""; echo "MODES = [${first_mode}:${last_mode}] (= ${All_mode})"; echo ""

# head and tail of U file
set N0 = ` cat ${dir_data_space}/../mean/1/U | awk '{ if ($1=="internalField") print NR }' | head -1 `
set N1 = ` cat ${dir_data_space}/../mean/1/U | sed s/"("/"( "/g | sed s/")"/" )"/g | \
  awk -v N=${N0} '{ if ((NF==5) && ($1="(") && (NR>N)) print NR }' | head -1 `
set N2 = ` cat ${dir_data_space}/../mean/1/U | sed s/"("/"( "/g | sed s/")"/" )"/g | \
  awk -v N=${N1} 'BEGIN{c=0}{ if (NR>N) { if (NF!=5) c=c+1;  if ((NF==5) && ($1="(") && (c==0)) print NR } }' | tail -1 `
  
# head file
if -e head.txt \rm head.txt
awk -v N=${N1} '{ if (NR<N) print $0 }' ${dir_data_space}/../mean/1/U > head.txt
# tail file
if -e tail.txt \rm tail.txt
awk -v N=${N2} '{ if (NR>N) print $0 }' ${dir_data_space}/../mean/1/U > tail.txt

# global file with all spatial mode
if -e spatial_mode_all.txt \rm spatial_mode_all.txt
set mode = 0
set N = ` echo ${nb_modes} | awk '{ print 1+$1 }' `
echo ""
while ( ${mode} != ${N} )
    echo "---- spatial mode ${mode} ---------"
    
    if ( ${mode} == 0 ) then 
        \cp ${dir_data_space}/../mean/1/U spatial_mode_all.txt
    else
        \mv spatial_mode_all.txt tmp.txt
        paste tmp.txt ${dir_data_space}/${mode}/U > spatial_mode_all.txt
    endif
    
    set mode = ` echo ${mode} | awk '{ print 1+$1 }' `
end
echo ""
\mv spatial_mode_all.txt tmp.txt
awk -v N1=${N1} -v N2=${N2} '{ if ((NR>=N1) && (NR<=N2)) print $0 }'  tmp.txt | \
    sed s/")"//g | sed s/"("//g > spatial_mode_all.txt

set n_t = 1
set n_t_max = ` echo ${n_t_last} | awk '{ print 1+$1 }' `

while ( ${n_t} != ${n_t_max} )

  set t = ` echo ${All_t} | awk -v n=${n_t} '{ print $n }' `
  echo ${t} | awk '{ printf("--- t=%6.2f -> sum( bt(t=%6.2f)*phi...*C... ) ---\n",$1,$1) }'

  if -e Ut \rm Ut; touch Ut
  cat temporal_mode_U_mat.txt | awk -v n=${n_t} '{ if (NR==n) print "1.",$0 }' >> Ut
  cat ${dir_ici}/vect_num_mode_to_reverse.txt | awk 'BEGIN{ printf("%.1f ",1.) }{ printf("%.1f ",$2+0.) }END{print ""}' >> Ut
  cat spatial_mode_all.txt >> Ut

  if -e internal_U \rm internal_U
  awk -v N=${nb_modes} '{ \
      if (NR==1) split($0,bt," "); \
      if (NR==2) split($0,C," "); \
      if (NR>2) { \
          s1=0.; s2=0.; s3=0. \
          for (i=1;i<=N+1;i++) { \
              j=1+3*(i-1); k=j+1; l=k+1; \
              s1=s1+bt[i]*C[i]*$j \
              s2=s2+bt[i]*C[i]*$k \
              s3=s3+bt[i]*C[i]*$l \
          } \
          printf("( %.6f %.6f %.6f )\n", s1, s2, s3) \
      } \
  }' Ut > internal_U

  # reconstructed U
  if -e ${path_extractU}/${t} \rm -R ${path_extractU}/${t}; mkdir ${path_extractU}/${t}
  cat head.txt > ${path_extractU}/${t}/U
  cat internal_U >> ${path_extractU}/${t}/U
  cat tail.txt >> ${path_extractU}/${t}/U
  
  # last time for U reconstructed
  set t_last = ${t}
  
  set n_t = `echo ${n_t} | awk '{ print 1+$1 }' `
    
end

# time : to measure how long it takes to reconstruct U
set t2 = `date +%s`
echo ${t1} ${t2} ${n_t} | awk '{ print ""; print "---- It takes",$2-$1,"s to reconstruct U for",$3-1,"iterations"; print "" }'

#------------------------------------------------------------------------------
  
cd ${path_extractU}

# with or without time shift : moving folder
if ( ${time_shift} == 1 ) then

  set n_t = 1
  set n_t_max = ` echo ${n_t_last} | awk '{ print 1+$1 }' `
  
  set n_t = ${n_t_last}
  while ( ${n_t} != 0 )
  
    set t1 = ` echo ${All_t} | awk -v n=${n_t} '{ print $n }' `
    set t2 = ` echo ${All_t} | awk -v n=${n_t} -v time_step=${time_step} '{ print $n+time_step }' `
    echo ${t1} ${t2} | awk '{ printf("--- time shift : %6.2f  moved to folder %6.2f ---\n",$1,$2) }'
    if -e ${t2} \rm -R ${t2}
    \mv ${t1} ${t2}
   
    set n_t = `echo ${n_t} | awk '{ print $1-1 }' `
     
  end
  echo ${timeStart} | awk '{ printf("\n--- time shift : %6s copied to folder %6.2f ---\n\n","mean", $1) }'
  \cp -R mean ${timeStart}

else

  set n_t = 1
  set t_max = ` echo ${time_step} ${t_last} | awk '{ print  $1+$2 }' `
  
  echo ${t_max} | awk '{ printf("\n--- no time shift : %6s copied to folder %6.2f ---\n\n","mean", $1) }'
  \cp -R mean ${t_max}
 
endif

#------------------------------------------------------------------------------

cd ${dir_ici}

#\cp -R ${dir_extractU} ${src_ROM_case}

echo ""
echo "Cf. time files in ${src_ROM_case}/${dir_extractU}"
echo ""

#------------------------------------------------------------------------------

