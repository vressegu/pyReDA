Laurence Wallian - ACTA - OPAALE - INRAE Rennes [Juin 2022 : Février 2023]

MORAANE project : Scalian - INRAE

------------------------------------------------------------------------------

main shell script [openfoamDNS_to_pseudoPIV_all.csh] : 

  it creates synthetic PIV file from 2 types of input file

  1) Raw result of Openfoam DNS simulation : 
  
      - the input files are all located in [.../openfoam_data] directory
      - the output files are all located in [.../FakePIV_noise...] directory
        for example : 
          input = RedLUM/data_red_lum_cpp/DNS300-D1_Lz1pi/openfoam_data
          output = RedLUM/data_red_lum_cpp/DNS300-D1_Lz1pi/FakePIV_noise2 when noise_MAX=2
      
      this kind of data is named [DNS] in the script [openfoamDNS_to_pseudoPIV_all.csh]
  
  2) Result of ROM applied on Openfoam DNS simulation data :
  
      - the input files are all located in [.../ROM-v...] subdirectories
      - the output files are all located in the run script directory
        for example : 
          input = RedLUM/data_red_lum_cpp/DNS300-D1_Lz1pi/ROM-v1/ITHACAoutput/mean
          output = RedLUM/data_red_lum_cpp/DNS300-D1_Lz1pi/ROM-v1/ROM_PIV/mean
     
      this kind of data is named [ROM] in the script [openfoamDNS_to_pseudoPIV_all.csh]
        
  NOTE : here, DNS is a generic word for "Numerical Simulation"
      
        tree example :
        ├── data_red_lum_cpp
        │    ├── DNS300-D1_Lz1pi
        │    │    ├── FakePIV_noise2
        │    │    ├── openfoam_data
        │    │    │    ├── 0
        │    │    │    .......
        │    │    │    ├── 800
        │    │    │    ├── constant
        │    │    │    └── system
        │    │    ├── ROM-v1
        │    │    │    ├── 0
        │    │    │    ├── constant
        │    │    │    ├── ITHACAoutput
        │    │    │    ├── ROM_PIV
        │    │    │    │    ├── mean
        │    │    │    │    ├── residualSpeed_2
        │    │    │    │    └── spatialModes_2modes
        │    │    │    └── system
        │    │    └── util
        │    │          ├── DNS_info.txt
        │    │          ├── DNS_to_FakePIV_info.txt
        │    │          └── PIV_info.txt
        └──podfs2
             ├── run_info.txt
             └── util
                   ├── calculator_PointVolumeInterpolation_model.py
                   ├── cov_before_gaussSmoothing.csh
                   ├── cov_before_gaussSmoothing_model.py
                   ├── dim_DNS_cyl.csh
                   ├── openfoamDNS_to_pseudoPIV_param.txt
                   └── openfoamDNS_to_pseudoPIV.csh

------------------------------------------------------------------------------

HOW to have the script RUNNING

1) The script [openfoamDNS_to_pseudoPIV_all.csh] can work without input arguments :

  command = tcsh openfoamDNS_to_pseudoPIV_all.csh
  
  however, the USER is always prompted to valid (or choose another value) for two parameters :
  
    1.a) the PATH for [run_info.txt] file
    1.b) the PATH for [util] directory 
      
      tree example :
      ├── data_red_lum_cpp
      │    └── DNS300-D1_Lz1pi
      └──podfs2
           ├── run_info.txt
           └── util
  
2) It can also have three optional arguments (Cf. below [WHAT CAN be MODIFIED by the USER]) :

  2.a) arg1 = Zslice value (ex : tcsh tcsh openfoamDNS_to_pseudoPIV_all.csh 2.45)
  2.b) arg2 = Case type ( ex : tcsh tcsh openfoamDNS_to_pseudoPIV_all.csh 1.6 DNS)
  2.c) arg3 = ROM type ( ex : tcsh tcsh openfoamDNS_to_pseudoPIV_all.csh 1.6 ROM mean)

------------------------------------------------------------------------------

WHAT CAN be MODIFIED by the USER in (*) [openfoamDNS_to_pseudoPIV_all.csh] :

(*) or during RUNNING [openfoamDNS_to_pseudoPIV_all.csh] 

1) parameters that define the input datas (DNS simulation, or ROM) used :

  1.a) [dir_RedLUM] : be default a directory which includes a [podfs2] directory
  1.b) [fic_run_info] : by default fic_run_info=dir_RedLUM/podfs2/run_info.txt
  
  NOTEa : the script prompts the USER to valid or to choose another [fic_run_info] 
  
  NOTEb : the [util] directory is by default in the same directory as [fic_run_info]
                the script prompts the USER to valid or to choose another [util] directory
      
      tree example :
      ├── data_red_lum_cpp
      │    └── DNS300-D1_Lz1pi
      └──podfs2
           ├── run_info.txt
           └── util

2) parameters that define the synthetic PIV from DNS :

  2.a) Z position of the slice for pseudoPIV 
         by default Zslice=1 : this parameter is the first command line argument
         
         for example :
         
          [tcsh openfoamDNS_to_pseudoPIV_all.csh 2.3] means 
            - Zlice=2.3

3) parameters that define case types : FakePIV or ROM_PIV and ROM folders :

  3.a) parameters that define case types : FakePIV or ROM_PIV 
         by default, All_CASE=("DNS" "ROM") : it can be modified by the second command line argument
         
         for example :
         
          [tcsh openfoamDNS_to_pseudoPIV_all.csh 2.3 ROMppp] means
            - Zlice=2.3
            - only ROM_PIV is concerned
            
          [tcsh openfoamDNS_to_pseudoPIV_all.csh 2.3 ROM---DNS] means
            - Zlice=2.3
            - FakePIV and ROM_PIV are concerned

          [tcsh openfoamDNS_to_pseudoPIV_all.csh 2.3 aaDNS] means
            - Zlice=2.3
            - only FakePIV is concerned
          
          WARNING : the second argument musn't have BLANK characters : 
              the following expressions don't work :
              - [tcsh openfoamDNS_to_pseudoPIV_all.csh 2.3 DNS ROM]
              - [tcsh openfoamDNS_to_pseudoPIV_all.csh 2.3 "DNS ROM"]
          
  3.b) the subdirectories in the case of ROM_PIV
          by default, all subdirectories [mean], [spatialModes_...] and [residualSpeed_...] are used :
          it can be modified by the third command line argument
         
         for example :
         
          [tcsh openfoamDNS_to_pseudoPIV_all.csh 2.3 ROMppp mean] means
            - Zlice=2.3
            - only ROM_PIV is concerned
            - only mean is concerned
  
          WARNING : the third argument musn't have BLANK characters and must correspond to an existant directory : 
              the following expressions don't work :
              - [tcsh openfoamDNS_to_pseudoPIV_all.csh 2.3 ROM mean_ppp] means
              - [tcsh openfoamDNS_to_pseudoPIV_all.csh 2.3 ROM spatialModes_567] means
                 
4) for preleminary tests, it can also be useful to modify time [t_first] and [t_last] 

  4.a) when the subdirectory=[residualSpeed_...] in case of ROM datas
  4.b) when the input datas is raw DNS simulation (directory [.../openfoam_data...])        

------------------------------------------------------------------------------

FILE or DIRECTORY that must be present in the run script directory :

1) The shell script file [openfoamDNS_to_pseudoPIV_all.csh] 
     that can be modified by the user

FILE or DIRECTORY that must be accessible by the run script directory :

1) The [util] directory which contains files used by [openfoamDNS_to_pseudoPIV_all.csh] : 
     the user doesn't have to modify files in this directory

------------------------------------------------------------------------------

DIRECTORY where RESULTS are created :

All directories from the script [openfoamDNS_to_pseudoPIV_all.csh]
are created relatively to informations from the [run_info.txt] file : 

  the upper directory DIR0 depends of case type

    - for Fake PIV from OpenFoam DNS, DIR0 is defined by [PATH_openfoam_data]
      and [type_data_C] parameters : DIR0=PATH_openfoam_data/type_data_C.
      in this case, results are saved DIR0/FakePIV_noise...
 
        tree example :
        ├── data_red_lum_cpp
        │    ├── DNS300-D1_Lz1pi
        │    │    ├── FakePIV_noise2
        │    │    ├── openfoam_data
      
    - for ROM PIV from ITHACA ROM, the parameter [redlumcpp_code_version] is added :
      DIR0=PATH_openfoam_data/type_data_C/redlumcpp_code_version.
      in this case, results are saved DIR0/ROM_PIV.
      
        tree example :
        ├── data_red_lum_cpp
        │    ├── DNS300-D1_Lz1pi
        │    │    ├── ROM-v1
        │    │    │    ├── ROM_PIV
        │    │    │    │    ├── mean
        │    │    │    │    ├── residualSpeed_2
        │    │    │    │    └── spatialModes_2modes

!!! BE CAREFUL  to have enough memory to save results!!!
!!!    for example, size of some results directories when
!!!        time subdirectories are spaced by dt=0.25 :
!!!        45M	mean : 1 subdirectory (=[1])
!!!        75M	Modes_2modes : 2 subdirectories (=mode [1] and mode [2])
!!!        61G	residualSpeed_2 : 2000  subdirectories (= t=[100] to t=[600])
!!!        11G	openfoam_data : 400  subdirectories (= t=[600] to t=[700])
------------------------------------------------------------------------------

WHAT ERRORS may occur

1) No dimensionless input simulation : 

    in this case, the diameter of the cylinder isn't equal to DNS_Dcyl=1
    
2) Missing files in the [util] directory
       
     - [util/dim_DNS_cyl.csh] :
       shell script to verify the cylinder diameter [DNS_Dcyl] value

     - [util/openfoamDNS_to_pseudoPIV.csh] : 
       this is the script called by the present script [openfoamDNS_to_pseudoPIV_all.csh]
       
     - [util/openfoamDNS_to_pseudoPIV_param.txt] :
       liste of parameters adjusted by the present script [openfoamDNS_to_pseudoPIV_all.csh]
       
     - [util/calculator_PointVolumeInterpolation_model.py] : 
       python script model used by the script [openfoamDNS_to_pseudoPIV.csh]
       
     - [util/cov_before_gaussSmoothing.csh] :
       shell script used to calculated (1/cov) in case of [residualSpeed_...]
       
       NOTE : Eigen library must be installed, for example in [/usr/local] directory as does the script [install\_eigen.csh] :
       
              wget https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.tar.gz
              tar xvfz eigen-3.4.0.tar.gz
              cd eigen-3.4.0
              set source_dir = `pwd` 
              set build_dir = build_eigen
              mkdir ${build_dir}
              cd ${build_dir}
              cmake ${source_dir} -DCMAKE_INSTALL_PREFIX=/usr/local
              sudo make install
              cd ..
              sudo chmod ugo+rX -R /usr/local/include/eigen3
     - [util/cov_before_gaussSmoothing_model.py]
       python script model used by the script [cov_before_gaussSmoothing.csh]
        
        tree example :
        ├── data_red_lum_cpp
        │    └── DNS300-D1_Lz1pi
        └──podfs2
             ├── run_info.txt
             └── util
                   ├── calculator_PointVolumeInterpolation_model.py
                   ├── cov_before_gaussSmoothing.csh
                   ├── cov_before_gaussSmoothing_model.py
                   ├── dim_DNS_cyl.csh
                   ├── openfoamDNS_to_pseudoPIV_param.txt
                   └── openfoamDNS_to_pseudoPIV.csh
    
3) Missing files in the input upper DNS directory containing the following folders (*)

      - openfoam_data : raw DNS openfoam simulation
      - ROM-v... : ROM results
    
      (*) for example upper DNS directory=[data_red_lum_cpp/DNS300-GeoLES3900]
      
    this upper directory must also include a [util] directory 
    with at least the 3 following files inside :
    
      - [util/DNS_info.txt] for DNS characteristics
      - [util/PIV_info.txt] for PIV characteristics
      - [util/DNS_to_FakePIV_info.txt] for transformation DNS to pseudo PIV
        
        tree example :
        ├── data_red_lum_cpp
        │    ├── DNS300-D1_Lz1pi
        │    │    └── util
        │    │          ├── DNS_info.txt
        │    │          ├── DNS_to_FakePIV_info.txt
        │    │          └── PIV_info.txt
        
        NOTES concerning [util/DNS_info.txt] 
        
            NOTE 1 : this file must at least contain values for DNS_xcyl, DNS_ycyl and DNS_Dcyl; other
                           parameters will be redefined by the script [openfoamDNS_to_pseudoPIV_all_CR.csh] 
                           from openfoam_data files [constant/polyMesh/points], [constant/transportProperties] 
                           and [system/controlDict] 

            NOTE 2 : the script [dim_DNS_cyl.csh] uses this file to compare [DNS_Dcyl] value with
                           the value extracted from geometry (in [constant/polyMesh/points] file)
                           - if the two values are different, there is an ERROR
                           - if DNS_Dcyl!=1, the openfoam result is not dimensionless !

------------------------------------------------------------------------------

SUMMARY of the method used :

1) Paraview operation (pvbatch [python file]) is used to generate CSV file

 step1 = calculator -> Ux(y) scalar
 step2 = Ux(y) gaussian interpolation on bounded box
 step3 = slice Z=1 (or Lz/2) of the Ux(y) gaussian interpolation
 
           => CSV file

2) Next operation (tcsh [shell script]) generates synthetic PIV file from CSV file

 step1 = rewritting with column IsValid
 step2 = adding noise for data type [CASE_DNS] 
 step3 = dimentionless PIV for data type [CASE_ROM] 

           => synthetic PIV file

NOTE : PNG files are created either by [pvbatch], or by [gnuplot], 
            and are merged in a single [Uxy.png] file to show successive operations

------------------------------------------------------------------------------
