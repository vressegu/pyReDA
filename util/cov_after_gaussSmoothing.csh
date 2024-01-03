#!/bin/tcsh
#
#
# Laurence Wallian - ACTA - OPAALE - INRAE Rennes [Decembre 2023 - Janvier 2024]
#
#------------------------------------------------------------------------------
#
# MORAANE : cov(Ux,Uy), cov(Uy,Uz) and cov(Uz,Ux)
#
# USAGE : tcsh DIR0_name DIR1_name 
#               with DIR0 = folder including 
#                                       [ROM_PIV] folder
#                                       [ROM_PIV/DIR1/cov_after_gaussSmoothing] folder 
#                                       created by previous part of script [openfoamDNS_to_pseudoPIV_all.csh]
#               with DIR1 = sub directory of [DIR0/ITHACAoutput] directory
#
# EXAMPLE : tcsh /workspace/MORAANE/exemple_openfoam/DNS300/ROM-v3.2.3 residualSpeed_2_U
#
# FILES used : 
#          files in [DIR0/ROM_PIV] : openfoamDNS_to_pseudoPIV.info
#          files in [DIR0/ROM_PIV/DIR1/cov_after_gaussSmoothing] : list_fic_time.txt and other U*.txt files
#          files in [DIR0/util] : cov_after_gaussSmoothing_stat.C
#
# NOTE : script [openfoamDNS_to_pseudoPIV_all.csh] must have been run before
#              with a command like this :
#                       tcsh openfoamDNS_to_pseudoPIV_all.csh 1.5 ROM residualSpeed_2_U
#              according to the [run_info.txt] file
#
#------------------------------------------------------------------------------

# pvbatch PATH

alias pvbatch '/usr/local/ParaView-5.10.1-MPI-Linux-Python3.9-x86_64/bin/pvbatch'

# alias for color prompt

alias WRITE_LINE 'echo ""'
alias WRITE_INFO 'echo "    \033[32;7m  \!*  \033[0m"'
alias WRITE_WARNING 'echo "\033[34;7m  \!*  \033[0m"'
alias ASK_QUESTION 'echo -n "  \033[34;5m  \!*  \033[0m  " '
alias READ_ANSWER 'echo -n "\033[34;7m        \!*  \033[0m   "'
alias WRITE_ERROR 'echo "\033[31;7m \\!\\!\\! OUPS \\!\\!\\!   \!*  \\!\\!\\!\033[0m"'

#------------------------------------------------------------------------------

# current directory

set dir_ici = ` pwd `
alias lsd  ' ls -l | awk '\''{i=0; i=index($1,"d"); if (i==1) print $9 }'\'' '

# D folder : for example [residualSpeed_2_U] # 
#                 must be in [ROM_PIV] folder and contain the folder [cov_after_gaussSmoothing] 
#                 which includes txt files extracted from previous pvbatch smooth/crop operations

# D folder : default value
set All_D = ( residualSpeed_2_U )

# D folder : input value
if ( $1 != "" ) set All_D = ( $1 )

# DIR0 folder :  for example .../RedLum_from_OpenFoam/D1_Lz*pi_Re*/ROM-v1

# DIR0 folder : default value
set DIR0 = /media/laurence.wallian/Val4To/RedLUM/data_red_lum_cpp/DNS300-GeoLES3900/ROM-v3.1.2

# DIR0 folder : input value
if ( $2 != "" ) set DIR0 = $2

#------------------------------------------------------------------------------

foreach D ( ${All_D} ) 

  echo ""; echo "--- ${DIR0}/ROM_PIV/${D} ---"; echo ""
  
  set dir_work_up = ${DIR0}/ROM_PIV
  set dir_work = ${dir_work_up}/${D}
  
  if (!(-e ${dir_work}/cov_after_gaussSmoothing)) then
    set error = "${dir_work}/cov_after_gaussSmoothing NOT FOUND"
    WRITE_LINE; WRITE_ERROR "${error}"; WRITE_LINE
    exit()
  endif
 
  if (!(-e ${dir_work}/cov_after_gaussSmoothing/list_fic_time.txt)) then
    set error = "${dir_work}/cov_after_gaussSmoothing/list_fic_time.txt NOT FOUND"
    WRITE_LINE; WRITE_ERROR "${error}"; WRITE_LINE
    exit()
  endif
   
  if (!(-e ${dir_work}/openfoamDNS_to_pseudoPIV.info)) then
    set error = "${dir_work}/openfoamDNS_to_pseudoPIV.info NOT FOUND"
    WRITE_LINE; WRITE_ERROR "${error}"; WRITE_LINE
    exit()
  endif
   
  if (!(-e ${dir_work_up}/util/cov_after_gaussSmoothing_stat.C)) then
    set error = "${dir_work}/util/cov_after_gaussSmoothing_stat.C NOT FOUND"
    WRITE_LINE; WRITE_ERROR "${error}"; WRITE_LINE
    exit()
  endif

  set Zslice = ` cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "ZSLICE_VALUE=" | awk -F'=' '{ print $2 }' `

  cd ${dir_work}/cov_after_gaussSmoothing
  
  set Utxt_first = `  cat list_fic_time.txt | grep U | head -1 `
  set Nrow = ` cat ${Utxt_first} | wc -l `
  set Ntime = ` cat list_fic_time.txt | wc -l | awk '{ print $1-1 }' `
  \cp ${dir_work_up}/util/cov_after_gaussSmoothing_stat.C .
  
  g++ -I/usr/local/include/eigen3 -std=c++11 cov_after_gaussSmoothing_stat.C -o cov_after_gaussSmoothing_stat
  ./cov_after_gaussSmoothing_stat list_fic_time.txt ${Nrow} ${Ntime}
  
  # CSV file => inverse COV+diag_matrix() as PIV file

  # PIV point coordinates : PIV_Dcyl != 1 or PIV_Dcyl = 1
  set DNS_Dcyl=`cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "DNS_Dcyl=" | awk -F'=' '{ print $2 }' `
  set DNS_crop_x0=`cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "DNS_crop_x0=" | awk -F'=' '{ print $2 }' `
  set DNS_crop_y0=`cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "DNS_crop_y0=" | awk -F'=' '{ print $2 }' `
  set PIV_Dcyl=`cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "PIV_Dcyl=" | awk -F'=' '{ print $2 }' `
  set PIV_xcyl=`cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "PIV_xcyl=" | awk -F'=' '{ print $2 }' `
  set PIV_ycyl=`cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "PIV_ycyl=" | awk -F'=' '{ print $2 }' `
  set PIV_xmin=`cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "PIV_xmin=" | awk -F'=' '{ print $2 }' `
  set PIV_ymin=`cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "PIV_ymin=" | awk -F'=' '{ print $2 }' `

  if -e XY.txt \rm XY.txt
  cat XYcrop.txt | \
    awk -v P_d=${PIV_Dcyl} -v D_d=${DNS_Dcyl} -v D_x0=${DNS_crop_x0} -v P_x0=${PIV_xmin} -v D_y0=${DNS_crop_y0} -v P_y0=${PIV_ymin} '{ \
    printf("%10.6f %10.6f\n", ($1-D_x0+0.)*(P_d+0.)/(D_d+0.)+P_x0+0., ($2-D_y0+0.)*(P_d+0.)/(D_d+0.)+P_y0+0) }' > XY.txt
  
  # inv(cov+diag_mat(0.006**2)) (Cf. http://w3.gel.ulaval.ca/~fortier/MAT19961/powerpoint2000/sec2-3-4/sld016.htm)
  set A_mat_diag=0.06
  if -e cov_xx.txt \rm cov_xx.txt
  cat cov_xx.csv | grep -v cov | awk  -v A=${A_mat_diag} '{ print $1+A**2 }' > cov_xx.txt
  if -e cov_yy.txt \rm cov_yy.txt
  cat cov_yy.csv | grep -v cov | awk  -v A=${A_mat_diag} '{ print $1+A**2 }' > cov_yy.txt
  if -e cov_xy.txt \rm cov_xy.txt
  cat cov_xy.csv | grep -v cov > cov_xy.txt
  if -e tmp.txt \rm tmp.txt
  paste cov_xx.txt  cov_yy.txt cov_xy.txt > tmp.txt
  
  set PIV_velocity=`cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "PIV_Velocity=" | awk -F'=' '{ print $2 }' `
  if -e COV.txt \rm COV.txt
  awk -v V=${PIV_velocity} '{ \
    V2=V**2; \
    a=($2+0.); b=($1+0.); c=-($3+0.); \
    det=a*b-c*c; d=sqrt(det*det); \
    print a/det*V2, b/det*V2, c/det*V2}' tmp.txt > COV.txt
  if -e COV.txt \rm COV.txt
  awk '{ \
    a=($2+0.); b=($1+0.); c=-($3+0.); \
    det=a*b-c*c; d=sqrt(det*det); \
    print a/det, b/det, c/det}' tmp.txt > COV.txt

  # all COV values
  set PIV_file_new = Inv_COVxy.dat
  if -e ${PIV_file_new} \rm ${PIV_file_new}; touch ${PIV_file_new}
  echo "# Cov = ((cov_xx+A2,cov_xy),(cov_xy,cov_yy+A2)) " >> ${PIV_file_new}
  echo "#   with A2 = ${A_mat_diag}**2" >> ${PIV_file_new}
  echo "# => InvCov = 1/Cov = ((cov_yy+A2,-cov_xy), (-cov_xy,cov_xx+A2))/det " >> ${PIV_file_new}
  echo "# x   y  InvCov[1][1]   InvCov[2][2]   InvCov[1][2] " >> ${PIV_file_new}
  paste XY.txt COV.txt >> ${PIV_file_new}
  
  #  same order (x,y) as  PIV model
  
  if -e PIV_new_x.txt \rm PIV_new_x.txt
  cat ${PIV_file_new} | grep -v "#" | \
    awk '{ x=$1+0. ; if (NF!=0) printf("%.0f\n", 1000000.*x) }' | sort -n  | uniq | \
    awk '{ x=$1+0. ; printf("%.6f\n",x/1000000.)}' > PIV_new_x.txt
  #set All_PIV_yinv = ` cat All_PIV_x.txt | sed s/"-"/"\\-"/g`
  set All_PIV_x = ` cat PIV_new_x.txt `
  
  set dx_max = ` echo ${All_PIV_x} | sort -n | awk '{ d=$NF-$1; d=sqrt(d*d); print d }' `
  
  if -e PIV_new_yinv.txt \rm PIV_new_yinv.txt
  cat ${PIV_file_new} | grep -v "#" | \
    awk '{ x=$2+0. ; if (NF!=0) printf("%.0f\n", 1000000.*x) }' | sort -n -r  | uniq | \
    awk '{ x=$1+0. ; printf("%.6f\n",x/1000000.)}' > PIV_new_yinv.txt
  #set All_PIV_new_yinv = ` cat PIV_new_yinv.txt | sed s/"-"/"\\-"/g`
  set All_PIV_new_yinv = ` cat PIV_new_yinv.txt `

  if -e tmp.txt \rm tmp.txt
  cat ${PIV_file_new} | grep -v "#" | awk '{ for (i=1; i<=NF; i++) printf("%s ",$i); print "" }' > tmp.txt
  \rm ${PIV_file_new}; touch ${PIV_file_new}
  echo "# Cov = ((cov_xx+A2,cov_xy),(cov_xy,cov_yy+A2)) " >> ${PIV_file_new}
  echo "#   with A2 = ${A_mat_diag}**2" >> ${PIV_file_new}
  echo "# => InvCov = 1/Cov = ((cov_yy+A2,-cov_xy), (-cov_xy,cov_xx+A2))/det " >> ${PIV_file_new}
  echo "# x   y  InvCov[1][1]   InvCov[2][2]   InvCov[1][2] " >> ${PIV_file_new}
  foreach y ( ${All_PIV_new_yinv} )
    cat tmp.txt | awk -v y=${y} -v dx_max=${dx_max} '{ if ($2==y) print $1+dx_max, $0 }' | \
    sort -n | uniq | \
    awk '{ for (i=2;i<NF; i++) printf("%s ",$i); print $NF }' >> ${PIV_file_new}
  end

  # visu gnuplot
  set fic_gnp = Inv_COVxy.gnp
  if -e ${fic_gnp} \rm ${fic_gnp}; touch ${fic_gnp}

  echo 'set grid' >> ${fic_gnp}
  echo 'set size ratio -1' >> ${fic_gnp}
  echo 'set key box outside center bottom horizontal maxcols 5 maxrows 5' >> ${fic_gnp}
  echo 'set title "pvbatch on ROM '${D}' : grid1 to uniform grid2 (Gaussian Smoothing then Slice Z='${Zslice}')" noenhanced' >> ${fic_gnp}
  echo 'set terminal png crop size 1000,1000 font "LiberationSans-Regular,18  noenhanced' >> ${fic_gnp}
  echo 'set palette color' >> ${fic_gnp}
  echo 'set palette model RGB' >> ${fic_gnp}
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

  cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "DNS_xcyl=" >> ${fic_gnp} 
  cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "DNS_ycyl=" >> ${fic_gnp} 
  cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "DNS_Dcyl=" >> ${fic_gnp} 
  cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "DNS_xr1=" | grep -v PIV >> ${fic_gnp} 
  cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "DNS_yr1=" | grep -v PIV >> ${fic_gnp} 
  cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "DNS_xr2=" | grep -v PIV >> ${fic_gnp} 
  cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "DNS_yr2=" | grep -v PIV >> ${fic_gnp} 
  cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "PIV_xcyl=" >> ${fic_gnp} 
  cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "PIV_ycyl=" >> ${fic_gnp} 
  cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "PIV_Dcyl=" >> ${fic_gnp} 
  cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "PIV_xr1=" >> ${fic_gnp} 
  cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "PIV_yr1=" >> ${fic_gnp} 
  cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "PIV_xr2=" >> ${fic_gnp} 
  cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "PIV_yr2=" >> ${fic_gnp} 
  cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "PIV_DNS_xr1=" >> ${fic_gnp} 
  cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "PIV_DNS_yr1=" >> ${fic_gnp} 
  cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "PIV_DNS_xr2=" >> ${fic_gnp} 
  cat ${dir_work}/openfoamDNS_to_pseudoPIV.info | grep "PIV_DNS_yr2=" >> ${fic_gnp} 

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
  
  echo 'set terminal png crop size 1700,600 font "LiberationSans-Regular,18  noenhanced' >> ${fic_gnp}

  echo 'set cbrange [0:250]' >> ${fic_gnp}
  echo 'set output "PIV_new_covInv_Uxx.png"' >> ${fic_gnp}
  echo 'plot [PIV_DNS_xr1-0.01:PIV_DNS_xr2+0.01][PIV_DNS_yr1-0.01:PIV_DNS_yr2+0.01] \' >> ${fic_gnp}
  echo '  "Inv_COVxy.dat" u (($1-(PIV_xcyl))/PIV_Dcyl):(($2-(PIV_ycyl))/PIV_Dcyl):3 w p pt 5 ps 1 palette title "M[1][1] with M=inv(  (  (cov(ux*ux)+'${A_mat_diag}'**2), cov(ux*uy)),   ((cov(ux*uy), (cov(uy*uy)+'${A_mat_diag}'**2) )  )"' >> ${fic_gnp}
  echo 'set output "PIV_new_covInv_Uyy.png"' >> ${fic_gnp}
  echo 'plot [PIV_DNS_xr1-0.01:PIV_DNS_xr2+0.01][PIV_DNS_yr1-0.01:PIV_DNS_yr2+0.01] \' >> ${fic_gnp}
  echo '  "Inv_COVxy.dat" u (($1-(PIV_xcyl))/PIV_Dcyl):(($2-(PIV_ycyl))/PIV_Dcyl):4 w p pt 5 ps 1 palette title "M[2][2] with M=inv(  (  (cov(ux*ux)+'${A_mat_diag}'**2), cov(ux*uy)),   ((cov(ux*uy), (cov(uy*uy)+'${A_mat_diag}'**2) )  )"' >> ${fic_gnp}
  echo 'set cbrange [-100:100]' >> ${fic_gnp}
  echo 'set output "PIV_new_covInv_Uxy.png"' >> ${fic_gnp}
  echo 'plot [PIV_DNS_xr1-0.01:PIV_DNS_xr2+0.01][PIV_DNS_yr1-0.01:PIV_DNS_yr2+0.01] \' >> ${fic_gnp}
  echo '  "Inv_COVxy.dat" u (($1-(PIV_xcyl))/PIV_Dcyl):(($2-(PIV_ycyl))/PIV_Dcyl):5 w p pt 5 ps 1 palette title "M[1][2] with M=inv(  (  (cov(ux*ux)+'${A_mat_diag}'**2), cov(ux*uy)),   ((cov(ux*uy), (cov(uy*uy)+'${A_mat_diag}'**2) )  )"' >> ${fic_gnp}
  
  gnuplot ${fic_gnp}

  # other visu
  
  if -e visu_cov.gnp \rm visu_cov.gnp; touch visu_cov.gnp
  echo 'set grid ' >> visu_cov.gnp
  echo 'set key box outside center bottom horizontal maxcols 5 maxrows 5 ' >> visu_cov.gnp
  echo 'set title "temporal average" noenhanced ' >> visu_cov.gnp
  echo 'set terminal png crop size 1000,1000 font "LiberationSans-Regular,18  noenhanced ' >> visu_cov.gnp
  echo 'set palette color ' >> visu_cov.gnp
  echo 'set palette model RGB ' >> visu_cov.gnp
  echo 'set output "cov_xx.png" ' >> visu_cov.gnp
  echo 'plot \' >> visu_cov.gnp
  echo '  "cov_xx.csv" w p pt 7 lc rgb "red" title "mean(x*x)-mean(x)*mean(x)", \' >> visu_cov.gnp
  echo '  "mean_xx.csv" w p pt 6 lc rgb "blue"  title "mean(x*x)"  ' >> visu_cov.gnp
  echo '   ' >> visu_cov.gnp
  echo 'set output "cov_yy.png" ' >> visu_cov.gnp
  echo 'plot \' >> visu_cov.gnp
  echo '  "cov_yy.csv" w p pt 7 lc rgb "red"  title "mean(y*y)-mean(y)*mean(y)", \' >> visu_cov.gnp
  echo '  "mean_yy.csv" w p pt 6 lc rgb "blue"  title "mean(y*y)"  ' >> visu_cov.gnp
  echo ' ' >> visu_cov.gnp
  echo 'set output "cov_zz.png" ' >> visu_cov.gnp
  echo 'plot \' >> visu_cov.gnp
  echo '  "cov_zz.csv" w p pt 7 lc rgb "red" title "mean(z*z)-mean(z)*mean(z)", \' >> visu_cov.gnp
  echo '  "mean_zz.csv" w p pt 6 lc rgb "blue"  title "mean(z*z)"  ' >> visu_cov.gnp
  echo '   ' >> visu_cov.gnp
  echo 'set output "cov_xy.png" ' >> visu_cov.gnp
  echo 'plot \' >> visu_cov.gnp
  echo '  "cov_xy.csv" w p pt 7 lc rgb "red"  title "mean(x*y)-mean(x)*mean(y)", \' >> visu_cov.gnp
  echo '  "mean_xy.csv" w p pt 6 lc rgb "blue" title "mean(x*y)" ' >> visu_cov.gnp
  echo ' ' >> visu_cov.gnp
  echo 'set output "cov_yz.png" ' >> visu_cov.gnp
  echo 'plot \' >> visu_cov.gnp
  echo '  "cov_yz.csv" w p pt 7 lc rgb "red"  title "mean(y*z)-mean(y)*mean(z)", \' >> visu_cov.gnp
  echo '  "mean_yz.csv" w p pt 6 lc rgb "blue" title "mean(y*z)" ' >> visu_cov.gnp
  echo '   ' >> visu_cov.gnp
  echo 'set output "cov_zx.png" ' >> visu_cov.gnp
  echo 'plot \' >> visu_cov.gnp
  echo '  "cov_zx.csv" w p pt 7 lc rgb "red"  title "mean(z*x)-mean(z)*mean(x)", \' >> visu_cov.gnp
  echo '  "mean_zx.csv" w p pt 6 lc rgb "blue"  title "mean(z*x)"  ' >> visu_cov.gnp
  echo '  ' >> visu_cov.gnp
  
  gnuplot visu_cov.gnp
  
  \cp PIV_new_covInv_U*.png ..
  \cp Inv_COVxy.* ..
  \cp visu_cov.gnp ..
  \cp cov*.png ..
  \cp cov*.csv ..
  \cp mean*.csv ..
          
  cd ${dir_ici}
  
  echo ""; echo "Cf. cov_after_gaussSmoothing/*.png (in ${dir_work})"; echo ""
 
end

#------------------------------------------------------------------------------
