#!/bin/tcsh
#
# Laurence Wallian - ACTA - OPAALE - INRAE Rennes [Juin 2022 : Février 2023]
#
# MORAANE project : Scalian - INRAE
#
#------------------------------------------------------------------------------
#
# Object : Openfoam DNS file -> synthetic PIV file
#
#     This script creates synthetic PIV files from openfoam time/U files
#
#        NOTE : here, DNS is a generic word for "Numerical Simulation"
#
#------------------------------------------------------------------------------
##
## SUMMARY of the method used :
##
## Paraview operation (pvbatch [python file]) : Openfoam DNS file -> CSV file
##
## step1 = calculator -> Ux scalar
## step2 = Ux gaussian interpolation
## step3 = slice Z=Lz/2 of the Ux gaussian interpolation
## 
##           => CSV file
##
## Next operation (tcsh [shell script]) : CSV file -> synthetic PIV file
##
## step1 = rewritting with column IsValid
## step2 = adding noise for data type [raw openfoam results]
## step3 = dimentionless PIV for data type [ROM applied on openfoam results]
##
##           => synthetic PIV file
## 
## NOTE : PNG files are created either by [pvbatch], or by [gnuplot], 
##             and are merged in a single [Uxy.png] file to show successive operations
##
#------------------------------------------------------------------------------
#
# Script used to generate pseudo PIV from openfoam results
#
# The present directory must contain DNS openfoam directories [0], [system] and [constant] directories
#
#   A) DNS openfoam directories :
#
#      A.1) [0], [system] and [constant] directories can be found in 
#         A.1.a) raw openfoam directory (=data_Redlum_cpp/.../openfoam_data...)
#         A.1.b) ROM directory (=data_Redlum_cpp/.../ROMDNS...)
#
#      A.2) But [0] directory is usually a copy of openfoam result directory 
#         for example :
#           data_red_lum_cpp/DNS300-D1_Lz1pi/openfoam_data/0 ...
#           data_red_lum_cpp/DNS300-D1_Lz1pi/ITHACAoutput/ROMDNS-v1/mean/1
#           data_red_lum_cpp/DNS300-D1_Lz1pi/ITHACAoutput/ROMDNS-v1/spatialModes_2modes/1 ...
#           data_red_lum_cpp/DNS300-D1_Lz1pi/ITHACAoutput/ROMDNS-v1/residualSpeed_2/100 ...
#
#
#   B) Files used :
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
# 
#            NOTE 1 : execpted for parameters DNS_xcyl, DNS_ycyl and DNS_Dcyl, other parameters can be 
#                           redefined from openfoam_data files [constant/polyMesh/points], [constant/transportProperties] 
#                           and [system/controlDict] (Cf. calling script [openfoamDNS_to_pseudoPIV_all_VR.csh]) 
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
#         B.3.a) for the case of [residualSpeed_*] only :
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
#                	DNS_info.txt            # DNS conditions
#                	DNS_to_FakePIV_info.txt # crop and smoothing conditions for creating FakePIV form DNS
#                	
#                	#
#                	# parameters for Python script (pvbatch) : 
#                	#
#                	
#                 POINTS # mode_view_NoGrid : =POINTS for no smoothing view, =SURFACE for smoothing view
#                	0	#    code_view_withGrid : =1 if PNG file view with grid 
#                	1	#    code_view_slice_Ux1 : =1 if PNG file showing Ux(Z=Zslice) openfoam result
#                	1	#    code_view_slice_Uy1 : =1 if PNG file showing Uy(Z=Zslice) openfoam result
#                	0	#    code_view_pointVolumeInterpolator_Ux : =1 if PNG file showing Ux openfoam after smoothing
#                	0	#    code_view_pointVolumeInterpolator_Uy : =1 if PNG file showing Uy openfoam after smoothing
#                	1	#    code_view_slice_Ux2 : =1 if PNG file showing Ux(Z=Zslice) openfoam after smoothing
#                	1	#    code_view_slice_Uy2 : =1 if PNG file showing Uy(Z=Zslice) openfoam after smoothing
#                	0	#    code_csv_slice_Ux1 : =1 if CSV file showing Ux(Z=Zslice) openfoam result
#                	0	#    code_csv_slice_Uy1 : =1 if CSV file showing Uy(Z=Zslice) openfoam result
#                	1	#    code_csv_slice_Ux2 : =1 if CSV file showing Ux(Z=Zslice) openfoam after smoothing
#                	1	#    code_csv_slice_Uy2 : =1 if CSV file showing Uy(Z=Zslice) openfoam after smoothing
#                	
#
#      B.5) optional files
#
#         B.5.a) optional PIV model files : useful to compare with FakePIV when [PIV_info.txt]=f(PIV model files)
#            for example :
#              [util/B0001.dat]
#
#         B.5.b) optional script files : [dim_DNS_cyl.csh]
#            useful to compare cylinder diameter DNS_Dcyl 
#                  - defined in [DNS_info.txt] file and 
#                  - deduced from geometry [.../constant/polyMesh/points] file
#
#
#   C) directories created in PRESENT directory :
#       for the case of [residualSpeed_*] only, the folder [cov_after_gaussSmoothing]
#
#   D) Files created :
#
#      D.1) CSV file created in current DNS directory :
#         D.1.a) if PIV model file est present : [slice_Uxy1.csv]
#
#      D.2) FakePIV file created in current DNS directory :
#         D.2.a) for the case of [residualSpeed_*] only : [Inv_COVxy.dat]
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
#------------------------------------------------------------------------------
#      
# INPUT Parameters for [openfoamDNS_to_pseudoPIV_VR.csh] : 
#      fic_param IsValid_ON noise_MAX PIV_file_model case_dir Zslice code_adim DNS_info
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
# Script command example : only reading parameter file : 
#   tcsh openfoamDNS_to_pseudoPIV_VR.csh \
#     oepnfoamDNS_to_pseudoPIV_param.txt \
#
# Script command example : noise ON with max(noise)=2%, adim=OK, Zslice=1.75, ..., IsValid OFF : 
#   tcsh openfoamDNS_to_pseudoPIV_VR.csh \
#     oepnfoamDNS_to_pseudoPIV_param.txt \
#     residualSpeed_2 \
#     2. \
#     1 \
#     1.75 \
#     "residualSpeed_2 t=100" \
#     util/B0001.dat \
#     0
#   
#------------------------------------------------------------------------------
#   
#  IMPORTANT : current directory must contain the 3 files below
#    1) PIV_info.txt : PIV characteristics (Reynolds number, velocity, dimensions...)
#    2) DNS_info.txt : DNS characteristics (Reynolds number, velocity, dimensions...)
#    3) DNS_to_FakePIV_info.txt : DNS crop and smoothing conditions to generate FakePIV
#
if (!( ( -e PIV_info.txt ) &&  ( -e DNS_info.txt ) && (-e DNS_to_FakePIV_info.txt))) then
  echo ""
  echo "\!\!\! At least one of the three INFO files (DNS_info.txt, PIV_info.txt or DNS_to_FakePIV_info.txt) is missing \!\!\!"
  foreach fic_info ( DNS_info.txt PIV_info.txt DNS_to_FakePIV_info.txt )
    if (!(-e ${fic_info} )) echo "\!\!\! => file [${fic_info}] is missing \!\!\!"
  end
  echo ""
  exit()
else
  echo ""
  echo "OK, the three INFO files (DNS_info.txt, PIV_info.txt or DNS_to_FakePIV_info.txt) are present"
  echo ""
endif
#   
#------------------------------------------------------------------------------

### pvbatch PATH

alias pvbatch '/usr/local/ParaView-5.10.1-MPI-Linux-Python3.9-x86_64/bin/pvbatch'

#------------------------------------------------------------------------------

### INPUT parameters

## Parameters file : 

# Parameters file : defauflt values
set fic_param = openfoamDNS_to_pseudoPIV_param.txt

# Parameters file : input value
if ( $1 != "" ) set fic_param = $1

# Parameters file : check for exist
if (!( -e ${fic_param})) then
    echo ""
    echo "\!\!\! Parameters file [${fic_param}] not found \!\!\!"
    echo ""
    exit()
endif


## case = ROM folders (mean, residual_speed*, spatial*_modes) or raw openfoam DNS folder (D1_Lz1pi_Re300...)

# case : value from file parameters
set case_dir = ` cat ${fic_param} | grep "case_dir" | awk -F'#' '{ print $1 }' `

# case : input value
if ( $2 != "" ) set case_dir = $2


## noise value applied for FakePIV (always=0 for ROM_PIV)

# noise : value  from file parameters
set noise_MAX = ` cat ${fic_param} | grep "noise_MAX" | awk -F'#' '{ print $1 }' `

# noise : input value
if ( $3 != "" ) set noise_MAX = $3

## Fake PIV with adim spatial values (if code_adim=1 : always=1 for ROM_PIV folders and =0 for FakePIV )

# Fake PIV with adim spatial values : value  from file parameters
set code_adim = ` cat ${fic_param} | grep "code_adim" | awk -F'#' '{ print $1 }' `

# Fake PIV with adim spatial values : input value
if ( $4 != "" ) set code_adim = $4


## Z value for slice defining FakePIV

# Z slice : value  from file parameters 
set Zslice = ` cat ${fic_param} | grep "Zslice" | awk -F'#' '{ print $1 }' `

# Z slice : input value
if ( $5 != "" ) set Zslice = $5


## DNS info for PNG files

#set DNS_info = "example t=0 IsValid=${IsValid_ON} noise=${noise_MAX}%"
# DNS info for PNG files : value  from file parameters 
set DNS_info = ` cat ${fic_param} | grep "# " | grep " DNS_info" | grep -v "\.txt" | awk -F'#' '{ print $1 }' `

# DNS info for PNG files : input value
if ( $6 != "" ) set DNS_info = $6


## PIV model file

# PIV model file : value  from file parameters 
set PIV_file_model = ` cat ${fic_param} | grep "PIV file model" | awk -F'#' '{ print $1 }' `

# PIV model file : input value
if ( $7 != "" ) set PIV_file_model = $7

# PIV model file : check for exist
if (!( -e ${PIV_file_model})) then
    echo ""
    echo "\!\!\! PIV model file [${PIV_file_model}] not found => no PNG file [PIV_model_*.png] created\!\!\!"
    echo ""
endif


## PIV correction : change value of column [IsValid] added to FakePIV

# PIV correction : value  from file parameters 
set IsValid_ON = ` cat ${fic_param} | grep "IsValid_ON" | awk -F'#' '{ print $1 }' `

# PIV correction : input value
if ( $8 != "" ) set IsValid_ON = $8

#------------------------------------------------------------------------------

# DNS directories : contains [0], [system] and [constant] directories

if ( (!(-e 0 )) || (!(-e constant )) || (!(-e system )) ) then
  echo ""; echo "\!\!\! Directory [0], [constant] or [system] NOT FOUND \!\!\!"; echo ""
  echo "     -> Copy these directories from openfoam test directory"
  echo "          for example from [.../data_red_lum_cpp/DNS300-D1_Lz1pi]"
  echo ""
  exit()
else
  echo ""; echo "--- Using Directories [0], [constant] and [system] ---"; echo ""
  if (!(-e 1 )) then
    \cp -R 0 1
  else
    \cp 0/U 1/U
  endif
endif

#------------------------------------------------------------------------------

# extracting informations from string DNS_info

echo ""
echo "-----------------------------------------------   ${DNS_info} ------------------------------------------------------------"
echo ""
pwd
set t_DNS = `echo ${DNS_info} | sed s/"t="/"\nt="/g | grep "t=" | awk '{ print $1 }' | sed s/"t="//g `
if ( ${t_DNS} != "" ) then 
  set dt_DNS = ` cat system/controlDict | grep writeInterval | awk '{ print $2 }' | sed s/";"//g  `
  set num_DNS = `echo ${t_DNS} ${dt_DNS} | awk '{ n=$1/$2; printf("%4.4d",n) }' `
else
  set t_DNS = 0
  set dt_DNS = 0
  set num_DNS = 0000
endif

#------------------------------------------------------------------------------

# Info test file

if -e openfoamDNS_to_pseudoPIV.info \rm openfoamDNS_to_pseudoPIV.info
touch openfoamDNS_to_pseudoPIV.info

#------------------------------------------------------------------------------

# PIV file model : default values

if -e ${PIV_file_model} then

  # PIV file model : X and Y values in PIV files
  
  if -e PIV_x.txt \rm PIV_x.txt
  cat ${PIV_file_model} | grep -v "=" | \
    awk '{ x=$1+0. ; if (NF!=0) printf("%.0f\n", 1000000.*x) }' | sort -n  | uniq | \
    awk '{ x=$1+0. ; printf("%.6f\n",x/1000000.)}' > PIV_x.txt
  set PIV_xmin = `cat PIV_x.txt  | head -1 `
  set PIV_xmax = `cat PIV_x.txt  | tail -1 `

  if -e PIV_y.txt \rm PIV_y.txt
  cat ${PIV_file_model} | grep -v "=" | \
    awk '{ y=$2+0. ; if (NF!=0) printf("%.0f\n", 1000000.*y) }' | sort -n  | uniq | \
    awk '{ y=$1+0. ; printf("%.6f\n",y/1000000.)}' > PIV_y.txt
  set PIV_ymin = `cat PIV_y.txt  | head -1 `
  set PIV_ymax = `cat PIV_y.txt  | tail -1 `

  set PIV_Lx = `echo ${PIV_xmin} ${PIV_xmax} | awk '{ printf("%.6f\n", $2-$1) }' `
  set PIV_Ly = `echo ${PIV_ymin} ${PIV_ymax} | awk '{ printf("%.6f\n", $2-$1) }' `
  
  # PIV file model : other information like cylinder position and diameter
  
  set DNS_crop_Nx = `cat ${PIV_file_model} | grep ZONE | awk -F',' '{ print $2 }'  | awk -F'=' '{ print $2 }' `
  set DNS_crop_Ny = `cat ${PIV_file_model} | grep ZONE | awk -F',' '{ print $3 }'  | awk -F'=' '{ print $2 }' `

  # are these values equal to those in file [PIV_info.txt] ?

  foreach var ( PIV_xmin PIV_xmax PIV_ymin PIV_ymax )
  
    if ( ${var} == PIV_xmin ) set x = ${PIV_xmin}
    if ( ${var} == PIV_ymin ) set x = ${PIV_ymin}
    if ( ${var} == PIV_xmax ) set x = ${PIV_xmax}
    if ( ${var} == PIV_ymax ) set x = ${PIV_ymax}
    set y = ` cat PIV_info.txt | grep "# " | grep " ${var}" | awk '{ print $1 }' `
    set code_var = ` echo ${x} ${y} | awk '{ d=$2-$1; d=sqrt(d*d); if (d<0.000001) print 1; else print 0 }' `
    if ( ${code_var} == 0 ) then
      echo ""
      echo "\!\!\! ${var} value from [PIV_info.txt] file =${y} != ${x} \!\!\!"
      echo ""
      echo "\!\!\! [PIV_info.txt] file or [${PIV_file_model}] file must be changed\!\!\!"
    endif
    
  end

  foreach var ( DNS_crop_Nx DNS_crop_Ny )
  
    if ( ${var} == DNS_crop_Nx ) set x = ${DNS_crop_Nx}
    if ( ${var} == DNS_crop_Ny ) set x = ${DNS_crop_Ny}
    set y = ` cat DNS_to_FakePIV_info.txt | grep "# " | grep " ${var}" | awk '{ print $1 }' `
    set code_var = ` echo ${x} ${y} | awk '{ d=$2-$1; d=sqrt(d*d); if (d<0.000001) print 1; else print 0 }' `
    if ( ${code_var} == 0 ) then
      echo ""
      echo "\!\!\! ${var} value from [DNS_to_FakePIV_info.txt] file =${y} != ${x} \!\!\!"
      echo ""
      echo "\!\!\! [DNS_to_FakePIV_info.txt] file or [${PIV_file_model}] file must be changed\!\!\!"
    endif
    
endif

# values from [PIV_info.txt] and [DNS_to_FakePIV_info.txt] : chosen values

set PIV_xmin = ` cat PIV_info.txt | grep "# " | grep " PIV_xmin" | awk '{ print $1 }' `
set PIV_ymin = ` cat PIV_info.txt | grep "# " | grep " PIV_ymin" | awk '{ print $1 }' `
set PIV_xmax = ` cat PIV_info.txt | grep "# " | grep " PIV_xmax" | awk '{ print $1 }' `
set PIV_ymax = ` cat PIV_info.txt | grep "# " | grep " PIV_ymax" | awk '{ print $1 }' `

set PIV_Lx = `echo ${PIV_xmin} ${PIV_xmax} | awk '{ printf("%.6f\n", $2-$1) }' `
set PIV_Ly = `echo ${PIV_ymin} ${PIV_ymax} | awk '{ printf("%.6f\n", $2-$1) }' `

set DNS_crop_Nx = ` cat DNS_to_FakePIV_info.txt | grep "# " | grep " DNS_crop_Nx" | awk '{ print $1 }' `
set DNS_crop_Ny = ` cat DNS_to_FakePIV_info.txt | grep "# " | grep " DNS_crop_Ny" | awk '{ print $1 }' `

# other PIV info :

set PIV_Dcyl = ` cat PIV_info.txt | grep PIV_Dcyl | awk '{ print $1 }' `
set PIV_xcyl = ` cat PIV_info.txt | grep PIV_xcyl | awk '{ print $1 }' `
set PIV_ycyl = ` cat PIV_info.txt | grep PIV_ycyl | awk '{ print $1 }' `
set PIV_Velocity = ` cat PIV_info.txt | grep PIV_Velocity | awk '{ print $1 }' `

# updating INFO file

echo "" >> openfoamDNS_to_pseudoPIV.info
echo ""  >> openfoamDNS_to_pseudoPIV.info
if -e ${PIV_file_model} then
  echo "PIV model : INFO from file [${PIV_file_model}] : default values" >> openfoamDNS_to_pseudoPIV.info
  cat ${PIV_file_model} | \
    grep "="  | sed s/" ="/"="/g | sed s/"= "/"="/g | \
    awk  '{ for (i=1;i<NF;i++) printf("%s ",$i); print $NF; }' | \
    awk -F'=' '{ printf("%-10s = ",$1); for (i=2;i<NF;i++) printf("%s ",$i); print $NF; }' >> openfoamDNS_to_pseudoPIV.info
endif
echo ""  >> openfoamDNS_to_pseudoPIV.info
echo "PIV model : INFO from file [PIV_info.txt] and from file [DNS_to_FakePIV_info.txt]" >> openfoamDNS_to_pseudoPIV.info
echo "" >> openfoamDNS_to_pseudoPIV.info
echo "   -> PIV from DNS geometry : " >> openfoamDNS_to_pseudoPIV.info
echo "      X=[${PIV_xmin}:${PIV_xmax}] Y=[${PIV_ymin}:${PIV_ymax}]" >> openfoamDNS_to_pseudoPIV.info
echo "      Box=[ ${PIV_Lx} x ${PIV_Ly} ] (mm2)" >> openfoamDNS_to_pseudoPIV.info
echo "      cylinder center=(${PIV_xcyl},${PIV_ycyl}) Radius=${PIV_Dcyl}/2 (mm)"  >> openfoamDNS_to_pseudoPIV.info
echo "      [ ${DNS_crop_Nx} x ${DNS_crop_Ny} ] points" >> openfoamDNS_to_pseudoPIV.info
echo "" >> openfoamDNS_to_pseudoPIV.info

echo "" >> openfoamDNS_to_pseudoPIV.info
echo "PIV model : INFO from file [PIV_info.txt]" >> openfoamDNS_to_pseudoPIV.info
echo "" >> openfoamDNS_to_pseudoPIV.info
echo "  PIV Velocity    : PIV_Velocit=${PIV_Velocity}" >> openfoamDNS_to_pseudoPIV.info
echo "" >> openfoamDNS_to_pseudoPIV.info

set DNS_crop_GaussSmooth = ` cat DNS_to_FakePIV_info.txt | grep "# " | grep " DNS_crop_GaussSmooth" | awk '{ print $1 }' `

echo "" >> openfoamDNS_to_pseudoPIV.info
echo "PIV model : INFO from file [DNS_to_FakePIV_info.txt]" >> openfoamDNS_to_pseudoPIV.info
echo "" >> openfoamDNS_to_pseudoPIV.info
echo "  Gauss Value applied on DNS to create FakePIV    : DNS_crop_GaussSmooth=${DNS_crop_GaussSmooth}" >> openfoamDNS_to_pseudoPIV.info
echo "" >> openfoamDNS_to_pseudoPIV.info


# DNS domain

set DNS_xmin = ` cat DNS_info.txt | grep "# " | grep " DNS_xmin" | awk '{ print $1 }' `
set DNS_ymin = ` cat DNS_info.txt | grep "# " | grep " DNS_ymin" | awk '{ print $1 }' `
set DNS_zmin = ` cat DNS_info.txt | grep "# " | grep " DNS_zmin" | awk '{ print $1 }' `
set DNS_xmax = ` cat DNS_info.txt | grep "# " | grep " DNS_xmax" | awk '{ print $1 }' `
set DNS_ymax = ` cat DNS_info.txt | grep "# " | grep " DNS_ymax" | awk '{ print $1 }' `
set DNS_zmax = ` cat DNS_info.txt | grep "# " | grep " DNS_zmax" | awk '{ print $1 }' `

set DNS_xmid = `echo ${DNS_xmin} ${DNS_xmax} | awk '{ printf("%.6f\n", ($2+$1+0.)/2.) }' `
set DNS_ymid = `echo ${DNS_ymin} ${DNS_ymax} | awk '{ printf("%.6f\n", ($2+$1+0.)/2.) }' `
set DNS_zmid = `echo ${DNS_zmin} ${DNS_zmax} | awk '{ printf("%.6f\n", ($2+$1+0.)/2.) }' `

set DNS_Lx = `echo ${DNS_xmin} ${DNS_xmax} | awk '{ printf("%.6f\n", $2-$1) }' `
set DNS_Ly = `echo ${DNS_ymin} ${DNS_ymax} | awk '{ printf("%.6f\n", $2-$1) }' `
set DNS_Lz = `echo ${DNS_zmin} ${DNS_zmax} | awk '{ printf("%.6f\n", $2-$1) }' `

set DNS_Dcyl = ` cat DNS_info.txt | grep DNS_Dcyl | awk '{ print $1 }' `
set DNS_xcyl = ` cat DNS_info.txt | grep DNS_xcyl | awk '{ print $1 }' `
set DNS_ycyl = ` cat DNS_info.txt | grep DNS_ycyl | awk '{ print $1 }' `
set DNS_Velocity = ` cat DNS_info.txt | grep DNS_Velocity | awk '{ print $1 }' `

# # !!! if DNS_Dcyl != 1.0 => updating INFO file then exit !!! 
# 
# echo ""  >> openfoamDNS_to_pseudoPIV.info
# \cp util/dim_DNS_cyl.csh .
# set DNS_cyl = ` tcsh dim_DNS_cyl.csh | grep "=> Cylinder diameter =" | awk '{ print $5 }' `
# set dd = ` echo ${DNS_cyl} | awk '{ dd=sqrt(($1-1.)**2); if (dd<=0.0001) print 0; else print 1 }' `
# echo ""
# if ( ${dd} == 0 ) then
#   echo "DNS points : OK, cylinder diameter = 1 : Cf. dim_DNS_cyl.png"
#   echo ""
#   echo "DNS points : OK, cylinder diameter = 1 : Cf. dim_DNS_cyl.png"  >> openfoamDNS_to_pseudoPIV.info
#   echo ""  >> openfoamDNS_to_pseudoPIV.info
# else
#   echo "\!\!\! OUPS \!\!\! cylinder diameter = ${DNS_cyl} != 1 \!\!\! : Cf. dim_DNS_cyl.png"
#   echo ""
#   echo "\!\!\! OUPS \!\!\! cylinder diameter = ${DNS_cyl} != 1 \!\!\! : Cf. dim_DNS_cyl.png"  >> openfoamDNS_to_pseudoPIV.info
#   echo ""  >> openfoamDNS_to_pseudoPIV.info
#   exit()
# endif

# updating INFO file

echo ""  >> openfoamDNS_to_pseudoPIV.info
echo "DNS OpenFoam : INFO from file 1/U" >> openfoamDNS_to_pseudoPIV.info
echo ""  >> openfoamDNS_to_pseudoPIV.info
echo "   -> OpenFoam geometry : " >> openfoamDNS_to_pseudoPIV.info
echo "      X=[${DNS_xmin}:${DNS_xmax}] Y=[${DNS_ymin}:${DNS_ymax}]" >> openfoamDNS_to_pseudoPIV.info
echo "      Box=[ ${DNS_Lx} x ${DNS_Ly} ]" >> openfoamDNS_to_pseudoPIV.info
echo "      cylinder center=(${DNS_xcyl},${DNS_ycyl}) Radius=${DNS_Dcyl}/2" >> openfoamDNS_to_pseudoPIV.info
echo "" >> openfoamDNS_to_pseudoPIV.info

# DNS domain => DNS subdomain [x0:x0+Lx][y0:y0+Ly]

# DNS domain when DNS_Dcyl=1 (as expected for geometry of DNS adimensionnal simulation)

set DNS_crop_x0 = ` echo ${DNS_xcyl} ${PIV_xcyl} ${PIV_xmin} ${PIV_Dcyl} | awk '{ D_c=$1+0.; P_c=$2+0.; P_m=$3+0.; P_d=$4+0.; print D_c-(P_c-P_m)/P_d }' `
set DNS_crop_y0 = ` echo ${DNS_ycyl} ${PIV_ycyl} ${PIV_ymin} ${PIV_Dcyl} | awk '{ D_c=$1+0.; P_c=$2+0.; P_m=$3+0.; P_d=$4+0.; print D_c-(P_c-P_m)/P_d }' `
set DNS_crop_Lx = ` echo ${PIV_xmax} ${PIV_xmin} ${PIV_Dcyl} | awk '{ P_M=$1+0.; P_m=$2+0.; P_d=$3+0.; print (P_M-P_m)/P_d }' `
set DNS_crop_Ly = ` echo ${PIV_ymax} ${PIV_ymin} ${PIV_Dcyl} | awk '{ P_M=$1+0.; P_m=$2+0.; P_d=$3+0.; print (P_M-P_m)/P_d }' `

# # DNS domain when DNS_Dcyl != 1 (why ????!!!)
# 
# set DNS_crop_x0 = ` echo ${DNS_xcyl} ${PIV_xcyl} ${PIV_xmin} ${PIV_Dcyl} ${DNS_Dcyl} | \
#                                      awk '{ D_c=$1+0.; P_c=$2+0.; P_m=$3+0.; P_d=$4+0.; D_d=$5+0.; print D_c-(P_c-P_m)/P_d*D_d }' `
# set DNS_crop_y0 = ` echo ${DNS_ycyl} ${PIV_ycyl} ${PIV_ymin} ${PIV_Dcyl} ${DNS_Dcyl} | \
#                                      awk '{ D_c=$1+0.; P_c=$2+0.; P_m=$3+0.; P_d=$4+0.; D_d=$5+0.; print D_c-(P_c-P_m)/P_d*D_d }' `
#                                      
# set DNS_crop_Lx = ` echo ${PIV_xmax} ${PIV_xmin} ${PIV_Dcyl} ${DNS_Dcyl} | \
#                                      awk '{ P_M=$1+0.; P_m=$2+0.; P_d=$3+0.; D_d=$4+0.; print (P_M-P_m)/P_d*D_d }' `
# set DNS_crop_Ly = ` echo ${PIV_ymax} ${PIV_ymin} ${PIV_Dcyl} ${DNS_Dcyl} | \
#                                      awk '{ P_M=$1+0.; P_m=$2+0.; P_d=$3+0.; D_d=$4+0.; print (P_M-P_m)/P_d*D_d }' `

# set DNS_crop_Lx = ` echo ${DNS_crop_x0} ${DNS_crop_Lx} ${DNS_Lx} | awk '{ if ($1+$2>$3) print $3-$1-0.01; else print $2-0.01 }' `
# set DNS_crop_Ly = ` echo ${DNS_crop_y0} ${DNS_crop_Ly} ${DNS_Ly} | awk '{ if ($1+$2>$3) print $3-$1-0.01; else print $2-0.01 }' `

# DNS gauss resolution to extract slice=new PIV

set DNS_crop_Rx = ` echo ${DNS_crop_Nx} | awk '{ print $1-1 }' `
set DNS_crop_Ry = ` echo ${DNS_crop_Ny} | awk '{ print $1-1 }' `

# updating INFO file

echo "" >> openfoamDNS_to_pseudoPIV.info
echo "Lines to add/modifiy in PYTHON paraview file" >> openfoamDNS_to_pseudoPIV.info
echo "" >> openfoamDNS_to_pseudoPIV.info
echo "       pointVolumeInterpolator_U*.Kernel.Radius = ${DNS_crop_GaussSmooth}" >> openfoamDNS_to_pseudoPIV.info
echo "       pointVolumeInterpolator_U*.Source.Origin = [${DNS_crop_x0}, ${DNS_crop_y0}]" >> openfoamDNS_to_pseudoPIV.info
echo "       pointVolumeInterpolator_U*.Source.Scale = [${DNS_crop_Lx}, ${DNS_crop_Ly}]" >> openfoamDNS_to_pseudoPIV.info
echo "       pointVolumeInterpolator_U*.Source.RefinementMode = 'Use resolution'" >> openfoamDNS_to_pseudoPIV.info
echo "       pointVolumeInterpolator_U*.Source.Resolution = [${DNS_crop_Rx}, ${DNS_crop_Ry}, 20]" >> openfoamDNS_to_pseudoPIV.info
echo "" >> openfoamDNS_to_pseudoPIV.info

echo "# SUMMARY : " >> openfoamDNS_to_pseudoPIV.info
echo "PIV_Dcyl=${PIV_Dcyl}" >> openfoamDNS_to_pseudoPIV.info
echo "PIV_xcyl=${PIV_xcyl}" >> openfoamDNS_to_pseudoPIV.info
echo "PIV_ycyl=${PIV_ycyl}" >> openfoamDNS_to_pseudoPIV.info
echo "PIV_xmin=${PIV_xmin}" >> openfoamDNS_to_pseudoPIV.info
echo "PIV_ymin=${PIV_ymin}" >> openfoamDNS_to_pseudoPIV.info
echo "PIV_xmax=${PIV_xmax}" >> openfoamDNS_to_pseudoPIV.info
echo "PIV_ymax=${PIV_ymax}" >> openfoamDNS_to_pseudoPIV.info
echo "  => PIV_Lx=${PIV_Lx}" >> openfoamDNS_to_pseudoPIV.info
echo "  => PIV_Ly=${PIV_Ly}" >> openfoamDNS_to_pseudoPIV.info
echo "PIV_Velocity=${PIV_Velocity}" >> openfoamDNS_to_pseudoPIV.info
echo "" >> openfoamDNS_to_pseudoPIV.info
echo "DNS_Dcyl=${DNS_Dcyl}" >> openfoamDNS_to_pseudoPIV.info
echo "DNS_xcyl=${DNS_xcyl}" >> openfoamDNS_to_pseudoPIV.info
echo "DNS_ycyl=${DNS_ycyl}" >> openfoamDNS_to_pseudoPIV.info
echo "DNS_xmin=${DNS_xmin}" >> openfoamDNS_to_pseudoPIV.info
echo "DNS_ymin=${DNS_ymin}" >> openfoamDNS_to_pseudoPIV.info
echo "DNS_xmax=${DNS_xmax}" >> openfoamDNS_to_pseudoPIV.info
echo "DNS_ymax=${DNS_ymax}" >> openfoamDNS_to_pseudoPIV.info
echo "  => DNS_Lx=${DNS_Lx}" >> openfoamDNS_to_pseudoPIV.info
echo "  => DNS_Ly=${DNS_Ly}" >> openfoamDNS_to_pseudoPIV.info
echo "DNS_Velocity=${DNS_Velocity}" >> openfoamDNS_to_pseudoPIV.info
echo "" >> openfoamDNS_to_pseudoPIV.info
echo "DNS_crop_Nx=${DNS_crop_Nx}" >> openfoamDNS_to_pseudoPIV.info
echo "DNS_crop_Ny=${DNS_crop_Ny}" >> openfoamDNS_to_pseudoPIV.info
echo "DNS_crop_x0=${DNS_crop_x0}" >> openfoamDNS_to_pseudoPIV.info
echo "DNS_crop_y0=${DNS_crop_y0}" >> openfoamDNS_to_pseudoPIV.info
echo "DNS_crop_GaussSmooth=${DNS_crop_GaussSmooth}" >> openfoamDNS_to_pseudoPIV.info
echo "" >> openfoamDNS_to_pseudoPIV.info

# DNS crop BOX reduction if necessary => new Lx, Rx, Ly and Ry
#   NOTE : usually not used when DNS_Dcyl=1 as expected

set code_Lx = `echo ${DNS_crop_x0} ${DNS_crop_Lx} ${DNS_Lx} | awk '{ d=$3-($1+$2)+0.; if (d<0.) print 1; else print 0 }' `
if ( ${code_Lx} == 1 ) then

  set dNx = `echo ${DNS_crop_x0} ${DNS_crop_Lx} ${DNS_Lx} ${DNS_crop_Nx} | awk '{ d=$3-($1+$2)+0.; dx=($1+$2+0.) /($4-1.); printf("%.0f",-d/dx+1.) }' `
  set DNS_crop_Lx = `echo ${DNS_crop_Lx} ${DNS_crop_Rx} ${dNx} | awk '{ print ($1+0.)/($2+0.)*($2-$3+0.) }' `
  set DNS_crop_Rx = `echo ${DNS_crop_Rx} ${dNx} | awk '{ print ($1-$2+0.) }' `
  echo "  -> reduced BOX with ${DNS_crop_Nx}-${dNx} points on X axis" >> openfoamDNS_to_pseudoPIV.info
  
endif

set code_Ly = `echo ${DNS_crop_y0} ${DNS_crop_Ly} ${DNS_Ly} | awk '{ d=$3-($1+$2)+0.; if (d<0.) print 1; else print 0 }' `
if ( ${code_Ly} == 1 ) then

  set dNy = `echo ${DNS_crop_y0} ${DNS_crop_Ly} ${DNS_Ly} ${DNS_crop_Ny} | awk '{ d=$3-($1+$2)+0.; dx=($1+$2+0.) /($4-1.); printf("%.0f",-d/dx+1.) }' `
  set DNS_crop_Ly = `echo ${DNS_crop_Ly} ${DNS_crop_Ry} ${dNy} | awk '{ print ($1+0.)/($2+0.)*($2-$3+0.) }' `
  set DNS_crop_Ry = `echo ${DNS_crop_Ry} ${dNy} | awk '{ print ($1-$2+0.) }' `
  echo "  -> reduced BOX with ${DNS_crop_Ny}-${dNy} points on Y axis" >> openfoamDNS_to_pseudoPIV.info
  
endif

echo "DNS_crop_Lx=${DNS_crop_Lx}" >> openfoamDNS_to_pseudoPIV.info
echo "  => DNS_crop_Rx=${DNS_crop_Rx}" >> openfoamDNS_to_pseudoPIV.info
echo "DNS_crop_Ly=${DNS_crop_Ly}" >> openfoamDNS_to_pseudoPIV.info
echo "  => DNS_crop_Ry=${DNS_crop_Ry}" >> openfoamDNS_to_pseudoPIV.info

if ( ( ${code_Lx} == 1 ) || ( ${code_Ly} == 1 ) ) then

  # updating INFO file

  echo "" >> openfoamDNS_to_pseudoPIV.info
  echo "Lines to add/modifiy in PYTHON paraview file" >> openfoamDNS_to_pseudoPIV.info
  echo "" >> openfoamDNS_to_pseudoPIV.info
  echo "       pointVolumeInterpolator_U*.Kernel.Radius = ${DNS_crop_GaussSmooth}" >> openfoamDNS_to_pseudoPIV.info
  echo "       pointVolumeInterpolator_U*.Source.Origin = [${DNS_crop_x0}, ${DNS_crop_y0}]" >> openfoamDNS_to_pseudoPIV.info
  echo "       pointVolumeInterpolator_U*.Source.Scale = [${DNS_crop_Lx}, ${DNS_crop_Ly}]" >> openfoamDNS_to_pseudoPIV.info
  echo "       pointVolumeInterpolator_U*.Source.RefinementMode = 'Use resolution'" >> openfoamDNS_to_pseudoPIV.info
  echo "       pointVolumeInterpolator_U*.Source.Resolution = [${DNS_crop_Rx}, ${DNS_crop_Ry}, 20]" >> openfoamDNS_to_pseudoPIV.info
  
endif

# INFO file

cat openfoamDNS_to_pseudoPIV.info

#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# present directory must contain the [0], [system] and [constant] openfoam directories 

set BaseCalc_dir = `pwd `
set last_dir = ` echo ${BaseCalc_dir} | awk -F'/' '{ print $NF }' `
set path_dir_SED = ` echo ${BaseCalc_dir} | sed s/"\/${last_dir}"//g | sed s/"\/"/"\\\/"/g `

set other_info = "(${DNS_info})"

# noise not applied here
set other_info = `echo ${DNS_info} | awk '{ I=NF; for (i=1;i<=NF;i++) if ($i=="noise") I=i-1; for (i=1;i<I;i++) printf("%s ",$i); print $I }' `
set other_info = "(${other_info})"

set code_view_withGrid = ` cat ${fic_param} | grep "code_view_withGrid" | awk -F'#' '{ print $1 }' `
set code_view_slice_Ux1 = ` cat ${fic_param} | grep "code_view_slice_Ux1" | awk -F'#' '{ print $1 }' `
set code_view_slice_Uy1 = ` cat ${fic_param} | grep "code_view_slice_Uy1" | awk -F'#' '{ print $1 }' `
set code_view_pointVolumeInterpolator_Ux = ` cat ${fic_param} | grep "code_view_pointVolumeInterpolator_Ux" | awk -F'#' '{ print $1 }' `
set code_view_pointVolumeInterpolator_Uy = ` cat ${fic_param} | grep "code_view_pointVolumeInterpolator_Uy" | awk -F'#' '{ print $1 }' `
set code_view_slice_Ux2 = ` cat ${fic_param} | grep "code_view_slice_Ux2" | awk -F'#' '{ print $1 }' `
set code_view_slice_Uy2 = ` cat ${fic_param} | grep "code_view_slice_Uy2" | awk -F'#' '{ print $1 }' `
set code_csv_slice_Ux1 = ` cat ${fic_param} | grep "code_csv_slice_Ux1" | awk -F'#' '{ print $1 }' `
set code_csv_slice_Uy1 = ` cat ${fic_param} | grep "code_csv_slice_Uy1" | awk -F'#' '{ print $1 }' `
set code_csv_slice_Ux2 = ` cat ${fic_param} | grep "code_csv_slice_Ux2" | awk -F'#' '{ print $1 }' `
set code_csv_slice_Uy2 = ` cat ${fic_param} | grep "code_csv_slice_Uy2" | awk -F'#' '{ print $1 }' `
 
# mode view without grid : POINTS (no smoothing for VISU) or SURFACE (VISU with smoothing)
set mode_view_NoGrid = "SURFACE"
set mode_view_NoGrid = "POINTS"

if -e slice.py \rm slice.py
cat util/calculator_PointVolumeInterpolation_model.py | \
  sed s/"CASE_DIR_NAME"/"${case_dir}"/g | \
  sed s/"LAST_DIR_NAME"/"${last_dir}"/g | \
  sed s/"PATH_DIR_NAME"/"${path_dir_SED}"/g | \
  sed s/"XCYL_VALUE"/"${DNS_xcyl}"/g | \
  sed s/"YCYL_VALUE"/"${DNS_ycyl}"/g | \
  sed s/"X1_DOM_VALUE"/"${DNS_xmin}"/g | \
  sed s/"Y1_DOM_VALUE"/"${DNS_ymin}"/g | \
  sed s/"Z1_DOM_VALUE"/"${DNS_zmin}"/g | \
  sed s/"X2_DOM_VALUE"/"${DNS_xmax}"/g | \
  sed s/"Y2_DOM_VALUE"/"${DNS_ymax}"/g | \
  sed s/"Z2_DOM_VALUE"/"${DNS_zmax}"/g | \
  sed s/"ZSLICE_VALUE"/"${Zslice}"/g | \
  sed s/"RADIUS_VALUE"/"${DNS_crop_GaussSmooth}"/g | \
  sed s/"ORIGIN_X_VALUE"/"${DNS_crop_x0}"/g | \
  sed s/"ORIGIN_Y_VALUE"/"${DNS_crop_y0}"/g | \
  sed s/"SCALE_X_VALUE"/"${DNS_crop_Lx}"/g | \
  sed s/"SCALE_Y_VALUE"/"${DNS_crop_Ly}"/g | \
  sed s/"RESOLUTION_X_VALUE"/"${DNS_crop_Rx}"/g | \
  sed s/"RESOLUTION_Y_VALUE"/"${DNS_crop_Ry}"/g | \
  sed s/"OTHER_INFO"/"${other_info}"/g | \
  sed s/"MODE_VIEW_NOGRID_VALUE"/"${mode_view_NoGrid}"/g | \
  sed s/"CODE_VIEW_WITHGRID_VALUE"/"${code_view_withGrid}"/g | \
  sed s/"CODE_VIEW_SLICE_UX1_VALUE"/"${code_view_slice_Ux1}"/g | \
  sed s/"CODE_VIEW_SLICE_UY1_VALUE"/"${code_view_slice_Uy1}"/g | \
  sed s/"CODE_VIEW_POINTVOLUMEINTERPOLATOR_UX_VALUE"/"${code_view_pointVolumeInterpolator_Ux}"/g | \
  sed s/"CODE_VIEW_POINTVOLUMEINTERPOLATOR_UY_VALUE"/"${code_view_pointVolumeInterpolator_Uy}"/g | \
  sed s/"CODE_VIEW_SLICE_UX2_VALUE"/"${code_view_slice_Ux2}"/g | \
  sed s/"CODE_VIEW_SLICE_UY2_VALUE"/"${code_view_slice_Uy2}"/g | \
  sed s/"CODE_CSV_SLICE_UX1_VALUE"/"${code_csv_slice_Ux1}"/g | \
  sed s/"CODE_CSV_SLICE_UY1_VALUE"/"${code_csv_slice_Uy1}"/g | \
  sed s/"CODE_CSV_SLICE_UX2_VALUE"/"${code_csv_slice_Ux2}"/g | \
  sed s/"CODE_CSV_SLICE_UY2_VALUE"/"${code_csv_slice_Uy2}"/g > slice.py

# slice INFO file

if -e slice_param.info \rm slice_param.info; touch slice_param.info

echo "# Slice parameters" >> slice_param.info
echo "ZSLICE_VALUE=${Zslice}" >> slice_param.info
echo "X1_DOM_VALUE=${DNS_xmin}" >> slice_param.info
echo "X2_DOM_VALUE=${DNS_xmax}" >> slice_param.info
echo "Y1_DOM_VALUE=${DNS_ymin}" >> slice_param.info
echo "Y2_DOM_VALUE=${DNS_ymax}" >> slice_param.info
echo "Z1_DOM_VALUE=${DNS_zmin}" >> slice_param.info
echo "Z2_DOM_VALUE=${DNS_zmax}" >> slice_param.info
echo "RADIUS_VALUE=${DNS_crop_GaussSmooth}" >> slice_param.info
echo "ORIGIN_X_VALUE=${DNS_crop_x0}" >> slice_param.info
echo "ORIGIN_Y_VALUE=${DNS_crop_y0}" >> slice_param.info
echo "SCALE_X_VALUE=${DNS_crop_Lx}" >> slice_param.info
echo "SCALE_Y_VALUE=${DNS_crop_Ly}" >> slice_param.info
echo "RESOLUTION_X_VALUE=${DNS_crop_Rx}" >> slice_param.info
echo "RESOLUTION_Y_VALUE=${DNS_crop_Ry}" >> slice_param.info

# updating INFO file

echo "" >> openfoamDNS_to_pseudoPIV.info
cat slice_param.info >> openfoamDNS_to_pseudoPIV.info

\cp openfoamDNS_to_pseudoPIV.info ..

#------------------------------------------------------------------------------

#echo ""
#echo "file to modify : calculator_PointVolumeInterpolation.py"
#echo ""
#echo "  Lines to modifiy"
#echo ""
#echo "       pointVolumeInterpolator_U*.Kernel.Radius = 0.203125"
#echo "       pointVolumeInterpolator_Ux.Source.Origin = [1.5408, 1.7793, 0]"
#echo "       pointVolumeInterpolator_Ux.Source.Scale = [13.9154, 8.5670, 3.14]"
#echo "       pointVolumeInterpolator_Ux.Source.RefinementMode = 'Use resolution'"
#echo "       pointVolumeInterpolator_Ux.Source.Resolution = [294, 181, 20]"
#echo ""

#------------------------------------------------------------------------------
echo ""
echo "First : for each openfoeam file U (like 0/U), you should copy this file in 2 directories (1 and 2 for example)"
echo "          since the script [pvbatch slice.py] can't detect time step (missing instruction ?!)"
echo ""

echo ""
echo "Second : Result of [pvbatch slice.py] command : "
echo ""

# running slice paraview command file

pvbatch slice.py

# merging CSV files to created one (ux,uy) file or (ux,uy,uz) file

# CSV file with Ux,Uy in the same file

if ( (-e slice_Ux1.csv) && (-e slice_Uy1.csv) ) then
  if -e slice_Uxy1.csv \rm slice_Uxy1.csv
  paste slice_Ux1.csv slice_Uy1.csv | sed s/"\t"/","/g > slice_Uxy1.csv
  \rm slice_Ux1.csv slice_Uy1.csv
endif
if ( (-e slice_Ux2.csv) && (-e slice_Uy2.csv) ) then
  if -e slice_Uxy2.csv \rm slice_Uxy2.csv
  paste slice_Ux2.csv slice_Uy2.csv | sed s/"\t"/","/g > slice_Uxy2.csv
  \rm slice_Ux2.csv slice_Uy2.csv
endif
if ( (-e slice_Uxy2.csv) && (-e slice_Uz2.csv) ) then
  if -e slice_Uxyz2.csv \rm slice_Uxyz2.csv
  paste slice_Uxy2.csv slice_Uz2.csv | sed s/"\t"/","/g > slice_Uxyz2.csv
  \rm slice_Uz2.csv
endif

echo ""
echo 'Cf. PNG files ("_withGrid":slice with grid, "_withoutGrid":slice without grid) :'
echo "  Ux_calculator_w*.png Ux_calculator_pointVolumeInterpolator_slice_w*.png"
echo "  Uy_calculator_w*.png Uy_calculator_pointVolumeInterpolator_slice_w*.png"
echo ""
echo "Cf. CSV files (1:openfoam grid, 2:gaussian smooth+crop -> uniform grid) :"
echo "  slice_Uxy?.csv"
echo ""

#------------------------------------------------------------------------------
# DNS BOX grid

if -e slice_Uxy1.csv then
  if -e slice_Uxy1.txt \rm slice_Uxy1.txt
  cat slice_Uxy1.csv | grep -v Points | awk -F',' '{ print $1,$2 }' > slice_Uxy1.txt
endif

if -e slice_Uxy2.csv then

  set Nx = `cat slice_Uxy2.csv | grep -v Points | \
    awk -F',' '{ x=$1+0. ; if ( NF!=0 ) printf ( "%.0f\n", 1000000.*x ) }' | sort -n | uniq | awk '{ x=$1+0. ; printf ( "%.6f\n",x/1000000. ) }' | wc -l `
  set Ny = `cat slice_Uxy2.csv | grep -v Points | \
    awk -F',' '{ x=$2+0. ; if ( NF!=0 ) printf ( "%.0f\n", 1000000.*x ) }' | sort -n | uniq | awk '{ x=$1+0. ; printf ( "%.6f\n",x/1000000. ) }' | wc -l `
  set Nz = `cat slice_Uxy2.csv | grep -v Points | \
    awk -F',' '{ x=$3+0. ; if ( NF!=0 ) printf ( "%.0f\n", 1000000.*x ) }' | sort -n | uniq | awk '{ x=$1+0. ; printf ( "%.6f\n",x/1000000. ) }' | wc -l `

  if -e slice_Uxy2.txt \rm slice_Uxy2.txt
  cat slice_Uxy2.csv | \
    grep -v Points | awk -F',' '{ print $1,$2 }' > slice_Uxy2.txt

  # gnuplot file
  
  set fic_gnp = slice.gnp
  if -e ${fic_gnp} \rm ${fic_gnp}; touch ${fic_gnp}
  
  # gnuplot file 

  echo 'set grid' >> ${fic_gnp}
  echo 'set size ratio -1' >> ${fic_gnp}
  echo 'set key box outside center bottom horizontal maxcols 5 maxrows 5' >> ${fic_gnp}
  echo 'set title "pvbatch on openfoam datas : grid1 to uniform grid2 (gaussian smoothing)" noenhanced' >> ${fic_gnp}
  echo 'set terminal png crop size 1000,1000 font "LiberationSans-Regular,18  noenhanced' >> ${fic_gnp}
  echo 'set palette color' >> ${fic_gnp}
  echo 'set palette model RGB' >> ${fic_gnp}
  echo "x0=${DNS_xcyl}" >> ${fic_gnp}
  echo "y0=${DNS_ycyl}" >> ${fic_gnp}
  echo 'set output "slice_grid.png"'  >> ${fic_gnp}
  if -e slice_Uxy1.txt then
    echo 'plot [x0-2.5:x0+1.5][y0-2.:y0+2.] "slice_Uxy1.txt" u 1:2 w p pt 6 lc rgb "red" title "grid1", "slice_Uxy2.txt" u 1:2 w p pt 7 lc rgb "blue" title "grid2"' >> ${fic_gnp}
  else
    echo 'plot [x0-2.5:x0+1.5][y0-2.:y0+2.] "slice_Uxy2.txt" u 1:2 w p pt 7 lc rgb "blue" title "grid2"' >> ${fic_gnp}
  endif

  gnuplot ${fic_gnp}

  echo ""
  echo "New DNS grid :  ${Nx}x${Ny}x${Nz} points : Cf. slice_grid.png"
  echo ""

  #------------------------------------------------------------------------------
  # back to new PIV file
  #   1) same order (x,y) (xmin->xmax and ymax->ymin)
  #   2) same value for [isValid] parameter as PIV model (if IsValid_ON=1)
  #   3) => U=0 when [isValid=0] (if IsValid_ON=1)
  
  if ( -e ${PIV_file_model} ) then
    set PIV_file_model_new = `echo ${PIV_file_model} | awk -F'/' '{ print $NF }' | sed s/"\.dat"/"_new\.dat"/g `
  else
    set PIV_file_model_new = B0001_new.dat
  endif
  
  # IsValid = 1 everywhere by default
  
  set IsValid = 1
  
  # FakePIV is dimentionless (from [ROMDNS] files) or not (from [openfoam_data...] files)
  #   NOTE : case for DNS_Dcyl = 1 (as expected for geometry used in openfoam simulation)
  
  if ( ${code_adim} == 1 ) then
    
    if -e ${PIV_file_model_new} \rm ${PIV_file_model_new}
    cat slice_Uxy2.csv | grep -v Point | \
      awk -F',' -v d_c=${PIV_Dcyl} -v D_x0=${DNS_crop_x0} -v P_x0=${PIV_xmin} -v D_y0=${DNS_crop_y0} -v P_y0=${PIV_ymin} -v I=${IsValid} '{ \
      printf("%10.6f %10.6f %s %s %d\n", ($1-D_x0+0.)+(P_x0+0.)/(d_c+0.), ($2-D_y0+0.)+(P_y0+0.)/(d_c+0.), $4, $5, I) }' > ${PIV_file_model_new}
    
  else
    
    if -e ${PIV_file_model_new} \rm ${PIV_file_model_new}
    cat slice_Uxy2.csv | grep -v Point | \
      awk -F',' -v d_c=${PIV_Dcyl} -v D_x0=${DNS_crop_x0} -v P_x0=${PIV_xmin} -v D_y0=${DNS_crop_y0} -v P_y0=${PIV_ymin} -v I=${IsValid} '{ \
      printf("%10.6f %10.6f %s %s %d\n", ($1-D_x0+0.)*(d_c+0.)+P_x0, ($2-D_y0+0.)*(d_c+0.)+P_y0+0., $4, $5, I) }' > ${PIV_file_model_new}
  
  endif

  #  same order (x,y) as  PIV model : file ordered from ymin to ymax
  
  if -e PIV_new_x.txt \rm PIV_new_x.txt
  cat ${PIV_file_model_new} | grep -v "#" | \
    awk '{ x=$1+0. ; if (NF!=0) printf("%.0f\n", 1000000.*x) }' | sort -n  | uniq | \
    awk '{ x=$1+0. ; printf("%.6f\n",x/1000000.)}' > PIV_new_x.txt
  #set All_PIV_yinv = ` cat All_PIV_x.txt | sed s/"-"/"\\-"/g`
  set All_PIV_x = ` cat PIV_new_x.txt `
  
  set dx_max = ` echo ${All_PIV_x} | sort -n | awk '{ d=$NF-$1; d=sqrt(d*d); print d }' `

  if -e PIV_new_yinv.txt \rm PIV_new_yinv.txt
  cat ${PIV_file_model_new} | grep -v "#" | grep -v "=" | \
    awk '{ x=$2+0. ; if (NF!=0) printf("%.0f\n", 1000000.*x) }' | sort -n -r  | uniq | \
    awk '{ x=$1+0. ; printf("%.6f\n",x/1000000.)}' > PIV_new_yinv.txt
  #set All_PIV_new_yinv = ` cat PIV_new_yinv.txt | sed s/"-"/"\\-"/g`
  set All_PIV_new_yinv = ` cat PIV_new_yinv.txt `

  \mv ${PIV_file_model_new} tmp.txt; touch  ${PIV_file_model_new}
  foreach y ( ${All_PIV_new_yinv} )
    cat tmp.txt | awk -v y=${y} -v dx_max=${dx_max} '{ if ($2==y) print $1+dx_max, $0 }' | \
    sort -n | uniq | \
    awk '{ for (i=2;i<NF; i++) printf("%s ",$i); print $NF }' >> ${PIV_file_model_new}
  end

  # according [isValid] parameter with PIV model, and changing Ux,Uy to Ux=0, Uy=0 if isValid=0

  if (( ${IsValid_ON} == 1 ) && (-e ${PIV_file_model}))  then
   
    # min(X) and max(X) value with IsValid=1 => Radius Rx
    
    if -e PIV_xIsValid.txt \rm PIV_xIsValid.txt
    cat ${PIV_file_model} | grep -v "=" | \
      awk '{ x=$1+0. ; if ((NF!=0) && ($5==1)) printf("%.0f\n", 1000000.*x) }' | sort -n  | uniq | \
      awk '{ x=$1+0. ; printf("%.6f\n",x/1000000.)}' > PIV_xIsValid.txt
    set PIV_xminIsValid = `cat PIV_xIsValid.txt  | head -1 `
    set PIV_xmaxIsValid = `cat PIV_xIsValid.txt  | tail -1 `
    set PIV_LxIsValid = `echo ${PIV_xminIsValid} ${PIV_xmaxIsValid} | awk '{ printf("%.6f\n", $2-$1) }' `

    # min(Y) and max(Y) value with IsValid=1 => Radius Ry
    
    if -e PIV_yIsValid.txt \rm PIV_yIsValid.txt
    cat ${PIV_file_model} | grep -v "=" | \
      awk '{ y=$2+0. ; if ((NF!=0) && ($5==1)) printf("%.0f\n", 1000000.*y) }' | sort -n  | uniq | \
      awk '{ y=$1+0. ; printf("%.6f\n",y/1000000.)}' > PIV_yIsValid.txt
    set PIV_yminIsValid = `cat PIV_yIsValid.txt  | head -1 `
    set PIV_ymaxIsValid = `cat PIV_yIsValid.txt  | tail -1 `
    set PIV_LyIsValid = `echo ${PIV_yminIsValid} ${PIV_ymaxIsValid} | awk '{ printf("%.6f\n", $2-$1) }' `

    echo "  BOX IsValid = [${PIV_xminIsValid}:${PIV_xmaxIsValid}]x[${PIV_yminIsValid}:${PIV_ymaxIsValid}]"
    
    #  switch on difference between ${PIV_file_model_new} and ${PIV_file_model} number of points
    
    set N1 = ` cat ${PIV_file_model_new} | grep -v "#" | grep -v "=" | wc -l `
    set N2 = ` cat ${PIV_file_model} | grep -v "=" | wc -l `
    if ( ${N1} == ${N2} ) then
    
      echo ""
      echo "${PIV_file_model_new} and ${PIV_file_model} have the same number of points"
      echo ""
      
      set code_IsValid = 1
      \mv ${PIV_file_model_new} tmp1.txt
      if -e tmp2.txt \rm tmp2.txt; cat ${PIV_file_model} | grep -v "=" > tmp2.txt
      paste tmp1.txt tmp2.txt | \
        awk '{ \
          IsValid = $10; \
          if ( IsValid != 0 ) printf("%10.6f %10.6f %s %s 1\n", $1,$2,$3,$4); \
          else  printf("%10.6f %10.6f 0 0 0\n", $1,$2); \
        }' > ${PIV_file_model_new}
        
    else
   
      echo ""
      echo "${PIV_file_model_new} and ${PIV_file_model} don't have the same number of points"
      echo ""
      
      if -e PIV_new_x.txt \rm PIV_new_x.txt
      cat ${PIV_file_model_new} | grep -v "#" | grep -v "=" | \
        awk '{ x=$1+0. ; if (NF!=0) printf("%.0f\n", 1000000.*x) }' | sort -n | uniq | \
        awk '{ x=$1+0. ; printf("%.6f\n",x/1000000.)}' > PIV_new_x.txt
      set x_PIV_new_max = ` cat PIV_new_x.txt | tail -1 `
      
      if -e PIV_new_y.txt \rm PIV_new_y.txt
      cat ${PIV_file_model_new} | grep -v "#" | grep -v "=" | \
        awk '{ x=$2+0. ; if (NF!=0) printf("%.0f\n", 1000000.*x) }' | sort -n | uniq | \
        awk '{ x=$1+0. ; printf("%.6f\n",x/1000000.)}' > PIV_new_y.txt
      set y_PIV_new_max = ` cat PIV_new_y.txt | tail -1 `
      
      \mv ${PIV_file_model_new} tmp1.txt
      if -e tmp2.txt \rm tmp2.txt
      cat ${PIV_file_model} | grep -v "=" | \
        awk -v xM=${x_PIV_new_max} -v yM=${y_PIV_new_max} '{ \
        if (($1<=xM+0.5) && ($2 <=yM+0.5)) print $0 }' > tmp2.txt
      paste tmp1.txt tmp2.txt | \
        awk '{ \
          IsValid = $10; \
          if ( IsValid != 0 ) printf("%10.6f %10.6f %s %s 1\n", $1,$2,$3,$4); \
          else  printf("%10.6f %10.6f 0 0 0\n", $1,$2); \
        }' > ${PIV_file_model_new}
      
    endif

  endif

  # adding noise

  set noise_ON = ` echo ${noise_MAX} | awk '{ if ($1>0.01) print 1; else print 0 }' `
  if ( ${noise_ON} == 1 ) then

    # adding noise : Cf. https://en.wikipedia.org/wiki/Normal_distribution#Generating_values_from_normal_distribution
    
    set Nzero = 20 # zero=pow(10,-Nzero)
    set R = ` echo ${Nzero} | awk '{ r=10.**(-$1); R=sqrt(-2.*log(r)); print R }' `
    echo "";  echo "minimum value for R=${R} with r=10**(-${Nzero})";  

    # noise_type : multiplied (Ux*(1+noise)) or simply added (Ux+noise)
    set noise_type = "multiplied"
    set noise_type = "added"

    \mv ${PIV_file_model_new} tmp1.txt
    cat tmp1.txt | grep -v "=" | \
      awk -v n=${noise_MAX} -v Nzero=${Nzero} -v noise_type=${noise_type} ' { \
        pi=4.*atan2(1.,1.); \
        x=$1+0.; y=$2+0.; Ux = $3+0.; Uy = $4+0.; IsValid = $5; \
        if ( uniform_case == 1 ) { Ux = Ux0; Uy = Uy0; } \
        \
        r=10.**(-Nzero); R=sqrt(-2.*log(r)); \
        \
        rx1=r*0.9; \
        while ( rx1 < r ) { \
          cmd ="date \"+%s\""; cmd | getline date; Nd=split(date,d,""); \
          N=split(Ux,X,"."); Rx1=NR; for (i=1;i<=N;i++) Rx1=Rx1+X[i]+0.; \
          srand(date+Rx1); rx1=rand(); \
        } \
        \
        cmd ="date \"+%s\""; cmd | getline date; Nd=split(date,d,""); \
        N=split(Ux,X,""); Rx2=-NR; for (i=1;i<=N;i++) { if ((X[i]!="-") && (X[i]!=".")) Rx2=Rx2+X[i]**3; } \
        srand(date+Rx2); rx2=rand(); \
        X1 = sqrt(-2.*log(rx1))*cos(2.*pi*rx2); \
        X2 = sqrt(-2.*log(rx1))*sin(2.*pi*rx2); \
        \
        ry1=r*0.9; \
        while ( ry1 < r ) { \
          cmd ="date \"+%s\""; cmd | getline date; Nd=split(date,d,""); \
          N=split(Uy,Y,"."); Ry1=-NR; for (i=1;i<=N;i++) Ry1=Ry1+Y[i]; \
          srand(date+Ry1); ry1=rand(); \
        } \
        \
        cmd ="date \"+%s\""; cmd | getline date; Nd=split(date,d,""); \
        N=split(Uy,Y,""); Ry2=NR; for (i=1;i<=N;i++) { if ((Y[i]!="-") && (Y[i]!=".")) Ry2=Ry2+Y[i]**3; } \
        srand(date+Ry2); ry2=rand(); \
        Y1 = sqrt(-2.*log(ry1))*sin(2.*pi*ry2); \
        Y2 = sqrt(-2.*log(ry1))*cos(2.*pi*ry2); \
        \
        if ( NR%4 == 0 ) { n_x=X1; n_y=Y1; } \
        if ( NR%4 == 1 ) { n_x=X1; n_y=Y2; } \
        if ( NR%4 == 2 ) { n_x=X2; n_y=Y1; } \
        if ( NR%4 == 3 ) { n_x=X2; n_y=Y2; } \
        dUx = n/100.*n_x; dUy = n/100.*n_y; \
        if ( noise_type == "multiplied" ) {dUx = Ux*dUx; dUy = Uy*dUy; } \
        if ( IsValid == 1 ) printf("%f %f %f %f %d\n", x, y, Ux+dUx, Uy+dUy, IsValid); \
        else printf("%f %f 0. 0. 0\n", x, y); \
      }' > ${PIV_file_model_new}

  endif

  # Velocity Factor applied only if no adim
  
  if ( ${code_adim} == 1 ) then
    
    set VelFac_ON = 0
    
  else
  
    set VelFac_ON = ` echo ${PIV_Velocity} | awk '{ if (($1>1.0001) || ($1<0.9999)) print 1; else print 0 }' `
    
  endif
  
  if ( ${VelFac_ON} == 1 ) then
      
      \mv ${PIV_file_model_new} tmp1.txt
      head tmp1.txt | grep "="  > ${PIV_file_model_new}
      cat tmp1.txt | grep -v "=" | \
        awk -v r=${PIV_Velocity} '{ \
          printf("%10.6f %10.6f %10.6f %10.6f %s\n", $1,$2,($3+0.)*r,($4+0.)*r,$5); \
        }' >> ${PIV_file_model_new}
 
  endif
   
  # X and Y values in new PIV files
  
  if ( ${code_adim} == 1 ) then
  
    if -e PIV_x_adim.txt \rm PIV_x_adim.txt
    cat ${PIV_file_model_new} | grep -v "#" | grep -v "=" | \
      awk '{ x=$1+0. ; if (NF!=0) printf("%.0f\n", 1000000.*x) }' | sort -n  | uniq | \
      awk '{ x=$1+0. ; printf("%.6f\n",x/1000000.)}' > PIV_x_adim.txt

    if -e PIV_y_adim.txt \rm PIV_y_adim.txt
    cat ${PIV_file_model_new} | grep -v "#" | grep -v "=" | \
      awk '{ y=$2+0. ; if (NF!=0) printf("%.0f\n", 1000000.*y) }' | sort -n  | uniq | \
      awk '{ y=$1+0. ; printf("%.6f\n",y/1000000.)}' > PIV_y_adim.txt
      
    if -e PIV_x.txt \rm PIV_x.txt
    awk -v  D=${PIV_Dcyl} '{ printf("%f\n",($1+0.)*(D+0.) ) }' PIV_x_adim.txt > PIV_x.txt

    if -e PIV_y.txt \rm PIV_y.txt
    awk -v  D=${PIV_Dcyl} '{ printf("%f\n",($1+0.)*(D+0.) ) }' PIV_y_adim.txt > PIV_y.txt
      
  else
  
    if -e PIV_x.txt \rm PIV_x.txt
    cat ${PIV_file_model_new} | grep -v "#" | grep -v "=" | \
      awk '{ x=$1+0. ; if (NF!=0) printf("%.0f\n", 1000000.*x) }' | sort -n  | uniq | \
      awk '{ x=$1+0. ; printf("%.6f\n",x/1000000.)}' > PIV_x.txt

    if -e PIV_y.txt \rm PIV_y.txt
    cat ${PIV_file_model_new} | grep -v "#" | grep -v "=" | \
      awk '{ y=$2+0. ; if (NF!=0) printf("%.0f\n", 1000000.*y) }' | sort -n  | uniq | \
      awk '{ y=$1+0. ; printf("%.6f\n",y/1000000.)}' > PIV_y.txt
  
    if -e PIV_x_adim.txt \rm PIV_x_adim.txt
    awk -v  D=${PIV_Dcyl} '{ printf("%f\n",($1+0.)/(D+0.) ) }' PIV_x.txt > PIV_x_adim.txt

    if -e PIV_y_adim.txt \rm PIV_y_adim.txt
    awk -v  D=${PIV_Dcyl} '{ printf("%f\n",($1+0.)/(D+0.) ) }' PIV_y.txt > PIV_y_adim.txt
      
  endif
  
  # adding headline
  
  set t0 = ` echo ${PIV_Dcyl} ${PIV_Velocity} | awk '{ print ($1+0.)*0.001/($2+0.) }' `
  set t_PIV = ` echo ${t_DNS} ${t0} | awk '{ print ($1+0.)*($2+0.) }' `

  \mv ${PIV_file_model_new} tmp1.txt
  echo 'TITLE = "'${num_DNS}'"' > ${PIV_file_model_new}
  echo 'VARIABLES = "x [mm]", "y [mm]", "Vx [m/s]", "Vy [m/s]", "isValid"' >> ${PIV_file_model_new}
  echo 'ZONE T="Frame 0", I='${DNS_crop_Nx}', J='${DNS_crop_Ny}', F=POINT' >> ${PIV_file_model_new}
  echo "STRANDID=1, SOLUTIONTIME=${t_PIV}" >> ${PIV_file_model_new}
  cat tmp1.txt | grep -v "="  >> ${PIV_file_model_new}

  # xy range for PIV and DNS
  
  set PIV_xr1 = ` cat DNS_to_FakePIV_info.txt | grep "# " | grep " PIV_crop_x1" | awk '{ print $1 }' `
  set PIV_xr2 = ` cat DNS_to_FakePIV_info.txt | grep "# " | grep " PIV_crop_x2" | awk '{ print $1 }' `
  set PIV_yr1 = ` cat DNS_to_FakePIV_info.txt | grep "# " | grep " PIV_crop_y1" | awk '{ print $1 }' `
  set PIV_yr2 = ` cat DNS_to_FakePIV_info.txt | grep "# " | grep " PIV_crop_y2" | awk '{ print $1 }' `
  
  set DNS_xr1 = ` cat DNS_to_FakePIV_info.txt | grep "# " | grep " DNS_crop_x1" | awk '{ print $1 }' `
  set DNS_xr2 = ` cat DNS_to_FakePIV_info.txt | grep "# " | grep " DNS_crop_x2" | awk '{ print $1 }' `
  set DNS_yr1 = ` cat DNS_to_FakePIV_info.txt | grep "# " | grep " DNS_crop_y1" | awk '{ print $1 }' `
  set DNS_yr2 = ` cat DNS_to_FakePIV_info.txt | grep "# " | grep " DNS_crop_y2" | awk '{ print $1 }' `
    
  set PIV_DNS_xr1 = ` echo ${PIV_xr1} ${DNS_xr1} | awk '{ if ($1<=$2) print $1; else print $2 }' `
  set PIV_DNS_xr2 = ` echo ${PIV_xr2} ${DNS_xr2} | awk '{ if ($1>=$2) print $1; else print $2 }' `
  set PIV_DNS_yr1 = ` echo ${PIV_yr1} ${DNS_yr1} | awk '{ if ($1<=$2) print $1; else print $2 }' `
  set PIV_DNS_yr2 = ` echo ${PIV_yr2} ${DNS_yr2} | awk '{ if ($1>=$2) print $1; else print $2 }' `

  #echo "${DNS_xr1} ${DNS_xr2} ${DNS_yr1} ${DNS_yr2} ${DNS_Lx} ${DNS_Ly}" | awk '{ dx=$2-$1;dy=$4-$3; printf("\n\nDNS range : dx=%.3f dy=%.3f Lx/dx=%.3f Ly/dy=%.3f\n\n",dx,dy, ($5+0.)/(dx+0.), ($6+0.)/(dy+20)) }'
        
  # plotting result

  echo 'set palette rgbformulae 33,13,10' >> ${fic_gnp}
  echo "set palette defined (0 'dark-violet', 1 'blue', 2 'green', 3 'yellow', 4 'red', 5 'brown', 6 'magenta', 7 'pink')" >> ${fic_gnp}
  
  # same palette as paraview : rainbow
  
  echo 'set palette defined ( \' >> ${fic_gnp}
  echo '  1.0  0.3  0.3  0.9, \' >> ${fic_gnp}
  echo '  2.0  0.0  0.0  0.4, \' >> ${fic_gnp}
  echo '  3.0  0.0  1.0  1.0, \' >> ${fic_gnp}
  echo '  4.0  0.0  0.5  0.0, \' >> ${fic_gnp}
  echo '  5.0  1.0  1.0  0.0, \' >> ${fic_gnp}
  echo '  6.0  1.0  0.4  0.0, \' >> ${fic_gnp}
  echo '  7.0  0.4  0.0  0.0, \' >> ${fic_gnp}
  echo '  8.0  0.9  0.3  0.3 \' >> ${fic_gnp}
  echo ')' >> ${fic_gnp}
  
  # same palette as paraview : blue orange
  
  echo 'set palette defined ( \' >> ${fic_gnp}
  echo '  1.0 0.086275 0.003922 0.298039, \' >> ${fic_gnp}
  echo '  2.0 0.113725 0.023529 0.450980, \' >> ${fic_gnp}
  echo '  3.0 0.105882 0.050980 0.509804, \' >> ${fic_gnp}
  echo '  4.0 0.039216 0.039216 0.560784, \' >> ${fic_gnp}
  echo '  5.0 0.031372 0.098039 0.600000, \' >> ${fic_gnp}
  echo '  6.0 0.043137 0.164706 0.639216, \' >> ${fic_gnp}
  echo '  7.0 0.054902 0.243137 0.678431, \' >> ${fic_gnp}
  echo '  8.0 0.054902 0.317647 0.709804, \' >> ${fic_gnp}
  echo '  9.0 0.050980 0.396078 0.741176, \' >> ${fic_gnp}
  echo ' 10.0 0.039216 0.466667 0.768627, \' >> ${fic_gnp}
  echo ' 11.0 0.031372 0.537255 0.788235, \' >> ${fic_gnp}
  echo ' 12.0 0.031372 0.615686 0.811765, \' >> ${fic_gnp}
  echo ' 13.0 0.023529 0.709804 0.831373, \' >> ${fic_gnp}
  echo ' 14.0 0.050980 0.800000 0.850980, \' >> ${fic_gnp}
  echo ' 15.0 0.070588 0.854902 0.870588, \' >> ${fic_gnp}
  echo ' 16.0 0.262745 0.901961 0.862745, \' >> ${fic_gnp}
  echo ' 17.0 0.423529 0.941176 0.874510, \' >> ${fic_gnp}
  echo ' 18.0 0.572549 0.964706 0.835294, \' >> ${fic_gnp}
  echo ' 19.0 0.658824 0.980392 0.843137, \' >> ${fic_gnp}
  echo ' 20.0 0.764706 0.980392 0.866667, \' >> ${fic_gnp}
  echo ' 21.0 0.827451 0.980392 0.886275, \' >> ${fic_gnp}
  echo ' 22.0 0.913725 0.988235 0.937255, \' >> ${fic_gnp}
  echo ' 23.0 1.000000 1.000000 0.972549, \' >> ${fic_gnp}
  echo ' 24.0 0.988235 0.980392 0.870588, \' >> ${fic_gnp}
  echo ' 25.0 0.992157 0.972549 0.803922, \' >> ${fic_gnp}
  echo ' 26.0 0.992157 0.964706 0.713725, \' >> ${fic_gnp}
  echo ' 27.0 0.988235 0.956863 0.643137, \' >> ${fic_gnp}
  echo ' 28.0 0.980392 0.917647 0.509804, \' >> ${fic_gnp}
  echo ' 29.0 0.968627 0.874510 0.407843, \' >> ${fic_gnp}
  echo ' 30.0 0.949020 0.823529 0.321569, \' >> ${fic_gnp}
  echo ' 31.0 0.929412 0.776471 0.278431, \' >> ${fic_gnp}
  echo ' 32.0 0.909804 0.717647 0.235294, \' >> ${fic_gnp}
  echo ' 33.0 0.890196 0.658824 0.196078, \' >> ${fic_gnp}
  echo ' 34.0 0.878431 0.619608 0.168627, \' >> ${fic_gnp}
  echo ' 35.0 0.870588 0.549020 0.156863, \' >> ${fic_gnp}
  echo ' 36.0 0.850980 0.474510 0.145098, \' >> ${fic_gnp}
  echo ' 37.0 0.831373 0.411765 0.133333, \' >> ${fic_gnp}
  echo ' 38.0 0.811765 0.345098 0.113725, \' >> ${fic_gnp}
  echo ' 39.0 0.788235 0.266667 0.094118, \' >> ${fic_gnp}
  echo ' 40.0 0.741176 0.184314 0.074510, \' >> ${fic_gnp}
  echo ' 41.0 0.690196 0.125490 0.062745, \' >> ${fic_gnp}
  echo ' 42.0 0.619608 0.062745 0.043137, \' >> ${fic_gnp}
  echo ' 43.0 0.549020 0.027451 0.070588, \' >> ${fic_gnp}
  echo ' 44.0 0.470588 0.015686 0.090196, \' >> ${fic_gnp}
  echo ' 45.0 0.400000 0.003922 0.101961, \' >> ${fic_gnp}
  echo ' 46.0 0.188235 0.000000 0.070588 \' >> ${fic_gnp}
  echo ')' >> ${fic_gnp}

  # plotting PIV_model, and grid difference between PIV_model and FakePIV
  
  if (-e ${PIV_file_model}) then
  
    if -e tmp.txt \rm tmp.txt
    cat  ${PIV_file_model} | grep -v "#" > tmp.txt
    
    if ( ${code_adim} == 0 ) then

      set code_every59 = 0
      if ( ${code_every59} != 0 ) then
        echo 'set output "PIV_grid_every59.png"'  >> ${fic_gnp}
        echo 'plot [][] \'  >> ${fic_gnp}
        echo '  "tmp.txt" u 1:2 every 59 w p pt 6 ps 2 lc rgb "red" title "PIV model : grid", \'  >> ${fic_gnp}
        echo '  "'${PIV_file_model_new}'" u 1:2 every 59 w p pt 7 lc rgb "blue" title "PIV new : grid"' >> ${fic_gnp}
      endif
      
      set code_every91 = 0
      if ( ${code_every91} != 0 ) then
        echo 'set output "PIV_grid_every91.png"'  >> ${fic_gnp}
        echo 'plot [][] \'  >> ${fic_gnp}
        echo ' "tmp.txt" u 1:2 every 91 w p pt 6 ps 2 lc rgb "red" title "PIV model : grid", \'  >> ${fic_gnp}
        echo '  "'${PIV_file_model_new}'" u 1:2 every 91 w p pt 7 lc rgb "blue" title "PIV new : grid"' >> ${fic_gnp}
      endif
      
      echo 'set output "PIV_grid_zoom.png"'  >> ${fic_gnp}
      echo 'plot [0:4][4:8] \'  >> ${fic_gnp}
      echo '  "'${PIV_file_model}'" u 1:2 w p pt 6 ps 2 lc rgb "red" title "PIV model : grid", \'  >> ${fic_gnp}
      echo '  "'${PIV_file_model_new}'" u 1:2 w p pt 7 lc rgb "blue" title "PIV new : grid"' >> ${fic_gnp}
    
    endif
  
  endif
  
  # xy range for PIV (orange rectangle) and DNS (green rectangle)
 
  echo "PIV_Dcyl=${PIV_Dcyl}" >> ${fic_gnp}
  echo "PIV_xr1=${PIV_xr1}" >> ${fic_gnp}
  echo "PIV_xr2=${PIV_xr2}" >> ${fic_gnp}
  echo "PIV_yr1=${PIV_yr1}" >> ${fic_gnp}
  echo "PIV_yr2=${PIV_yr2}" >> ${fic_gnp}
  echo "DNS_xr1=${DNS_xr1}" >> ${fic_gnp}
  echo "DNS_xr2=${DNS_xr2}" >> ${fic_gnp}
  echo "DNS_yr1=${DNS_yr1}" >> ${fic_gnp}
  echo "DNS_yr2=${DNS_yr2}" >> ${fic_gnp}
  echo "PIV_DNS_xr1=${PIV_DNS_xr1}" >> ${fic_gnp}
  echo "PIV_DNS_xr2=${PIV_DNS_xr2}" >> ${fic_gnp}
  echo "PIV_DNS_yr1=${PIV_DNS_yr1}" >> ${fic_gnp}
  echo "PIV_DNS_yr2=${PIV_DNS_yr2}" >> ${fic_gnp} 
  
  echo "" >> ../openfoamDNS_to_pseudoPIV.info
  echo "# Gnuplot parameters" >> ../openfoamDNS_to_pseudoPIV.info
  echo "PIV_xr1=${PIV_xr1}" >> ../openfoamDNS_to_pseudoPIV.info
  echo "PIV_xr2=${PIV_xr2}" >> ../openfoamDNS_to_pseudoPIV.info
  echo "PIV_yr1=${PIV_yr1}" >> ../openfoamDNS_to_pseudoPIV.info
  echo "PIV_yr2=${PIV_yr2}" >> ../openfoamDNS_to_pseudoPIV.info
  echo "DNS_xr1=${DNS_xr1}" >> ../openfoamDNS_to_pseudoPIV.info
  echo "DNS_xr2=${DNS_xr2}" >> ../openfoamDNS_to_pseudoPIV.info
  echo "DNS_yr1=${DNS_yr1}" >> ../openfoamDNS_to_pseudoPIV.info
  echo "DNS_yr2=${DNS_yr2}" >> ../openfoamDNS_to_pseudoPIV.info
  echo "PIV_DNS_xr1=${PIV_DNS_xr1}" >> ../openfoamDNS_to_pseudoPIV.info
  echo "PIV_DNS_xr2=${PIV_DNS_xr2}" >> ../openfoamDNS_to_pseudoPIV.info
  echo "PIV_DNS_yr1=${PIV_DNS_yr1}" >> ../openfoamDNS_to_pseudoPIV.info
  echo "PIV_DNS_yr2=${PIV_DNS_yr2}" >> ../openfoamDNS_to_pseudoPIV.info 
  
  echo 'set arrow from PIV_xr1,PIV_yr1 to PIV_xr1,PIV_yr2 lc rgb "orange" lw 4 nohead front'  >> ${fic_gnp}
  echo 'set arrow from PIV_xr2,PIV_yr1 to PIV_xr2,PIV_yr2 lc rgb "orange" lw 4 nohead front'  >> ${fic_gnp}
  echo 'set arrow from PIV_xr1,PIV_yr1 to PIV_xr2,PIV_yr1 lc rgb "orange" lw 4 nohead front'  >> ${fic_gnp}
  echo 'set arrow from PIV_xr1,PIV_yr2 to PIV_xr2,PIV_yr2 lc rgb "orange" lw 4 nohead front'  >> ${fic_gnp}
  echo 'set arrow from DNS_xr1,DNS_yr1 to DNS_xr1,DNS_yr2 lc rgb "green" lw 4 nohead front'  >> ${fic_gnp}
  echo 'set arrow from DNS_xr2,DNS_yr1 to DNS_xr2,DNS_yr2 lc rgb "green" lw 4 nohead front'  >> ${fic_gnp}
  echo 'set arrow from DNS_xr1,DNS_yr1 to DNS_xr2,DNS_yr1 lc rgb "green" lw 4 nohead front'  >> ${fic_gnp}
  echo 'set arrow from DNS_xr1,DNS_yr2 to DNS_xr2,DNS_yr2 lc rgb "green" lw 4 nohead front'  >> ${fic_gnp}
  
  # cylinder : black disk diameter D=1.0
  
  echo 'set object 1 circle center 0,0 size 0.5 fc rgb "#FF00FF" fillstyle transparent pattern 2 lw 1 front'  >> ${fic_gnp}
 
  # gnuplot PNG files
  
  # plot : if code_plot == "point" no smoothing between points
  
  set code_plot = "point"
  #set code_plot = "smooth"
  
  echo 'set terminal png crop size 1700,600 font "LiberationSans-Regular,18  noenhanced' >> ${fic_gnp}
   
  # cas [smooth] => tempory file for splot use (adding blanck lines to PIV file)
  
  if ( ${code_plot} == "smooth" ) then
    if (-e ${PIV_file_model} ) then
      if -e tmp1.txt \rm tmp1.txt
      cat ${PIV_file_model} | grep "=" | awk '{ print "#",$0 }' > tmp1.txt
      cat ${PIV_file_model} | grep -v "=" | awk '{ if (($2!=prec) && (NR>1)) print ""; print $0; prec=$2 }' >> tmp1.txt
    endif
    if -e tmp2.txt \rm tmp2.txt
    cat ${PIV_file_model_new} | grep "=" | awk '{ print "#",$0 }' > tmp2.txt
    cat ${PIV_file_model_new} | grep -v "#" | grep -v "=" | awk '{ if (($2!=prec) && (NR>1)) print ""; print $0; prec=$2 }' >> tmp2.txt
  endif
  
  # cas [smooth] => splot view
  
  if ( ${code_plot} == "smooth" ) then
    echo 'set pm3d implicit at b' >> ${fic_gnp}
    echo 'set view map' >> ${fic_gnp}
    echo 'set style data pm3d' >> ${fic_gnp}
    echo 'set style function pm3d' >> ${fic_gnp}
    echo 'set pm3d interpolate 5,5' >> ${fic_gnp}
  endif
  
  # PIV model
  
  if (-e ${PIV_file_model} ) then
  
    echo 'set title "PIV model"' >> ${fic_gnp}
    
    # PIV model : Ux
    
    echo 'set cbrange [-0.9: 1.9]' >> ${fic_gnp}
    echo 'set output "PIV_model_Ux.png"'  >> ${fic_gnp}

    if ( ${code_plot} == "point" ) then
      echo 'plot [PIV_DNS_xr1-0.01:PIV_DNS_xr2+0.01][PIV_DNS_yr1-0.01:PIV_DNS_yr2+0.01] \' >> ${fic_gnp}
      echo '  "'${PIV_file_model}'" u (($1-('${PIV_xcyl}'))/'${PIV_Dcyl}'):(($2-('${PIV_ycyl}'))/'${PIV_Dcyl}'):($3/'${PIV_Velocity}')  w p pt 5 ps 1 palette title "PIV model : Ux/'${PIV_Velocity}'"' >> ${fic_gnp}
    endif
    if ( ${code_plot} == "smooth" ) then
      echo 'splot [PIV_DNS_xr1-0.01:PIV_DNS_xr2+0.01][PIV_DNS_yr1-0.01:PIV_DNS_yr2+0.01][] \' >> ${fic_gnp}
      echo '  "tmp1.txt" u (($1-('${PIV_xcyl}'))/'${PIV_Dcyl}'):(($2-('${PIV_ycyl}'))/'${PIV_Dcyl}'):($3/'${PIV_Velocity}')  title "PIV model : Ux/'${PIV_Velocity}'"' >> ${fic_gnp}
    endif
    
    # PIV model : Uy
    
    echo 'set output "PIV_model_Uy.png"'  >> ${fic_gnp}
    echo 'set cbrange [-0.9: 0.9]' >> ${fic_gnp}
    
    if ( ${code_plot} == "point" ) then
      echo 'plot [PIV_DNS_xr1-0.01:PIV_DNS_xr2+0.01][PIV_DNS_yr1-0.01:PIV_DNS_yr2+0.01] \' >> ${fic_gnp}
      echo '  "'${PIV_file_model}'" u (($1-('${PIV_xcyl}'))/'${PIV_Dcyl}'):(($2-('${PIV_ycyl}'))/'${PIV_Dcyl}'):($4/'${PIV_Velocity}') w p pt 5 ps 1 palette title "PIV model : Uy/'${PIV_Velocity}'"' >> ${fic_gnp}
    endif
    if ( ${code_plot} == "smooth" ) then
      echo 'splot [PIV_DNS_xr1-0.01:PIV_DNS_xr2+0.01][PIV_DNS_yr1-0.01:PIV_DNS_yr2+0.01][] \' >> ${fic_gnp}
      echo '  "tmp1.txt" u (($1-('${PIV_xcyl}'))/'${PIV_Dcyl}'):(($2-('${PIV_ycyl}'))/'${PIV_Dcyl}'):($4/'${PIV_Velocity}') title "PIV model : Uy/'${PIV_Velocity}'"' >> ${fic_gnp}
    endif
    
    # PIV model : IsValid
    
    echo 'set output "PIV_model_IsValid.png"'  >> ${fic_gnp}
    echo 'set cbrange [0:1]' >> ${fic_gnp}
    
    if ( ${code_plot} == "point" ) then
      echo 'plot [PIV_DNS_xr1-0.01:PIV_DNS_xr2+0.01][PIV_DNS_yr1-0.01:PIV_DNS_yr2+0.01] \' >> ${fic_gnp}
      echo '  "'${PIV_file_model}'" u (($1-('${PIV_xcyl}'))/'${PIV_Dcyl}'):(($2-('${PIV_ycyl}'))/'${PIV_Dcyl}'):5 w p pt 5 ps 1 palette title "PIV model : IsValid"' >> ${fic_gnp}
    endif
    if ( ${code_plot} == "smooth" ) then
      echo 'splot [PIV_DNS_xr1-0.01:PIV_DNS_xr2+0.01][PIV_DNS_yr1-0.01:PIV_DNS_yr2+0.01][] \' >> ${fic_gnp}
      echo '  "tmp1.txt" u (($1-('${PIV_xcyl}'))/'${PIV_Dcyl}'):(($2-('${PIV_ycyl}'))/'${PIV_Dcyl}'):5 title "PIV model : IsValid"' >> ${fic_gnp}
    endif
    
  endif
  
  # Fake PIV : PIV new
  
  if ( ${code_adim} == 0 ) then
    
    # PIV new
    
    echo 'set title "PIV new (Z='${Zslice}') from gaussian smoothing of DNS ['${DNS_info}']" noenhanced' >> ${fic_gnp}
      
    # PIV new : Ux
    
    echo 'set cbrange [-0.9: 1.9]' >> ${fic_gnp} # default = wake cylinder
    set code = ` echo ${DNS_info} | grep "mean" | wc -l `
    if ( ${code} != 0 ) echo 'set cbrange [-0.9: 1.9]' >> ${fic_gnp}
    set code = ` echo ${DNS_info} | grep "spatialModes_" | grep "modes" | wc -l `
    if ( ${code} != 0 ) echo 'set cbrange [-0.2: 0.2]' >> ${fic_gnp}
    set code = ` echo ${DNS_info} | grep "residualSpeed_" | wc -l `
    if ( ${code} != 0 ) echo 'set cbrange [-0.7: 0.7]' >> ${fic_gnp}
    set code = ` echo ${DNS_info} | grep "sillageDNSRe300" | wc -l `
    if ( ${code} != 0 ) echo 'set cbrange [-0.9: 1.9]' >> ${fic_gnp}

    echo 'set output "PIV_new_Ux.png"'  >> ${fic_gnp}
    
    if ( ${code_plot} == "point" ) then
      echo 'plot [PIV_DNS_xr1-0.01:PIV_DNS_xr2+0.01][PIV_DNS_yr1-0.01:PIV_DNS_yr2+0.01] \' >> ${fic_gnp}
      echo '  "'${PIV_file_model_new}'" u (($1-('${PIV_xcyl}'))/'${PIV_Dcyl}'):(($2-('${PIV_ycyl}'))/'${PIV_Dcyl}'):($3/'${PIV_Velocity}') w p pt 5 ps 1 palette title "PIV new : Z='${Zslice}' Ux/'${PIV_Velocity}'"' >> ${fic_gnp}
      endif
    if ( ${code_plot} == "smooth" ) then
      echo 'splot [PIV_DNS_xr1-0.01:PIV_DNS_xr2+0.01][PIV_DNS_yr1-0.01:PIV_DNS_yr2+0.01][] \' >> ${fic_gnp}
      echo '  "tmp2.txt" u (($1-('${PIV_xcyl}'))/'${PIV_Dcyl}'):(($2-('${PIV_ycyl}'))/'${PIV_Dcyl}'):($3/'${PIV_Velocity}') title "PIV new : Ux/'${PIV_Velocity}'"' >> ${fic_gnp}
    endif
    
    # PIV new : Uy
    
    echo 'set cbrange [-0.9: 0.9]' >> ${fic_gnp} # default = wake cylinder
    
    set code = ` echo ${DNS_info} | grep "mean" | wc -l `
    if ( ${code} != 0 ) echo 'set cbrange [-0.9: 0.9]' >> ${fic_gnp}
    set code = ` echo ${DNS_info} | grep "spatialModes_" | grep "modes" | wc -l `
    if ( ${code} != 0 ) echo 'set cbrange [-0.2: 0.2]' >> ${fic_gnp}
    set code = ` echo ${DNS_info} | grep "residualSpeed_" | wc -l `
    if ( ${code} != 0 ) echo 'set cbrange [-0.7: 0.7]' >> ${fic_gnp}
    set code = ` echo ${DNS_info} | grep "sillageDNSRe300" | wc -l `
    if ( ${code} != 0 ) echo 'set cbrange [-0.9: 0.9]' >> ${fic_gnp}
    
    echo 'set output "PIV_new_Uy.png"'  >> ${fic_gnp}
    if ( ${code_plot} == "point" ) then
      echo 'plot [PIV_DNS_xr1-0.01:PIV_DNS_xr2+0.01][PIV_DNS_yr1-0.01:PIV_DNS_yr2+0.01] \' >> ${fic_gnp}
      echo '  "'${PIV_file_model_new}'" u (($1-('${PIV_xcyl}'))/'${PIV_Dcyl}'):(($2-('${PIV_ycyl}'))/'${PIV_Dcyl}'):($4/'${PIV_Velocity}') w p pt 5 ps 1 palette title "PIV new : Z='${Zslice}' Uy/'${PIV_Velocity}'"' >> ${fic_gnp}
      endif
    if ( ${code_plot} == "smooth" ) then
      echo 'splot [PIV_DNS_xr1-0.01:PIV_DNS_xr2+0.01][PIV_DNS_yr1-0.01:PIV_DNS_yr2+0.01][] \' >> ${fic_gnp}
      echo '  "tmp2.txt" u (($1-('${PIV_xcyl}'))/'${PIV_Dcyl}'):(($2-('${PIV_ycyl}'))/'${PIV_Dcyl}'):($4/'${PIV_Velocity}') title "PIV new : Uy/'${PIV_Velocity}'"' >> ${fic_gnp}
    endif
    
    # PIV new : IsValid
    
    echo 'set cbrange [0:1]' >> ${fic_gnp}
    echo 'set output "PIV_new_IsValid.png"'  >> ${fic_gnp}
    
    if ( ${code_plot} == "point" ) then
      echo 'plot [PIV_DNS_xr1-0.01:PIV_DNS_xr2+0.01][PIV_DNS_yr1-0.01:PIV_DNS_yr2+0.01] \' >> ${fic_gnp}
      echo '  "'${PIV_file_model_new}'" u (($1-('${PIV_xcyl}'))/'${PIV_Dcyl}'):(($2-('${PIV_ycyl}'))/'${PIV_Dcyl}'):5 w p pt 5 ps 1 palette title "PIV new : IsValid"' >> ${fic_gnp}
    endif
    if ( ${code_plot} == "smooth" ) then
      echo 'splot [PIV_DNS_xr1-0.01:PIV_DNS_xr2+0.01][PIV_DNS_yr1-0.01:PIV_DNS_yr2+0.01][] \' >> ${fic_gnp}
      echo '  "tmp2.txt" u (($1-('${PIV_xcyl}'))/'${PIV_Dcyl}'):(($2-('${PIV_ycyl}'))/'${PIV_Dcyl}'):5 title "PIV new : IsValid"' >> ${fic_gnp}
    endif
  
  else
 
    # PIV new
    
    echo 'set title "PIV new (Z='${Zslice}') from gaussian smoothing of DNS ['${DNS_info}']" noenhanced' >> ${fic_gnp}
      
    # PIV new : Ux
    
    echo 'set cbrange [-0.9: 1.9]' >> ${fic_gnp} # default = wake cylinder
    set code = ` echo ${DNS_info} | grep "mean" | wc -l `
    if ( ${code} != 0 ) echo 'set cbrange [-0.9: 1.9]' >> ${fic_gnp}
    set code = ` echo ${DNS_info} | grep "spatialModes_" | grep "modes" | wc -l `
    if ( ${code} != 0 ) echo 'set cbrange [-0.2: 0.2]' >> ${fic_gnp}
    set code = ` echo ${DNS_info} | grep "residualSpeed_" | wc -l `
    if ( ${code} != 0 ) echo 'set cbrange [-0.7: 0.7]' >> ${fic_gnp}
    set code = ` echo ${DNS_info} | grep "sillageDNSRe300" | wc -l `
    if ( ${code} != 0 ) echo 'set cbrange [-0.9: 1.9]' >> ${fic_gnp}

    echo 'set output "PIV_new_Ux.png"'  >> ${fic_gnp}
    
    if ( ${code_plot} == "point" ) then
      echo 'plot [PIV_DNS_xr1-0.01:PIV_DNS_xr2+0.01][PIV_DNS_yr1-0.01:PIV_DNS_yr2+0.01] \' >> ${fic_gnp}
      echo '  "'${PIV_file_model_new}'" u  ($1-('${PIV_xcyl}'/'${PIV_Dcyl}')):($2-('${PIV_ycyl}'/'${PIV_Dcyl}')):($3) w p pt 5 ps 1 palette title "PIV new : Z='${Zslice}' Ux"' >> ${fic_gnp}
    endif
    if ( ${code_plot} == "smooth" ) then
      echo 'splot [PIV_DNS_xr1-0.01:PIV_DNS_xr2+0.01][PIV_DNS_yr1-0.01:PIV_DNS_yr2+0.01][] \' >> ${fic_gnp}
      echo '  "tmp2.txt" u  ($1-('${PIV_xcyl}'/'${PIV_Dcyl}')):($2-('${PIV_ycyl}'/'${PIV_Dcyl}')):($3) title "PIV new : Ux"' >> ${fic_gnp}
    endif
    
    # PIV new : Uy
    
    echo 'set cbrange [-0.9: 0.9]' >> ${fic_gnp} # default = wake cylinder
    
    set code = ` echo ${DNS_info} | grep "mean" | wc -l `
    if ( ${code} != 0 ) echo 'set cbrange [-0.9: 0.9]' >> ${fic_gnp}
    set code = ` echo ${DNS_info} | grep "spatialModes_" | grep "modes" | wc -l `
    if ( ${code} != 0 ) echo 'set cbrange [-0.2: 0.2]' >> ${fic_gnp}
    set code = ` echo ${DNS_info} | grep "residualSpeed_" | wc -l `
    if ( ${code} != 0 ) echo 'set cbrange [-0.7: 0.7]' >> ${fic_gnp}
    set code = ` echo ${DNS_info} | grep "sillageDNSRe300" | wc -l `
    if ( ${code} != 0 ) echo 'set cbrange [-0.9: 0.9]' >> ${fic_gnp}
    
    echo 'set output "PIV_new_Uy.png"'  >> ${fic_gnp}
    if ( ${code_plot} == "point" ) then
      echo 'plot [PIV_DNS_xr1-0.01:PIV_DNS_xr2+0.01][PIV_DNS_yr1-0.01:PIV_DNS_yr2+0.01] \' >> ${fic_gnp}
      echo '  "'${PIV_file_model_new}'" u ($1-('${PIV_xcyl}'/'${PIV_Dcyl}')):($2-('${PIV_ycyl}'/'${PIV_Dcyl}')):($4) w p pt 5 ps 1 palette title "PIV new : Z='${Zslice}' Uy"' >> ${fic_gnp}
    endif
    if ( ${code_plot} == "smooth" ) then
      echo 'splot [PIV_DNS_xr1-0.01:PIV_DNS_xr2+0.01][PIV_DNS_yr1-0.01:PIV_DNS_yr2+0.01][] \' >> ${fic_gnp}
      echo '  "tmp2.txt" u  ($1-('${PIV_xcyl}'/'${PIV_Dcyl}')):($2-('${PIV_ycyl}'/'${PIV_Dcyl}')):($4) title "PIV new : Uy"' >> ${fic_gnp}
    endif
    
    # PIV new : IsValid
    
    echo 'set cbrange [0:1]' >> ${fic_gnp}
    echo 'set output "PIV_new_IsValid.png"'  >> ${fic_gnp}
    
    if ( ${code_plot} == "point" ) then
      echo 'plot [PIV_DNS_xr1-0.01:PIV_DNS_xr2+0.01][PIV_DNS_yr1-0.01:PIV_DNS_yr2+0.01] \' >> ${fic_gnp}
      echo '  "'${PIV_file_model_new}'" u  ($1-('${PIV_xcyl}'/'${PIV_Dcyl}')):($2-('${PIV_ycyl}'/'${PIV_Dcyl}')):5 w p pt 5 ps 1 palette title "PIV new : IsValid"' >> ${fic_gnp}
    endif
    if ( ${code_plot} == "smooth" ) then
      echo 'splot [PIV_DNS_xr1-0.01:PIV_DNS_xr2+0.01][PIV_DNS_yr1-0.01:PIV_DNS_yr2+0.01][] \' >> ${fic_gnp}
      echo '  "tmp2.txt" u  ($1-('${PIV_xcyl}'/'${PIV_Dcyl}')):($2-('${PIV_ycyl}'/'${PIV_Dcyl}')):5 title "PIV new : IsValid"' >> ${fic_gnp}
    endif

  endif
  
  gnuplot ${fic_gnp}

  echo ""
  echo "New PIV : ${PIV_file_model_new} = ${Nx}x${Ny}x${Nz} points : Cf. PIV_*.png (and PIV_model*.png)"
  echo ""
  
  # merging PNG files
  
  foreach U ( Ux Uy )
  
    convert \
      ${U}_calculator_withoutGrid.png \
      -font courier-bold -fill black -pointsize 60 -undercolor '#99776699' -gravity South \
      -annotate +0+120 "${U} : Openfoam DNS " \
      tmp1.png
      
    convert \
      ${U}_calculator_pointVolumeInterpolator_slice_withoutGrid.png \
      -font courier-bold -fill black -pointsize 50 -undercolor '#99776699' -gravity South \
      -annotate +0+120 "${U} : DNS to cropped slice uniform grid" \
      tmp2.png
      
    convert \
      -resize 63% \
      PIV_new_${U}.png \
      -font courier-bold -fill black -pointsize 35 -undercolor '#99776699' -gravity South \
      -annotate +0+60 "${U} : cropped slice to pseudo PIV" \
      tmp3.png
     
    montage tmp1.png tmp2.png tmp3.png -geometry +1+1 -border 1 -bordercolor "blue" -tile 3x1 ${U}.png 
    
  end
  \rm  tmp1.png tmp2.png tmp3.png
  montage Ux.png Uy.png -geometry +1+1 -border 1 -bordercolor "red" -tile 1x2 Uxy.png 
  
endif

#------------------------------------------------------------------------------
