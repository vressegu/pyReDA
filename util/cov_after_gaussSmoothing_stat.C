//
// Laurence Wallian - ACTA - OPAALE - INRAE Rennes [Decembre 2023 - Janvier 2024]
//
// ------------------------------------------------------------------------------
//
// Files read are defined in [file_XYUxyz]
//
//    for example : the file [list_fic_time.txt] created by the script [openfoamDNS_to_pseudoPIV_all.csh]
//    this file is like this :
//       first line : file with  (x,y) coordinates (ex: XYcrop.txt) corresponding to the following U*.txt file name
//       second line and other : file with U value for each time (U5000000.txt U5012500.txt ...)
//
// Example : 
//
//    [list_fic_time.txt]
//       XYcrop.txt
//       U5000000.txt
//       U5012500.txt
//       U5025000.txt
//       ...
//
//    [XYcrop.txt]
//       4.04082 -4.22067
//       4.08815 -4.22067
//       ...
//
//    [U5000000.txt]
//       "Ux" "Uy" "Uz"
//       -2.72815e-05 -5.03747e-05 -7.77155e-06
//       ...
//
// The main file can use 3 input arguments :
//
//    1) file listing [file_XYUxyz]
//    2) number of lines for each files of the listing
//    3) number of times = number of files of the listing
//
// Output files are CSV files :
//
//    A) mean values :
//         [mean_xx.csv] : mean (ux*ux)
//         [mean_yy.csv] : mean (uy*uy)
//         [mean_zz.csv] : mean (uz*uz)
//         [mean_xy.csv] : mean (ux*uy)
//         [mean_yz.csv] : mean (uy*uz)
//         [mean_zx.csv] : mean (uz*ux)
//
//    B) cov values :
//         [cov_xx.csv] : cov (ux*ux) = mean (ux*ux)-mean (ux)*mean (ux)
//         [cov_yy.csv] : cov (uy*uy) = mean (uy*uy)-mean (uy)*mean (uy)
//         [cov_zz.csv] : cov (uz*uz) = mean (uz*uz)-mean (uz)*mean (uz)
//         [cov_xy.csv] : cov (ux*uy) = mean (ux*uy)-mean (ux)*mean (uy)
//         [cov_yz.csv] : cov (uy*uz) = mean (uy*uz)-mean (uy)*mean (uz)
//         [cov_zx.csv] : cov (uz*ux) = mean (uz*ux)-mean (uz)*mean (ux)
//
// ------------------------------------------------------------------------------

#ifdef __GNUC__
#pragma GCC diagnostic ignored "-Wold-style-cast"
#endif

#include <Eigen/Eigen>
#include <unsupported/Eigen/CXX11/Tensor>

#include <iomanip>      
#include <fstream>
#include <iostream>
#include <string>
#include <cmath>

#include <list>
#include <string>

// wait for user press ENTER
void wait_until_char ( )
{
  std::cout << "\n Press ENTER to continue ... ";
  std::cin.get();
}

// io format function for files name
void str_format_io(std::string const& s, int nMax)
{
  int N = (int)s.length();
  if ( nMax > N )
  {
    for (int n=0; n<N; n++) std::cout << s[n];
    for (int n=N; n<nMax; n++) std::cout << " ";
  }
  else
  {
    for (int n=0; n<nMax-3; n++) std::cout << s[n];
    for (int n=nMax-3; n<nMax; n++) std::cout << ".";
  }
}

// parameters from file [simu_info.txt] (this file can be changed by the user)
void stat_from_file( std::string file_list_XYUxyz, int Nrow, int Ntime,  Eigen::MatrixXd& XY, Eigen::MatrixXd& Uxyz)
{
  std::string line1("aaa bbb"), line2("aaa bbb");
  std::string word_read1("bbb"),  word_read2("bbb");
  std::string word_comment("#"), word_XY("XYcrop.txt");
  std::string file_XYUxyz;
  std::ifstream  pt_file_in1, pt_file_in2;
  double read_value=0.;
 
 // Eigen::MatrixXd XYUxyz;
 // XYUxyz.resize(Nrow, Ntime); XYUxyz = Eigen::MatrixXd::Zero(Nrow, Ntime);
 
  XY.resize(Nrow+1,2); XY = Eigen::MatrixXd::Zero(Nrow+1, 2);
  Uxyz.resize(Nrow+1, Ntime*3); Uxyz = Eigen::MatrixXd::Zero(Nrow+1, Ntime*3);

  pt_file_in1.open ( file_list_XYUxyz );
  if ( pt_file_in1.is_open() )
  {
    std::cout << "\nReading file "; str_format_io( file_list_XYUxyz, 45 );
    std::cout << "\n" << std::endl;
    int i1 = 0, j1 = 0, k1=0;
    while ( pt_file_in1.good() )
    {
      std::getline ( pt_file_in1, line1 );
      std::stringstream split_line1( line1 );
      j1 = 0, k1=0;
      int code_XY = 0;
     while ( std::getline ( split_line1, word_read1, ' ' ) )
      {
        if ( ( j1 == 0 ) && ( word_read1.compare( word_comment ) == 0 )) k1=k1+1;
        if ( ( j1 == 0 ) && ( word_read1.compare( word_XY ) == 0 )) code_XY=1; // i1=0
        if   ( k1 <= 0 )
        {
          file_XYUxyz = word_read1;
          pt_file_in2.open ( file_XYUxyz );
          if ( pt_file_in2.is_open() )
          {
            std::cout << "  Reading file "; str_format_io( file_XYUxyz, 45 );
            int i2 = 0, j2 = 0, k2=0;
            while ( pt_file_in2.good() )
            {
              std::getline ( pt_file_in2, line2 );
              std::stringstream split_line2( line2 );
              j2 = 0, k2=0;
              while ( std::getline ( split_line2, word_read2, ' ' ) )
              {
                if ( ( j2 == 0 ) && ( word_read2.compare( word_comment ) == 0 )) k2=k2+1;
                if   ( k2 <= 0 )
                {
                  char * cstr = new char [word_read2.length()+1]; std::strcpy (cstr, word_read2.c_str());
                  char* pEnd;
                  
                  read_value = std::strtof( cstr, &pEnd );
                  
                  if ( code_XY == 1 ) 
                  {
                    XY(i2,j2) = (float)read_value;
                  }
                  else
                  { 
                    Uxyz(i2,j2+(i1-1)*3) = (double)read_value;
                  }
                }
                if ( word_read2.compare( "" ) != 0 ) j2 = j2+1; // empty word_read2 not taken into account
              }
              i2 = i2+1;
            }
            pt_file_in2.close ();
            pt_file_in2.clear ();
            std::cout << " : " << std::fixed << std::setw(8) << i2 << " lines read" << std::endl;
          }
          if ( word_read1.compare( "" ) != 0 ) j1 = j1+1; // empty word_read1 not taken into account
        }
        i1 = i1+1;
      }          
    }
    pt_file_in1.close ();
    pt_file_in1.clear ();
    std::cout << "\nReading file "; str_format_io( file_list_XYUxyz, 45 );
    std::cout << " : " << std::fixed << std::setw(8) << i1 << " lines read\n" << std::endl;
  }
  
  // mean(U)
  Eigen::MatrixXd meanU = Eigen::MatrixXd::Zero(Nrow,3);
  for (int i=0; i<Nrow;i++) 
  {
     for (int j=0; j<Ntime;j++) 
     {
       for (int k=0; k<3; k++ )
       {
         if ( j%3 == k ) meanU(i,k) = meanU(i,k)+Uxyz(i,j);
      }
    }
  }
  for (int i=0; i<Nrow;i++) 
  {
     for (int j=0; j<3;j++) 
     {
        meanU(i,j) = meanU(i,j)/(double)Ntime;
     }
  }
  //for (int i=0; i<4;i++) std::cout << "1 mean) Ux=" << meanU(i,0) << " Uy=" << meanU(i,1) << " Uz=" << meanU(i,2) << std::endl;
  
  // mean(ux*ux,uy*uy,uz*uz) et mean(ux*uy,uy*uz,uz*ux)
  Eigen::MatrixXd meanUaa = Eigen::MatrixXd::Zero(Nrow,3);
  Eigen::MatrixXd meanUab = Eigen::MatrixXd::Zero(Nrow,3);
  for (int i=0; i<Nrow;i++) 
  {
     for (int j=0; j<Ntime;j++) 
     {
       for (int k=0; k<3; k++ )
       {
         if ( j%3 == k ) meanUaa(i,k) = meanUaa(i,k)+Uxyz(i,j)*Uxyz(i,j);
         int l=k+1; if (l==3) l=-2;
         if ( j%3 == k ) meanUab(i,k) = meanUab(i,k)+Uxyz(i,j)*Uxyz(i,j+l);
      }
    }
  }
  for (int i=0; i<Nrow;i++) 
  {
     for (int j=0; j<3;j++) 
     {
        meanUaa(i,j) = meanUaa(i,j)/(double)Ntime;
        meanUab(i,j) = meanUab(i,j)/(double)Ntime;
     }
  }
  //for (int i=0; i<4;i++) std::cout << "2 mean) Ux*Ux=" << meanUaa(i,0) << " Uy*Uy=" << meanUaa(i,1) << " Uz*Uz=" << meanUaa(i,2) << std::endl;
  
  //for (int i=0; i<4;i++) std::cout << "3 mean) Ux*Uy=" << meanUab(i,0) << " Uy*Uz=" << meanUab(i,1) << " Uz*Ux=" << meanUab(i,2) << std::endl;
 
  // covariance
  Eigen::MatrixXd covUaa = Eigen::MatrixXd::Zero(Nrow,3);
  Eigen::MatrixXd covUab = Eigen::MatrixXd::Zero(Nrow,3);
  for (int i=0; i<Nrow;i++) 
  {
     for (int k=0; k<3;k++) 
     {
        covUaa(i,k) = meanUaa(i,k)-meanU(i,k)*meanU(i,k);
        int l=k+1; if (l==3) l=0;
        covUab(i,k) = meanUab(i,k)-meanU(i,k)*meanU(i,l);
     }
  }
  
  // writting CSV files
  
  std::string file_mean_cov = "";
  std::ofstream pt_file_out;
    
  // writing mean files
  
  file_mean_cov = "mean_xx.csv";
  pt_file_out.open ( file_mean_cov );
  if ( pt_file_out.is_open() )
  {
    std::cout << "\nWritting file "; str_format_io( file_mean_cov, 45 );
    for (int i=0; i<Nrow;i++) 
    {
      pt_file_out << meanUaa(i,0) << std::endl;
    }    
    pt_file_out.close ();
    pt_file_out.clear ();
  }
  
  file_mean_cov = "mean_yy.csv";
  pt_file_out.open ( file_mean_cov );
  if ( pt_file_out.is_open() )
  {
    std::cout << "\nWritting file "; str_format_io( file_mean_cov, 45 );
    for (int i=0; i<Nrow;i++) 
    {
      pt_file_out << meanUaa(i,1) << std::endl;
    }    
    pt_file_out.close ();
    pt_file_out.clear ();
  }
  
  file_mean_cov = "mean_zz.csv";
  pt_file_out.open ( file_mean_cov );
  if ( pt_file_out.is_open() )
  {
    std::cout << "\nWritting file "; str_format_io( file_mean_cov, 45 );
    for (int i=0; i<Nrow;i++) 
    {
      pt_file_out << meanUaa(i,2) << std::endl;
    }    
    pt_file_out.close ();
    pt_file_out.clear ();
  }
  
  file_mean_cov = "mean_xy.csv";
  pt_file_out.open ( file_mean_cov );
  if ( pt_file_out.is_open() )
  {
    std::cout << "\nWritting file "; str_format_io( file_mean_cov, 45 );
    for (int i=0; i<Nrow;i++) 
    {
      pt_file_out << meanUab(i,0) << std::endl;
    }    
    pt_file_out.close ();
    pt_file_out.clear ();
  }
  
  file_mean_cov = "mean_yz.csv";
  pt_file_out.open ( file_mean_cov );
  if ( pt_file_out.is_open() )
  {
    std::cout << "\nWritting file "; str_format_io( file_mean_cov, 45 );
    for (int i=0; i<Nrow;i++) 
    {
      pt_file_out << meanUab(i,1) << std::endl;
    }    
    pt_file_out.close ();
    pt_file_out.clear ();
  }
  
  file_mean_cov = "mean_zx.csv";
  pt_file_out.open ( file_mean_cov );
  if ( pt_file_out.is_open() )
  {
    std::cout << "\nWritting file "; str_format_io( file_mean_cov, 45 );
    for (int i=0; i<Nrow;i++) 
    {
      pt_file_out << meanUab(i,2) << std::endl;
    }    
    pt_file_out.close ();
    pt_file_out.clear ();
  }
  
  // writing cov files
  
  file_mean_cov = "cov_xx.csv";
  pt_file_out.open ( file_mean_cov );
  if ( pt_file_out.is_open() )
  {
    std::cout << "\nWritting file "; str_format_io( file_mean_cov, 45 );
    for (int i=0; i<Nrow;i++) 
    {
      pt_file_out << covUaa(i,0) << std::endl;
    }    
    pt_file_out.close ();
    pt_file_out.clear ();
  }
  
  file_mean_cov = "cov_yy.csv";
  pt_file_out.open ( file_mean_cov );
  if ( pt_file_out.is_open() )
  {
    std::cout << "\nWritting file "; str_format_io( file_mean_cov, 45 );
    for (int i=0; i<Nrow;i++) 
    {
      pt_file_out << covUaa(i,1) << std::endl;
    }    
    pt_file_out.close ();
    pt_file_out.clear ();
  }
  
  file_mean_cov = "cov_zz.csv";
  pt_file_out.open ( file_mean_cov );
  if ( pt_file_out.is_open() )
  {
    std::cout << "\nWritting file "; str_format_io( file_mean_cov, 45 );
    for (int i=0; i<Nrow;i++) 
    {
      pt_file_out << covUaa(i,2) << std::endl;
    }    
    pt_file_out.close ();
    pt_file_out.clear ();
  }
    
  file_mean_cov = "cov_xy.csv";
  pt_file_out.open ( file_mean_cov );
  if ( pt_file_out.is_open() )
  {
    std::cout << "\nWritting file "; str_format_io( file_mean_cov, 45 );
    for (int i=0; i<Nrow;i++) 
    {
      pt_file_out << covUab(i,0) << std::endl;
    }    
    pt_file_out.close ();
    pt_file_out.clear ();
  }
  
  file_mean_cov = "cov_yz.csv";
  pt_file_out.open ( file_mean_cov );
  if ( pt_file_out.is_open() )
  {
    std::cout << "\nWritting file "; str_format_io( file_mean_cov, 45 );
    for (int i=0; i<Nrow;i++) 
    {
      pt_file_out << covUab(i,1) << std::endl;
    }    
    pt_file_out.close ();
    pt_file_out.clear ();
  }
  
  file_mean_cov = "cov_zx.csv";
  pt_file_out.open ( file_mean_cov );
  if ( pt_file_out.is_open() )
  {
    std::cout << "\nWritting file "; str_format_io( file_mean_cov, 45 );
    for (int i=0; i<Nrow;i++) 
    {
      pt_file_out << covUab(i,2) << std::endl;
    }    
    pt_file_out.close ();
    pt_file_out.clear ();
  }
    
  std::cout << "\n" << std::endl;  
}
  
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
int main(int argc, char *argv[])
{
  std::string file_XYUxyz;
  int Nrow, Ntime;
  
  //for (int i=0;i<argc; i++) std::cout << "argv["<<i<<"]=" <<  argv[i] << std::endl;
  
  file_XYUxyz = argv[1];
  Nrow = atoi ( argv[2] );
  Ntime = atoi ( argv[3] ); 
  
  Eigen::MatrixXd XY;
  Eigen::MatrixXd Uxyz;
  stat_from_file( file_XYUxyz, Nrow, Ntime, XY, Uxyz );
}
