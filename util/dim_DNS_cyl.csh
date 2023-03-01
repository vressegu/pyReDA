#!/bin/tcsh
#
#
# Laurence Wallian - ACTA - OPAALE - INRAE Rennes [Juin 2022 : Janvier 2023]
#
#------------------------------------------------------------------------------
#
# MORAANE : Openfoam DNS file -> cylinder diameter
#
#------------------------------------------------------------------------------
#
# script usage :
#    tcsh dim_DNS_cyl.csh name_dir : name_dir = directory where to find file [constant/polyMesh/points] 
#
# script usage example :
#    1) without INPUT parameter -> name_dir = present directory
#       tcsh dim_DNS_cyl.csh 
#
#    2) with INPUT parameter = name_dir
#      tcsh dim_DNS_cyl.csh /media/laurence.wallian/Val4To/RedLUM/data_red_lum_cpp/DNS300-GeoLES3900
#      tcsh dim_DNS_cyl.csh /media/laurence.wallian/Val4To/RedLUM/data_red_lum_cpp/DNS300-D1_Lz1pi
#      tcsh dim_DNS_cyl.csh /media/laurence.wallian/Val4To/RedLUM/data_red_lum_cpp/DNS300-Dsqrt2_Lz1pi
#
#------------------------------------------------------------------------------
#
# NOTE: file [util/DNS_info.txt] must be present in [name_dir] : 
#             3 parameters are used : cylinder center : (DNS_xcyl,DNS_ycyl) 
#                                                    cylinder diameter : DNS_Dcyl
#
#            the script [dim_DNS_cyl.csh] uses this file to compare [DNS_Dcyl] value with
#            the value extracted from geometry (in [constant/polyMesh/points] file), by considering that
#            points on a cylinder Zslice must be the nearest points to cylinder center : (DNS_xcyl,DNS_ycyl) 
#                         - if the two values are different, there is an ERROR
#                         - if DNS_Dcyl!=1, the openfoam test is not dimensionless !
#------------------------------------------------------------------------------

set dir_ici = `pwd `

#------------------------------------------------------------------------------

set dir_P = ${dir_ici}
if ( $1 != "" ) set dir_P = $1

echo ""
echo "Directory used = [${dir_P}]"
echo ""

#------------------------------------------------------------------------------

set All_fic_points = ()
set N=0
echo ""
echo "List of file [.../constant/polyMesh/points] found"
set All_sub_dir = ( FakePIV 	openfoam_data  ROMDNS )
foreach sub_dir ( ${All_sub_dir} )
  set sub_dir_name = ` ls ${dir_P} | grep ${sub_dir} | head -1 ` 
  if ( ( ${dir_P}/${sub_dir_name} != "" ) && ( -f ${dir_P}/${sub_dir_name}/constant/polyMesh/points )) then
    set fic_points = ${dir_P}/${sub_dir_name}/constant/polyMesh/points
    set All_fic_points = ( ${All_fic_points} ${fic_points} )
    set N = ` echo ${N} | awk '{ print $1+1 }' `
    echo "  ${N} : file [${fic_points}]"
  endif
end

echo ""
if ( ${N} != "" ) then
  echo "${N} file(s) [.../constant/polyMesh/points] found => first file used :"
  set fic_P = ` echo  ${All_fic_points} | awk '{ print $1 }' ` 
  echo "  -> [${fic_P}]"
else
  echo ""
  echo "\!\!\! No file [.../constant/polyMesh/points] found => searching in present directory \!\!\!"
  echo ""
  if -e constant/polyMesh/points then
    set fic_P = constant/polyMesh/points
    echo "file [constant/polyMesh/points] found"
  else
    echo ""
    echo "\!\!\! No file [constant/polyMesh/points] found \!\!\!"
    echo ""
  endif
endif

#------------------------------------------------------------------------------

set z1 = ` cat ${fic_P} | grep ")" | grep "(" | sed s/"("//g | sed s/")"//g | awk '{ printf("%.6f\n", $3) }' | sort -n | uniq | head -1 `
set z2 = ` cat ${fic_P} | grep ")" | grep "(" | sed s/"("//g | sed s/")"//g | awk '{ printf("%.6f\n", $3) }' | sort -n | uniq | tail -1 `
set z0 = ` echo ${z1} ${z2} | awk '{ print ($1+$2+0.)/2. }' `

set z0 = ${z1}

if -e points.txt \rm points.txt
cat ${fic_P} | grep ")" | grep "(" | sed s/"("//g | sed s/")"//g | awk -v z0=${z0} '{ dz=$3-z0+0.; dz=sqrt(dz*dz); if (dz<=0.00001) printf("%.6f %.6f %.6f\n",$1,$2,$3) }' > points.txt

if (-e ${dir_P}/util/DNS_info.txt) then
  set fic_info = ${dir_P}/util/DNS_info.txt
else
  set fic_info = ` find ${dir_P} -name "DNS_info.txt" | head -1 `
  if ( ${fic_info} == "" ) then
    echo ""
    echo "\!\!\! No file [.../DNS_info.txt] found => EXIT \!\!\!"
    echo ""
    exit()
  endif
endif

set x0 = ` cat ${fic_info} | grep DNS_xcyl | awk '{ print $1 }' `
set y0 = ` cat ${fic_info} | grep DNS_ycyl | awk '{ print $1 }' `
set D0 = ` cat ${fic_info} | grep DNS_Dcyl | awk '{ print $1 }' `

echo ""
echo "According to the file [${fic_info}], "
echo "   cylinder center=(${x0},${y0}) and cylinder diameter=${D0}"
echo "These values will be compared to those from the file [${fic_P}] ..."
echo ""

# min radius from (x0,y0)

set D_cyl = ` cat points.txt | \
                        awk -v x0=${x0} -v y0=${y0} -v D0=${D0} '{ \
                          d=2.*sqrt(($1-x0+0.)**2+($2-y0+0.)**2); \
                          if ((d<=2.*D0) && (d>=D0/2.)) print d \
                        }' | sort -n | head -1 | awk -v D0=${D0} '{ dd=sqrt((D0-$1+0.)**2); if ( dd<=0.01 ) print D0; else print $1 }' ` 
                        
set fic_gnp = dim_DNS_cyl.gnp
if -e ${fic_gnp} \rm ${fic_gnp}; touch ${fic_gnp}
echo 'set grid' >> ${fic_gnp}
echo 'set size ratio -1' >> ${fic_gnp}
echo 'set key box outside center bottom horizontal maxcols 5 maxrows 5' >> ${fic_gnp}
echo 'set title "pvbatch on openfoam datas : grid1 to uniform grid2 (gaussian smoothing)"' >> ${fic_gnp}
echo 'set terminal png crop size 1000,1000 font "LiberationSans-Regular,18  noenhanced' >> ${fic_gnp}
echo 'set palette color' >> ${fic_gnp}
echo 'set palette model RGB' >> ${fic_gnp}

if ( ${D_cyl} != "" ) then

  if -e points_cyl.txt \rm points_cyl.txt               
  cat points.txt | \
                          awk -v x0=${x0} -v y0=${y0} -v D0=${D_cyl} '{ \
                            dd=sqrt( (2.*sqrt(($1-x0+0.)**2+($2-y0+0.)**2)-D0+0)**2); \
                            if (dd<=0.01) print $1,$2 \
                          }' > points_cyl.txt
                          
  echo "x0=${x0}" >> ${fic_gnp}
  echo "y0=${y0}" >> ${fic_gnp}
  echo "D=${D_cyl}" >> ${fic_gnp}
  echo 'set output "dim_DNS_cyl.png"'  >> ${fic_gnp}
  set dd = ` echo ${D0} ${D_cyl} | awk '{ dd=sqrt(($1-$2+0.)**2); if (dd<=0.0001) print 0; else print 1 }' `
  if ( ${dd} == 0 ) then
    echo 'set title "DNS points : OK, cylinder diameter = '${D_cyl}'"'  >> ${fic_gnp}
  else
    echo 'set title "DNS points : OUPS ! cylinder diameter = '${D_cyl}' != '${D0}'"'  >> ${fic_gnp}
  endif
  echo 'plot [x0-D*0.7:x0+D*0.7][y0-D*0.7:y0+D*0.7] \'  >> ${fic_gnp}
  echo '  "points.txt" w p pt 6 ps 1 lc rgb "blue" notitle, \'  >> ${fic_gnp}
  echo '  "points_cyl.txt" w p pt 7 ps 2 lc rgb "red" notitle '  >> ${fic_gnp}

  echo ""
  echo "DNS (${fic_P}) :"
  echo "   => Cylinder diameter = ${D_cyl} (Cf. dim_DNS_cyl.png)"
  echo ""

else

  echo 'set output "dim_DNS_cyl.png"'  >> ${fic_gnp}
  echo 'set title "DNS points => all domain"'  >> ${fic_gnp}
  echo 'plot \'  >> ${fic_gnp}
  echo '  "points.txt" w p pt 6 ps 1 lc rgb "blue" notitle'  >> ${fic_gnp}

  echo ""
  echo "DNS (${fic_P}) :"
  echo "   => Cylinder diameter = UKNOWN (Cf. dim_DNS_cyl.png)"
  echo ""

endif

gnuplot ${fic_gnp}

#------------------------------------------------------------------------------
