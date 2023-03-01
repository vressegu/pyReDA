#! /usr/bin/env bash

#sudo bash Anaconda3-2021.11-Linux-x86_64.sh -u -b -p "/usr/local/anaconda3"
#conda create --name mecflu
#conda activate mecflu
#conda config --env --add channels conda-forge
conda install -y -c anaconda spyder 
conda install -y -c conda-forge matplotlib 
conda install -y -c anaconda numpy 
conda install -y -c anaconda scipy 
conda install -y -c conda-forge hdf5storage 
conda install -y -c anaconda h5py 
conda install -y -c anaconda scikit-learn 
conda install -y -c conda-forge openmp 
conda update --all
