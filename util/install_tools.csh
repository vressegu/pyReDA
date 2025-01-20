#!/bin/tcsh
#
# Laurence Wallian - ACTA - OPAALE - INRAE Rennes [Juin 2022 : Février 2023]
#
# update for Ubuntu 22.04 : Janvier 2025
#
# MORAANE project : Scalian - INRAE
#
#  ------------------------------------------------------------------------------
#
# OBJECT : Openfoam DNS file -> synthetic PIV file
#
#  ------------------------------------------------------------------------------

# Instructions to install useful tools for running
# Cshell [openfoamDNS_to_pseudoPIV_all_VR.csh] script

# OS tested : Ubuntu 18.04, 20.04 and 22.04

#  ------------------------------------------------------------------------------

### updating installed packages ###

sudo apt-get update

### Shell environment : updating [.cshrc] and [.bashrc] files ###

## Cshell environment (after installing tcsh) ##
if (!(-e ~/.cshrc)) touch  ~/.cshrc
## Bourne shell environment (after installing bash) ##
if (!(-e ~/.bashrc)) touch  ~/.bashrc

### linux tools ###

set All_Package = ( \
  gawk \
  sed \
  coreutils \
  ffmpeg \
  mencoder \
  imagemagick \
  build-essential \
  libgl1-mesa-dev \
  wget \
)
foreach package ( ${All_Package} )
  echo ""; echo "------ installation package ${package} -----------"; echo ""
  sudo apt-get install ${package}
end


### paraview 5.10.1 ###

## packages used by paraview 5.10.1 ##

# ???? python3 : perhaps not necessary ???? #

set All_Package = ( \
  python3 \
)
foreach package ( ${All_Package} )
  echo ""; echo "------ installation package ${package} -----------"; echo ""
  sudo apt-get install ${package}
end

# Qt 5 #

echo "\n# Qt 5 installation\n"

wget https://download.qt.io/official_releases/qt/5.15/5.15.16/single/qt-everywhere-opensource-src-5.15.16.tar.xz
tar xvfz qt-everywhere-opensource-src-5.15.16.tar.xz
cd qt-everywhere-src-5.15.16/
ls
./configure -prefix /usr/local/Qt/5.15.16 -opensource -confirm-license
make -j8
make install
sudo make install
cd  ~

#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/Qt/5.15.16/lib
setenv LD_LIBRARY_PATH $LD_LIBRARY_PATH:/usr/local/Qt/5.15.16/lib

# gnuplot with Qt 5 #

echo "\n# gnuplot installation\n"

wget https://sourceforge.net/projects/gnuplot/files/gnuplot/5.4.2/gnuplot-5.4.2.tar.gz

tar xvfz gnuplot-5.4.2.tar.gz
cd gnuplot-5.4.2
./configure -prefix=/usr/local
make
sudo make install
cd ~

# test gnuplot
if -e /tmp/test_gnuplot.gnp \rm /tmp/test_gnuplot.gnp
echo "set terminal png" > /tmp/test_gnuplot.gnp
echo 'set output "/tmp/test_gnuplot.png"' >> /tmp/test_gnuplot.gnp
echo 'plot sin(x) w l lc rgb "red" title "test gnuplot : sin(x)" ' >> /tmp/test_gnuplot.gnp
gnuplot /tmp/test_gnuplot.gnp
if (-e /tmp/test_gnuplot.png ) then
  echo "\n  gnuplot OK : Cf. /tmp/test_gnuplot.png\n"
  eog /tmp/test_gnuplot.png
else
  echo "\n  \!\!\! OUPS \! BAD gnuplot installation \!\!\! \n"
  exit()
endif

## updating ressource files ##

set install_tools_date = ` date | awk '{ printf ("# "); for (i=1;i<=NF;i++) printf("%s ",$i); print(" : part added by pyReDA/util/install_tools.csh")}' `

cd ~
echo ""
echo "------ [.cshrc] : --------"
echo ""
echo "\n${install_tools_date}" >> ~/.cshrc
echo 'setenv LD_LIBRARY_PATH $LD_LIBRARY_PATH:/usr/local/Qt/5.15.16/lib' >> ~/.cshrc
echo 'alias gnuplot '"'"'/usr/local/gnuplot \!*'"'" >> ~/.cshrc
tail -4 ~/.cshrc
echo ""
echo "------ [.bashrc] : --------"
echo ""
echo "\n${install_tools_date}" >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/Qt/5.15.16/lib' >> ~/.bashrc
echo 'alias gnuplot='"'"'/usr/local/gnuplot \!*'"'" >> ~/.bashrc
tail -4 ~/.bashrc
echo ""

## paraview 5.10.1 installation ##

cd  ~

wget https://www.paraview.org/paraview-downloads/download.php\?submit=Download\&version=v5.10\&type=binary\&os=Linux\&downloadFile=ParaView-5.10.1-MPI-Linux-Python3.9-x86_64.tar.gz

sudo \mv download.php\?submit=Download\&version=v5.10\&type=binary\&os=Linux\&downloadFile=ParaView-5.10.1-MPI-Linux-Python3.9-x86_64.tar.gz /usr/local/ParaView-5.10.1-MPI-Linux-Python3.9-x86_64.tar.gz
cd /usr/local
sudo tar xvfz ParaView-5.10.1-MPI-Linux-Python3.9-x86_64.tar.gz
sudo chmod ugo+rX -R ParaView-5.10.1-MPI-Linux-Python3.9-x86_64
  
## updating ressource files ##

set install_tools_date = ` date | awk '{ printf ("# "); for (i=1;i<=NF;i++) printf("%s ",$i); print(" : part added by pyReDA/util/install_tools.csh")}' `

cd ~
echo "" 
echo ""
echo ""
echo "------ [.cshrc] : --------"
echo ""
echo "\n${install_tools_date}" >> ~/.cshrc
echo "setenv DIR_PARAVIEW /usr/local/ParaView-5.10.1-MPI-Linux-Python3.9-x86_64" >> ~/.cshrc
echo '  setenv PATH ${PATH}:${DIR_PARAVIEW}/bin:${DIR_PARAVIEW}/lib' >> ~/.cshrc
echo '  setenv LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:${DIR_PARAVIEW}/lib' >> ~/.cshrc
echo '  alias paraview '"'"'${DIR_PARAVIEW}/bin/paraview'"'" >> ~/.cshrc
echo '  alias parafoam '"'"'touch log.foam; ${DIR_PARAVIEW}/bin/paraview log.foam'"'" >> ~/.cshrc
echo '  alias pvbatch  '"'"'${DIR_PARAVIEW}/bin/pvbatch'"'" >> ~/.cshrc
tail -7 ~/.cshrc
echo ""
echo "" 
echo "------ [.bashrc] : --------" 
echo ""
echo "\n${install_tools_date}" >> ~/.bashrc
echo "export DIR_PARAVIEW=/usr/local/ParaView-5.10.1-MPI-Linux-Python3.9-x86_64" >> ~/.bashrc
echo '  export PATH=${PATH}:${DIR_PARAVIEW}/bin:${DIR_PARAVIEW}/lib' >> ~/.bashrc
echo '  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${DIR_PARAVIEW}/lib' >> ~/.bashrc
echo '  alias paraview='"'"'${DIR_PARAVIEW}/bin/paraview'"'" >> ~/.bashrc
echo '  alias parafoam='"'"'touch log.foam; ${DIR_PARAVIEW}/bin/paraview log.foam'"'" >> ~/.bashrc
echo '  alias pvbatch='"'"'${DIR_PARAVIEW}/bin/pvbatch'"'" >> ~/.bashrc
tail -7 ~/.bashrc
echo ""
  
## alternative to updating ressource files : aliases defined in script files ##

echo ''
echo 'NOTE : since aliases defined in [.bashrc] (or [.cshrc]) are sometime unrecognized,'
echo '            you should check if [pvbatch alias] are well defined in script files'
echo '              [util/cov_before_gaussSmoothing.csh] and'
echo '              [util/openfoamDNS_to_pseudoPIV.csh]'
echo ''

### openfoam tested : 2106 ( !!! always installed after paraview !!!) ###

# NOTE : should work with 2206 and 2212 releases too

## packages used by openfoam 2106 ##

cd  ~

set All_Package = ( \
  build-essential \
  autoconf \
  autotools-dev \
  cmake \
  flex \
  libfl-dev \
  libreadline-dev\
  zlib1g-dev\
  openmpi-bin \
  libopenmpi-dev \
  mpi-default-bin \
  mpi-default-dev \
  libgmp-dev \
  libmpfr-dev \
  libmpc-dev \
  libfftw3-dev \
  libscotch-dev \
  libptscotch-dev \
  libboost-system-dev \
  libboost-thread-dev \
  libcgal-dev \
)
foreach package ( ${All_Package} )
  echo ""; echo "------ installation package ${package} -----------"; echo ""
  sudo apt-get install ${package}
end

set All_Package = ( \
  libopenmpi-dev \
)
foreach package ( ${All_Package} )
  echo ""; echo "------ package ${package} -----------"; echo ""
  sudo apt-cache show ${package}
end

## openfoam 2106 installation : ##
##        binary (easiest way) or 
##        source package (useful when you have to modify the code) 

cd  ~

set choix = binary
if ( ${choix} == "binary" ) then

  # adding repository
  
  curl https://dl.openfoam.com/add-debian-repo.sh | sudo bash
  
  # installing openfoam2106
  
  sudo apt-get install openfoam2106-default
  
  # updating ressource files
  
  set install_tools_date = ` date | awk '{ printf ("# "); for (i=1;i<=NF;i++) printf("%s ",$i); print(" : part added by pyReDA/util/install_tools.csh")}' `

  cd ~
  echo "" 
  echo "------ [.cshrc] : --------" 
  echo ""
  echo "\n${install_tools_date}" >> ~/.cshrc
  echo 'alias paraFoam '"'"/usr/lib/openfoam/openfoam2106/bin/paraFoam"'" >> ~/.cshrc
  tail -3 ~/.cshrc
  echo ""
  echo "------ [.bashrc] : --------" 
  echo ""
  echo "\n${install_tools_date}" >> ~/.bashrc
  echo 'alias paraFoam='"'"/usr/lib/openfoam/openfoam2106/bin/paraFoam"'" >> ~/.bashrc
  tail -3 ~/.bashrc
  echo ""
  
else
  
  # loading openfoam2106 source and moving it to /usr/local
  
  wget https://dl.openfoam.com/source/v2106/OpenFOAM-v2106.tgz
  sudo \mv OpenFOAM-v2106.tgz /usr/local
  
  # installing openfoam2106
  
  cd /usr/local
  sudo tar xvfz OpenFOAM-v2106.tgz
  bash
  cd OpenFOAM-v2106
  source etc/bashrc
  foamSystemCheck
  foam
  wmake -help
  NbCpus=4 # =4 for parallel use on 4 Cpus
  sudo ./Allwmake -s -l  -j ${NbCpus}
  # sudo ./Allwmake -s -l  -j ${NbCpus} -k # if not taking into account compilation errors ...
  
  # updating ressource files

  set install_tools_date = ` date | awk '{ printf ("# "); for (i=1;i<=NF;i++) printf("%s ",$i); print(" : part added by pyReDA/util/install_tools.csh")}' `

  cd ~
  echo "" 
  echo "------ [.cshrc] : --------" 
  echo ""
  echo "\n${install_tools_date}" >> ~/.cshrc
  echo 'alias paraFoam '"'"/usr/local/OpenFOAM-v2106/bin/paraFoam"'" >> ~/.cshrc
  tail -3 ~/.cshrc
  echo ""
  echo "------ [.bashrc] : --------" 
  echo ""
  echo "\n${install_tools_date}" >> ~/.bashrc
  echo 'alias paraFoam='"'"/usr/local/OpenFOAM-v2106/bin/paraFoam"'" >> ~/.bashrc
  tail -3 ~/.bashrc
  echo ""
  
endif

echo "\nCf. ressource files [.cshrc] and [.bashrc] for new aliases :"
echo "  - gnuplot"
echo "  - paraview"
echo "  - parafoam and pvbatch = f(paraview)"
echo "  - paraFoam = f(OpenFOAM)\n"

#  ------------------------------------------------------------------------------

