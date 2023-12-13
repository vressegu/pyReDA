#!/bin/tcsh
#
# Laurence Wallian - ACTA - OPAALE - INRAE Rennes [Juin 2022 : Février 2023]
#
# MORAANE project : Scalian - INRAE
#
#  ------------------------------------------------------------------------------
#
# OBJECT : Openfoam DNS file -> synthetic PIV file
#
#     This script creates synthetic PIV files from 2 types of input file
#
#        NOTE : here, DNS is a generic word for "Numerical Simulation"
#  
#    1) Raw result of Openfoam DNS simulation : 
#    
#        - the input files are all located in [.../openfoam_data] directory
#        - the output files are all located in [.../FakePIV_noise...] directory
#          for example : 
#            input = RedLUM/data_red_lum_cpp/DNS300-D1_Lz1pi/openfoam_data
#            output = RedLUM/data_red_lum_cpp/DNS300-D1_Lz1pi/FakePIV_noise2 when noise_MAX=2
#        
#        this kind of data is named [DNS] in the script [openfoamDNS_to_pseudoPIV_all.csh]
#    
#    2) Result of ROM applied on Openfoam DNS simulation data :
#    
#        - the input files are all located in [.../ROMDNS...] subdirectories
#        - the output files are all located in the run script directory
#          for example : 
#            input = RedLUM/data_red_lum_cpp/DNS300-D1_Lz1pi/ROMDNS-v1/ITHACAoutput/mean
#            output = RedLUM/data_red_lum_cpp/DNS300-D1_Lz1pi/ROMDNS-v1/ROM_PIV/mean
#       
#        this kind of data is named [ROM] in the script [openfoamDNS_to_pseudoPIV_all.csh]
#  ------------------------------------------------------------------------------
#  
#  USE : HOW to have the script RUNNING
#  
#  1) The script [openfoamDNS_to_pseudoPIV_all.csh] can work without input arguments :
#  
#    command = tcsh openfoamDNS_to_pseudoPIV_all.csh
#    
#    however, the USER is always prompted to valid (or choose another value) for two parameters :
#    
#      1.a) the PATH for [run_info.txt] file
#      1.b) the PATH for [util] directory 
#        
#        tree example :
#        ├── data_red_lum_cpp
#        │    └── DNS300-D1_Lz1pi
#        └──podfs2
#             ├── run_info.txt
#             └── util
#    
#  2) It can also have three optional arguments (Cf. README.txt part [WHAT CAN be MODIFIED by the USER]) :
#  
#    2.a) arg1 = Zslice value (ex : tcsh tcsh openfoamDNS_to_pseudoPIV_all.csh 2.45)
#    2.b) arg2 = Case type ( ex : tcsh tcsh openfoamDNS_to_pseudoPIV_all.csh 1.6 DNS)
#    2.c) arg3 = ROM type ( ex : tcsh tcsh openfoamDNS_to_pseudoPIV_all.csh 1.6 ROM mean)
#  
#  ------------------------------------------------------------------------------
# 
# Cf. more informations at END of this file or in [README.txt] file
# 
#  ------------------------------------------------------------------------------

# alias to show directories

alias lsd  ' ls -l | awk '\''{i=0; i=index($1,"d"); if (i==1) print $9 }'\'' '

# alias for color prompt

alias WRITE_LINE 'echo ""'
alias WRITE_INFO 'echo "    \033[32;7m  \!*  \033[0m"'
alias WRITE_WARNING 'echo "\033[34;7m  \!*  \033[0m"'
alias ASK_QUESTION 'echo -n "  \033[34;5m  \!*  \033[0m  " '
alias READ_ANSWER 'echo -n "\033[34;7m        \!*  \033[0m   "'
alias WRITE_ERROR 'echo "\033[31;7m \\!\\!\\! OUPS \\!\\!\\!   \!*  \\!\\!\\!\033[0m"'

#  ------------------------------------------------------------------------------

# pvbatch PATH : check aliases defined in called scripts

foreach file_csh ( cov_after_gaussSmoothing.csh openfoamDNS_to_pseudoPIV.csh )

  set pvbatch_alias = ` cat util/${file_csh} | grep pvbatch | grep alias | tail -1 | awk '{ print $3 }' | sed s/"'"//g `
  if ( -e ${pvbatch_alias} ) then
  
    set info = "pvbatch alias OK in util/${file_csh} : ${pvbatch_alias} exist"
    WRITE_LINE; WRITE_INFO "${info}"; WRITE_LINE
    
  else
  
    set error = "pvbatch alias ${pvbatch_alias} defined in util/${file_csh} NOT FOUND"
    WRITE_LINE; WRITE_ERROR "${error}"; WRITE_LINE
    exit()
    
  endif
  
end

#  ------------------------------------------------------------------------------

# current directory

set dir_ici = ` pwd `

# RedLUM directory -> run_info.txt

set dir_RedLUM = ` pwd `
set fic_run_info = ${dir_RedLUM}/run_info.txt

set code_fic_run_info = 0
while ( ${code_fic_run_info} == 0 )

  if -e ${fic_run_info} set code_fic_run_info = 1
  
  if ( ${code_fic_run_info} == 1 ) then
  
    set warning = "NOTE : info file used is  ${fic_run_info}"
    WRITE_LINE; WRITE_WARNING "${warning}"; WRITE_LINE
    set question = "  is-it OK (enter Y (YES) or RETURN (NO))  "
    ASK_QUESTION "${question}" 
    set choix = $< 
    set choix = ` echo ${choix} | tr a-z A-Z | grep Y | wc -l `
    WRITE_LINE
   
  else

    set error = "file ${fic_run_info} NOT FOUND"
    WRITE_LINE; ERROR "${error}"; WRITE_LINE
    set choix = 0
    
  endif
  
  if ( ${choix} == 0 ) then
    
    set fic_run_info = ""
    while ( ${fic_run_info} == "" )
      set answer = "        -> enter FULL NAME for info file : "
      WRITE_LINE; READ_ANSWER "${answer}" 
      set fic_run_info = $< 
      WRITE_LINE
    end
    
  endif

   if (!(-e ${fic_run_info})) then 
    set code_fic_run_info = 0
  else
    set code_fic_run_info = 1
  endif
    
end

# util directory : default value is [run_info.txt] directory

set dir_fic_run_info = ` echo ${fic_run_info} | awk -F'/' '{ for (i=2;i<NF;i++) printf("/%s",$i) }' `
set dir_util = ${dir_fic_run_info}/util

set code_dir_util = 0
while ( ${code_dir_util} == 0 )

  if -d ${dir_util} set code_dir_util = 1
  if ( (!(-e ${dir_util}/openfoamDNS_to_pseudoPIV.csh)) || \
        (!(-e ${dir_util}/openfoamDNS_to_pseudoPIV_param.txt)) || \
        (!(-e ${dir_util}/calculator_PointVolumeInterpolation_model.py)) ||  \
        (!(-e ${dir_util}/cov_after_gaussSmoothing.csh)) ||  \
        (!(-e ${dir_util}/cov_after_gaussSmoothing_model.py)) ||  \
        (!(-e ${dir_util}/dim_DNS_cyl.csh)) ) set code_dir_util = 0
  
  if ( ${code_dir_util} == 1 ) then
  
    set warning = "NOTE : util directory used is  ${dir_util}"
    WRITE_LINE; WRITE_LINE; WRITE_WARNING "${warning}"; WRITE_LINE
    set question = "  is-it OK (enter Y (YES) or RETURN (NO))  "
    ASK_QUESTION "${question}" 
    set choix = $< 
    set choix = ` echo ${choix} | tr a-z A-Z | grep Y | wc -l `
    WRITE_LINE
    
  else
  
    set error = "directory ${dir_util} ${fic_run_info} NOT FOUND or MISSING files"
    WRITE_LINE; WRITE_ERROR "${error}"; WRITE_LINE
    set choix = 0
    
  endif
  
  if ( ${choix} == 0 ) then
    
    set dir_util = ""
    while ( ${dir_util} == "" )
      set answer = "        -> enter FULL NAME for util directory : "
      WRITE_LINE; READ_ANSWER "${answer}" 
      set dir_util = $< 
      WRITE_LINE
    end
    
  endif
    
end

set info = "NOTE :\n"
set info = "${info}\tinfo file used is ${fic_run_info}\n" 
set info = "${info}\tutil directory used is ${dir_util}" 
WRITE_LINE; WRITE_INFO "${info}"; WRITE_LINE

#------------------------------------------------------------------------------

set dir_OpenFoam = ` cat ${fic_run_info} | sed s/"^ #"/"#"/g | grep -v "^#" | \
                                 grep "PATH_openfoam_data" | awk '{ print $2 }' | tail -1 `

set case_OpenFoam = ` cat ${fic_run_info} | sed s/"^ #"/"#"/g | grep -v "^#" | \
                                 grep "type_data_C" | awk '{ print $2 }' | tail -1 `
                                 
set dir_ROMDNS = ` cat ${fic_run_info} | sed s/"^ #"/"#"/g | grep -v "^#" | \
                                 grep "redlumcpp_code_version" | awk '{ print $2 }' | tail -1 `

#------------------------------------------------------------------------------
# default values for first INPUT parameter

# Z position of the slice for pseudoPIV, in CFD unities

set Zslice = 1.
set warning = "Default Slice position is Z=${Zslice}"
WRITE_LINE; WRITE_WARNING "${warning}"; WRITE_LINE

# if first input arg !=0 -> other choice
if ( $1 != "" ) then
  set Zslice = $1
  set info = "arg1=$1 -> Chosen Slice position is Z=${Zslice}"
  WRITE_INFO "${info}" 
endif

# other parameters depending of [case_OpenFoam]
#  - code_adim : code related to final ASCII file cooresponding to the slice : 
#     1) if ASCII file is related to ROM coefficients then code_adim = 1 
#     2) if ASCII file is related to flux, then dimensions are those of real PIV and  code_adim = 0
#  - noise_MAX : noise applied to DNS values to make FakePIV

#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#
# "DNS" : 
#                       1) source folder D is in [openfoam_data*]
#                            (for example D=DNS300-D1_Lz1pi)
#                       2) result is in current directory
#                           2.a) with noise applied =2%
#                           2.b) spatial and velocity values will have real dimensions (i.e. like PIV)
#                           2.c) time directories created are the same as openFoam DNS directories (i.e. dimensionless)
#
# "ROM"  : 
#                       1) source folder D=mean, spatialModes_*modes or residualSpeed_* in [.../ROMDNS.../ITHACAoutput] folder
#                            (for example D=DNS300-D1_Lz1pi/ROMDNS-v1/ITHACAoutput/mean)
#                       2) result is in current directory
#                           2.a) without noise applied
#                           2.b) spatial and velocity values are dimensionless
#                           2.c) time directories created are the same as openFoam DNS directories (i.e. dimensionless)
#
#------------------------------------------------------------------------------

# default values for second INPUT parameter

set All_CASE =  ( "DNS" "ROM" )
set warning = "Default CASES = ( ${All_CASE} )"
WRITE_LINE; WRITE_WARNING "${warning}"; WRITE_LINE

# if second input arg !=0 -> other choice
if ( $2 != "" ) then

  set All_CASE =  ( )
  set code_DNS = ` echo $2 | grep DNS | wc -l `
  if ( ${code_DNS} != 0 ) set All_CASE =  ( ${All_CASE} "DNS" )
  set code_ROM = ` echo $2 | grep ROM | wc -l `
  if ( ${code_ROM} != 0 ) set All_CASE =  ( ${All_CASE} "ROM" )
  set info = "arg2=$2 -> Chosen CASES = ( ${All_CASE} )"
  WRITE_INFO "${info}" 
  
endif

foreach CASE ( ${All_CASE} )

  #------------------------------------------------------------------------------
  # "DNS" = cylinder wake : openfoam_data... -> FakePIV_noise...
  #    input folders :
  #       folders [0], [system] and [constant] must be in ${DIR0}/${D} 
  #          with D=openfoam_data
  #       folders [600] to [700] must be in ${DIR0}/${D}
  #    output folders = ${DIR0}/FakePIV_noise${noise_MAX}
  #------------------------------------------------------------------------------
 
  if ( ${CASE} == "DNS" ) then

    # directories DIR0 and DIR1
    set DIR0 = ${dir_OpenFoam}/${case_OpenFoam}
    set DIR1 = ""
    
    # only one directory D
    set All_D = ( openfoam_data )
 
    # noise applied to create Fake PIV
    set noise_MAX = 2
    
    # dimensional values
    set code_adim = 0 
    
    # working directory
    set dir_work_up = ${DIR0}/FakePIV_noise${noise_MAX}
    
  endif
  
  #------------------------------------------------------------------------------
  # "ROM" = red LUM result : ROMDNS.../mean -> ROMDNS.../ROM_PIV/mean 
  #    input folders :
  #       folders [0], [system] and [constant] must be in ${DIR0} or in ${DIR0}/${DIR1}/${D} 
  #          with D=mean, spatialModes_*modes or residualSpeed_*
  #       folders [0] to [600] must be in ${DIR0}/${DIR1}/${D}
  #    output folders = ${DIR0}/ROM_PIV/${D}
  #------------------------------------------------------------------------------
  
  if ( ${CASE} == "ROM" ) then

    # directories DIR0 and DIR1
    set DIR0 = ${dir_OpenFoam}/${case_OpenFoam}/${dir_ROMDNS}
    set DIR1 =  ITHACAoutput
      
    # creating ROM_PIV directory
    if (!(-d ${DIR0}/ROM_PIV)) mkdir ${DIR0}/ROM_PIV
    
#     set All_D = ( \
#       mean \
#       spatialModes_2modes \
#       residualSpeed_2 \
#     )
    
    set D_sed = ` echo ${DIR0}/${DIR1} | sed s/"\/"/"\\\/"/g`
    set mean_D = ` ls ${DIR0}/${DIR1} | sed s/"${D_sed}"//g | grep "mean" `
    set spatialModes_D = ` ls ${DIR0}/${DIR1} | sed s/"${D_sed}"//g | grep "spatialModes_" `
    set residualSpeed_D = ` ls ${DIR0}/${DIR1} | sed s/"${D_sed}"//g | grep "residualSpeed_" `
    
    set mean_D_U = ()
    set mean_D_notU = ()
    foreach d ( ${mean_D} )
      set c = ` find ${DIR0}/${DIR1}/${d} -name U | wc -l `
      if ( ${c} != 0 ) then
        set mean_D_U = ( ${mean_D_U} ${d} )
      else
        set mean_D_notU = ( ${mean_D_notU} ${d} )
      endif
    end
    
    set spatialModes_D_U = ()
    set spatialModes_D_notU = ()
    foreach d ( ${spatialModes_D} )
      set c = ` find ${DIR0}/${DIR1}/${d} -name U | wc -l `
      if ( ${c} != 0 ) then
        set spatialModes_D_U = ( ${spatialModes_D_U} ${d} )
      else
        set spatialModes_D_notU = ( ${spatialModes_D_notU} ${d} )
      endif
    end
    
    set residualSpeed_D_U = ()
    set residualSpeed_D_notU = ()
    foreach d ( ${residualSpeed_D} )
      set c = ` find ${DIR0}/${DIR1}/${d} -name U | wc -l `
      if ( ${c} != 0 ) then
        set residualSpeed_D_U = ( ${residualSpeed_D_U} ${d} )
      else
        set residualSpeed_D_notU = ( ${residualSpeed_D_notU} ${d} )
      endif
    end
    
    set warning = "For ROM_PIV from\n"
    set warning = "${warning}\t${DIR0}\n"
    set warning = "${warning}\tDefault directories are All_D = ( \\\n"
    set warning = "${warning}\t\t${mean_D_U} \\\n"
    set warning = "${warning}\t\t${spatialModes_D_U} \\\n"
    set warning = "${warning}\t\t${residualSpeed_D_U} \\\n"
    set warning = "${warning}\t)"
    WRITE_LINE; WRITE_WARNING "${warning}"; WRITE_LINE
    
    set info = "Other directories without U files :\n"
    set info = "${info}\t\t${mean_D_notU} ${spatialModes_D_notU}${residualSpeed_D_notU}"
    WRITE_LINE; WRITE_INFO "${info}"; WRITE_LINE
    
    # default values for third INPUT parameter
    set All_D = ( ${mean_D_U} ${spatialModes_D_U} ${residualSpeed_D_U} )
    
    # if third input arg !=0 -> other choice : directories among [mean], [spatialModes_*modes] and [residualSpeed_*]
    if ( $3 != "" ) then
      set All_D = ( $3 )
      set info = "arg3=$3 -> Chosen directory is All_D = ( ${All_D} )"
      WRITE_INFO "${info}" 
    endif
 
    # noise applied to create Fake PIV
    set noise_MAX = 0
    
    # adimensional values
    set code_adim = 1  
  
    # working directory
    set dir_work_up = ${DIR0}/ROM_PIV
  
    if (!(-d ${dir_work_up})) mkdir ${dir_work_up}
    
  endif
   
  #------------------------------------------------------------------------------

  foreach D ( ${All_D} ) 
  
    if (! (-d ${DIR0}/${DIR1}/${D} )) then
   
      set error = "directory ${DIR0}/${DIR1}/${D} NOT FOUND"
      WRITE_LINE; WRITE_ERROR "${error}"; WRITE_LINE
      exit()
      
    endif
  
    set code_mean = ` echo ${D} | grep "mean" | wc -l `
    set code_spatialModes = ` echo ${D} | grep "spatialModes_" | grep "modes" | wc -l `
    set code_residualSpeed = ` echo ${D} | grep "residualSpeed_" | wc -l `
    
    if ((${code_mean} == 0) && (${code_spatialModes} == 0) && (${code_residualSpeed} == 0)) then
    
      set dir_work = ${dir_work_up}
      
    else
    
      set dir_work = ${dir_work_up}/${D}
    
    endif
   
    # code_D : if =1 -> go ON, else -> go to next D
    set code_D = 1
    
    if (!(-d ${dir_work})) then
    
      mkdir ${dir_work}
      set info = "${dir_work} directory is created"
      WRITE_LINE; WRITE_INFO "${info}";  WRITE_LINE
      
    else
    
      set error = "directory ${dir_work} already EXIST"
      WRITE_LINE; WRITE_ERROR "${error}"; WRITE_LINE
      set question = "  regenerate-it anyway (enter Y (YES) or RETURN (NO))  "
      ASK_QUESTION "${question}" 
      set choix = $< 
      echo ""
      set choix = ` echo ${choix} | tr a-z A-Z | grep Y | wc -l `
      if ( ${choix} == 0 ) set code_D = 0
      
    endif
    
    if ( ${code_D} == 1 ) then
    
      cd ${dir_work}
      
      echo ""; echo "--- ${DIR0}/${DIR1}/${D} ---"; echo ""
      
      ### temporary folder with useful directories and files
      
      if (!(-d tmp_dir)) mkdir tmp_dir
      
      if -e ${dir_util}/openfoamDNS_to_pseudoPIV.csh then
        \cp ${dir_util}/openfoamDNS_to_pseudoPIV.csh tmp_dir
      else
          set error = "file ${dir_util}/openfoamDNS_to_pseudoPIV.csh NOT FOUND"
          WRITE_LINE; WRITE_ERROR "${error}"; WRITE_LINE
          exit()
      endif
      
      if -e ${dir_util}/openfoamDNS_to_pseudoPIV_param.txt then
        \cp ${dir_util}/openfoamDNS_to_pseudoPIV_param.txt tmp_dir
      else
          set error = "file ${dir_util}/openfoamDNS_to_pseudoPIV_param.txt NOT FOUND"
          WRITE_LINE; WRITE_ERROR "${error}"; WRITE_LINE
          exit()
      endif
      
      foreach fic_info ( DNS_info.txt PIV_info.txt DNS_to_FakePIV_info.txt )
      
        if ( -e ${DIR0}/../util/${fic_info} ) then
          echo "copy of ${DIR0}/../util/${fic_info} to  tmp_dir"
          \cp ${DIR0}/../util/${fic_info} tmp_dir
        endif
        
        if ( ${CASE} == "DNS" ) then
          if ( -e ${DIR0}/util/${fic_info} ) then
            echo "copy of ${DIR0}/util/${fic_info} to  tmp_dir"
            \cp ${DIR0}/util/${fic_info} tmp_dir
          endif
        endif
        
        if (!(-e  tmp_dir/${fic_info})) then
          set error = "file tmp_dir/${fic_info} NOT EXIST"
          WRITE_LINE; WRITE_ERROR "${error}"; WRITE_LINE
        endif
        
      end
   
      ## temporary folder : dir util
      
      if (!(-d tmp_dir/util)) mkdir tmp_dir/util
      
      foreach fic_info ( DNS_info.txt PIV_info.txt DNS_to_FakePIV_info.txt )
        \cp tmp_dir/${fic_info} tmp_dir/util
      end
    
      # necessary files to copy in temporary folder util
      
      if -e ${dir_util}/calculator_PointVolumeInterpolation_model.py then
        \cp ${dir_util}/calculator_PointVolumeInterpolation_model.py tmp_dir/util
      else
        set error = "file ${dir_util}/calculator_PointVolumeInterpolation_model.py NOT FOUND"
        WRITE_LINE; WRITE_ERROR "${error}"; WRITE_LINE
        exit()
      endif
      
      \cp ${dir_util}/openfoamDNS_to_pseudoPIV.csh tmp_dir/util
      
      # optional files to copy in temporary folder util
      
      if -e ${dir_util}/B0001.dat \cp ${dir_util}/B0001.dat tmp_dir/util
      \cp ${dir_util}/dim_DNS_cyl.csh tmp_dir/util
      
      ## temporary folder : dir system
      
      if -d ${DIR0}/${DIR1}/${D}/system then
        \cp -R ${DIR0}/${DIR1}/${D}/system tmp_dir
      else
        \cp -R ${DIR0}/system tmp_dir
      endif
      
      ## temporary folder : dir constant
      
      if -d  ${DIR0}/${DIR1}/${D}/constant then
        \cp -R ${DIR0}/${DIR1}/${D}/constant tmp_dir
      else
        \cp -R ${DIR0}/constant tmp_dir
      endif
      
      # Adjusting tmp_dir/util/DNS_info.txt from [constant/polyMesh/points],  [constant/transportProperties] and [system/controlDict] files
      
      set fic_info = DNS_info.txt
      
      set fic_src = tmp_dir/constant/polyMesh/points
      set DNS_xmin = ` cat ${fic_src} | grep ")" | grep "(" | sed s/"("//g | sed s/")"//g | awk '{ printf("%.6f\n", $1) }' | sort -n | uniq | head -1 `
      set DNS_xmax = ` cat ${fic_src} | grep ")" | grep "(" | sed s/"("//g | sed s/")"//g | awk '{ printf("%.6f\n", $1) }' | sort -n | uniq | tail -1 `
      set DNS_ymin = ` cat ${fic_src} | grep ")" | grep "(" | sed s/"("//g | sed s/")"//g | awk '{ printf("%.6f\n", $2) }' | sort -n | uniq | head -1 `
      set DNS_ymax = ` cat ${fic_src} | grep ")" | grep "(" | sed s/"("//g | sed s/")"//g | awk '{ printf("%.6f\n", $2) }' | sort -n | uniq | tail -1 `
      set DNS_zmin = ` cat ${fic_src} | grep ")" | grep "(" | sed s/"("//g | sed s/")"//g | awk '{ printf("%.6f\n", $3) }' | sort -n | uniq | head -1 `
      set DNS_zmax = ` cat ${fic_src} | grep ")" | grep "(" | sed s/"("//g | sed s/")"//g | awk '{ printf("%.6f\n", $3) }' | sort -n | uniq | tail -1 ` 
      foreach mot ( "DNS_xmin" "DNS_xmax" "DNS_ymin" "DNS_ymax" "DNS_zmin" "DNS_zmax" )
        if ( ${mot} == "DNS_xmin" ) set x = ${DNS_xmin}
        if ( ${mot} == "DNS_xmax" ) set x = ${DNS_xmax}
        if ( ${mot} == "DNS_ymin" ) set x = ${DNS_ymin}
        if ( ${mot} == "DNS_ymax" ) set x = ${DNS_ymax}
        if ( ${mot} == "DNS_zmin" ) set x = ${DNS_zmin}
        if ( ${mot} == "DNS_zmax" ) set x = ${DNS_zmax}
        set N = ` cat -n tmp_dir/util/${fic_info} | grep ${mot} | awk '{ print $1 }' `
        if ( ${N} != "" ) then
          \mv tmp_dir/util/${fic_info} tmp.txt
          awk -v N=${N} '{ if (NR<N) print $0 }' tmp.txt > tmp_dir/util/${fic_info}
          echo "${x} # ${mot}" >> tmp_dir/util/${fic_info}
          awk -v N=${N} '{ if (NR>N) print $0 }' tmp.txt >> tmp_dir/util/${fic_info}
        else
          echo "${x} # ${mot}" >> tmp_dir/util/${fic_info}
        endif
      end

      set fic_src = tmp_dir/constant/transportProperties
      set mot = "DNS_Re"
      set DNS_Re = ` cat ${fic_src} | grep nu | grep "\]" | grep "\[" | awk '{ printf("%.1f\n", 1./($12+0.)) }' | sort -n | uniq | head -1 `
      set N = ` cat -n tmp_dir/util/${fic_info} | grep ${mot} | awk '{ print $1 }' `
      if ( ${N} != "" ) then
        \mv tmp_dir/util/${fic_info} tmp.txt
        awk -v N=${N} '{ if (NR<N) print $0 }' tmp.txt > tmp_dir/util/${fic_info}
        echo "${DNS_Re} # ${mot}" >> tmp_dir/util/${fic_info}
        awk -v N=${N} '{ if (NR>N) print $0 }' tmp.txt >> tmp_dir/util/${fic_info}
      else
        echo "${DNS_Re} # ${mot}" >> tmp_dir/util/${fic_info}
      endif
      
      set fic_src = tmp_dir/system/controlDict
      set dt_DNS = ` cat ${fic_src} | \
                                 awk 'BEGIN{code=0}{if ($1=="{") code=code+1; if ($1=="}") code=code-1; if (code==0) print $0 }' | \
                                 sed s/";"//g | awk '{ if ($1=="deltaT") print  $2 }' `
      set t0_DNS = ` cat ${fic_src} | \
                                 awk 'BEGIN{code=0}{if ($1=="{") code=code+1; if ($1=="}") code=code-1; if (code==0) print $0 }' | \
                                 sed s/";"//g | awk '{ if ($1=="startTime") print  $2 }' `
      set t1_DNS = ` cat ${fic_src} | \
                                  awk 'BEGIN{code=0}{if ($1=="{") code=code+1; if ($1=="}") code=code-1; if (code==0) print $0 }' | \
                                  sed s/";"//g | awk '{ if ($1=="endTime") print  $2 }' `
      foreach mot ( "dt_DNS" "t0_DNS" "t1_DNS" )
        if ( ${mot} == "dt_DNS" ) set x = ${dt_DNS}
        if ( ${mot} == "t0_DNS" ) set x = ${t0_DNS}
        if ( ${mot} == "t1_DNS" ) set x = ${t1_DNS}
        set N = ` cat -n tmp_dir/util/${fic_info} | grep ${mot} | awk '{ print $1 }' `
        if ( ${N} != "" ) then
          \mv tmp_dir/util/${fic_info} tmp.txt
          awk -v N=${N} '{ if (NR<N) print $0 }' tmp.txt > tmp_dir/util/${fic_info}
          echo "${x} # ${mot}" >> tmp_dir/util/${fic_info}
          awk -v N=${N} '{ if (NR>N) print $0 }' tmp.txt >> tmp_dir/util/${fic_info}
        else
          echo "${x} # ${mot}" >> tmp_dir/util/${fic_info}
        endif
      end
      
      if -e ${DIR0}/../util/${fic_info} then
      
        \cp tmp_dir/util/${fic_info} ${DIR0}/../util/${fic_info}
       
      else 
      
        if -e ${DIR0}/util/${fic_info} \cp tmp_dir/util/${fic_info} ${DIR0}/util/${fic_info}
        
      endif

      # is Zslice OK ?
      
      set code_z = ` echo ${Zslice} ${DNS_zmin} ${DNS_zmax} | awk '{ if (($1-$2)*($1-$3) <= 0 ) print 0; else print 1 }' `
      if ( ${code_z} == 0 ) then
        set info = "Zslice OK : ${DNS_zmin}<Zslice=${Zslice}<${DNS_zmax}"
        WRITE_LINE; WRITE_INFO "${info}" ; WRITE_LINE
      else
        set error = "Zslice = ${Zslice} OUT of domain Z=(${DNS_zmin}:${DNS_zmax})"
        WRITE_LINE; WRITE_ERROR "${error}"; WRITE_LINE
        exit()
      endif      
      
      ## temporary folder : dir 0 and 1
      
      if (!(-d tmp_dir/0)) mkdir tmp_dir/0
      if (!(-d tmp_dir/1)) mkdir tmp_dir/1      

      ### time interval
    
      ## time interval : default value
      
      cd ${DIR0}/${DIR1}/${D}
      set All_t_default = ` lsd | grep -v '[a-Z;A-Z]' | awk '{ printf("%.0f %s\n",1000.*($1+0.), $1) }' | sort -n | awk '{ print $2 }' `
      cd ${dir_work}
      
      ## time interval : general value = default value
      
      set All_t = ( ${All_t_default} )
      
      ## time interval : specific case

      # time interval : specific case = residualSpeed_* (to create ROM_PIV/residualSpeed_*)

      if (( ${CASE} == "ROM" ) && ( ${code_residualSpeed} != 0 )) then

        #set t_first = 100
        #set t_last = 600

        set fic_src = ${DIR0}/system/ITHACAdict
        set t_first = ` cat ${fic_src} | \
                                  awk 'BEGIN{code=0}{if ($1=="{") code=code+1; if ($1=="}") code=code-1; if (code==0) print $0 }' | \
                                  sed s/";"//g | awk '{ if ($1=="InitialTime") print  $2 }' `
        set t_last = ` cat ${fic_src} | \
                                  awk 'BEGIN{code=0}{if ($1=="{") code=code+1; if ($1=="}") code=code-1; if (code==0) print $0 }' | \
                                  sed s/";"//g | awk '{ if ($1=="FinalTime") print  $2 }' `

        set All_t = ` echo ${All_t} | \
                               awk -v t1=${t_first} -v t2=${t_last} '{ for (i=1;i<=NF; i++) { t=$i+0.; if ((t>=t1+0.) && (t<=t2+0.)) print $i } }' `
        
        set N_t = ` echo ${All_t} | awk '{ print NF }' `
        if ( ${N_t} == 0 ) set All_t = ( ${All_t_default} ) 
        
      endif
    
      # time interval : specific case = openfoam raw result (to create FakePIV)
      
      if ( ${CASE} == "DNS" ) then
        
        #set t_first = 600
        #set t_last = 700

        set fic_src = ${DIR0}/${D}/system/ITHACAdict
        set t_first = ` cat ${fic_src} | \
                                  awk 'BEGIN{code=0}{if ($1=="{") code=code+1; if ($1=="}") code=code-1; if (code==0) print $0 }' | \
                                  sed s/";"//g | awk '{ if ($1=="FinalTime") print  $2 }' `
        set t_last = ` cat ${fic_src} | \
                                  awk 'BEGIN{code=0}{if ($1=="{") code=code+1; if ($1=="}") code=code-1; if (code==0) print $0 }' | \
                                  sed s/";"//g | awk '{ if ($1=="FinalTimeSimulation") print  $2 }' `
                                  
        set All_t = ` echo ${All_t} | \
                               awk -v t1=${t_first} -v t2=${t_last} '{ for (i=1;i<=NF; i++) { t=$i+0.; if ((t>=t1+0.) && (t<=t2+0.)) print $i } }' `
        
        set N_t = ` echo ${All_t} | awk '{ print NF }' `
        if ( ${N_t} == 0 ) set All_t = ( ${All_t_default} )
        
      endif

      ## redifining first time value
      
      set t_first = ` echo ${All_t} | awk '{ print $1 }' `
 
      #------------------------------------------------------------------------------

      set N_t = ` echo ${All_t} | awk '{ print NF }' `
      if ( ${N_t} == 0 ) then
      
          set error = "No time directory in ${DIR0}/${DIR1}/${D}"
          WRITE_LINE; WRITE_ERROR "${error}"; WRITE_LINE
          
      else
      
        ### running [openfoamDNS_to_pseudoPIV.csh] script
      
        cd ${dir_work}/tmp_dir
        
        foreach t ( ${All_t} )

          if (! (-e ${DIR0}/${DIR1}/${D}/${t}/U )) then
    
            set error = "file ${DIR0}/${DIR1}/${D}/${t}/U NOT FOUND"
            WRITE_LINE; WRITE_ERROR "${error}"; WRITE_LINE
        
          else

            \cp ${DIR0}/${DIR1}/${D}/${t}/U .; chmod +w U
            \cp U 0; \cp U 1
            
            set fic_param = openfoamDNS_to_pseudoPIV_param.txt 
            
            ## choosing IsValid : can be useful to compare with PIV model
            
            set IsValid_ON = 1
            set IsValid_ON = 0
            
            ## INFO value
            
            # INFO value : default
            
            set DNS_info = "${D} : t=${t} noise<${noise_MAX}%"
            
            # INFO value : specific case
            
            if ( ${CASE} == "DNS" ) then
              set DNS_info = `echo ${D} ${Zslice} ${t} ${noise_MAX} | awk '{ printf("%s : Z=%.3f t=%06.2f noise <%s\%",$1,$2,$3,$4) }' `
            endif
            if ( ${CASE} == "ROM" ) then
              if ( ${code_mean} != 0 ) set DNS_info = `echo ${D} ${Zslice} | awk '{ printf("%s : Z=%.3f mode 0",$1,$2) }' `
              if ( ${code_spatialModes} != 0 ) set DNS_info = `echo ${D} ${Zslice} ${t} | awk '{ printf("%s : Z=%.3f mode %2d",$1,$2,$3) }' `
              if ( ${code_residualSpeed} != 0 ) set DNS_info = `echo ${D} ${Zslice} ${t} | awk '{ printf("%s : Z=%.3f t=%06.2f",$1,$2,$3) }' `
            endif
          
            ## PIV model
            
            if -e util/B0001.dat then
              set PIV_file_model = util/B0001.dat
            else
              set warning = "PIV model file util/B0001.dat NOT FOUND"
              WRITE_LINE; WRITE_WARNING "${warning}"; WRITE_LINE
              set IsValid_ON = 0
            endif
            
            ## DNS info : useful for Ux or Uy range in visu
            
            \mv ${fic_param} tmp.txt
            set N = ` cat -n tmp.txt | grep "# " | grep " DNS_info" | grep -v "\.txt" | awk '{ print $1 }' `
            awk -v N=${N} '{ if (NR<N) print $0 }' tmp.txt > ${fic_param}
            echo "${DNS_info} # DNS_info" >> ${fic_param}
            awk -v N=${N} '{ if (NR>N) print $0 }' tmp.txt >> ${fic_param}
        
            ## CSV and PNG files created according to time t
            
            # CSV  and PNG files created according to time t : 
            #    saving [slice_Ux1] and [slice_Uy1] (original openfoam mesh) only for first time 
            
            if ( ${t} == ${t_first} ) set code = 1
            if ( ${t} != ${t_first} ) set code = 0
            
            \mv ${fic_param} tmp.txt
            set N = ` cat -n tmp.txt | grep code_csv_slice_Ux1 | awk '{ print $1 }' `
            awk -v N=${N} '{ if (NR<N) print $0 }' tmp.txt > ${fic_param}
            echo "${code} # code_csv_slice_Ux1" >> ${fic_param}
            awk -v N=${N} '{ if (NR>N) print $0 }' tmp.txt >> ${fic_param}
              
            \mv ${fic_param} tmp.txt
            set N = ` cat -n tmp.txt | grep code_csv_slice_Uy1 | awk '{ print $1 }' `
            awk -v N=${N} '{ if (NR<N) print $0 }' tmp.txt > ${fic_param}
            echo "${code} # code_csv_slice_Uy1" >> ${fic_param}
            awk -v N=${N} '{ if (NR>N) print $0 }' tmp.txt >> ${fic_param}

            # CSV  and PNG files created according to time t : 
            #    saving view with grid only for first time 
            
            if ( ${t} == ${t_first} ) set code = 1
            if ( ${t} != ${t_first} ) set code = 0
            
            \mv ${fic_param} tmp.txt
            set N = ` cat -n tmp.txt | grep code_view_withGrid | awk '{ print $1 }' `
            awk -v N=${N} '{ if (NR<N) print $0 }' tmp.txt > ${fic_param}
            echo "${code} # code_view_withGrid" >> ${fic_param}
            awk -v N=${N} '{ if (NR>N) print $0 }' tmp.txt >> ${fic_param}
          
            # cylinder diameter define in [DNS_info.txt] must be the same as the one deduced from [.../constant/polyMesh/points]
            
            if ( ${t} == ${t_first} ) then

              \cp util/dim_DNS_cyl.csh .
              set DNS_cyl = ` tcsh dim_DNS_cyl.csh | grep "=> Cylinder diameter =" | awk '{ print $5 }' `
             
              if ( ${DNS_cyl} != "UKNOWN" ) then                   
            
                set dd = ` echo ${DNS_cyl} | awk '{ dd=sqrt(($1-1.)**2); if (dd<=0.0001) print 0; else print 1 }' `
                echo ""
                if ( ${dd} == 0 ) then
                  set info = "DNS points : OK, cylinder diameter = 1 : \nCf. ${dir_work}/dim_DNS_cyl.png"
                  WRITE_LINE; WRITE_INFO "${info}"; WRITE_LINE
                  \cp ${dir_work}/tmp_dir/dim_DNS_cyl.png ${dir_work}
                else
                  set error = "cylinder diameter = ${DNS_cyl} NOT EQUAL to 1"
                  WRITE_LINE; WRITE_ERROR "${error}"; WRITE_LINE
                  cd ${dir_work}
                  \mv tmp_dir/* ${dir_work}
                  \rm -R tmp_dir
                  exit()
                endif
            
              else
                
                \cp dim_DNS_cyl.png ..
              
                set error1 = "In file ${DIR0}/util/DNS_info.txt, \n"
                set error2 = "\t\tValue of  DNS_xcyl and/or DNS_ycyl must be CORRECTED to verify DNS_Dcyl\n"
                set dom_XYlimits = `echo ${DNS_xmin} ${DNS_xmax} ${DNS_ymin} ${DNS_ymax} | \
                                                    awk '{ printf("(%.3f:%.3f)x(%.3f:%.3f)",$1,$2,$3,$4) }' `
                set error3 = "\t\tand should be in domain limits : ${dom_XYlimits}\n"
                set error4 = "\t-> Cf. ${dir_work}/dim_DNS_cyl.png"
                WRITE_LINE; WRITE_ERROR "${error1}${error2}${error3}${error4}"; WRITE_LINE
                
                exit()

              endif
            
            endif

            ## running [openfoamDNS_to_pseudoPIV.csh] script
            #tcsh openfoamDNS_to_pseudoPIV.csh ${fic_param} ${D} ${noise_MAX} ${code_adim} ${Zslice} ${DNS_info} ${PIV_file_model} ${IsValid_ON}
            tcsh openfoamDNS_to_pseudoPIV.csh ${fic_param} ${D} ${noise_MAX} ${code_adim} ${Zslice}

            ## copying (or moving) tempory directory results in UP directory
            
            # copying (or moving) tempory directory results in UP directory : copying slice conditions file 
            
            if (!( -e slice_param.info)) then
              set error = "file ${DIR0}/${DIR1}/${D}/slice_param.info NOT FOUND\nCf. file ${dir_work}/openfoamDNS_to_pseudoPIV.info"
              WRITE_LINE; WRITE_ERROR "${error}"; WRITE_LINE
              cd ${dir_work}
              \mv tmp_dir/* ${dir_work}
              \rm -R tmp_dir
              exit()
            else
              \cp slice_param.info ..
            endif
            
            # copying (or moving) tempory directory results in UP directory : moving CSV and PNG file in UP directory
                  
            if ( ${t} == ${t_first} ) then
            
              set All_fic_to_move = ( )
              foreach mot ( "PIV_grid_" "slice_grid" "PIV_model" )
                set list = ` ls | grep "^${mot}" | grep "\.png" `
                set All_fic_to_move = ( ${All_fic_to_move} ${list} )
              end
              set list = ` ls | grep "^slice_Uxy1\." `
              set All_fic_to_move = ( ${All_fic_to_move} ${list} )
              set list = ` ls | grep "_withGrid\.png" `
              set All_fic_to_move = ( ${All_fic_to_move} ${list} )
              set list = ` ls | grep "^PIV_new_IsValid\.png" `
              set All_fic_to_move = ( ${All_fic_to_move} ${list} )
              set list = ` ls | grep "^PIV_xIsValid\.txt" `
              set All_fic_to_move = ( ${All_fic_to_move} ${list} )
              set list = ` ls | grep "^PIV_yIsValid\.txt" `
              set All_fic_to_move = ( ${All_fic_to_move} ${list} )
              set list = ` ls | grep "^dim_DNS_cyl\." `
              set All_fic_to_move = ( ${All_fic_to_move} ${list} )
              set upper_dir = `pwd | awk -F'/' '{ j=NF-1; for (i=1;i<j;i++) printf("%s/",$i); print $j}' `
              echo ""
              echo "All these files will be moved in Upper directory [${upper_dir}] :"
              echo " ${All_fic_to_move}" | sed s/" "/"\n     "/g 
              echo ""
              foreach fic_to_move ( ${All_fic_to_move} )
                \mv ${fic_to_move} ..
              end
              
            else
            
              set All_fic_to_delete = ( )
              foreach mot ( "PIV_grid_" "slice_grid" "PIV_model" )
                set list = ` ls | grep "^${mot}" | grep "\.png" `
                set All_fic_to_delete = ( ${All_fic_to_delete} ${list} )
              end
              set list = ` ls | grep "_withGrid\.png" `
              set All_fic_to_delete = ( ${All_fic_to_delete} ${list} )
              set list = ` ls | grep "^PIV_new_IsValid\.png" `
              set All_fic_to_delete = ( ${All_fic_to_delete} ${list} )
              set list = ` ls | grep "^PIV_xIsValid\.txt" `
              set All_fic_to_delete = ( ${All_fic_to_delete} ${list} )
              set list = ` ls | grep "^PIV_yIsValid\.txt" `
              set All_fic_to_delete = ( ${All_fic_to_delete} ${list} )
              set list = ` ls | grep "^dim_DNS_cyl\." `
              set All_fic_to_delete = ( ${All_fic_to_delete} ${list} )
              set present_dir = `pwd`
              echo ""
              echo "All these files will be removed from present directory [${present_dir}] :"
              echo " ${All_fic_to_delete}" | sed s/" "/"\n     "/g 
              echo ""
              foreach fic_to_delete ( ${All_fic_to_delete} )
                \rm ${fic_to_delete}
              end
              
            endif
            
            ## creating UP [t] directory 
            
            if (!(-d ../${t})) mkdir ../${t}
          
            # creating UP [t] directory : copying results in UP [t] directory 
            
            set All_fic_to_copy = ( ${fic_param} )
            foreach mot ( "slice" "PIV" )
              set list = ` ls | grep "^${mot}" | grep "\." `
              set All_fic_to_copy = ( ${All_fic_to_copy} ${list} )
            end
            foreach mot ( "png" "csh" "py" "dat" )
              set list = ` ls | grep "\.${mot}" `
              set All_fic_to_copy = ( ${All_fic_to_copy} ${list} )
            end
            set present_dir = `pwd`
            echo ""
            echo "All these files will be copied to time/mode directory [${upper_dir}/${t}] :"
            echo " ${All_fic_to_copy}" | sed s/" "/"\n     "/g 
            echo ""
            foreach fic_to_copy ( ${All_fic_to_copy} )
              \cp ${fic_to_copy} ../${t}
            end
          
            ## deleting results in tempory directory 
            
            \rm *.png *.csv
            
            set info = "Cf. files in ${dir_work}/${t}"
            WRITE_LINE; WRITE_INFO "${info}"; WRITE_LINE
            
            chmod +w -R 0; \rm 0/*
            chmod +w -R 1; \rm 1/*
        
          endif
      
        end
      
        cd ${dir_work}        
        chmod +w -R tmp_dir; \rm -R tmp_dir
  
        #------------------------------------------------------------------------------
        
        ## time values in D folder created in work directory
        
        cd ${dir_work}
        set All_t = ` lsd | grep -v '[a-Z;A-Z]' `
        cd ${dir_work_up}
    
        #------------------------------------------------------------------------------
        
        ### creating movies from PNG files (if more than [min_Nb_t] time directories)
        
        # flv : bad quality
        # avi : good quality but bigger than MP4 file
        # mp4 : good quality
        set movie_type = flv 
        set movie_type = avi 
        set movie_type = mp4 
        
        ## temporary movie folder : PNG files from D folder are renamed and copied in temporary movie folder,
        #                                         if there is more than min_Nb_t (=5) time directories (i.e. when D=residualSpeed_*)
        #                                         (for example [residualSpeed_2/750.25/PIV_new_Ux.png] is copied in [tmp_movie/75025.png])
        
        if -e ${dir_work_up}/tmp_movie \rm -R ${dir_work_up}/tmp_movie

        set min_Nb_t = 8
        set code_Nb_t = ` echo ${All_t} | awk -v min_N=${min_Nb_t} '{ if (NF>min_N) print 1; else print 0 }' `
        if ( ${code_Nb_t} == 1 ) then

          if (!(-e ${dir_work_up}/tmp_movie)) mkdir ${dir_work_up}/tmp_movie

          set All_png = ( \
            Ux_calculator_pointVolumeInterpolator_slice_withoutGrid.png \
            Uy_calculator_pointVolumeInterpolator_slice_withoutGrid.png \
            PIV_new_Ux.png \
            PIV_new_Uy.png \
          )
          foreach png_file ( ${All_png} )
                        
            cd ${dir_work_up}

            set flv_file = ` echo ${png_file} | sed s/"png"/"flv"/g `
            set avi_file = ` echo ${png_file} | sed s/"png"/"avi"/g `
            set mp4_file = ` echo ${png_file} | sed s/"png"/"mp4"/g `

            set i = 1
            foreach t ( ${All_t} )

              set nom = `echo ${i} | awk '{ printf("%04d",$1) }' `
              if -e ${dir_work}/${t}/${png_file} \cp ${dir_work}/${t}/${png_file} ${dir_work_up}/tmp_movie/${nom}.png
              
              set i = ` echo ${i} | awk '{ print $1+1}' `
              
            end
            
            if ( ${movie_type} == "mp4" ) then
            
              ffmpeg -r 10 -i ${dir_work_up}/tmp_movie/%04d.png ${dir_work}/${mp4_file}
              set info = "Cf. file ${dir_work}/${mp4_file}\n (mplayer -speed 0.5 ${dir_work}/${mp4_file}) "
           
            else
           
              # creating AVI movie
              
              mencoder "mf://${dir_work_up}/tmp_movie/????.png" -o frame.avi -ovc lavc -lavcopts vcodec=mjpeg
              #mplayer -speed 0.1 frame.avi

              if  ( ${movie_type} == "avi" ) then
              
                mv frame.avi ${dir_work}/${avi_file}
                set info = "Cf. file ${dir_work}/${avi_file}\n (mplayer -speed 0.5 ${dir_work}/${avi_file}) "
              
              else
              
                # converting AVI to FLV
                
                ffmpeg -i frame.avi -f flv -y frame.flv
                if -e frame.avi \rm frame.avi
                #vlc --rate 0.5 frame.flv
                # mplayer -speed 0.5 frame.flv
                if -e frame.flv \mv frame.flv ${dir_work}/${flv_file}
                
                set info = "Cf. file ${dir_work}/${flv_file}\n (mplayer -speed 0.5 ${dir_work}/${flv_file}) "
                
              endif
          
            endif

            WRITE_LINE; WRITE_INFO "${info}";  WRITE_LINE
          
          end
          
        else
        
          set warning = "${D} : not enough PNG files to create movies (less than ${min_Nb_t})"
          WRITE_LINE; WRITE_WARNING "${warning}";  WRITE_LINE
          
        endif
       
        ## deleting temporary movie folder 
      
        if -e tmp_movie \rm -R tmp_movie
  
        #------------------------------------------------------------------------------
        
        ### covariance for residualSpeed_* (if more than [min_Nb_t] time directories)
        
        set min_Nb_t = 3
        set code_Nb_t = ` echo ${All_t} | awk -v min_N=${min_Nb_t} '{ if (NF>min_N) print 1; else print 0 }' `

        #set code_residualSpeed = ` echo ${D} | grep "residualSpeed_" | wc -l `
        if (( ${code_residualSpeed} != 0 ) && ( ${code_Nb_t} == 1 )) then
        
          # covariance is calculated by paraview script (like [util/cov_after_gaussSmoothing_model.py])
          # before slicing and smoothing 
          # NOTE : cov(x*y)=mean(x*y)-mean(x)*mean(y) should be equal to mean(x*y) 
          #              since mean(x) and mean(y) should be =0
          
          cd ${dir_work_up}
          \cp -R ${dir_util} .
          \cp util/cov_after_gaussSmoothing.csh .
          tcsh cov_after_gaussSmoothing.csh ${D} ${DIR0} ${DIR1} ${t_first} ${t_last}
          \cp cov_after_gaussSmoothing.csh ${D}
          \rm -R ${D}/tmp*
          
          set info = "Cf. files in ${dir_work} :\n\t1) PIV_new_covInv_U(...).png\n"
          set info = "${info}\t2) cov_after_gaussSmoothing/cov_mean_(...).png :\n"
          set info = "${info}\t\tLeft  = cov ( mean(ui x uj)-mean(ui) x mean(uj) )\n"
          set info = "${info}\t\tRight = cov ( mean(ui x uj) )"
          WRITE_LINE; WRITE_INFO "${info}";  WRITE_LINE
          
        else
        
          if (  ${code_residualSpeed} != 0 ) then
          
            set warning = "${D} : not enough time files to calculate covariance (less than ${min_Nb_t})"
            WRITE_LINE; WRITE_WARNING "${warning}";  WRITE_LINE
            
          endif
          
        endif
      
      endif
  
      cd ${dir_ici}
      
    endif
    #------------------------------------------------------------------------------
      
  end

end
#------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# tree example for input and output results :
# 
#         ├── data_red_lum_cpp
#         │    ├── DNS300-D1_Lz1pi
#         │    │    ├── FakePIV_noise2
#         │    │    ├── openfoam_data
#         │    │    │    ├── 0
#         │    │    │    .......
#         │    │    │    ├── 800
#         │    │    │    ├── constant
#         │    │    │    └── system
#         │    │    ├── ROMDNS-v1
#         │    │    │    ├── 0
#         │    │    │    ├── constant
#         │    │    │    ├── ITHACAoutput
#         │    │    │    ├── ROM_PIV
#         │    │    │    │    ├── mean
#         │    │    │    │    ├── residualSpeed_2
#         │    │    │    │    └── spatialModes_2modes
#         │    │    │    └── system
#         │    │    └── util
#         │    │          ├── DNS_info.txt
#         │    │          ├── DNS_to_FakePIV_info.txt
#         │    │          └── PIV_info.txt
#         └──podfs2
#              ├── run_info.txt
#              └── util
#                    ├── calculator_PointVolumeInterpolation_model.py
#                    ├── cov_after_gaussSmoothing.csh
#                    ├── cov_after_gaussSmoothing_model.py
#                    ├── dim_DNS_cyl.csh
#                    ├── openfoamDNS_to_pseudoPIV_param.txt
#                    └── openfoamDNS_to_pseudoPIV.csh
#
# ------------------------------------------------------------------------------
# 
# HOW to have the script RUNNING
# 
# 1) The script [openfoamDNS_to_pseudoPIV_all.csh] can work without input arguments :
# 
#   command = tcsh openfoamDNS_to_pseudoPIV_all.csh
#   
#   however, the USER is always prompted to valid (or choose another value) for two parameters :
#   
#     1.a) the PATH for [run_info.txt] file
#     1.b) the PATH for [util] directory 
#       
#       tree example :
#       ├── data_red_lum_cpp
#       │    └── DNS300-D1_Lz1pi
#       └──podfs2
#            ├── run_info.txt
#            └── util
#   
# 2) It can also have three optional arguments (Cf. below [WHAT CAN be MODIFIED by the USER]) :
# 
#   2.a) arg1 = Zslice value (ex : tcsh tcsh openfoamDNS_to_pseudoPIV_all.csh 2.45)
#   2.b) arg2 = Case type ( ex : tcsh tcsh openfoamDNS_to_pseudoPIV_all.csh 1.6 DNS)
#   2.c) arg3 = ROM type ( ex : tcsh tcsh openfoamDNS_to_pseudoPIV_all.csh 1.6 ROM mean)
# 
# ------------------------------------------------------------------------------
# 
# WHAT CAN be MODIFIED by the USER in (*) [openfoamDNS_to_pseudoPIV_all.csh] :
# 
# (*) or during RUNNING [openfoamDNS_to_pseudoPIV_all.csh] 
# 
# 1) parameters that define the input datas (DNS simulation, or ROMDNS) used :
# 
#   1.a) [dir_RedLUM] : be default a directory which includes a [podfs2] directory
#   1.b) [fic_run_info] : by default fic_run_info=dir_RedLUM/podfs2/run_info.txt
#   
#   NOTEa : the script prompts the USER to valid or to choose another [fic_run_info] 
#   
#   NOTEb : the [util] directory is by default in the same directory as [fic_run_info]
#                 the script prompts the USER to valid or to choose another [util] directory
#       
#       tree example :
#       ├── data_red_lum_cpp
#       │    └── DNS300-D1_Lz1pi
#       └──podfs2
#            ├── run_info.txt
#            └── util
# 
# 2) parameters that define the synthetic PIV from DNS :
# 
#   2.a) Z position of the slice for pseudoPIV 
#          by default Zslice=1 : this parameter is the first command line argument
#          
#          for example :
#          
#           [tcsh openfoamDNS_to_pseudoPIV_all.csh 2.3] means 
#             - Zlice=2.3
# 
# 3) parameters that define case types : FakePIV or ROM_PIV and ROM folders :
# 
#   3.a) parameters that define case types : FakePIV or ROM_PIV 
#          by default, All_CASE=("DNS" "ROM") : it can be modified by the second command line argument
#          
#          for example :
#          
#           [tcsh openfoamDNS_to_pseudoPIV_all.csh 2.3] means ROMppp
#             - Zlice=2.3
#             - only ROM_PIV is concerned
#             
#           [tcsh openfoamDNS_to_pseudoPIV_all.csh 2.3] means ROM---DNS
#             - Zlice=2.3
#             - FakePIV and ROM_PIV are concerned
# 
#           [tcsh openfoamDNS_to_pseudoPIV_all.csh 2.3] means aaDNS
#             - Zlice=2.3
#             - only FakePIV is concerned
#           
#           WARNING : the second argument musn't have BLANK characters : 
#               the following expressions don't work :
#               - [tcsh openfoamDNS_to_pseudoPIV_all.csh 2.3] means DNS ROM
#               - [tcsh openfoamDNS_to_pseudoPIV_all.csh 2.3] means "DNS ROM"
#           
#   3.b) the subdirectories in the case of ROM_PIV
#           by default, all subdirectories [mean], [spatialModes_...] and [residualSpeed_...] are used :
#           it can be modified by the third command line argument
#          
#          for example :
#          
#           [tcsh openfoamDNS_to_pseudoPIV_all.csh 2.3] means ROMppp mean
#             - Zlice=2.3
#             - only ROM_PIV is concerned
#             - only mean is concerned
#   
#           WARNING : the third argument musn't have BLANK characters and must correspond to an existant directory : 
#               the following expressions don't work :
#               - [tcsh openfoamDNS_to_pseudoPIV_all.csh 2.3] means ROM mean_ppp
#               - [tcsh openfoamDNS_to_pseudoPIV_all.csh 2.3] means ROM spatialModes_567
#                  
# 4) for preleminary tests, it can also be useful to modify time [t_first] and [t_last] 
# 
#   4.a) when the subdirectory=[residualSpeed_...] in case of ROMDNS datas
#   4.b) when the input datas is raw DNS simulation (directory [.../openfoam_data...])        
# 
# ------------------------------------------------------------------------------
# 
# FILE or DIRECTORY that must be present in the run script directory :
# 
# 1) The shell script file [openfoamDNS_to_pseudoPIV_all.csh] 
#      that can be modified by the user
# 
# FILE or DIRECTORY that must be accessible by the run script directory :
# 
# 1) The [util] directory which contains files used by [openfoamDNS_to_pseudoPIV_all.csh] : 
#      the user doesn't have to modify files in this directory
# 
# ------------------------------------------------------------------------------
# 
# DIRECTORY where RESULTS are created :
# 
# All directories from the script [openfoamDNS_to_pseudoPIV_all.csh]
# are created relatively to informations from the [run_info.txt] file : 
# 
#   the upper directory DIR0 depends of case type
# 
#     - for Fake PIV from OpenFoam DNS, DIR0 is defined by [PATH_openfoam_data]
#       and [type_data_C] parameters : DIR0=PATH_openfoam_data/type_data_C.
#       in this case, results are saved DIR0/FakePIV_noise...
#  
#         tree example :
#         ├── data_red_lum_cpp
#         │    ├── DNS300-D1_Lz1pi
#         │    │    ├── FakePIV_noise2
#         │    │    ├── openfoam_data
#       
#     - for ROM PIV from ITHACA ROM, the parameter [redlumcpp_code_version] is added :
#       DIR0=PATH_openfoam_data/type_data_C/redlumcpp_code_version.
#       in this case, results are saved DIR0/ROM_PIV.
#       
#         tree example :
#         ├── data_red_lum_cpp
#         │    ├── DNS300-D1_Lz1pi
#         │    │    ├── ROMDNS-v1
#         │    │    │    ├── ROM_PIV
#         │    │    │    │    ├── mean
#         │    │    │    │    ├── residualSpeed_2
#         │    │    │    │    └── spatialModes_2modes
# 
# !!! BE CAREFUL  to have enough memory to save results!!!
# !!!    for example, size of some results directories when
# !!!        time subdirectories are spaced by dt=0.25 :
# !!!        45M	mean : 1 subdirectory (=[1])
# !!!        75M	Modes_2modes : 2 subdirectories (=mode [1] and mode [2])
# !!!        61G	residualSpeed_2 : 2000  subdirectories (= t=[100] to t=[600])
# !!!        11G	openfoam_data : 400  subdirectories (= t=[600] to t=[700])
#
# ------------------------------------------------------------------------------
# 
# WHAT ERRORS may occur
# 
# 1) No dimensionless input simulation : 
# 
#     in this case, the diameter of the cylinder isn't equal to DNS_Dcyl=1
#     
# 2) Missing files in the [util] directory
#        
#      - [util/dim_DNS_cyl.csh] :
#        shell script to verify the cylinder diameter [DNS_Dcyl] value
# 
#      - [util/openfoamDNS_to_pseudoPIV.csh] : 
#        this is the script called by the present script [openfoamDNS_to_pseudoPIV_all.csh]
#        
#      - [util/openfoamDNS_to_pseudoPIV_param.txt] :
#        liste of parameters adjusted by the present script [openfoamDNS_to_pseudoPIV_all.csh]
#        
#      - [util/calculator_PointVolumeInterpolation_model.py] : 
#        python script model used by the script [openfoamDNS_to_pseudoPIV.csh]
#        
#      - [util/cov_after_gaussSmoothing.csh] :
#        shell script used to calculated (1/cov) in case of [residualSpeed_...]
#        
#      - [util/cov_after_gaussSmoothing_model.py]
#        python script model used by the script [cov_after_gaussSmoothing.csh]
#         
#         tree example :
#         ├── data_red_lum_cpp
#         │    └── DNS300-D1_Lz1pi
#         └──podfs2
#              ├── run_info.txt
#              └── util
#                    ├── calculator_PointVolumeInterpolation_model.py
#                    ├── cov_after_gaussSmoothing.csh
#                    ├── cov_after_gaussSmoothing_model.py
#                    ├── dim_DNS_cyl.csh
#                    ├── openfoamDNS_to_pseudoPIV_param.txt
#                    └── openfoamDNS_to_pseudoPIV.csh
#     
# 3) Missing files in the input upper DNS directory containing the following folders (*)
# 
#       - openfoam_data : raw DNS openfoam simulation
#       - ROMDNS... : ROM results
#     
#       (*) for example upper DNS directory=[data_red_lum_cpp/DNS300-GeoLES3900]
#       
#     this upper directory must also include a [util] directory 
#     with at least the 3 following files inside :
#     
#       - [util/DNS_info.txt] for DNS characteristics
#       - [util/PIV_info.txt] for PIV characteristics
#       - [util/DNS_to_FakePIV_info.txt] for transformation DNS to pseudo PIV
#         
#         tree example :
#         ├── data_red_lum_cpp
#         │    ├── DNS300-D1_Lz1pi
#         │    │    └── util
#         │    │          ├── DNS_info.txt
#         │    │          ├── DNS_to_FakePIV_info.txt
#         │    │          └── PIV_info.txt
# 
# ------------------------------------------------------------------------------
# 
# SUMMARY of the method used :
# 
# 1) Paraview operation (pvbatch [python file]) is used to generate CSV file
# 
#  step1 = calculator -> Ux(y) scalar
#  step2 = Ux(y) gaussian interpolation on bounded box
#  step3 = slice Z=1 (or Lz/2) of the Ux(y) gaussian interpolation
#  
#            => CSV file
# 
# 2) Next operation (tcsh [shell script]) generates synthetic PIV file from CSV file
# 
#  step1 = rewritting with column IsValid
#  step2 = adding noise for data type [CASE_DNS] 
#  step3 = dimentionless PIV for data type [CASE_ROM] 
# 
#            => synthetic PIV file
# 
# NOTE : PNG files are created either by [pvbatch], or by [gnuplot], 
#             and are merged in a single [Uxy.png] file to show successive operations
# 
# ------------------------------------------------------------------------------
 
# ------------------------------------------------------------------------------
#
# Other informations concerning util files used by the present script :
#
# 1) This script calls the script [util/openfoamDNS_to_pseudoPIV.csh]
#
# 2) For the case [residualSpeed_*], after calling the script [util/openfoamDNS_to_pseudoPIV.csh], 
#   the script [util/cov_after_gaussSmoothing.csh] is also used, 
#
# ------------------------------------------------------------------------------
#
# A) example of Files used by the script [util/cov_after_gaussSmoothing.csh] :
#
#      A.1) Info file used that MUST be PRESENT in the UP directory :
#
#         A.1.a) slice_param.info created by script [util/openfoamDNS_to_pseudoPIV.csh]
#
#         A.1.b) openfoamDNS_to_pseudoPIV.info created by script [util/openfoamDNS_to_pseudoPIV.csh]
#
#      A.2) model file that MUST be PRESENT in CURRENT [util] directory :
#
#         A.2.a) python model files for [pvbatch] script :[util/cov_after_gaussSmoothing_model.py]
#
# ------------------------------------------------------------------------------
#
# B) example of Files used by the script [util/openfoamDNS_to_pseudoPIV.csh] :
#
#      B.1) Info file used that MUST be PRESENT in the CURRENT directory :
#
#         B.1.a) [DNS_info.txt] : list of characteristics of the DNS (Reynolds number, velocity, dimensions...)
#            for example :
#                #          DNS characteristics
#                300        # DNS_Re
#                1.0        # DNS_Velocity
#                5.0        # DNS_xcyl
#                0.0        # DNS_ycyl
#                1.0        # DNS_Dcyl
#                0.0        # DNS_xmin
#                20.0       # DNS_xmax
#                -10.0      # DNS_ymin
#                10.0       # DNS_ymax
#                0.0         # DNS_zmin
#                3.14       # DNS_zmax
#                0.25       # dt_DNS
#                0.0        # t0_DNS
#                800.0      # t1_DNS
# 
#            NOTE 1 : this file must at least contain values for DNS_xcyl, DNS_ycyl and DNS_Dcyl; other
#                           parameters will be redefined here from openfoam_data files [constant/polyMesh/points], 
#                           [constant/transportProperties] and [system/controlDict] 
#
#            NOTE 2 : the script [dim_DNS_cyl.csh] uses this file to compare [DNS_Dcyl] value with
#                           the value extracted from geometry (in [constant/polyMesh/points] file)
#                           - if the two values are different, there is an ERROR
#                           - if DNS_Dcyl!=1, the openfoam result is not dimensionless !
#
#         B.1.b) [PIV_info.txt] : list of characteristics of the PIV (Reynolds number, velocity, dimensions...)
#            for example :
#                #          PIV characteristics
#                300        # PIV_Re
#                0.388      # PIV_Velocity
#                -75.60     # PIV_xcyl
#                0.75       # PIV_ycyl
#                12.0       # PIV_Dcyl
#                -87.110109 # PIV_xmin
#                79.874545  # PIV_xmax
#                -49.898065 # PIV_ymin
#                52.905412  # PIV_ymax
#                0.25       # dt_PIV
#
#
#        B.1.c) [DNS_to_FakePIV_info.txt] : DNS crop and smoothing conditions to generate FakePIV
#            for example :
#                #          DNS crop
#                0.203125   # DNS_crop_GaussSmooth
#                295        # DNS_crop_Nx
#                182        # DNS_crop_Ny
#                         
#                #          RedLum Test
#                0.74       # PIV_crop_x1
#                10.44      # PIV_crop_x2
#                -2.84      # PIV_crop_y1
#                2.83       # PIV_crop_y2
#                -2.5       # DNS_crop_x1
#                15.04      # DNS_crop_x2
#                -1.95      # DNS_crop_y1
#                1.95       # DNS_crop_y2
#
#      B.2) model file that MUST be PRESENT in CURRENT [util] directory :
#         B.2.a) python model files for [pvbatch] script
#             [util/calculator_PointVolumeInterpolation_model.py]
#
#      B.3) script file that MUST be PRESENT in CURRENT [util] directory :
#         B.3.a) to verify cylinder diameter (must be equal to DNS_Dcyl=1) :
#             [util/dim_DNS_cyl.csh]
#         B.3.b) for the case of [residualSpeed_*] only :
#             [util/cov_after_gaussSmoothing.csh]
#
#      B.4) parameters file : [openfoamDNS_to_pseudoPIV_param.txt]
#            for example :
#                	#
#                	# parameters used to define pseudo PIV
#                	#
#                	
#                	mean           # case_dir
#                	2.	           # noise_MAX : max(noise) value in percent
#                	0              # code_adim
#                	1.             # Zslice
#                	TEST t=0       # DNS_info
#                	util/B0001.dat # PIV file model
#                	1	             # IsValid_ON : if=1, column IsValid like in PIV file
#                	
#                	#
#                	# other file parameters  : 
#                	#
#                	
#                	PIV_info.txt            # PIV conditions
#                	DNS_info.txt            # DNS conditions (or LES ... conditions)
#                	DNS_to_FakePIV_info.txt # crop and smoothing conditions for creating FakePIV form DNS (or LES ... )
#                	
#                	#
#                	# parameters for Python script (pvbatch) : 
#                	#
#                	
#                	0	#    code_view_withGrid : =1 if PNG file view with grid 
#                	1	#    code_view_slice_Ux1 : =1 if PNG file showing Ux(Z=Lz/2) openfoam result
#                	1	#    code_view_slice_Uy1 : =1 if PNG file showing Uy(Z=Lz/2) openfoam result
#                	0	#    code_view_pointVolumeInterpolator_Ux : =1 if PNG file showing Ux openfoam after smoothing
#                	0	#    code_view_pointVolumeInterpolator_Uy : =1 if PNG file showing Uy openfoam after smoothing
#                	1	#    code_view_slice_Ux2 : =1 if PNG file showing Ux(Z=Lz/2) openfoam after smoothing
#                	1	#    code_view_slice_Uy2 : =1 if PNG file showing Uy(Z=Lz/2) openfoam after smoothing
#                	0	#    code_csv_slice_Ux1 : =1 if CSV file showing Ux(Z=Lz/2) openfoam result
#                	0	#    code_csv_slice_Uy1 : =1 if CSV file showing Uy(Z=Lz/2) openfoam result
#                	1	#    code_csv_slice_Ux2 : =1 if CSV file showing Ux(Z=Lz/2) openfoam after smoothing
#                	1	#    code_csv_slice_Uy2 : =1 if CSV file showing Uy(Z=Lz/2) openfoam after smoothing
#                	
#
#      B.5) optional PIV model files : useful to compare with FakePIV when PIV_info.txt=f(PIV model files)
#         for example :
#           util/B0001.dat
#
#
#   C) directories created in WORKING directory :
#       for the case of [residualSpeed_*] only, the folder [cov_after_gaussSmoothing]
#
#   D) Files created :
#
#      D.1) CSV file created in current DNS directory :
#         D.1.a) if PIV model file est present : slice_Uxy1.csv
#
#      D.2) FakePIV file created in current DNS directory :
#         D.2.a) for the case of [residualSpeed_*] only : Inv_COVxy.dat
#
#      D.3) PNG file created in current DNS directory :
#
#         D.3.a) Visu parafoam of DNS with original grid : 
#            Ux_calculator_withGrid.png and Uy_calculator_withGrid.png
#         D.3.b) Visu parafoam of crop DNS with uniform Zslice grid : 
#            Ux_calculator_point*_withGrid.png and Uy_calculator_point*_withGrid.png 
#         D.3.c) Visu gnuplot of a PIV model (if PIV model file est present !) : 
#            PIV_model_*.png
#         D.3.d) Visu parafoam of Inv(cov) for the case of [residualSpeed_*] only :
#            PIV_new_covInv_*.png
#
#      D.4) PNG file created in EACH TIME current DNS directory :
#
#         D.4.a) Visu parafoam of DNS without grid : 
#            Ux_calculator_withoutGrid.png and Uy_calculator_withoutGrid.png
#         D.4.b) Visu parafoam of crop DNS without grid : 
#            Ux_calculator_point*_withoutGrid.png and Uy_calculator_point*_withoutGrid.png 
#         D.4.c) Visu gnuplot of a FakePIV : 
#            PIV_new_*.png
#         D.4.d) picture montage of above file : 
#            Uxy.png
#
#      D.4) Info file created in current DNS directory :
#
#         D.4.a) openfoamDNS_to_pseudoPIV.info 
#         D.4.b) slice.info 
#
# ------------------------------------------------------------------------------
#
# INPUT Parameters for [openfoamDNS_to_pseudoPIV.csh] :
#      fic_param IsValid_ON noise_MAX PIV_file_model case_dir Zslice code_adim DNS_info
#      fic_param   case_dir   noise_MAX   code_adim   Zslice   DNS_info   PIV_file_model   IsValid_ON 
#
#   Default parameters for python pvbatch script (PNG and CSV files to create) etc :
#      1) fic_param = openfoamDNS_to_pseudoPIV_param.txt
# 
#   Input chosen values for some of these parameters :
#
#   DNS openfoam case : mean, spatialModes_2modes, residualSpeed_2 or sillageDNSRe300
#      2) case_dir = residualSpeed_2
#   Adding white noise to pseudo PIV file generated by smoothing DNS result
#      3) noise_MAX = max(noise) value in percent
#   ASCII file coorresponding to pseudo PIV : if real values dimension (like in real PIV) code_adim = 0
#      4) code_adim = 0
#   DNS Z slice value for pseudo PIV
#      5) Zslice = 1.
#   DNS openfoam directories INFO : for example, name of directory (mean, ...) and time step 
#      6) DNS_info = "residualSpeed_2 t=100"
#   PIV model file :
#      7) PIV_file_model = util/B0001.dat
#   Adding column IsValid like in PIV file : by default value=1 for this column
#      8) IsValid_ON = 1 (yes) =0 (no)
#
# Minimal Script command example (only reading parameter file) : 
#   tcsh openfoamDNS_to_pseudoPIV.csh \
#     oepnfoamDNS_to_pseudoPIV_param.txt \
#
# Optional Script command example : noise ON with max(noise)=2%, adim=OK, Zslice=1.75, ..., IsValid OFF : 
#   tcsh openfoamDNS_to_pseudoPIV.csh \
#     oepnfoamDNS_to_pseudoPIV_param.txt \
#     residualSpeed_2 \
#     2. \
#     1 \
#     1.75 \
#     "residualSpeed_2 t=100" \
#     util/B0001.dat \
#     0
#   
# ------------------------------------------------------------------------------
