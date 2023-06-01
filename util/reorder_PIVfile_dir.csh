#!/bin/tcsh
#
#
# Laurence Wallian - ACTA - OPAALE - INRAE Rennes - Aout 2022 - Juin 2023
#
#------------------------------------------------------------------------------
#
# MORAANE : reordering PIV file : x increasing while y decreases
#
#  x0 yn ...
#  x1 yn ...
#  ...  yn ...
#  xn yn ...
#  ... ... ...
#  x0 y0 ...
#  x1 y0 ...
#  ...  y0 ...
#  xn y0 ...
#
#------------------------------------------------------------------------------
#
# input variables :  
#
#    arg1 = upper directory for B0001_new.dat and Inv_COVxy.dat files
#                   (recursively searched in this upper directory)
#
#      command example : tcsh reorder_PIVfile_dir.csh /workspace/MORAANE/exemple_openfoam
#
#      by default, this upper directory is defined from parameter in run_info.txt :
#         upper directory is as [PATH_openfoam_data]/[type_data_C]
# 
#    arg2 = sub-directory
#
#      command example : tcsh reorder_PIVfile_dir.csh /workspace/MORAANE/exemple_openfoam FakePIV_noise2
#
#      by default, sub-directory concerned  are all 
#         - FakePIV_noise directory
#         - ROM_PIV directory include in [redlumcpp_code_version] run_info.txt parameter
#
#------------------------------------------------------------------------------

set dir_ici = ` pwd `

# first input argument : upper directory (for example /workspace/MORAANE/exemple_openfoam )

if ( $1 == "" ) then
  set dir_up = ${dir_ici}
  if -e run_info.txt then
    set dir0 = ` cat run_info.txt | grep -v "#" | grep "PATH_openfoam_data" | awk '{ print $2 }' | tail -1 `
    set dir1 = ` cat run_info.txt | grep -v "#" | grep "type_data_C" | awk '{ print $2 }' | tail -1 `
    set dir_up = ( ${dir0}/${dir1} )
  endif
else
  set dir_up = $1
endif

echo ${dir_up}

# second input argument : sub-directory (for example FakePIV_noise2 ...)

if ( $2 == "" ) then
  set sub_dir_FakePIV = ` find ${dir_up} -name "FakePIV_noise*" `
  set sub_dir_ROM = ` find ${dir_up} -name "ROM_PIV" `
  if -e run_info.txt then
    set dir2 = ` cat run_info.txt | grep -v "#" | grep "redlumcpp_code_version" | awk '{ print $2 }' | tail -1 `
    set sub_dir_ROM = ${dir_up}/${dir2}/ROM_PIV
  endif
  set sub_dir = ( ${sub_dir_FakePIV} ${sub_dir_ROM} )
else
  set sub_dir = ( ${dir_up}/$2 )
endif

echo ""
echo "----------------------------------------------------------------------"
echo "--- PIV files ar searched in following directories : ---"
echo ""
echo ${sub_dir} | sed s/" "/"\n"/g
echo ""
echo "----------------------------------------------------------------------"
echo ""

#------------------------------------------------------------------------------

set All_file = ()
set All_name_file = ( B0001_new.dat Inv_COVxy.dat )
foreach f ( ${All_name_file} )
  set A = ` find ${sub_dir} -name ${f} `
  set All_file = ( ${All_file} ${A} )
end

foreach fic ( ${All_file} )

  set fic_base = ` echo ${fic} | awk -F'.' '{ N=NF-1; for (i=1;i<N;i++) printf("%s.", $i); print $N }' `
  set fic_ext = ` echo ${fic} | awk -F'.' '{ N=NF; print $N }' `
  set fic_old = ${fic_base}_old.${fic_ext}

  ### reordering file ###

  \mv ${fic} ${fic_old}

  if -e All_PIV_x.txt \rm All_PIV_x.txt
  cat ${fic_old} | grep -v "#" | \
    awk '{ x=$1+0. ; if (NF!=0) printf("%.0f\n", 1000000.*x) }' | sort -n  | uniq | \
    awk '{ x=$1+0. ; printf("%.6f\n",x/1000000.)}' > All_PIV_x.txt
  #set All_PIV_yinv = ` cat All_PIV_x.txt | sed s/"-"/"\\-"/g`
  set All_PIV_x = ` cat All_PIV_x.txt `

  if -e All_PIV_yinv.txt \rm All_PIV_yinv.txt
  cat ${fic_old} | grep -v "#" | \
    awk '{ x=$2+0. ; if (NF!=0) printf("%.0f\n", 1000000.*x) }' | sort -n -r  | uniq | \
    awk '{ x=$1+0. ; printf("%.6f\n",x/1000000.)}' > All_PIV_yinv.txt
  set All_PIV_yinv = ` cat All_PIV_yinv.txt `

  set dx_max = ` echo ${All_PIV_x} | sort -n | awk '{ d=$NF-$1; d=sqrt(d*d); print d }' `

  if -e tmp.txt \rm tmp.txt
  cat ${fic_old} | grep "#" > tmp.txt
  cat ${fic_old} | grep "TITLE" >> tmp.txt
  cat ${fic_old} | grep "VARIABLE" >> tmp.txt
  cat ${fic_old} | grep "ZONE" >> tmp.txt
  cat ${fic_old} | grep "STRANDID" >> tmp.txt
  cat tmp.txt | uniq > ${fic}
  
  if -e tmp.txt \rm tmp.txt
  cat ${fic_old} | \
    grep -v "#" | \
    grep -v "TITLE" | \
    grep -v "VARIABLE" | \
    grep -v "ZONE" | \
    grep -v "STANDID" | \
    awk '{ for (i=1; i<=NF; i++) printf("%s ",$i); print "" }' > tmp.txt
  foreach y ( ${All_PIV_yinv} )
    cat tmp.txt | awk -v y=${y} -v dx_max=${dx_max} '{ if ($2==y) print $1+dx_max, $0 }' | sort -n | uniq | \
    awk '{ for (i=2;i<NF; i++) printf("%s ",$i); print $NF }' >> ${fic}
  end

  ### visu gnuplot ###

  set code_visu = 0
  if ( ${code_visu} == 1 ) then

    set fic_gnp = reorder_PIVfile.gnp
    if -e ${fic_gnp} \rm ${fic_gnp}; touch ${fic_gnp}

    echo 'set grid' >> ${fic_gnp}
    echo 'set size ratio -1' >> ${fic_gnp}
    echo 'set key box outside center bottom horizontal maxcols 5 maxrows 5' >> ${fic_gnp}
    echo 'set title "reordering PIV file)" noenhanced' >> ${fic_gnp}
    echo 'set terminal png crop size 1000,1000 font "LiberationSans-Regular,18  noenhanced' >> ${fic_gnp}
    echo 'set palette color' >> ${fic_gnp}
    echo 'set palette model RGB' >> ${fic_gnp}
    echo 'set palette rgbformulae 33,13,10' >> ${fic_gnp}
    echo "set palette defined (0 'dark-violet', 1 'blue', 2 'green', 3 'yellow', 4 'red', 5 'brown', 6 'magenta', 7 'pink')" >> ${fic_gnp}

    set N = ` cat  ${fic_old} | grep -v "#" | wc -l `
    if -e tmp1.txt \rm tmp1.txt
    cat ${fic_old} | grep -v "#" | awk -v N=${N} '{ x=$1; y=$2; z=sqrt(x*x); if (z>0.000001) z=x/z; else z=1;  z=z*(NR+0.)/(N+0.); print x, y, z }' > tmp1.txt

    if -e tmp2.txt \rm tmp2.txt
    cat ${fic} | grep -v "#" | awk -v N=${N} '{ x=$1; y=$2; z=sqrt(x*x); if (z>0.000001) z=x/z; else z=1; z=z*(NR+0.)/(N+0.); print x, y, z }' > tmp2.txt
    
    echo 'set cbrange [-1:1]' >> ${fic_gnp}
    echo 'set terminal png crop size 1500,1500 font "LiberationSans-Regular,18  noenhanced' >> ${fic_gnp}

    echo 'set output "reorder_PIVfile_old.png"' >> ${fic_gnp}
    echo 'plot "tmp1.txt" u 1:2:3 w p pt 5 ps 1 palette title "old order"' >> ${fic_gnp}
    echo 'set output "reorder_PIVfile_new.png"' >> ${fic_gnp}
    echo 'plot "tmp2.txt" u 1:2:3 w p pt 5 ps 1 palette title "new order"' >> ${fic_gnp}

    if -e tmp1.txt \rm tmp1.txt
    cat ${fic_old} | grep -v "#" | \
      awk -v dx_max=${dx_max} 'BEGIN{c=0;}{ \
        x=$1; y=$2; dx=x-x0; dx=sqrt(dx*dx); if (NR>1) {dy=y-y0; dy=sqrt(dy*dy); c=0; }  \
        if ((dx>dx_max/100.) && (dy<=0.000001)) c=1; print x,y,c; x0=x; y0=y; \
      }' > tmp1.txt

    if -e tmp2.txt \rm tmp2.txt
    cat ${fic} | grep -v "#" | \
      awk -v dx_max=${dx_max} 'BEGIN{c=0}{ \
        x=$1; y=$2; dx=x-x0; dx=sqrt(dx*dx); if (NR>1) {dy=y-y0; dy=sqrt(dy*dy); c=0; } \
        if ((dx>dx_max/100.) && (dy<=0.000001)) c=1; print x,y,c; x0=x; y0=y; \
      }' > tmp2.txt

    echo "set palette defined (0 'blue', 1 'red')" >> ${fic_gnp}

    echo 'set cbrange [0:1]' >> ${fic_gnp}
    echo 'set terminal png crop size 1500,1500 font "LiberationSans-Regular,18  noenhanced' >> ${fic_gnp}

    echo 'set output "reorder_PIVfile_old.png"' >> ${fic_gnp}
    echo 'plot "tmp1.txt" u 1:2:3 w p pt 1 ps 1 palette title "old order"' >> ${fic_gnp}
    echo 'set output "reorder_PIVfile_new.png"' >> ${fic_gnp}
    echo 'plot "tmp2.txt" u 1:2:3 w p pt 1 ps 1 palette title "new order"' >> ${fic_gnp}

    gnuplot  ${fic_gnp}

    echo ""; echo "Cf. reorder_PIVfile_*.png"; echo ""

  endif
  
  set N_old = ` cat ${fic_old} | wc -l `
  set N = ` cat ${fic} | wc -l `
  set dN = ` echo ${N_old} ${N} | awk '{ d=sqrt(($1-$2)**2); print d }' `
  if ((-e ${fic}) && (${dN} == 0)) then 
    echo ""; echo "Cf. reordered file ${fic}"; echo ""
    \rm ${fic_old}
  else
    echo ""; echo " \!\!\! ERROR reordering ${fic} \!\!\!"; echo ""
  endif
  
end

#------------------------------------------------------------------------------
