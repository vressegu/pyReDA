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
#  ------------------------------------------------------------------------------

# Instructions to install useful tools for running
# Cshell [openfoamDNS_to_pseudoPIV_all_VR.csh] script

# OS tested : Ubuntu 18.04 and 20.04 

#  ------------------------------------------------------------------------------

### updating installed packages ###

sudo apt-get update


### Cshell environment (after installing tcsh) ###

if (!(-e ~/.cshrc)) touch  ~/.cshrc

### linux tools ###

set All_Package = ( \
  gawk \
  sed \
  gnuplot \
  coreutils \
  ffmpeg \
  mencoder \
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

## paraview 5.10.1 installation ##

cd  ~

wget https://www.paraview.org/paraview-downloads/download.php\?submit=Download\&version=v5.10\&type=binary\&os=Linux\&downloadFile=ParaView-5.10.1-MPI-Linux-Python3.9-x86_64.tar.gz

sudo \mv download.php\?submit=Download\&version=v5.10\&type=binary\&os=Linux\&downloadFile=ParaView-5.10.1-MPI-Linux-Python3.9-x86_64.tar.gz /usr/local/ParaView-5.10.1-MPI-Linux-Python3.9-x86_64.tar.gz
cd /usr/local
sudo tar xvfz ParaView-5.10.1-MPI-Linux-Python3.9-x86_64.tar.gz
sudo chmod ugo+rX -R ParaView-5.10.1-MPI-Linux-Python3.9-x86_64
  
## updating ressource files ##

cd ~
echo "" 
echo "------ [.cshrc] : --------" 
echo ""
echo "setenv DIR_PARAVIEW /usr/local/ParaView-5.10.1-MPI-Linux-Python3.9-x86_64" >> ~/.cshrc
echo '  setenv PATH ${PATH}:${DIR_PARAVIEW}/bin:${DIR_PARAVIEW}/lib' >> ~/.cshrc
echo '  setenv LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:${DIR_PARAVIEW}/lib' >> ~/.cshrc
echo '  alias paraview '"'"'${DIR_PARAVIEW}/bin/paraview'"'" >> ~/.cshrc
echo '  alias pvbatch  '"'"'${DIR_PARAVIEW}/bin/pvbatch'"'" >> ~/.cshrc
echo ""
echo "" 
echo "------ [.bashrc] : --------" 
echo ""
echo "export DIR_PARAVIEW=/usr/local/ParaView-5.10.1-MPI-Linux-Python3.9-x86_64" >> ~/.bashrc
echo '  export PATH=${PATH}:${DIR_PARAVIEW}/bin:${DIR_PARAVIEW}/lib' >> ~/.bashrc
echo '  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${DIR_PARAVIEW}/lib' >> ~/.bashrc
echo '  alias paraview='"'"'${DIR_PARAVIEW}/bin/paraview'"'" >> ~/.bashrc
echo '  alias pvbatch='"'"'${DIR_PARAVIEW}/bin/pvbatch'"'" >> ~/.bashrc
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
  
  cd ~
  echo "" 
  echo "------ [.cshrc] : --------" 
  echo ""
  echo 'alias paraFoam '"'"/usr/lib/openfoam/openfoam2106/bin/paraFoam"'" >> ~/.cshrc
  echo "" 
  echo "------ [.bashrc] : --------" 
  echo ""
  echo 'alias paraFoam='"'"/usr/lib/openfoam/openfoam2106/bin/paraFoam"'" >> ~/.bashrc
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

  cd ~
  echo "" 
  echo "------ [.cshrc] : --------" 
  echo ""
  echo 'alias paraFoam '"'"/usr/local/OpenFOAM-v2106/bin/paraFoam"'" >> ~/.cshrc
  echo "" 
  echo "------ [.bashrc] : --------" 
  echo ""
  echo 'alias paraFoam='"'"/usr/local/OpenFOAM-v2106/bin/paraFoam"'" >> ~/.bashrc
  echo ""
  
endif

#  ------------------------------------------------------------------------------

