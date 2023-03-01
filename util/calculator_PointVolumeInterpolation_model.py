######################################
#
# Laurence Wallian - ACTA - OPAALE - INRAE Rennes - Juin 2022-Février 2023
#
######################################
#
# MORAANE : Openfoam DNS file -> synthetic PIV file
#
#     This script creates PNG and CSV files from openfoam time/U files
#
#        NOTE : here, DNS is a generic word for "Numerical Simulation"
#
######################################
##
## Paraview operation (pvbatch command) : Openfoam DNS file -> CSV file
##
## step1 = calculator -> Ux scalar
## step2 = Ux gaussian interpolation
## step3 = slice Z=Zslice (=Lz/2) of the Ux gaussian interpolation
## 
##           => CSV file
##
## Next operation (tcsh shell script) : CSV file -> synthetic PIV file
##
## step1 = rewritting with column IsValid
## step2 = adding noise for data type [raw openfoam results]
## step3 = dimentionless PIV for data type [ROM applied on openfoam results]
##
##           => synthetic PIV file
##
######################################
##
## IMPORTANT : just keeps 1 time step : values U is copied
##                      in directories 0 (=init) and 1 (any number>0 for this step)
##
######################################
# LIST of parameters to define
#
#    case type :
#      case_dir=CASE_DIR_NAME : mean,  spatialModes_2modes, residualSpeed_2 or sillageDNSRe300
#
#    case directory :
#      last_dir=LAST_DIR_NAME : present directory without PATH
#      path_case=PATH_DIR_NAME : PATH containing the present directory
#
#    cylinder type  (for target view, pink cylinder drawing, ...)
#      x0_cyl=XCYL_VALUE : x cylinder center
#      y0_cy=YCYL_VALUE : y cylinder center 
#
#    domain dim (for target view, pink cylinder drawing, ...)
#      x1_dom=X1_DOM_VALUE : min(x) 
#      y1_dom=Y1_DOM_VALUE : min(y) 
#      z1_dom=Z1_DOM_VALUE : min(z) 
#      x2_dom=X2_DOM_VALUE : max(x) 
#      y2_dom=Y2_DOM_VALUE : max(y) 
#      z2_dom=Z2_DOM_VALUE : max(z) 
#
#    Zslice characteristics for CSV and PNG files
#      Zslice=ZSLICE_VALUE : DNS Z slice value for pseudo PIV
#      Radius=RADIUS_VALUE : gaussian radius for smoothing
#      Origin_X=ORIGIN_X_VALUE : X left point of the BOX where applying smoothing
#      Origin_Y=ORIGIN_Y_VALUE : Y lower point of the BOX where applying smoothing
#      Scale_X=SCALE_X_VALUE : length of the BOX where applying smoothing
#      Scale_Y=SCALE_Y_VALUE : heigth of the BOX where applying smoothing
#      Resolution_X=RESOLUTION_X_VALUE : Nx-1 with Nx=number of points along X axis
#      Resolution_Y=RESOLUTION_Y_VALUE : Ny-1 with Ny=number of points along Y axis
#      Other_info=OTHER_INFO : PNG text
#
#      mode_view_NoGrid=MODE_VIEW_NOGRID_VALUE : =POINTS for no smoothing view, =SURFACE for smoothing view
#      code_view_whitgrid=CODE_VIEW_WITHGRID_VALUE : =1 if PNG file view with grid 
#      code_view_slice_ux1=CODE_VIEW_SLICE_UX1_VALUE : =1 if PNG file showing Ux(Z=Zslice) openfoam result
#      code_view_slice_uy1=CODE_VIEW_SLICE_UY1_VALUE : =1 if PNG file showing Uy(Z=Zslice) openfoam result
#      code_view_PtVol_ux1=CODE_VIEW_POINTVOLUMEINTERPOLATOR_UX_VALUE : =1 if PNG file showing Ux openfoam after smoothing
#      code_view_PtVol_uy1=CODE_VIEW_POINTVOLUMEINTERPOLATOR_UY_VALUE : =1 if PNG file showing Uy openfoam after smoothing
#      code_view_slice_ux2=CODE_VIEW_SLICE_UX2_VALUE : =1 if PNG file showing Ux(Z=Zslice) openfoam after smoothing
#      code_view_slice_uy2=CODE_VIEW_SLICE_UY2_VALUE : =1 if PNG file showing Uy(Z=Zslice) openfoam after smoothing
#      code_csv_slice_ux1=CODE_CSV_SLICE_UX1_VALUE : =1 if CSV file showing Ux(Z=Zslice) openfoam result
#      code_csv_slice_uy1=CODE_CSV_SLICE_UY1_VALUE : =1 if CSV file showing Uy(Z=Zslice) openfoam result
#      code_csv_slice_ux2=CODE_CSV_SLICE_UX2_VALUE : =1 if CSV file showing Ux(Z=Zslice) openfoam after smoothing
#      code_csv_slice_uy2=CODE_CSV_SLICE_UY2_VALUE : =1 if CSV file showing Uy(Z=Zslice) openfoam after smoothing
#
######################################

# state file generated using paraview version 5.10.1

# uncomment the following three lines to ensure this script works in future versions
#import paraview
#paraview.compatibility.major = 5
#paraview.compatibility.minor = 10

#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# ----------------------------------------------------------------
# setup views used in the visualization
# ----------------------------------------------------------------

# =====================================================

### main variables

## case type, name and path

# case name (Example :residualSpeed_2 )
case_dir = "CASE_DIR_NAME"

# directory name for case (Example : residualSpeed_2_t100-t200 )
last_dir="LAST_DIR_NAME"

# PATH for last_dir (Example : .../RedLUM/data_Redlum_cpp/DNS${Re}-GeoLES3900/ROMDNS-vNewCleanDEIMTest )
path_case="PATH_DIR_NAME"

# -> file name
file_name = str(path_case)+str("/")+ str(last_dir)+str("/")+str(last_dir)+str(".foam")

## cylinder

# cylinder center (Example : center = ( 2.5, 6 ) )
x0_cyl=XCYL_VALUE
y0_cyl=YCYL_VALUE

## domain

# domain limits (Example : dom = ( [0:20], [0:12], [0:3.14] )
x1_dom=X1_DOM_VALUE
y1_dom=Y1_DOM_VALUE
z1_dom=Z1_DOM_VALUE
x2_dom=X2_DOM_VALUE
y2_dom=Y2_DOM_VALUE
z2_dom=Z2_DOM_VALUE

# -> domain center
x0_dom = ( x1_dom + x2_dom )/2.
y0_dom = ( y1_dom + y2_dom )/2.
z0_dom = ( z1_dom + z2_dom )/2.

# -> domain length
Lx_dom = x2_dom - x1_dom
Ly_dom = y2_dom - y1_dom
Lz_dom = z2_dom - z1_dom

#print( str("\ndomain center : (")+str(x0_dom)+str(":")+str(y0_dom)+str(":")+str(z0_dom)+str(")") )
#print( str("domain length : (")+str(Lx_dom)+str(":")+str(Ly_dom)+str(":")+str(Lz_dom)+str(")\n") )

## slice and operations on this slice

# Z value for slice
Zslice = z0_dom
Zslice = ZSLICE_VALUE

# init the 'GaussianKernel' selected for 'Kernel' (Example : Radius = 0.203125)
Radius = RADIUS_VALUE

# init the 'Bounded Volume' selected for 'Source' (Example : Origin = [1.5408, 1.7793, 0])
Origin_X=ORIGIN_X_VALUE
Origin_Y=ORIGIN_Y_VALUE
Origin_Z=z1_dom

# init the 'Bounded Volume' selected for 'Source' (Example : Scale = [13.9154, 8.5670, 3.14])
Scale_X=SCALE_X_VALUE
Scale_Y=SCALE_Y_VALUE
Scale_Z=Lz_dom

# resolution (Example : Resolution = [294, 181, 20])
Resolution_X=RESOLUTION_X_VALUE
Resolution_Y=RESOLUTION_Y_VALUE
Resolution_Z=20

### other variables

## view text
Other_info = "OTHER_INFO"

## view conditions

# smoothed or not smoothed view : no smoothing if =POINTS
mode_view_NoGrid = "MODE_VIEW_NOGRID_VALUE"

# view with option : [Surface With Edges] if =1
code_view_withGrid=CODE_VIEW_WITHGRID_VALUE

# first view  = slice_Ux1 and slice_Uy1 : PNG files created if =1
code_view_slice_Ux1=CODE_VIEW_SLICE_UX1_VALUE
code_view_slice_Uy1=CODE_VIEW_SLICE_UY1_VALUE

# second view  = pointVolumeInterpolator_Ux and pointVolumeInterpolator_Uy : PNG files created if =1
code_view_pointVolumeInterpolator_Ux=CODE_VIEW_POINTVOLUMEINTERPOLATOR_UX_VALUE
code_view_pointVolumeInterpolator_Uy=CODE_VIEW_POINTVOLUMEINTERPOLATOR_UY_VALUE

# third view  = slice_Ux2 and slice_Uy2 : PNG files created if =1
code_view_slice_Ux2=CODE_VIEW_SLICE_UX2_VALUE
code_view_slice_Uy2=CODE_VIEW_SLICE_UY2_VALUE

## CSV files conditions

# CSV files [slice_Ux1.csv] and [slice_Uy1.csv] : CSV files created if =1
code_csv_slice_Ux1=CODE_CSV_SLICE_UX1_VALUE
code_csv_slice_Uy1=CODE_CSV_SLICE_UY1_VALUE

# CSV files [slice_Ux2.csv] and [slice_Uy2.csv] : CSV files created if =1
code_csv_slice_Ux2=CODE_CSV_SLICE_UX2_VALUE
code_csv_slice_Uy2=CODE_CSV_SLICE_UY2_VALUE

### other view conditions ##

# view size
viewSize_length = 1200
viewSize_height = 800
viewSize = [ viewSize_length, viewSize_height ]

# points size when display='Surface' or display='Points'
pointSize_for_SurfaceDisplay = 1.0
pointSize_for_PointsDisplay = 2.32
pointSize_for_PointsDisplay = viewSize_length/(RESOLUTION_X_VALUE+1.)*0.57

# color 
U_color_rainbow = [ 
  1, 0.3, 0.3, 0.9, 
  2, 0.0, 0.0, 0.4, 
  3, 0.0, 1.0, 1.0, 
  4, 0.0, 0.5, 0.0, 
  5, 1.0, 1.0, 0.0, 
  6, 1.0, 0.4, 0.0, 
  7, 0.4, 0.0, 0.0, 
  8, 0.9, 0.3, 0.3
]
U_color_blueOrange = [ 
  1, 0.086275, 0.003922, 0.298039, 
  2, 0.113725, 0.023529, 0.450980, 
  3, 0.105882, 0.050980, 0.509804, 
  4, 0.039216, 0.039216, 0.560784, 
  5, 0.031372, 0.098039, 0.600000, 
  6, 0.043137, 0.164706, 0.639216, 
  7, 0.054902, 0.243137, 0.678431, 
  8, 0.054902, 0.317647, 0.709804, 
  9, 0.050980, 0.396078, 0.741176, 
 10, 0.039216, 0.466667, 0.768627, 
 11, 0.031372, 0.537255, 0.788235, 
 12, 0.031372, 0.615686, 0.811765, 
 13, 0.023529, 0.709804, 0.831373, 
 14, 0.050980, 0.800000, 0.850980, 
 15, 0.070588, 0.854902, 0.870588, 
 16, 0.262745, 0.901961, 0.862745, 
 17, 0.423529, 0.941176, 0.874510, 
 18, 0.572549, 0.964706, 0.835294, 
 19, 0.658824, 0.980392, 0.843137, 
 20, 0.764706, 0.980392, 0.866667, 
 21, 0.827451, 0.980392, 0.886275, 
 22, 0.913725, 0.988235, 0.937255, 
 23, 1.000000, 1.000000, 0.972549, 
 24, 0.988235, 0.980392, 0.870588, 
 25, 0.992157, 0.972549, 0.803922, 
 26, 0.992157, 0.964706, 0.713725, 
 27, 0.988235, 0.956863, 0.643137, 
 28, 0.980392, 0.917647, 0.509804, 
 29, 0.968627, 0.874510, 0.407843, 
 30, 0.949020, 0.823529, 0.321569, 
 31, 0.929412, 0.776471, 0.278431, 
 32, 0.909804, 0.717647, 0.235294, 
 33, 0.890196, 0.658824, 0.196078, 
 34, 0.878431, 0.619608, 0.168627, 
 35, 0.870588, 0.549020, 0.156863, 
 36, 0.850980, 0.474510, 0.145098, 
 37, 0.831373, 0.411765, 0.133333, 
 38, 0.811765, 0.345098, 0.113725, 
 39, 0.788235, 0.266667, 0.094118, 
 40, 0.741176, 0.184314, 0.074510, 
 41, 0.690196, 0.125490, 0.062745, 
 42, 0.619608, 0.062745, 0.043137, 
 43, 0.549020, 0.027451, 0.070588, 
 44, 0.470588, 0.015686, 0.090196, 
 45, 0.400000, 0.003922, 0.101961, 
 46, 0.188235, 0.000000, 0.070588
]
# getting color : cat ... | sed s/","/"\n"/g | awk 'BEGIN{n=0; N=0}{n=n+1; if (n==1) {N=N+1; printf(" %2d, ",N);} else {printf("%8.6f, ",$1); if (n==4) {n=0; print ""} } }'

# =====================================================

# get the material library
materialLibrary1 = GetMaterialLibrary()

# Create a new 'Render View'
renderView1 = CreateView('RenderView')
#renderView1.ViewSize = [1200, 800]
renderView1.ViewSize = [ viewSize_length, viewSize_height ]
renderView1.AxesGrid = 'GridAxes3DActor'
renderView1.StereoType = 'Crystal Eyes'
renderView1.CameraFocalDisk = 1.0
renderView1.CameraParallelScale = 8.0
renderView1.CameraParallelProjection = 1
renderView1.BackEnd = 'OSPRay raycaster'
renderView1.OSPRayMaterialLibrary = materialLibrary1

renderView1.UseColorPaletteForBackground = 0
renderView1.Background = [1.0, 1.0, 1.0]

# init the 'GridAxes3DActor' selected for 'AxesGrid'
renderView1.AxesGrid.Visibility = 1

SetActiveView(None)

# vue centered on cylinder

renderView1.CenterOfRotation = [x0_cyl+7.5, y0_cyl, 0.]
renderView1.CameraFocalPoint = [x0_cyl+7.5, y0_cyl, 0.]
renderView1.CameraPosition = [x0_cyl+7.5, y0_cyl, 47.0]

# ----------------------------------------------------------------
# setup view layouts
# ----------------------------------------------------------------

# create new layout object 'Layout #1'
layout1 = CreateLayout(name='Layout #1')
layout1.AssignView(0, renderView1)
layout1.SetSize(1200, 800)

# ----------------------------------------------------------------
# restore active view
SetActiveView(renderView1)
# ----------------------------------------------------------------

# ----------------------------------------------------------------
# setup the data processing pipelines
# ----------------------------------------------------------------

# create a new 'Cylinder'
cylinder1 = Cylinder(registrationName='Cylinder1')
cylinder1.Resolution = 100
cylinder1.Height = Lz_dom
cylinder1.Center = [x0_cyl, z0_dom, -y0_cyl]

# create a new 'OpenFOAMReader'
# Example : base_Calcfoam = OpenFOAMReader(registrationName='LAST_DIR_NAME', FileName='PATH_DIR_NAME/LAST_DIR_NAME/LAST_DIR_NAME.foam')
base_Calcfoam = OpenFOAMReader(registrationName=str(last_dir), FileName=str(file_name))
base_Calcfoam.MeshRegions = ['internalMesh']
base_Calcfoam.CellArrays = ['U']


######## Ux ###########

# create a new 'Calculator'
calculator_Ux = Calculator(registrationName='Calculator_Ux', Input=base_Calcfoam)
calculator_Ux.ResultArrayName = 'Ux'
calculator_Ux.Function = 'U_X'

# create a new 'Slice'
slice_Ux1 = Slice(registrationName='Slice_Ux1', Input=calculator_Ux)
slice_Ux1.SliceType = 'Plane'
slice_Ux1.HyperTreeGridSlicer = 'Plane'
slice_Ux1.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_Ux1.SliceType.Origin = [x0_dom, y0_dom, Zslice]
slice_Ux1.SliceType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_Ux1.HyperTreeGridSlicer.Origin = [x0_dom, y0_dom, Zslice]


############################################
### Gaussian Interpolation on limited BOX ###

### INMPORTANT : ################################
# !!! the line defining the 'Origin' is missing when getting state file *.py !!!
# !!! by paraFoam MENU [File/Save State] -> must be added !!!
#      line example = pointVolumeInterpolator_Ux.Source.Origin = [1.5408, 1.7793, 0]
############################################
# Cf. https://kitware.github.io/paraview-docs/latest/python/paraview.simple.PointVolumeInterpolator.html
# Cf. ~/Bureau/MORAANE/podfs2/functions/stochastic/PIV_modes.m : std_space = 0.203125
############################################

# create a new 'Point Volume Interpolator'
pointVolumeInterpolator_Ux = PointVolumeInterpolator(registrationName='PointVolumeInterpolator_Ux', Input=calculator_Ux,
    Source='Bounded Volume')
pointVolumeInterpolator_Ux.Kernel = 'GaussianKernel'
pointVolumeInterpolator_Ux.Locator = 'Static Point Locator'

# init the 'GaussianKernel' selected for 'Kernel' (Example : pointVolumeInterpolator_Ux.Kernel.Radius = 0.203125 )
pointVolumeInterpolator_Ux.Kernel.Radius = Radius

# init the 'Bounded Volume' selected for 'Source' 
# Example : pointVolumeInterpolator_Ux.Source.Origin = [1.5408, 1.7793, 0] 
#                  pointVolumeInterpolator_Ux.Source.Scale = [13.9154, 8.5670, 3.14]
#                  pointVolumeInterpolator_Ux.Source.Resolution = [294, 181, 20]
pointVolumeInterpolator_Ux.Source.Origin = [Origin_X, Origin_Y, Origin_Z]
pointVolumeInterpolator_Ux.Source.Scale = [Scale_X, Scale_Y, Scale_Z]

#pointVolumeInterpolator_Ux.Source.RefinementMode = 'Use cell-size'
#pointVolumeInterpolator_Ux.Source.CellSize = 0.0470 # slice : 298x184x1 points / PIV ref : 295 x 182 points

pointVolumeInterpolator_Ux.Source.RefinementMode = 'Use resolution'
pointVolumeInterpolator_Ux.Source.Resolution = [Resolution_X, Resolution_Y, Resolution_Z]

pointVolumeInterpolator_Ux.NullPointsStrategy = 0 # ->MaskPoints (MASK_POINTS)
#pointVolumeInterpolator_Ux.NullPointsStrategy = 1 # -> NullPoint (NULL_VALUE)
#pointVolumeInterpolator_Ux.NullPointsStrategy = 2 # -> CLOSEST_POINT
pointVolumeInterpolator_Ux.NullValue = 0.0

############################################


# create a new 'Slice'
slice_Ux2 = Slice(registrationName='Slice_Ux2', Input=pointVolumeInterpolator_Ux)
slice_Ux2.SliceType = 'Plane'
slice_Ux2.HyperTreeGridSlicer = 'Plane'
slice_Ux2.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_Ux2.SliceType.Origin = [x0_dom, y0_dom, Zslice]
slice_Ux2.SliceType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_Ux2.HyperTreeGridSlicer.Origin = [x0_dom, y0_dom, Zslice]

######## Uy ###########

# create a new 'Calculator'
calculator_Uy = Calculator(registrationName='Calculator_Uy', Input=base_Calcfoam)
calculator_Uy.ResultArrayName = 'Uy'
calculator_Uy.Function = 'U_Y'

# create a new 'Slice'
slice_Uy1 = Slice(registrationName='Slice_Uy1', Input=calculator_Uy)
slice_Uy1.SliceType = 'Plane'
slice_Uy1.HyperTreeGridSlicer = 'Plane'
slice_Uy1.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_Uy1.SliceType.Origin = [x0_dom, y0_dom, Zslice]
slice_Uy1.SliceType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_Uy1.HyperTreeGridSlicer.Origin = [x0_dom, y0_dom, Zslice]


############################################
### Gaussian Interpolation on limited BOX ###

### INMPORTANT : ################################
# !!! the line defining the 'Origin' is missing when getting state file *.py !!!
# !!! by paraFoam MENU [File/Save State] -> must be added !!!
#      line example = pointVolumeInterpolator_Uy.Source.Origin = [1.5408, 1.7793, 0]
############################################
# Cf. https://kitware.github.io/paraview-docs/latest/python/paraview.simple.PointVolumeInterpolator.html
# Cf. ~/Bureau/MORAANE/podfs2/functions/stochastic/PIV_modes.m : std_space = 0.203125
############################################

# create a new 'Point Volume Interpolator'
pointVolumeInterpolator_Uy = PointVolumeInterpolator(registrationName='PointVolumeInterpolator_Uy', Input=calculator_Uy,
    Source='Bounded Volume')
pointVolumeInterpolator_Uy.Kernel = 'GaussianKernel'
pointVolumeInterpolator_Uy.Locator = 'Static Point Locator'

# init the 'GaussianKernel' selected for 'Kernel'
pointVolumeInterpolator_Uy.Kernel.Radius = Radius

# init the 'Bounded Volume' selected for 'Source'
pointVolumeInterpolator_Uy.Source.Origin = [Origin_X, Origin_Y, Origin_Z]
pointVolumeInterpolator_Uy.Source.Scale = [Scale_X, Scale_Y, Scale_Z]

pointVolumeInterpolator_Uy.Source.RefinementMode = 'Use resolution'
pointVolumeInterpolator_Uy.Source.Resolution = [Resolution_X, Resolution_Y, Resolution_Z]

pointVolumeInterpolator_Uy.NullPointsStrategy = 0 # ->MaskPoints (MASK_POINTS)
pointVolumeInterpolator_Uy.NullValue = 0.0

############################################


# create a new 'Slice'
slice_Uy2 = Slice(registrationName='Slice_Uy2', Input=pointVolumeInterpolator_Uy)
slice_Uy2.SliceType = 'Plane'
slice_Uy2.HyperTreeGridSlicer = 'Plane'
slice_Uy2.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_Uy2.SliceType.Origin = [x0_dom, y0_dom, Zslice]
slice_Uy2.SliceType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_Uy2.HyperTreeGridSlicer.Origin = [x0_dom, y0_dom, Zslice]



 
######## Uz ###########
 
#if case_dir == "residualSpeed_2":
if ((case_dir == "residualSpeed_2") or (case_dir == "residualSpeed_4")  or (case_dir == "residualSpeed_8")  or (case_dir == "residualSpeed_16")):

  # create a new 'Calculator'
  calculator_Uz = Calculator(registrationName='Calculator_Uz', Input=base_Calcfoam)
  calculator_Uz.ResultArrayName = 'Uz'
  calculator_Uz.Function = 'U_Z'

  # create a new 'Slice'
  slice_Uz1 = Slice(registrationName='Slice_Uz1', Input=calculator_Uz)
  slice_Uz1.SliceType = 'Plane'
  slice_Uz1.HyperTreeGridSlicer = 'Plane'
  slice_Uz1.SliceOffsetValues = [0.0]

  # init the 'Plane' selected for 'SliceType'
  slice_Uz1.SliceType.Origin = [x0_dom, y0_dom, Zslice]
  slice_Uz1.SliceType.Normal = [0.0, 0.0, 1.0]

  # init the 'Plane' selected for 'HyperTreeGridSlicer'
  slice_Uz1.HyperTreeGridSlicer.Origin = [x0_dom, y0_dom, Zslice]


  ############################################
  ### Gaussian Interpolation on limited BOX ###

  ### INMPORTANT : ################################
  # !!! the line defining the 'Origin' is missing when getting state file *.py !!!
  # !!! by paraFoam MENU [File/Save State] -> must be added !!!
  #      line example = pointVolumeInterpolator_Uz.Source.Origin = [1.5408, 1.7793, 0]
  ############################################
  # Cf. https://kitware.github.io/paraview-docs/latest/python/paraview.simple.PointVolumeInterpolator.html
  # Cf. ~/Bureau/MORAANE/podfs2/functions/stochastic/PIV_modes.m : std_space = 0.203125
  ############################################

  # create a new 'Point Volume Interpolator'
  pointVolumeInterpolator_Uz = PointVolumeInterpolator(registrationName='PointVolumeInterpolator_Uz', Input=calculator_Uz,
      Source='Bounded Volume')
  pointVolumeInterpolator_Uz.Kernel = 'GaussianKernel'
  pointVolumeInterpolator_Uz.Locator = 'Static Point Locator'

  # init the 'GaussianKernel' selected for 'Kernel'
  pointVolumeInterpolator_Uz.Kernel.Radius = Radius

  # init the 'Bounded Volume' selected for 'Source'
  pointVolumeInterpolator_Uz.Source.Origin = [Origin_X, Origin_Y, Origin_Z]
  pointVolumeInterpolator_Uz.Source.Scale = [Scale_X, Scale_Y, Scale_Z]

  pointVolumeInterpolator_Uz.Source.RefinementMode = 'Use resolution'
  pointVolumeInterpolator_Uz.Source.Resolution = [Resolution_X, Resolution_Y, Resolution_Z]

  pointVolumeInterpolator_Uz.NullPointsStrategy = 0 # ->MaskPoints (MASK_POINTS)
  pointVolumeInterpolator_Uz.NullValue = 0.0

  ############################################


  # create a new 'Slice'
  slice_Uz2 = Slice(registrationName='Slice_Uz2', Input=pointVolumeInterpolator_Uz)
  slice_Uz2.SliceType = 'Plane'
  slice_Uz2.HyperTreeGridSlicer = 'Plane'
  slice_Uz2.SliceOffsetValues = [0.0]

  # init the 'Plane' selected for 'SliceType'
  slice_Uz2.SliceType.Origin = [x0_dom, y0_dom, Zslice]
  slice_Uz2.SliceType.Normal = [0.0, 0.0, 1.0]

  # init the 'Plane' selected for 'HyperTreeGridSlicer'
  slice_Uz2.HyperTreeGridSlicer.Origin = [x0_dom, y0_dom, Zslice]
  
############################################



# ----------------------------------------------------------------
# setup the visualization in view 'renderView1' : cylinder
# ----------------------------------------------------------------

# show data from cylinder1
cylinder1Display = Show(cylinder1, renderView1, 'GeometryRepresentation')

# get color transfer function/color map for 'Normals'
cylinder1LUT = GetColorTransferFunction('Normals')
#cylinder1LUT.RGBPoints = [1.0, 1.0, 0.67, 0.0, 2.0, 0.25, 1.0, 0.25, 3.0, 1.0, 0.67, 0.0]
cylinder1LUT.RGBPoints = [1.0, 1.0, 0.67, 0.0,  2.0,1.,0.,1.,  3.0, 1.0, 0.67, 0.0]
cylinder1LUT.NumberOfTableValues = 1
cylinder1LUT.ScalarRangeInitialized = 1.0

# trace defaults for the display properties.
cylinder1Display.Representation = 'Surface'
cylinder1Display.ColorArrayName = ['POINTS', 'Normals']
cylinder1Display.LookupTable = cylinder1LUT
#cylinder1Display.Opacity = 1.0
cylinder1Display.Opacity = 0.4
cylinder1Display.Specular = 0.49
cylinder1Display.SelectTCoordArray = 'None'
cylinder1Display.SelectNormalArray = 'None'
cylinder1Display.SelectTangentArray = 'None'
cylinder1Display.RepeatTextures = 0
cylinder1Display.ShowTexturesOnBackface = 0
cylinder1Display.Orientation = [90.0, 0.0, 0.0]
cylinder1Display.OSPRayScaleArray = 'Normals'
cylinder1Display.OSPRayScaleFunction = 'PiecewiseFunction'
cylinder1Display.SelectOrientationVectors = 'None'
cylinder1Display.ScaleFactor = 0.31399999856948857
cylinder1Display.SelectScaleArray = 'None'
cylinder1Display.GlyphType = 'Arrow'
cylinder1Display.GlyphTableIndexArray = 'None'
cylinder1Display.GaussianRadius = 0.015699999928474425
cylinder1Display.SetScaleArray = ['POINTS', 'Normals']
cylinder1Display.ScaleTransferFunction = 'PiecewiseFunction'
cylinder1Display.OpacityArray = ['POINTS', 'Normals']
cylinder1Display.OpacityTransferFunction = 'PiecewiseFunction'
cylinder1Display.DataAxesGrid = 'GridAxesRepresentation'
cylinder1Display.PolarAxes = 'PolarAxesRepresentation'

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
cylinder1Display.OSPRayScaleFunction.Points = [1.0486473911441863e-09, 0.0, 0.5, 0.0, 2.847604226310929, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
cylinder1Display.ScaleTransferFunction.Points = [-1.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
cylinder1Display.OpacityTransferFunction.Points = [-1.0, 0.0, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

# init the 'PolarAxesRepresentation' selected for 'PolarAxes'
cylinder1Display.PolarAxes.Orientation = [90.0, 0.0, 0.0]

# ----------------------------------------------------------------
# setup color maps and opacity mapes used in the visualization
# note: the Get..() functions create a new object, if needed
# ----------------------------------------------------------------

# get opacity transfer function/opacity map for 'Normals'
cylinder1PWF = GetOpacityTransferFunction('Normals')
cylinder1PWF.Points = [0.9999999773419813, 0.0, 0.5, 0.0, 1.0000000250926921, 1.0, 0.5, 0.0]
cylinder1PWF.ScalarRangeInitialized = 1

# show data in view
Show(cylinder1, renderView1)



# ----------------------------------------------------------------
# setup the visualization in view 'renderView1' : Ux
# ----------------------------------------------------------------

# show data from slice_Ux1
slice_Ux1Display = Show(slice_Ux1, renderView1, 'UniformGridRepresentation')

# get color transfer function/color map for 'Ux'
uxLUT = GetColorTransferFunction('Ux')

#uxLUT.RGBPoints = [-0.5087437629699707, 0.278431372549, 0.278431372549, 0.858823529412, -0.33991622596979143, 0.0, 0.0, 0.360784313725, -0.17226930111646654, 0.0, 1.0, 1.0, -0.002261151969432884, 0.0, 0.501960784314, 0.0, 0.165385772883892, 1.0, 1.0, 0.0, 0.3342133098840713, 1.0, 0.380392156863, 0.0, 0.5030408468842507, 0.419607843137, 0.0, 0.0, 0.6718683838844299, 0.878431372549, 0.301960784314, 0.301960784314]

uxLUT.RGBPoints = U_color_rainbow
uxLUT.RGBPoints = U_color_blueOrange

uxLUT.ColorSpace = 'RGB'
uxLUT.NumberOfTableValues = 310
uxLUT.ScalarRangeInitialized = 1.0
#uxLUT.RescaleTransferFunctionToDataRange(True)

# this part (RescaleTransferFunction) must be defined before after a Render()
uxLUT.RescaleTransferFunction(-0.9, 1.9)
if case_dir == "mean":
  uxLUT.RescaleTransferFunction(-0.9, 1.9)
#if case_dir == "spatialModes_2modes":
if ((case_dir == "spatialModes_2modes") or (case_dir == "spatialModes_4modes")  or (case_dir == "spatialModes_8modes")  or (case_dir == "spatialModes_16modes")):
  uxLUT.RescaleTransferFunction(-0.2, 0.2)
#if case_dir == "residualSpeed_2":
if ((case_dir == "residualSpeed_2") or (case_dir == "residualSpeed_4")  or (case_dir == "residualSpeed_8")  or (case_dir == "residualSpeed_16")):
  uxLUT.RescaleTransferFunction(-0.7, 0.7)
if case_dir == "sillageDNSRe300":
  uxLUT.RescaleTransferFunction(-0.9, 1.9)
uxLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for uxLUT in view renderView1
uxLUTColorBar = GetScalarBar(uxLUT, renderView1)
uxLUTColorBar.AutoOrient = 0
uxLUTColorBar.Orientation = 'Horizontal'
uxLUTColorBar.WindowLocation = 'Any Location'
uxLUTColorBar.Position = [0.6, 0.02]
uxLUTColorBar.Title = 'Ux'
uxLUTColorBar.ComponentTitle = str(Other_info)
uxLUTColorBar.TitleBold = 1
uxLUTColorBar.TitleFontSize = 20
uxLUTColorBar.AutomaticLabelFormat = 0
uxLUTColorBar.LabelFormat = '%-#7.2f'
uxLUTColorBar.RangeLabelFormat = '%-#7.2f'

# set color bar visibility
uxLUTColorBar.Visibility = 0

# get opacity transfer function/opacity map for 'Ux'
uxPWF = GetOpacityTransferFunction('Ux')
#uxPWF.Points = [-0.5087437629699707, 0.0, 0.5, 0.0, 0.6718683838844299, 1.0, 0.5, 0.0]
uxPWF.ScalarRangeInitialized = 1
#uxPWF.RescaleTransferFunctionToDataRange(True)

uxPWF.Points = [1, 0.0, 0.5, 0.0, 8, 1.0, 0.5, 0.0]

# this part (RescaleTransferFunction) must be defined before after a Render()
uxPWF.RescaleTransferFunction(-0.9, 1.9)
if case_dir == "mean":
  uxPWF.RescaleTransferFunction(-0.9, 1.9)
#if case_dir == "spatialModes_2modes":
if ((case_dir == "spatialModes_2modes") or (case_dir == "spatialModes_4modes")  or (case_dir == "spatialModes_8modes")  or (case_dir == "spatialModes_16modes")):
  uxPWF.RescaleTransferFunction(-0.2, 0.2)
#if case_dir == "residualSpeed_2":
if ((case_dir == "residualSpeed_2") or (case_dir == "residualSpeed_4")  or (case_dir == "residualSpeed_8")  or (case_dir == "residualSpeed_16")):
  uxPWF.RescaleTransferFunction(-0.7, 0.7)
if case_dir == "sillageDNSRe300":
  uxPWF.RescaleTransferFunction(-0.9, 1.9)

# trace defaults for the display properties.
slice_Ux1Display.Representation = 'Surface With Edges'
slice_Ux1Display.ColorArrayName = ['POINTS', 'Ux']
slice_Ux1Display.LookupTable = uxLUT
slice_Ux1Display.SelectTCoordArray = 'None'
slice_Ux1Display.SelectNormalArray = 'None'
slice_Ux1Display.SelectTangentArray = 'None'
slice_Ux1Display.OSPRayScaleArray = 'Ux'
slice_Ux1Display.OSPRayScaleFunction = 'PiecewiseFunction'
slice_Ux1Display.SelectOrientationVectors = 'U'
slice_Ux1Display.ScaleFactor = 2.0
slice_Ux1Display.SelectScaleArray = 'Ux'
slice_Ux1Display.GlyphType = 'Arrow'
slice_Ux1Display.GlyphTableIndexArray = 'Ux'
slice_Ux1Display.GaussianRadius = 0.1
slice_Ux1Display.SetScaleArray = ['POINTS', 'Ux']
slice_Ux1Display.ScaleTransferFunction = 'PiecewiseFunction'
slice_Ux1Display.OpacityArray = ['POINTS', 'Ux']
slice_Ux1Display.OpacityTransferFunction = 'PiecewiseFunction'
slice_Ux1Display.DataAxesGrid = 'GridAxesRepresentation'
slice_Ux1Display.PolarAxes = 'PolarAxesRepresentation'
slice_Ux1Display.ScalarOpacityUnitDistance = 0.23534221904681663
slice_Ux1Display.ScalarOpacityFunction = uxPWF
slice_Ux1Display.OpacityArrayName = ['POINTS', 'Ux']
slice_Ux1Display.IsosurfaceValues = [0.08748531341552734]
slice_Ux1Display.SliceFunction = 'Plane'
slice_Ux1Display.Slice = 4

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
slice_Ux1Display.OSPRayScaleFunction.Points = [1.0486473911441863e-09, 0.0, 0.5, 0.0, 2.847604226310929, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_Ux1Display.ScaleTransferFunction.Points = [-0.49689775705337524, 0.0, 0.5, 0.0, 0.6718683838844299, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_Ux1Display.OpacityTransferFunction.Points = [-0.49689775705337524, 0.0, 0.5, 0.0, 0.6718683838844299, 1.0, 0.5, 0.0]

# init the 'Plane' selected for 'SliceFunction'
slice_Ux1Display.SliceFunction.Origin = [x0_dom, y0_dom, Zslice]


# show data from pointVolumeInterpolator_Ux
pointVolumeInterpolator_UxDisplay = Show(pointVolumeInterpolator_Ux, renderView1, 'UniformGridRepresentation')

# trace defaults for the display properties.
pointVolumeInterpolator_UxDisplay.Representation = 'Surface With Edges'
pointVolumeInterpolator_UxDisplay.ColorArrayName = ['POINTS', 'Ux']
pointVolumeInterpolator_UxDisplay.LookupTable = uxLUT
pointVolumeInterpolator_UxDisplay.SelectTCoordArray = 'None'
pointVolumeInterpolator_UxDisplay.SelectNormalArray = 'None'
pointVolumeInterpolator_UxDisplay.SelectTangentArray = 'None'
pointVolumeInterpolator_UxDisplay.OSPRayScaleArray = 'Ux'
pointVolumeInterpolator_UxDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
pointVolumeInterpolator_UxDisplay.SelectOrientationVectors = 'U'
pointVolumeInterpolator_UxDisplay.ScaleFactor = 2.0
pointVolumeInterpolator_UxDisplay.SelectScaleArray = 'Ux'
pointVolumeInterpolator_UxDisplay.GlyphType = 'Arrow'
pointVolumeInterpolator_UxDisplay.GlyphTableIndexArray = 'Ux'
pointVolumeInterpolator_UxDisplay.GaussianRadius = 0.1
pointVolumeInterpolator_UxDisplay.SetScaleArray = ['POINTS', 'Ux']
pointVolumeInterpolator_UxDisplay.ScaleTransferFunction = 'PiecewiseFunction'
pointVolumeInterpolator_UxDisplay.OpacityArray = ['POINTS', 'Ux']
pointVolumeInterpolator_UxDisplay.OpacityTransferFunction = 'PiecewiseFunction'
pointVolumeInterpolator_UxDisplay.DataAxesGrid = 'GridAxesRepresentation'
pointVolumeInterpolator_UxDisplay.PolarAxes = 'PolarAxesRepresentation'
pointVolumeInterpolator_UxDisplay.ScalarOpacityUnitDistance = 0.23534221904681663
pointVolumeInterpolator_UxDisplay.ScalarOpacityFunction = uxPWF
pointVolumeInterpolator_UxDisplay.OpacityArrayName = ['POINTS', 'Ux']
pointVolumeInterpolator_UxDisplay.IsosurfaceValues = [0.05886213178702046]
pointVolumeInterpolator_UxDisplay.SliceFunction = 'Plane'
pointVolumeInterpolator_UxDisplay.Slice = 50

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
pointVolumeInterpolator_UxDisplay.OSPRayScaleFunction.Points = [1.0486473911441863e-09, 0.0, 0.5, 0.0, 2.847604226310929, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
pointVolumeInterpolator_UxDisplay.ScaleTransferFunction.Points = [-0.21641091039631943, 0.0, 0.5, 0.0, 0.3341351739703604, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
pointVolumeInterpolator_UxDisplay.OpacityTransferFunction.Points = [-0.21641091039631943, 0.0, 0.5, 0.0, 0.3341351739703604, 1.0, 0.5, 0.0]

# init the 'Plane' selected for 'SliceFunction'
pointVolumeInterpolator_UxDisplay.SliceFunction.Origin = [x0_dom, y0_dom, Zslice]


# show data from slice_Ux2
slice_Ux2Display = Show(slice_Ux2, renderView1, 'GeometryRepresentation')

# trace defaults for the display properties.
slice_Ux2Display.Representation = 'Surface With Edges'
slice_Ux2Display.ColorArrayName = ['POINTS', 'Ux']
slice_Ux2Display.LookupTable = uxLUT
slice_Ux2Display.SelectTCoordArray = 'None'
slice_Ux2Display.SelectNormalArray = 'None'
slice_Ux2Display.SelectTangentArray = 'None'
slice_Ux2Display.OSPRayScaleArray = 'Ux'
slice_Ux2Display.OSPRayScaleFunction = 'PiecewiseFunction'
slice_Ux2Display.SelectOrientationVectors = 'U'
slice_Ux2Display.ScaleFactor = 2.0033000472933056
slice_Ux2Display.SelectScaleArray = 'Ux'
slice_Ux2Display.GlyphType = 'Arrow'
slice_Ux2Display.GlyphTableIndexArray = 'Ux'
slice_Ux2Display.GaussianRadius = 0.10016500236466527
slice_Ux2Display.SetScaleArray = ['POINTS', 'Ux']
slice_Ux2Display.ScaleTransferFunction = 'PiecewiseFunction'
slice_Ux2Display.OpacityArray = ['POINTS', 'Ux']
slice_Ux2Display.OpacityTransferFunction = 'PiecewiseFunction'
slice_Ux2Display.DataAxesGrid = 'GridAxesRepresentation'
slice_Ux2Display.PolarAxes = 'PolarAxesRepresentation'

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
slice_Ux2Display.OSPRayScaleFunction.Points = [1.0486473911441863e-09, 0.0, 0.5, 0.0, 2.847604226310929, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_Ux2Display.ScaleTransferFunction.Points = [-0.40389879742484885, 0.0, 0.5, 0.0, 0.546821789159444, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_Ux2Display.OpacityTransferFunction.Points = [-0.40389879742484885, 0.0, 0.5, 0.0, 0.546821789159444, 1.0, 0.5, 0.0]


# show color legend
slice_Ux1Display.SetScalarBarVisibility(renderView1, True)

# hide data in view
Hide(slice_Ux1, renderView1)

# show color legend
pointVolumeInterpolator_UxDisplay.SetScalarBarVisibility(renderView1, True)

# hide data in view
Hide(pointVolumeInterpolator_Ux, renderView1)

# show color legend
slice_Ux2Display.SetScalarBarVisibility(renderView1, True)

# hide data in view
Hide(slice_Ux2, renderView1)

# ----------------------------------------------------------------
# setup color maps and opacity mapes used in the visualization
# note: the Get..() functions create a new object, if needed
# ----------------------------------------------------------------




# ----------------------------------------------------------------
# setup the visualization in view 'renderView1' : Uy
# ----------------------------------------------------------------

# show data from slice_Uy1
slice_Uy1Display = Show(slice_Uy1, renderView1, 'UniformGridRepresentation')

# get color transfer function/color map for 'Uy'
uyLUT = GetColorTransferFunction('Uy')
#uyLUT.RGBPoints = [-0.5087437629699707, 0.278431372549, 0.278431372549, 0.858823529412, -0.33991622596979143, 0.0, 0.0, 0.360784313725, -0.17226930111646654, 0.0, 1.0, 1.0, -0.002261151969432884, 0.0, 0.501960784314, 0.0, 0.165385772883892, 1.0, 1.0, 0.0, 0.3342133098840713, 1.0, 0.380392156863, 0.0, 0.5030408468842507, 0.419607843137, 0.0, 0.0, 0.6718683838844299, 0.878431372549, 0.301960784314, 0.301960784314]

uyLUT.RGBPoints = U_color_rainbow
uyLUT.RGBPoints = U_color_blueOrange

uyLUT.ColorSpace = 'RGB'
uyLUT.NumberOfTableValues = 310
uyLUT.ScalarRangeInitialized = 1.0
#uyLUT.RescaleTransferFunctionToDataRange(True)

# this part (RescaleTransferFunction) must be defined before after a Render()
uyLUT.RescaleTransferFunction(-0.9, 0.9)
if case_dir == "mean":
  uyLUT.RescaleTransferFunction(-0.9, 0.9)
#if case_dir == "spatialModes_2modes":
if ((case_dir == "spatialModes_2modes") or (case_dir == "spatialModes_4modes")  or (case_dir == "spatialModes_8modes")  or (case_dir == "spatialModes_16modes")):
  uyLUT.RescaleTransferFunction(-0.2, 0.2)
#if case_dir == "residualSpeed_2":
if ((case_dir == "residualSpeed_2") or (case_dir == "residualSpeed_4")  or (case_dir == "residualSpeed_8")  or (case_dir == "residualSpeed_16")):
  uyLUT.RescaleTransferFunction(-0.7, 0.7)
if case_dir == "sillageDNSRe300":
  uyLUT.RescaleTransferFunction(-0.9, 0.9)
uyLUT.ScalarRangeInitialized = 1.0

# get color legend/bar for uyLUT in view renderView1
uyLUTColorBar = GetScalarBar(uyLUT, renderView1)
uyLUTColorBar.AutoOrient = 0
uyLUTColorBar.Orientation = 'Horizontal'
uyLUTColorBar.WindowLocation = 'Any Location'
uyLUTColorBar.Position = [0.6, 0.02]
uyLUTColorBar.Title = 'Uy'
uyLUTColorBar.ComponentTitle = str(Other_info)
uyLUTColorBar.TitleBold = 1
uyLUTColorBar.TitleFontSize = 20
uyLUTColorBar.AutomaticLabelFormat = 0
uyLUTColorBar.LabelFormat = '%-#7.2f'
uyLUTColorBar.RangeLabelFormat = '%-#7.2f'

# set color bar visibility
uyLUTColorBar.Visibility = 0


# get opacity transfer function/opacity map for 'Uy'
uyPWF = GetOpacityTransferFunction('Uy')
uyPWF.Points = [-0.5087437629699707, 0.0, 0.5, 0.0, 0.6718683838844299, 1.0, 0.5, 0.0]
uyPWF.ScalarRangeInitialized = 1
#uyPWF.RescaleTransferFunctionToDataRange(True)

uyPWF.Points = [1, 0.0, 0.5, 0.0, 8, 1.0, 0.5, 0.0]

# this part (RescaleTransferFunction) must be defined before after a Render()
uyPWF.RescaleTransferFunction(-0.9, 0.9)
if case_dir == "mean":
  uyPWF.RescaleTransferFunction(-0.9, 0.9)
#if case_dir == "spatialModes_2modes":
if ((case_dir == "spatialModes_2modes") or (case_dir == "spatialModes_4modes")  or (case_dir == "spatialModes_8modes")  or (case_dir == "spatialModes_16modes")):
  uyPWF.RescaleTransferFunction(-0.2, 0.2)
#if case_dir == "residualSpeed_2":
if ((case_dir == "residualSpeed_2") or (case_dir == "residualSpeed_4")  or (case_dir == "residualSpeed_8")  or (case_dir == "residualSpeed_16")):
  uyPWF.RescaleTransferFunction(-0.7, 0.7)
if case_dir == "sillageDNSRe300":
  uyPWF.RescaleTransferFunction(-0.9, 0.9)


# trace defaults for the display properties.
slice_Uy1Display.Representation = 'Surface With Edges'
slice_Uy1Display.ColorArrayName = ['POINTS', 'Uy']
slice_Uy1Display.LookupTable = uyLUT
slice_Uy1Display.SelectTCoordArray = 'None'
slice_Uy1Display.SelectNormalArray = 'None'
slice_Uy1Display.SelectTangentArray = 'None'
slice_Uy1Display.OSPRayScaleArray = 'Uy'
slice_Uy1Display.OSPRayScaleFunction = 'PiecewiseFunction'
slice_Uy1Display.SelectOrientationVectors = 'U'
slice_Uy1Display.ScaleFactor = 2.0
slice_Uy1Display.SelectScaleArray = 'Uy'
slice_Uy1Display.GlyphType = 'Arrow'
slice_Uy1Display.GlyphTableIndexArray = 'Uy'
slice_Uy1Display.GaussianRadius = 0.1
slice_Uy1Display.SetScaleArray = ['POINTS', 'Uy']
slice_Uy1Display.ScaleTransferFunction = 'PiecewiseFunction'
slice_Uy1Display.OpacityArray = ['POINTS', 'Uy']
slice_Uy1Display.OpacityTransferFunction = 'PiecewiseFunction'
slice_Uy1Display.DataAxesGrid = 'GridAxesRepresentation'
slice_Uy1Display.PolarAxes = 'PolarAxesRepresentation'
slice_Uy1Display.ScalarOpacityUnitDistance = 0.23534221904681663
slice_Uy1Display.ScalarOpacityFunction = uxPWF
slice_Uy1Display.OpacityArrayName = ['POINTS', 'Uy']
slice_Uy1Display.IsosurfaceValues = [0.08748531341552734]
slice_Uy1Display.SliceFunction = 'Plane'
slice_Uy1Display.Slice = 4

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
slice_Uy1Display.OSPRayScaleFunction.Points = [1.0486473911441863e-09, 0.0, 0.5, 0.0, 2.847604226310929, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_Uy1Display.ScaleTransferFunction.Points = [-0.49689775705337524, 0.0, 0.5, 0.0, 0.6718683838844299, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_Uy1Display.OpacityTransferFunction.Points = [-0.49689775705337524, 0.0, 0.5, 0.0, 0.6718683838844299, 1.0, 0.5, 0.0]

# init the 'Plane' selected for 'SliceFunction'
slice_Uy1Display.SliceFunction.Origin = [x0_dom, y0_dom, Zslice]


# show data from pointVolumeInterpolator_Uy
pointVolumeInterpolator_UyDisplay = Show(pointVolumeInterpolator_Uy, renderView1, 'UniformGridRepresentation')

# trace defaults for the display properties.
pointVolumeInterpolator_UyDisplay.Representation = 'Surface With Edges'
pointVolumeInterpolator_UyDisplay.ColorArrayName = ['POINTS', 'Uy']
pointVolumeInterpolator_UyDisplay.LookupTable = uyLUT
pointVolumeInterpolator_UyDisplay.SelectTCoordArray = 'None'
pointVolumeInterpolator_UyDisplay.SelectNormalArray = 'None'
pointVolumeInterpolator_UyDisplay.SelectTangentArray = 'None'
pointVolumeInterpolator_UyDisplay.OSPRayScaleArray = 'Uy'
pointVolumeInterpolator_UyDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
pointVolumeInterpolator_UyDisplay.SelectOrientationVectors = 'U'
pointVolumeInterpolator_UyDisplay.ScaleFactor = 2.0
pointVolumeInterpolator_UyDisplay.SelectScaleArray = 'Uy'
pointVolumeInterpolator_UyDisplay.GlyphType = 'Arrow'
pointVolumeInterpolator_UyDisplay.GlyphTableIndexArray = 'Uy'
pointVolumeInterpolator_UyDisplay.GaussianRadius = 0.1
pointVolumeInterpolator_UyDisplay.SetScaleArray = ['POINTS', 'Uy']
pointVolumeInterpolator_UyDisplay.ScaleTransferFunction = 'PiecewiseFunction'
pointVolumeInterpolator_UyDisplay.OpacityArray = ['POINTS', 'Uy']
pointVolumeInterpolator_UyDisplay.OpacityTransferFunction = 'PiecewiseFunction'
pointVolumeInterpolator_UyDisplay.DataAxesGrid = 'GridAxesRepresentation'
pointVolumeInterpolator_UyDisplay.PolarAxes = 'PolarAxesRepresentation'
pointVolumeInterpolator_UyDisplay.ScalarOpacityUnitDistance = 0.23534221904681663
pointVolumeInterpolator_UyDisplay.ScalarOpacityFunction = uxPWF
pointVolumeInterpolator_UyDisplay.OpacityArrayName = ['POINTS', 'Uy']
pointVolumeInterpolator_UyDisplay.IsosurfaceValues = [0.05886213178702046]
pointVolumeInterpolator_UyDisplay.SliceFunction = 'Plane'
pointVolumeInterpolator_UyDisplay.Slice = 50

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
pointVolumeInterpolator_UyDisplay.OSPRayScaleFunction.Points = [1.0486473911441863e-09, 0.0, 0.5, 0.0, 2.847604226310929, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
pointVolumeInterpolator_UyDisplay.ScaleTransferFunction.Points = [-0.21641091039631943, 0.0, 0.5, 0.0, 0.3341351739703604, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
pointVolumeInterpolator_UyDisplay.OpacityTransferFunction.Points = [-0.21641091039631943, 0.0, 0.5, 0.0, 0.3341351739703604, 1.0, 0.5, 0.0]

# init the 'Plane' selected for 'SliceFunction'
pointVolumeInterpolator_UyDisplay.SliceFunction.Origin = [x0_dom, y0_dom, Zslice]


# show data from slice_Uy2
slice_Uy2Display = Show(slice_Uy2, renderView1, 'GeometryRepresentation')

# trace defaults for the display properties.
slice_Uy2Display.Representation = 'Surface With Edges'
slice_Uy2Display.ColorArrayName = ['POINTS', 'Uy']
slice_Uy2Display.LookupTable = uyLUT
slice_Uy2Display.SelectTCoordArray = 'None'
slice_Uy2Display.SelectNormalArray = 'None'
slice_Uy2Display.SelectTangentArray = 'None'
slice_Uy2Display.OSPRayScaleArray = 'Uy'
slice_Uy2Display.OSPRayScaleFunction = 'PiecewiseFunction'
slice_Uy2Display.SelectOrientationVectors = 'U'
slice_Uy2Display.ScaleFactor = 2.0033000472933056
slice_Uy2Display.SelectScaleArray = 'Uy'
slice_Uy2Display.GlyphType = 'Arrow'
slice_Uy2Display.GlyphTableIndexArray = 'Uy'
slice_Uy2Display.GaussianRadius = 0.10016500236466527
slice_Uy2Display.SetScaleArray = ['POINTS', 'Uy']
slice_Uy2Display.ScaleTransferFunction = 'PiecewiseFunction'
slice_Uy2Display.OpacityArray = ['POINTS', 'Uy']
slice_Uy2Display.OpacityTransferFunction = 'PiecewiseFunction'
slice_Uy2Display.DataAxesGrid = 'GridAxesRepresentation'
slice_Uy2Display.PolarAxes = 'PolarAxesRepresentation'

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
slice_Uy2Display.OSPRayScaleFunction.Points = [1.0486473911441863e-09, 0.0, 0.5, 0.0, 2.847604226310929, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_Uy2Display.ScaleTransferFunction.Points = [-0.40389879742484885, 0.0, 0.5, 0.0, 0.546821789159444, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_Uy2Display.OpacityTransferFunction.Points = [-0.40389879742484885, 0.0, 0.5, 0.0, 0.546821789159444, 1.0, 0.5, 0.0]


# show color legend
slice_Uy1Display.SetScalarBarVisibility(renderView1, True)

# hide data in view
Hide(slice_Uy1, renderView1)

# show color legend
pointVolumeInterpolator_UyDisplay.SetScalarBarVisibility(renderView1, True)

# hide data in view
Hide(pointVolumeInterpolator_Uy, renderView1)

# show color legend
slice_Uy1Display.SetScalarBarVisibility(renderView1, True)

# hide data in view
Hide(slice_Uy2, renderView1)


# ----------------------------------------------------------------
# setup color maps and opacity mapes used in the visualization
# note: the Get..() functions create a new object, if needed
# ----------------------------------------------------------------

########## first view  =slice_Ux1 
if code_view_slice_Ux1 == 1:
  
  # hide data in view : Uy
  Hide(slice_Uy1, renderView1)
  slice_Uy1Display.SetScalarBarVisibility(renderView1, False)
  Hide(pointVolumeInterpolator_Uy, renderView1)
  pointVolumeInterpolator_UyDisplay.SetScalarBarVisibility(renderView1, False)
  Hide(slice_Uy2, renderView1)
  slice_Uy2Display.SetScalarBarVisibility(renderView1, False)
  
  uyLUTColorBar.Visibility = 0

  # hide data in view : Ux
  Hide(pointVolumeInterpolator_Ux, renderView1)
  pointVolumeInterpolator_UxDisplay.SetScalarBarVisibility(renderView1, False)
  Hide(slice_Ux2, renderView1)
  slice_Ux2Display.SetScalarBarVisibility(renderView1, False)

  Show(slice_Ux1, renderView1)
  slice_Ux1Display.SetScalarBarVisibility(renderView1, True)
  
  uxLUTColorBar.Visibility = 1
  #pointVolumeInterpolator_UxDisplay.SetScalarBarVisibility(renderView1, True)
  
  SetActiveSource(slice_Ux1)
  Render()
  view = GetActiveView()
  view.ViewSize = [ viewSize_length, viewSize_height ]
  
  # this part (RescaleTransferFunction) must be defined before after a Render()
  uxLUT.RescaleTransferFunction(-0.9, 1.9)
  uxPWF.RescaleTransferFunction(-0.9, 1.9)
  if case_dir == "mean":
    uxLUT.RescaleTransferFunction(-0.9, 1.9)
    uxPWF.RescaleTransferFunction(-0.9, 1.9)
  #if case_dir == "spatialModes_2modes":
  if ((case_dir == "spatialModes_2modes") or (case_dir == "spatialModes_4modes")  or (case_dir == "spatialModes_8modes")  or (case_dir == "spatialModes_16modes")):
    uxLUT.RescaleTransferFunction(-0.2, 0.2)
    uxPWF.RescaleTransferFunction(-0.2, 0.2)
  #if case_dir == "residualSpeed_2":
  if ((case_dir == "residualSpeed_2") or (case_dir == "residualSpeed_4")  or (case_dir == "residualSpeed_8")  or (case_dir == "residualSpeed_16")):
    uxLUT.RescaleTransferFunction(-0.7, 0.7)
    uxPWF.RescaleTransferFunction(-0.7, 0.7)
  if case_dir == "sillageDNSRe300":
    uxLUT.RescaleTransferFunction(-0.9, 1.9)
    uxPWF.RescaleTransferFunction(-0.9, 1.9)
  
  if code_view_withGrid == 1:
    slice_Ux1Display.Representation = 'Surface With Edges'
    slice_Ux1Display.PointSize = 1.0
    WriteImage('Ux_calculator_withGrid.png', Magnification=0.5)

  slice_Ux1Display.Representation = 'Surface'
  slice_Ux1Display.PointSize = 1.0
  WriteImage('Ux_calculator_withoutGrid.png', Magnification=0.5)
  
########## first view  =slice_Uy1 
if code_view_slice_Uy1 == 1:
  
  # hide data in view : Ux
  Hide(slice_Ux1, renderView1)
  slice_Ux1Display.SetScalarBarVisibility(renderView1, False)
  Hide(pointVolumeInterpolator_Ux, renderView1)
  pointVolumeInterpolator_UxDisplay.SetScalarBarVisibility(renderView1, False)
  Hide(slice_Ux2, renderView1)
  slice_Ux2Display.SetScalarBarVisibility(renderView1, False)
  
  uxLUTColorBar.Visibility = 0

  # hide data in view : Uy
  Hide(pointVolumeInterpolator_Uy, renderView1)
  pointVolumeInterpolator_UyDisplay.SetScalarBarVisibility(renderView1, False)
  Hide(slice_Uy2, renderView1)
  slice_Uy2Display.SetScalarBarVisibility(renderView1, False)

  Show(slice_Uy1, renderView1)
  slice_Uy1Display.SetScalarBarVisibility(renderView1, True)
  
  uyLUTColorBar.Visibility = 1
  uyLUTColorBar.Position = [0.6, 0.02]
  
  SetActiveSource(slice_Uy1)
  Render()
  view = GetActiveView()
  view.ViewSize = [ viewSize_length, viewSize_height ]
  
  # this part (RescaleTransferFunction) must be defined before after a Render()
  uyLUT.RescaleTransferFunction(-0.9, 0.9)
  uyPWF.RescaleTransferFunction(-0.9, 0.9)
  if case_dir == "mean":
    uyLUT.RescaleTransferFunction(-0.9, 0.9)
    uyPWF.RescaleTransferFunction(-0.9, 0.9)
  #if case_dir == "spatialModes_2modes":
  if ((case_dir == "spatialModes_2modes") or (case_dir == "spatialModes_4modes")  or (case_dir == "spatialModes_8modes")  or (case_dir == "spatialModes_16modes")):
    uyLUT.RescaleTransferFunction(-0.2, 0.2)
    uyPWF.RescaleTransferFunction(-0.2, 0.2)
  #if case_dir == "residualSpeed_2":
  if ((case_dir == "residualSpeed_2") or (case_dir == "residualSpeed_4")  or (case_dir == "residualSpeed_8")  or (case_dir == "residualSpeed_16")):
    uyLUT.RescaleTransferFunction(-0.7, 0.7)
    uyPWF.RescaleTransferFunction(-0.7, 0.7)
  if case_dir == "sillageDNSRe300":
    uyLUT.RescaleTransferFunction(-0.9, 0.9)
    uyPWF.RescaleTransferFunction(-0.9, 0.9)
  
  if code_view_withGrid == 1:
    slice_Uy1Display.Representation = 'Surface With Edges'
    slice_Uy1Display.PointSize = 1.0
    WriteImage('Uy_calculator_withGrid.png', Magnification=0.5)

  slice_Uy1Display.Representation = 'Surface'
  slice_Uy1Display.PointSize = 1.0
  WriteImage('Uy_calculator_withoutGrid.png', Magnification=0.5)
# ----------------------------------------------------------------

########## second view  =pointVolumeInterpolator_Ux
if code_view_pointVolumeInterpolator_Ux == 1:
  
  # hide data in view : Uy
  Hide(slice_Uy1, renderView1)
  slice_Uy1Display.SetScalarBarVisibility(renderView1, False)
  Hide(pointVolumeInterpolator_Uy, renderView1)
  pointVolumeInterpolator_UyDisplay.SetScalarBarVisibility(renderView1, False)
  Hide(slice_Uy2, renderView1)
  slice_Uy2Display.SetScalarBarVisibility(renderView1, False)
  
  uyLUTColorBar.Visibility = 0

  # hide data in view : Ux
  slice_Ux1Display.Opacity = 0.3
  Show(slice_Ux1, renderView1)
  slice_Ux1Display.SetScalarBarVisibility(renderView1, True)
  Hide(slice_Ux2, renderView1)
  slice_Ux2Display.SetScalarBarVisibility(renderView1, False)

  Show(pointVolumeInterpolator_Ux, renderView1)
  pointVolumeInterpolator_UxDisplay.SetScalarBarVisibility(renderView1, True)
  
  uxLUTColorBar.Visibility = 1
  
  SetActiveSource(pointVolumeInterpolator_Ux)
  Render()
  view = GetActiveView()
  view.ViewSize = [ viewSize_length, viewSize_height ]
  
  # this part (RescaleTransferFunction) must be defined before after a Render()
  uxLUT.RescaleTransferFunction(-0.9, 1.9)
  uxPWF.RescaleTransferFunction(-0.9, 1.9)
  if case_dir == "mean":
    uxLUT.RescaleTransferFunction(-0.9, 1.9)
    uxPWF.RescaleTransferFunction(-0.9, 1.9)
  #if case_dir == "spatialModes_2modes":
  if ((case_dir == "spatialModes_2modes") or (case_dir == "spatialModes_4modes")  or (case_dir == "spatialModes_8modes")  or (case_dir == "spatialModes_16modes")):
    uxLUT.RescaleTransferFunction(-0.2, 0.2)
    uxPWF.RescaleTransferFunction(-0.2, 0.2)
  #if case_dir == "residualSpeed_2":
  if ((case_dir == "residualSpeed_2") or (case_dir == "residualSpeed_4")  or (case_dir == "residualSpeed_8")  or (case_dir == "residualSpeed_16")):
    uxLUT.RescaleTransferFunction(-0.7, 0.7)
    uxPWF.RescaleTransferFunction(-0.7, 0.7)
  if case_dir == "sillageDNSRe300":
    uxLUT.RescaleTransferFunction(-0.9, 1.9)
    uxPWF.RescaleTransferFunction(-0.9, 1.9)

  if code_view_withGrid == 1:
    pointVolumeInterpolator_UxDisplay.Representation = 'Surface With Edges'
    pointVolumeInterpolator_UxDisplay.PointSize = pointSize_for_SurfaceDisplay
    WriteImage('Ux_calculator_pointVolumeInterpolator_withGrid.png', Magnification=0.5)

  if mode_view_NoGrid == "SURFACE":
    pointVolumeInterpolator_UxDisplay.Representation = 'Surface'
    pointVolumeInterpolator_UxDisplay.PointSize = pointSize_for_SurfaceDisplay

  if mode_view_NoGrid == "POINTS":
    pointVolumeInterpolator_UxDisplay.Representation = 'Points'
    pointVolumeInterpolator_UxDisplay.PointSize = pointSize_for_PointsDisplay
  
  WriteImage('Ux_calculator_pointVolumeInterpolator_withoutGrid.png', Magnification=0.5)
  
########## second view  =pointVolumeInterpolator_Uy
if code_view_pointVolumeInterpolator_Uy == 1:
  
  # hide data in view : Ux
  Hide(slice_Ux1, renderView1)
  slice_Ux1Display.SetScalarBarVisibility(renderView1, False)
  Hide(pointVolumeInterpolator_Ux, renderView1)
  pointVolumeInterpolator_UxDisplay.SetScalarBarVisibility(renderView1, False)
  Hide(slice_Ux2, renderView1)
  slice_Ux2Display.SetScalarBarVisibility(renderView1, False)
  
  uxLUTColorBar.Visibility = 0

  # hide data in view : Uy
  slice_Uy1Display.Opacity = 0.3
  slice_Uy1Display.Representation = 'Surface'
  Show(slice_Uy1, renderView1)
  slice_Uy1Display.SetScalarBarVisibility(renderView1, True)
  Hide(slice_Uy2, renderView1)
  slice_Uy2Display.SetScalarBarVisibility(renderView1, False)

  Show(pointVolumeInterpolator_Uy, renderView1)
  pointVolumeInterpolator_UyDisplay.SetScalarBarVisibility(renderView1, True)
  
  uyLUTColorBar.Visibility = 1
  
  SetActiveSource(pointVolumeInterpolator_Uy)
  Render()
  view = GetActiveView()
  view.ViewSize = [ viewSize_length, viewSize_height ]
  
  # this part (RescaleTransferFunction) must be defined before after a Render()
  uyLUT.RescaleTransferFunction(-0.9, 0.9)
  uyPWF.RescaleTransferFunction(-0.9, 0.9)
  if case_dir == "mean":
    uyLUT.RescaleTransferFunction(-0.9, 0.9)
    uyPWF.RescaleTransferFunction(-0.9, 0.9)
  #if case_dir == "spatialModes_2modes":
  if ((case_dir == "spatialModes_2modes") or (case_dir == "spatialModes_4modes")  or (case_dir == "spatialModes_8modes")  or (case_dir == "spatialModes_16modes")):
    uyLUT.RescaleTransferFunction(-0.2, 0.2)
    uyPWF.RescaleTransferFunction(-0.2, 0.2)
  #if case_dir == "residualSpeed_2":
  if ((case_dir == "residualSpeed_2") or (case_dir == "residualSpeed_4")  or (case_dir == "residualSpeed_8")  or (case_dir == "residualSpeed_16")):
    uyLUT.RescaleTransferFunction(-0.7, 0.7)
    uyPWF.RescaleTransferFunction(-0.7, 0.7)
  if case_dir == "sillageDNSRe300":
    uyLUT.RescaleTransferFunction(-0.9, 0.9)
    uyPWF.RescaleTransferFunction(-0.9, 0.9)
  
  if code_view_withGrid == 1:
    pointVolumeInterpolator_UyDisplay.Representation = 'Surface With Edges'
    pointVolumeInterpolator_UyDisplay.PointSize = pointSize_for_SurfaceDisplay
    WriteImage('Uy_calculator_pointVolumeInterpolator_withGrid.png', Magnification=0.5)

  if mode_view_NoGrid == "SURFACE":
    pointVolumeInterpolator_UyDisplay.Representation = 'Surface'
    pointVolumeInterpolator_UyDisplay.PointSize = pointSize_for_SurfaceDisplay

  if mode_view_NoGrid == "POINTS":
    pointVolumeInterpolator_UyDisplay.Representation = 'Points'
    pointVolumeInterpolator_UyDisplay.PointSize = pointSize_for_PointsDisplay
  
  WriteImage('Uy_calculator_pointVolumeInterpolator_withoutGrid.png', Magnification=0.5)

########## third view  =slice_Ux2
if code_view_slice_Ux2 == 1:
  
  # hide data in view : Uy
  Hide(slice_Uy1, renderView1)
  slice_Uy1Display.SetScalarBarVisibility(renderView1, False)
  Hide(pointVolumeInterpolator_Uy, renderView1)
  pointVolumeInterpolator_UyDisplay.SetScalarBarVisibility(renderView1, False)
  Hide(slice_Uy2, renderView1)
  slice_Uy2Display.SetScalarBarVisibility(renderView1, False)
  
  uyLUTColorBar.Visibility = 0

  # hide data in view : Ux
  slice_Ux1Display.Opacity = 0.3
  slice_Ux1Display.Representation = 'Surface'
  Show(slice_Ux1, renderView1)
  slice_Ux1Display.SetScalarBarVisibility(renderView1, True)
  Hide(pointVolumeInterpolator_Ux, renderView1)
  pointVolumeInterpolator_UxDisplay.SetScalarBarVisibility(renderView1, False)

  Show(slice_Ux2, renderView1)
  slice_Ux2Display.SetScalarBarVisibility(renderView1, True)
  
  uxLUTColorBar.Visibility = 1
  
  SetActiveSource(slice_Ux2)
  Render()
  view = GetActiveView()
  view.ViewSize = [ viewSize_length, viewSize_height ]
  
  # this part (RescaleTransferFunction) must be defined before after a Render()
  uxLUT.RescaleTransferFunction(-0.9, 1.9)
  uxPWF.RescaleTransferFunction(-0.9, 1.9)
  if case_dir == "mean":
    uxLUT.RescaleTransferFunction(-0.9, 1.9)
    uxPWF.RescaleTransferFunction(-0.9, 1.9)
  #if case_dir == "spatialModes_2modes":
  if ((case_dir == "spatialModes_2modes") or (case_dir == "spatialModes_4modes")  or (case_dir == "spatialModes_8modes")  or (case_dir == "spatialModes_16modes")):
    uxLUT.RescaleTransferFunction(-0.2, 0.2)
    uxPWF.RescaleTransferFunction(-0.2, 0.2)
  #if case_dir == "residualSpeed_2":
  if ((case_dir == "residualSpeed_2") or (case_dir == "residualSpeed_4")  or (case_dir == "residualSpeed_8")  or (case_dir == "residualSpeed_16")):
    uxLUT.RescaleTransferFunction(-0.7, 0.7)
    uxPWF.RescaleTransferFunction(-0.7, 0.7)
  if case_dir == "sillageDNSRe300":
    uxLUT.RescaleTransferFunction(-0.9, 1.9)
    uxPWF.RescaleTransferFunction(-0.9, 1.9)

  if code_view_withGrid == 1:
    slice_Ux2Display.Representation = 'Surface With Edges'
    slice_Ux2Display.PointSize = pointSize_for_SurfaceDisplay
    WriteImage('Ux_calculator_pointVolumeInterpolator_slicepointSize_for_PointsDisplay_withGrid.png', Magnification=0.5)

  if mode_view_NoGrid == "SURFACE":
    slice_Ux2Display.Representation = 'Surface'
    slice_Ux2Display.PointSize = pointSize_for_SurfaceDisplay

  if mode_view_NoGrid == "POINTS":
    slice_Ux2Display.Representation = 'Points'
    slice_Ux2Display.PointSize = pointSize_for_PointsDisplay
  
  WriteImage('Ux_calculator_pointVolumeInterpolator_slice_withoutGrid.png', Magnification=0.5)
  
########## third view  =slice_Uy2
if code_view_slice_Uy2 == 1:
  
  # hide data in view : Ux
  Hide(slice_Ux1, renderView1)
  slice_Ux1Display.SetScalarBarVisibility(renderView1, False)
  Hide(pointVolumeInterpolator_Ux, renderView1)
  pointVolumeInterpolator_UxDisplay.SetScalarBarVisibility(renderView1, False)
  Hide(slice_Ux2, renderView1)
  slice_Ux2Display.SetScalarBarVisibility(renderView1, False)
  
  uxLUTColorBar.Visibility = 0

  # hide data in view : Uy
  slice_Uy1Display.Opacity = 0.3
  slice_Uy1Display.Representation = 'Surface'
  Show(slice_Uy1, renderView1)
  slice_Uy1Display.SetScalarBarVisibility(renderView1, True)
  Hide(pointVolumeInterpolator_Uy, renderView1)
  pointVolumeInterpolator_UyDisplay.SetScalarBarVisibility(renderView1, False)

  Show(slice_Uy2, renderView1)
  slice_Uy2Display.SetScalarBarVisibility(renderView1, True)
  
  uyLUTColorBar.Visibility = 1
  
  SetActiveSource(slice_Uy2)
  Render()
  view = GetActiveView()
  view.ViewSize = [ viewSize_length, viewSize_height ]
  
  # this part (RescaleTransferFunction) must be defined before after a Render()
  uyLUT.RescaleTransferFunction(-0.9, 0.9)
  uyPWF.RescaleTransferFunction(-0.9, 0.9)
  if case_dir == "mean":
    uyLUT.RescaleTransferFunction(-0.9, 0.9)
    uyPWF.RescaleTransferFunction(-0.9, 0.9)
  #if case_dir == "spatialModes_2modes":
  if ((case_dir == "spatialModes_2modes") or (case_dir == "spatialModes_4modes")  or (case_dir == "spatialModes_8modes")  or (case_dir == "spatialModes_16modes")):
    uyLUT.RescaleTransferFunction(-0.2, 0.2)
    uyPWF.RescaleTransferFunction(-0.2, 0.2)
  #if case_dir == "residualSpeed_2":
  if ((case_dir == "residualSpeed_2") or (case_dir == "residualSpeed_4")  or (case_dir == "residualSpeed_8")  or (case_dir == "residualSpeed_16")):
    uyLUT.RescaleTransferFunction(-0.7, 0.7)
    uyPWF.RescaleTransferFunction(-0.7, 0.7)
  if case_dir == "sillageDNSRe300":
    uyLUT.RescaleTransferFunction(-0.9, 0.9)
    uyPWF.RescaleTransferFunction(-0.9, 0.9)

  if code_view_withGrid == 1:
    slice_Uy2Display.Representation = 'Surface With Edges'
    slice_Uy2Display.PointSize = pointSize_for_SurfaceDisplay
    WriteImage('Uy_calculator_pointVolumeInterpolator_slice_withGrid.png', Magnification=0.5)

  if mode_view_NoGrid == "SURFACE":
    slice_Uy2Display.Representation = 'Surface'
    slice_Uy2Display.PointSize = pointSize_for_SurfaceDisplay

  if mode_view_NoGrid == "POINTS":
    slice_Uy2Display.Representation = 'Points'
    slice_Uy2Display.PointSize = pointSize_for_PointsDisplay
  
  WriteImage('Uy_calculator_pointVolumeInterpolator_slice_withoutGrid.png', Magnification=0.5)

# ----------------------------------------------------------------

# ----------------------------------------------------------------
# CSV files

# Cf. https://kitware.github.io/paraview-docs/latest/python/paraview.simple.DataSetCSVWriter.html

# files Ux : x,y,z,Ux -> AddMetaData=1
# files Uy : Uy -> AddMetaData=0

if code_csv_slice_Ux1 == 1:
 
  # SaveData('slice_Ux1.csv',proxy=slice_Ux1)
  
  SaveData('slice_Ux1.csv',
  proxy=slice_Ux1,
  ChooseArraysToWrite=1,
  PointDataArrays=['Ux'],
  CellDataArrays=[],
  FieldDataArrays=[],
  VertexDataArrays=[],
  EdgeDataArrays=[],
  RowDataArrays=[],
  Precision=6,
  WriteTimeSteps=10,
  Filenamesuffix='%d',
  UseScientificNotation=0,
  FieldAssociation='Point Data',
  AddMetaData=1, 
  AddTime=0)
 
if code_csv_slice_Uy1 == 1:
 
  # SaveData('slice_Uy1.csv',proxy=slice_Uy1)
  
  SaveData('slice_Uy1.csv',
  proxy=slice_Uy1,
  ChooseArraysToWrite=1,
  PointDataArrays=['Uy'],
  CellDataArrays=[],
  FieldDataArrays=[],
  VertexDataArrays=[],
  EdgeDataArrays=[],
  RowDataArrays=[],
  Precision=6,
  WriteTimeSteps=10,
  Filenamesuffix='%d',
  UseScientificNotation=0,
  FieldAssociation='Point Data',
  AddMetaData=0, 
  AddTime=0)

if code_csv_slice_Ux2 == 1:
  
  # SaveData('slice_Ux2.csv',proxy=slice_Ux2)
  
  SaveData('slice_Ux2.csv',
  proxy=slice_Ux2,
  ChooseArraysToWrite=1,
  PointDataArrays=['Ux'],
  CellDataArrays=[],
  FieldDataArrays=[],
  VertexDataArrays=[],
  EdgeDataArrays=[],
  RowDataArrays=[],
  Precision=6,
  WriteTimeSteps=10,
  Filenamesuffix='%d',
  UseScientificNotation=0,
  FieldAssociation='Point Data',
  AddMetaData=1, 
  AddTime=0)

if code_csv_slice_Uy2 == 1:
  
  # SaveData('slice_Uy2.csv',proxy=slice_Uy2)
  
  SaveData('slice_Uy2.csv',
  proxy=slice_Uy2,
  ChooseArraysToWrite=1,
  PointDataArrays=['Uy'],
  CellDataArrays=[],
  FieldDataArrays=[],
  VertexDataArrays=[],
  EdgeDataArrays=[],
  RowDataArrays=[],
  Precision=6,
  WriteTimeSteps=10,
  Filenamesuffix='%d',
  UseScientificNotation=0,
  FieldAssociation='Point Data',
  AddMetaData=0, 
  AddTime=0)
  
  if case_dir == "residualSpeed_2":
  
    # SaveData('slice_Uz2.csv',proxy=slice_Uz2)
    
    SaveData('slice_Uz2.csv',
    proxy=slice_Uz2,
    ChooseArraysToWrite=1,
    PointDataArrays=['Uz'],
    CellDataArrays=[],
    FieldDataArrays=[],
    VertexDataArrays=[],
    EdgeDataArrays=[],
    RowDataArrays=[],
    Precision=6,
    WriteTimeSteps=10,
    Filenamesuffix='%d',
    UseScientificNotation=0,
    FieldAssociation='Point Data',
    AddMetaData=0, 
    AddTime=0)


if __name__ == '__main__':
    # generate extracts
    SaveExtracts(ExtractsOutputDirectory='extracts')
