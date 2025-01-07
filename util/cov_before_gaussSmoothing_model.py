######################################
#
# Laurence Wallian - ACTA - OPAALE - INRAE Rennes - Juin 2022-Février 2023
#
######################################
#
# MORAANE : Openfoam DNS file -> synthetic PIV file
#
#     This script creates PNG covariance files from openfoam time/U files
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
#      case_dir=CASE_DIR_NAME (for example residualSpeed_2)
#
#    case directory :
#      last_dir=LAST_DIR_NAME : present directory without PATH
#      path_case=PATH_DIR_NAME : PATH containing the present directory
#
#    cylinder type  (for target view and pink cylinder drawing)
#      x0_cyl=XCYL_VALUE : x cylinder center
#      y0_cy=YCYL_VALUE : y cylinder center 
# 
#    time=[t_first:t_last]
#      t_first=T_FIRST_VALUE : first time 
#      t_last=T_LAST_VALUE : last time
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
#
######################################
#
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

# case name : for example residualSpeed_2
case_dir = "CASE_DIR_NAME"

# directory name for case : for example residualSpeed_2_t100-t200
last_dir="LAST_DIR_NAME"

# PATH for last_dir : for example .../RedLUM/data_Redlum_cpp/DNS${Re}-GeoLES3900/ROMDNS-vNewCleanDEIMTest
path_case="PATH_DIR_NAME"

# -> file name
file_name = str(path_case)+str("/")+ str(last_dir)+str("/")+str(last_dir)+str(".foam")

## cylinder

# cylinder center (Example : center = ( 2.5, 6 ) )
x0_cyl=XCYL_VALUE
y0_cyl=YCYL_VALUE

## time

# time =[t_first:t_last]
t_first=T_FIRST_VALUE
t_last=T_LAST_VALUE

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

# create a new 'Calculator' : vector Uxyz1=(ux*uy, uy*uz, uz*ux )
calculator1 = Calculator(registrationName='Vector_Uxy_Uyz_Uzx', Input=base_Calcfoam)
calculator1.ResultArrayName = 'Uxyz1'
calculator1.Function = 'U_X*U_Y*iHat+U_Y*U_Z*jHat+U_Z*U_X*kHat'

# create a new 'Temporal Statistics' => mean( ux, uy, uz ) and mean( ux*uy, uy*uz, uz*ux )
temporalStatistics1 = TemporalStatistics(registrationName='TemporalStatistics1', Input=calculator1)
temporalStatistics1.ComputeMinimum = 0
temporalStatistics1.ComputeMaximum = 0




# mean(ux*uy)
temporalStatistics11 = Calculator(registrationName='Mean_xy', Input=temporalStatistics1)
temporalStatistics11.ResultArrayName = 'mean_xy'
temporalStatistics11.Function = 'Uxyz1_average_X'

# create a new 'Point Volume Interpolator'
box_mean_xy = PointVolumeInterpolator(registrationName='Box_mean_xy', Input=temporalStatistics11,
    Source='Bounded Volume')
box_mean_xy.Kernel = 'GaussianKernel'
box_mean_xy.Locator = 'Static Point Locator'

# init the 'GaussianKernel' selected for 'Kernel'
box_mean_xy.Kernel.Radius = Radius

# init the 'Bounded Volume' selected for 'Source'
box_mean_xy.Source.Origin = [Origin_X, Origin_Y, Origin_Z]
box_mean_xy.Source.Scale = [Scale_X, Scale_Y, Scale_Z]

#box_mean_xy.Source.RefinementMode = 'Use cell-size'
#box_mean_xy.Source.CellSize = 0.0470 # slice : 298x184x1 points / PIV ref : 295 x 182 points

box_mean_xy.Source.RefinementMode = 'Use resolution'
box_mean_xy.Source.Resolution = [Resolution_X, Resolution_Y, Resolution_Z]

box_mean_xy.NullPointsStrategy = 0 # ->MaskPoints (MASK_POINTS)
#box_mean_xy.NullPointsStrategy = 1 # -> NullPoint (NULL_VALUE)
#box_mean_xy.NullPointsStrategy = 2 # -> CLOSEST_POINT
box_mean_xy.NullValue = 0.0

# create a new 'Slice'
slice_Mean_xy = Slice(registrationName='Slice_Mean_xy', Input=box_mean_xy)
slice_Mean_xy.SliceType = 'Plane'
slice_Mean_xy.HyperTreeGridSlicer = 'Plane'
slice_Mean_xy.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_Mean_xy.SliceType.Origin = [x0_dom, y0_dom, Zslice]
slice_Mean_xy.SliceType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_Mean_xy.HyperTreeGridSlicer.Origin = [x0_dom, y0_dom, Zslice]


# mean(uy*uz)
temporalStatistics12 = Calculator(registrationName='Mean_yz', Input=temporalStatistics1)
temporalStatistics12.ResultArrayName = 'mean_yz'
temporalStatistics12.Function = 'Uxyz1_average_Y'

# create a new 'Point Volume Interpolator'
box_mean_yz = PointVolumeInterpolator(registrationName='Box_mean_yz', Input=temporalStatistics12,
    Source='Bounded Volume')
box_mean_yz.Kernel = 'GaussianKernel'
box_mean_yz.Locator = 'Static Point Locator'

# init the 'GaussianKernel' selected for 'Kernel'
box_mean_yz.Kernel.Radius = Radius

# init the 'Bounded Volume' selected for 'Source'
box_mean_yz.Source.Origin = [Origin_X, Origin_Y, Origin_Z]
box_mean_yz.Source.Scale = [Scale_X, Scale_Y, Scale_Z]

box_mean_yz.Source.RefinementMode = 'Use resolution'
box_mean_yz.Source.Resolution = [Resolution_X, Resolution_Y, Resolution_Z]

box_mean_yz.NullPointsStrategy = 0 # ->MaskPoints (MASK_POINTS)
box_mean_yz.NullValue = 0.0

# create a new 'Slice'
slice_Mean_yz = Slice(registrationName='Slice_Mean_yz', Input=box_mean_yz)
slice_Mean_yz.SliceType = 'Plane'
slice_Mean_yz.HyperTreeGridSlicer = 'Plane'
slice_Mean_yz.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_Mean_yz.SliceType.Origin = [x0_dom, y0_dom, Zslice]
slice_Mean_yz.SliceType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_Mean_yz.HyperTreeGridSlicer.Origin = [x0_dom, y0_dom, Zslice]


# mean(uz*ux)
temporalStatistics13 = Calculator(registrationName='Mean_zx', Input=temporalStatistics1)
temporalStatistics13.ResultArrayName = 'mean_zx'
temporalStatistics13.Function = 'Uxyz1_average_Z'

# create a new 'Point Volume Interpolator'
box_mean_zx = PointVolumeInterpolator(registrationName='Box_mean_zx', Input=temporalStatistics13,
    Source='Bounded Volume')
box_mean_zx.Kernel = 'GaussianKernel'
box_mean_zx.Locator = 'Static Point Locator'

# init the 'GaussianKernel' selected for 'Kernel'
box_mean_zx.Kernel.Radius = Radius

# init the 'Bounded Volume' selected for 'Source'
box_mean_zx.Source.Origin = [Origin_X, Origin_Y, Origin_Z]
box_mean_zx.Source.Scale = [Scale_X, Scale_Y, Scale_Z]

box_mean_zx.Source.RefinementMode = 'Use resolution'
box_mean_zx.Source.Resolution = [Resolution_X, Resolution_Y, Resolution_Z]

box_mean_zx.NullPointsStrategy = 0 # ->MaskPoints (MASK_POINTS)
box_mean_zx.NullValue = 0.0

# create a new 'Slice'
slice_Mean_zx = Slice(registrationName='Slice_Mean_zx', Input=box_mean_zx)
slice_Mean_zx.SliceType = 'Plane'
slice_Mean_zx.HyperTreeGridSlicer = 'Plane'
slice_Mean_zx.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_Mean_zx.SliceType.Origin = [x0_dom, y0_dom, Zslice]
slice_Mean_zx.SliceType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_Mean_zx.HyperTreeGridSlicer.Origin = [x0_dom, y0_dom, Zslice]


# create a new 'Calculator' : scalar cov(ux*uy)=mean(ux*uy)-mean(ux)*mean(uy)
calculator11 = Calculator(registrationName='Cov_xy', Input=temporalStatistics1)
calculator11.ResultArrayName = 'cov_xy'
calculator11.Function = 'Uxyz1_average_X-U_average_X*U_average_Y'

# create a new 'Point Volume Interpolator'
box_cov_xy = PointVolumeInterpolator(registrationName='Box_cov_xy', Input=calculator11,
    Source='Bounded Volume')
box_cov_xy.Kernel = 'GaussianKernel'
box_cov_xy.Locator = 'Static Point Locator'

# init the 'GaussianKernel' selected for 'Kernel'
box_cov_xy.Kernel.Radius = Radius

# init the 'Bounded Volume' selected for 'Source'
box_cov_xy.Source.Origin = [Origin_X, Origin_Y, Origin_Z]
box_cov_xy.Source.Scale = [Scale_X, Scale_Y, Scale_Z]

box_cov_xy.Source.RefinementMode = 'Use resolution'
box_cov_xy.Source.Resolution = [Resolution_X, Resolution_Y, Resolution_Z]

box_cov_xy.NullPointsStrategy = 0 # ->MaskPoints (MASK_POINTS)
box_cov_xy.NullValue = 0.0

# create a new 'Slice'
slice_Cov_xy = Slice(registrationName='Slice_Cov_xy', Input=box_cov_xy)
slice_Cov_xy.SliceType = 'Plane'
slice_Cov_xy.HyperTreeGridSlicer = 'Plane'
slice_Cov_xy.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_Cov_xy.SliceType.Origin = [x0_dom, y0_dom, Zslice]
slice_Cov_xy.SliceType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_Cov_xy.HyperTreeGridSlicer.Origin = [x0_dom, y0_dom, Zslice]


# create a new 'Calculator' : scalar cov(uy*uz)=mean(uy*uz)-mean(uy)*mean(uz)
calculator12 = Calculator(registrationName='Cov_yz', Input=temporalStatistics1)
calculator12.ResultArrayName = 'cov_yz'
calculator12.Function = 'Uxyz1_average_Y-U_average_Y*U_average_Z'

# create a new 'Point Volume Interpolator'
box_cov_yz = PointVolumeInterpolator(registrationName='Box_cov_yz', Input=calculator12,
    Source='Bounded Volume')
box_cov_yz.Kernel = 'GaussianKernel'
box_cov_yz.Locator = 'Static Point Locator'

# init the 'GaussianKernel' selected for 'Kernel'
box_cov_yz.Kernel.Radius = Radius

# init the 'Bounded Volume' selected for 'Source'
box_cov_yz.Source.Origin = [Origin_X, Origin_Y, Origin_Z]
box_cov_yz.Source.Scale = [Scale_X, Scale_Y, Scale_Z]

box_cov_yz.Source.RefinementMode = 'Use resolution'
box_cov_yz.Source.Resolution = [Resolution_X, Resolution_Y, Resolution_Z]

box_cov_yz.NullPointsStrategy = 0 # ->MaskPoints (MASK_POINTS)
box_cov_yz.NullValue = 0.0

# create a new 'Slice'
slice_Cov_yz = Slice(registrationName='Slice_Cov_yz', Input=box_cov_yz)
slice_Cov_yz.SliceType = 'Plane'
slice_Cov_yz.HyperTreeGridSlicer = 'Plane'
slice_Cov_yz.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_Cov_yz.SliceType.Origin = [x0_dom, y0_dom, Zslice]
slice_Cov_yz.SliceType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_Cov_yz.HyperTreeGridSlicer.Origin = [x0_dom, y0_dom, Zslice]


# create a new 'Calculator' : scalar cov(uz*ux)=mean(uz*ux)-mean(uz)*mean(ux)
calculator13 = Calculator(registrationName='Cov_zx', Input=temporalStatistics1)
calculator13.ResultArrayName = 'cov_zx'
calculator13.Function = 'Uxyz1_average_Z-U_average_Z*U_average_X'

# create a new 'Point Volume Interpolator'
box_cov_zx = PointVolumeInterpolator(registrationName='Box_cov_zx', Input=calculator13,
    Source='Bounded Volume')
box_cov_zx.Kernel = 'GaussianKernel'
box_cov_zx.Locator = 'Static Point Locator'

# init the 'GaussianKernel' selected for 'Kernel'
box_cov_zx.Kernel.Radius = Radius

# init the 'Bounded Volume' selected for 'Source'
box_cov_zx.Source.Origin = [Origin_X, Origin_Y, Origin_Z]
box_cov_zx.Source.Scale = [Scale_X, Scale_Y, Scale_Z]

box_cov_zx.Source.RefinementMode = 'Use resolution'
box_cov_zx.Source.Resolution = [Resolution_X, Resolution_Y, Resolution_Z]

box_cov_zx.NullPointsStrategy = 0 # ->MaskPoints (MASK_POINTS)
box_cov_zx.NullValue = 0.0

# create a new 'Slice'
slice_Cov_zx = Slice(registrationName='Slice_Cov_zx', Input=box_cov_zx)
slice_Cov_zx.SliceType = 'Plane'
slice_Cov_zx.HyperTreeGridSlicer = 'Plane'
slice_Cov_zx.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_Cov_zx.SliceType.Origin = [x0_dom, y0_dom, Zslice]
slice_Cov_zx.SliceType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_Cov_zx.HyperTreeGridSlicer.Origin = [x0_dom, y0_dom, Zslice]


# create a new 'Calculator' : vector Uxyz2=(ux*ux, uy*uy, uz*uz )
calculator2 = Calculator(registrationName='Vector_Uxx_Uyy_Uzz', Input=base_Calcfoam)
calculator2.ResultArrayName = 'Uxyz2'
calculator2.Function = 'U_X*U_X*iHat+U_Y*U_Y*jHat+U_Z*U_Z*kHat'

# create a new 'Temporal Statistics' => mean( ux, uy, uz ) and mean( ux*ux, uy*uy, uz*uz )
temporalStatistics2 = TemporalStatistics(registrationName='TemporalStatistics2', Input=calculator2)
temporalStatistics2.ComputeMinimum = 0
temporalStatistics2.ComputeMaximum = 0

# mean(ux*ux)
temporalStatistics21 = Calculator(registrationName='Mean_xx', Input=temporalStatistics2)
temporalStatistics21.ResultArrayName = 'mean_xx'
temporalStatistics21.Function = 'Uxyz2_average_X'

# create a new 'Point Volume Interpolator'
box_mean_xx = PointVolumeInterpolator(registrationName='Box_mean_xx', Input=temporalStatistics21,
    Source='Bounded Volume')
box_mean_xx.Kernel = 'GaussianKernel'
box_mean_xx.Locator = 'Static Point Locator'

# init the 'GaussianKernel' selected for 'Kernel'
box_mean_xx.Kernel.Radius = Radius

# init the 'Bounded Volume' selected for 'Source'
box_mean_xx.Source.Origin = [Origin_X, Origin_Y, Origin_Z]
box_mean_xx.Source.Scale = [Scale_X, Scale_Y, Scale_Z]

box_mean_xx.Source.RefinementMode = 'Use resolution'
box_mean_xx.Source.Resolution = [Resolution_X, Resolution_Y, Resolution_Z]

box_mean_xx.NullPointsStrategy = 0 # ->MaskPoints (MASK_POINTS)
box_mean_xx.NullValue = 0.0

# create a new 'Slice'
slice_Mean_xx = Slice(registrationName='Slice_Mean_xx', Input=box_mean_xx)
slice_Mean_xx.SliceType = 'Plane'
slice_Mean_xx.HyperTreeGridSlicer = 'Plane'
slice_Mean_xx.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_Mean_xx.SliceType.Origin = [x0_dom, y0_dom, Zslice]
slice_Mean_xx.SliceType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_Mean_xx.HyperTreeGridSlicer.Origin = [x0_dom, y0_dom, Zslice]


# mean(uy*uy)
temporalStatistics22 = Calculator(registrationName='Mean_yy', Input=temporalStatistics2)
temporalStatistics22.ResultArrayName = 'mean_yy'
temporalStatistics22.Function = 'Uxyz2_average_Y'

# create a new 'Point Volume Interpolator'
box_mean_yy = PointVolumeInterpolator(registrationName='Box_mean_yy', Input=temporalStatistics22,
    Source='Bounded Volume')
box_mean_yy.Kernel = 'GaussianKernel'
box_mean_yy.Locator = 'Static Point Locator'

# init the 'GaussianKernel' selected for 'Kernel'
box_mean_yy.Kernel.Radius = Radius

# init the 'Bounded Volume' selected for 'Source'
box_mean_yy.Source.Origin = [Origin_X, Origin_Y, Origin_Z]
box_mean_yy.Source.Scale = [Scale_X, Scale_Y, Scale_Z]

box_mean_yy.Source.RefinementMode = 'Use resolution'
box_mean_yy.Source.Resolution = [Resolution_X, Resolution_Y, Resolution_Z]

box_mean_yy.NullPointsStrategy = 0 # ->MaskPoints (MASK_POINTS)
box_mean_yy.NullValue = 0.0

# create a new 'Slice'
slice_Mean_yy = Slice(registrationName='Slice_Mean_yy', Input=box_mean_yy)
slice_Mean_yy.SliceType = 'Plane'
slice_Mean_yy.HyperTreeGridSlicer = 'Plane'
slice_Mean_yy.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_Mean_yy.SliceType.Origin = [x0_dom, y0_dom, Zslice]
slice_Mean_yy.SliceType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_Mean_yy.HyperTreeGridSlicer.Origin = [x0_dom, y0_dom, Zslice]

# mean(uz*uz)
temporalStatistics23 = Calculator(registrationName='Mean_zz', Input=temporalStatistics2)
temporalStatistics23.ResultArrayName = 'mean_zz'
temporalStatistics23.Function = 'Uxyz2_average_Z'

# create a new 'Point Volume Interpolator'
box_mean_zz = PointVolumeInterpolator(registrationName='Box_mean_zz', Input=temporalStatistics23,
    Source='Bounded Volume')
box_mean_zz.Kernel = 'GaussianKernel'
box_mean_zz.Locator = 'Static Point Locator'

# init the 'GaussianKernel' selected for 'Kernel'
box_mean_zz.Kernel.Radius = Radius

# init the 'Bounded Volume' selected for 'Source'
box_mean_zz.Source.Origin = [Origin_X, Origin_Y, Origin_Z]
box_mean_zz.Source.Scale = [Scale_X, Scale_Y, Scale_Z]

box_mean_zz.Source.RefinementMode = 'Use resolution'
box_mean_zz.Source.Resolution = [Resolution_X, Resolution_Y, Resolution_Z]

box_mean_zz.NullPointsStrategy = 0 # ->MaskPoints (MASK_POINTS)
box_mean_zz.NullValue = 0.0

# create a new 'Slice'
slice_Mean_zz = Slice(registrationName='Slice_Mean_zz', Input=box_mean_zz)
slice_Mean_zz.SliceType = 'Plane'
slice_Mean_zz.HyperTreeGridSlicer = 'Plane'
slice_Mean_zz.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_Mean_zz.SliceType.Origin = [x0_dom, y0_dom, Zslice]
slice_Mean_zz.SliceType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_Mean_zz.HyperTreeGridSlicer.Origin = [x0_dom, y0_dom, Zslice]


# create a new 'Calculator' : scalar cov(ux*ux)=mean(ux*ux)-mean(ux)*mean(ux)
calculator21 = Calculator(registrationName='Cov_xx', Input=temporalStatistics2)
calculator21.ResultArrayName = 'cov_xx'
calculator21.Function = 'Uxyz2_average_X-U_average_X*U_average_X'

# create a new 'Point Volume Interpolator'
box_cov_xx = PointVolumeInterpolator(registrationName='Box_cov_xx', Input=calculator21,
    Source='Bounded Volume')
box_cov_xx.Kernel = 'GaussianKernel'
box_cov_xx.Locator = 'Static Point Locator'

# init the 'GaussianKernel' selected for 'Kernel'
box_cov_xx.Kernel.Radius = Radius

# init the 'Bounded Volume' selected for 'Source'
box_cov_xx.Source.Origin = [Origin_X, Origin_Y, Origin_Z]
box_cov_xx.Source.Scale = [Scale_X, Scale_Y, Scale_Z]

box_cov_xx.Source.RefinementMode = 'Use resolution'
box_cov_xx.Source.Resolution = [Resolution_X, Resolution_Y, Resolution_Z]

box_cov_xx.NullPointsStrategy = 0 # ->MaskPoints (MASK_POINTS)
box_cov_xx.NullValue = 0.0

# create a new 'Slice'
slice_Cov_xx = Slice(registrationName='Slice_Cov_xx', Input=box_cov_xx)
slice_Cov_xx.SliceType = 'Plane'
slice_Cov_xx.HyperTreeGridSlicer = 'Plane'
slice_Cov_xx.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_Cov_xx.SliceType.Origin = [x0_dom, y0_dom, Zslice]
slice_Cov_xx.SliceType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_Cov_xx.HyperTreeGridSlicer.Origin = [x0_dom, y0_dom, Zslice]


# create a new 'Calculator' : scalar cov(uy*uy)=mean(uy*uy)-mean(uy)*mean(uy)
calculator22 = Calculator(registrationName='Cov_yy', Input=temporalStatistics2)
calculator22.ResultArrayName = 'cov_yy'
calculator22.Function = 'Uxyz2_average_Y-U_average_Y*U_average_Y'

# create a new 'Point Volume Interpolator'
box_cov_yy = PointVolumeInterpolator(registrationName='Box_cov_yy', Input=calculator22,
    Source='Bounded Volume')
box_cov_yy.Kernel = 'GaussianKernel'
box_cov_yy.Locator = 'Static Point Locator'

# init the 'GaussianKernel' selected for 'Kernel'
box_cov_yy.Kernel.Radius = Radius

# init the 'Bounded Volume' selected for 'Source'
box_cov_yy.Source.Origin = [Origin_X, Origin_Y, Origin_Z]
box_cov_yy.Source.Scale = [Scale_X, Scale_Y, Scale_Z]

box_cov_yy.Source.RefinementMode = 'Use resolution'
box_cov_yy.Source.Resolution = [Resolution_X, Resolution_Y, Resolution_Z]

box_cov_yy.NullPointsStrategy = 0 # ->MaskPoints (MASK_POINTS)
box_cov_yy.NullValue = 0.0

# create a new 'Slice'
slice_Cov_yy = Slice(registrationName='Slice_Cov_yy', Input=box_cov_yy)
slice_Cov_yy.SliceType = 'Plane'
slice_Cov_yy.HyperTreeGridSlicer = 'Plane'
slice_Cov_yy.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_Cov_yy.SliceType.Origin = [x0_dom, y0_dom, Zslice]
slice_Cov_yy.SliceType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_Cov_yy.HyperTreeGridSlicer.Origin = [x0_dom, y0_dom, Zslice]


# create a new 'Calculator' : scalar cov(uz*uz)=mean(uz*uz)-mean(uz)*mean(uz)
calculator23 = Calculator(registrationName='Cov_zz', Input=temporalStatistics2)
calculator23.ResultArrayName = 'cov_zz'
calculator23.Function = 'Uxyz2_average_Z-U_average_Z*U_average_Z'

# create a new 'Point Volume Interpolator'
box_cov_zz = PointVolumeInterpolator(registrationName='Box_cov_zz', Input=calculator23,
    Source='Bounded Volume')
box_cov_zz.Kernel = 'GaussianKernel'
box_cov_zz.Locator = 'Static Point Locator'

# init the 'GaussianKernel' selected for 'Kernel'
box_cov_zz.Kernel.Radius = Radius

# init the 'Bounded Volume' selected for 'Source'
box_cov_zz.Source.Origin = [Origin_X, Origin_Y, Origin_Z]
box_cov_zz.Source.Scale = [Scale_X, Scale_Y, Scale_Z]

box_cov_zz.Source.RefinementMode = 'Use resolution'
box_cov_zz.Source.Resolution = [Resolution_X, Resolution_Y, Resolution_Z]

box_cov_zz.NullPointsStrategy = 0 # ->MaskPoints (MASK_POINTS)
box_cov_zz.NullValue = 0.0

# create a new 'Slice'
slice_Cov_zz = Slice(registrationName='Slice_Cov_zz', Input=box_cov_zz)
slice_Cov_zz.SliceType = 'Plane'
slice_Cov_zz.HyperTreeGridSlicer = 'Plane'
slice_Cov_zz.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_Cov_zz.SliceType.Origin = [x0_dom, y0_dom, Zslice]
slice_Cov_zz.SliceType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_Cov_zz.HyperTreeGridSlicer.Origin = [x0_dom, y0_dom, Zslice]

# ----------------------------------------------------------------

All_color =U_color_blueOrange 
All_PWF_Points = [1, 0.0, 0.5, 0.0, 8, 1.0, 0.5, 0.0]

# ----------------------------------------------------------------
# setup the visualization in view 'renderView1'
# ----------------------------------------------------------------

# show data from base_Calcfoam
base_CalcfoamDisplay = Show(base_Calcfoam, renderView1, 'UnstructuredGridRepresentation')

# get color transfer function/color map for 'U'
uLUT = GetColorTransferFunction('U')

uLUT.ColorSpace = 'RGB'
uLUT.NumberOfTableValues = 310
uLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'U'
uPWF = GetOpacityTransferFunction('U')
uPWF.ScalarRangeInitialized = 1

# modified legend
uLUT.RGBPoints = All_color
uPWF.Points = All_PWF_Points
uLUT.RescaleTransferFunction(0., 1.5)
uPWF.RescaleTransferFunction(0., 1.5)

# trace defaults for the display properties.
base_CalcfoamDisplay.Representation = 'Surface'
base_CalcfoamDisplay.ColorArrayName = ['POINTS', 'U']
base_CalcfoamDisplay.LookupTable = uLUT
base_CalcfoamDisplay.Opacity = 0.6
base_CalcfoamDisplay.PointSize = 1.0
base_CalcfoamDisplay.SelectTCoordArray = 'None'
base_CalcfoamDisplay.SelectNormalArray = 'None'
base_CalcfoamDisplay.SelectTangentArray = 'None'
base_CalcfoamDisplay.OSPRayScaleArray = 'U'
base_CalcfoamDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
base_CalcfoamDisplay.SelectOrientationVectors = 'U'
base_CalcfoamDisplay.ScaleFactor = 2.0
base_CalcfoamDisplay.SelectScaleArray = 'None'
base_CalcfoamDisplay.GlyphType = 'Arrow'
base_CalcfoamDisplay.GlyphTableIndexArray = 'None'
base_CalcfoamDisplay.GaussianRadius = 0.1
base_CalcfoamDisplay.SetScaleArray = ['POINTS', 'U']
base_CalcfoamDisplay.ScaleTransferFunction = 'PiecewiseFunction'
base_CalcfoamDisplay.OpacityArray = ['POINTS', 'U']
base_CalcfoamDisplay.OpacityTransferFunction = 'PiecewiseFunction'
base_CalcfoamDisplay.DataAxesGrid = 'GridAxesRepresentation'
base_CalcfoamDisplay.PolarAxes = 'PolarAxesRepresentation'
base_CalcfoamDisplay.ScalarOpacityFunction = uPWF
base_CalcfoamDisplay.ScalarOpacityUnitDistance = 0.315133695380462
base_CalcfoamDisplay.OpacityArrayName = ['POINTS', 'U']

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
base_CalcfoamDisplay.OSPRayScaleFunction.Points = [1.05e-09, 0.0, 0.5, 0.0, 2.848, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
base_CalcfoamDisplay.ScaleTransferFunction.Points = [-0.51, 0.0, 0.5, 0.0, 0.67, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
base_CalcfoamDisplay.OpacityTransferFunction.Points = [-0.51, 0.0, 0.5, 0.0, 0.67, 1.0, 0.5, 0.0]

# setup the color legend parameters for each legend in this view

# get color legend/bar for uLUT in view renderView1
uLUTColorBar = GetScalarBar(uLUT, renderView1)
uLUTColorBar.WindowLocation = 'Upper Left Corner'
uLUTColorBar.AutoOrient = 0
uLUTColorBar.Orientation = 'Horizontal'
uLUTColorBar.WindowLocation = 'Any Location'
uLUTColorBar.Position = [0.6, 0.02]
uLUTColorBar.Title = 'U'
uLUTColorBar.ComponentTitle = 'Magnitude'
uLUTColorBar.TitleBold = 1
uLUTColorBar.TitleFontSize = 20
uLUTColorBar.AutomaticLabelFormat = 0
uLUTColorBar.LabelFormat = '%-#6.3f'
uLUTColorBar.RangeLabelFormat = '%-#6.3f'

# set color bar visibility
uLUTColorBar.Visibility = 0

# Hide view
Hide(base_Calcfoam, renderView1)


#############################

# ### cylinder ###

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


#############################

# ### mean(ux*uy) ###

# show data from temporalStatistics1
slice_Mean_xyDisplay = Show(slice_Mean_xy, renderView1, 'UnstructuredGridRepresentation')

# get color transfer function/color map for 'mean_xy'
mean_xyLUT = GetColorTransferFunction('mean_xy')

mean_xyLUT.ColorSpace = 'RGB'
mean_xyLUT.NumberOfTableValues = 310
mean_xyLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'mean_xy'
mean_xyPWF = GetOpacityTransferFunction('mean_xy')
mean_xyPWF.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]
mean_xyPWF.ScalarRangeInitialized = 1

# modified legend
mean_xyLUT.RGBPoints = All_color
mean_xyPWF.Points = All_PWF_Points
mean_xyLUT.RescaleTransferFunction(-0.05, 0.05)
mean_xyPWF.RescaleTransferFunction(-0.05, 0.05)

# trace defaults for the display properties.
slice_Mean_xyDisplay.Representation = 'Surface'
slice_Mean_xyDisplay.ColorArrayName = ['POINTS', 'mean_xy']
slice_Mean_xyDisplay.LookupTable = mean_xyLUT
slice_Mean_xyDisplay.Opacity = 0.6
slice_Mean_xyDisplay.PointSize = 1.0
slice_Mean_xyDisplay.SelectTCoordArray = 'None'
slice_Mean_xyDisplay.SelectNormalArray = 'None'
slice_Mean_xyDisplay.SelectTangentArray = 'None'
slice_Mean_xyDisplay.OSPRayScaleArray = 'mean_xy'
slice_Mean_xyDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
slice_Mean_xyDisplay.SelectOrientationVectors = 'None'
slice_Mean_xyDisplay.ScaleFactor = 2.0
slice_Mean_xyDisplay.SelectScaleArray = 'mean_xy'
slice_Mean_xyDisplay.GlyphType = 'Arrow'
slice_Mean_xyDisplay.GlyphTableIndexArray = 'mean_xy'
slice_Mean_xyDisplay.GaussianRadius = 0.1
slice_Mean_xyDisplay.SetScaleArray = ['POINTS', 'mean_xy']
slice_Mean_xyDisplay.ScaleTransferFunction = 'PiecewiseFunction'
slice_Mean_xyDisplay.OpacityArray = ['POINTS', 'mean_xy']
slice_Mean_xyDisplay.OpacityTransferFunction = 'PiecewiseFunction'
slice_Mean_xyDisplay.DataAxesGrid = 'GridAxesRepresentation'
slice_Mean_xyDisplay.PolarAxes = 'PolarAxesRepresentation'
slice_Mean_xyDisplay.ScalarOpacityFunction = mean_xyPWF
slice_Mean_xyDisplay.ScalarOpacityUnitDistance = 0.315133695380462
slice_Mean_xyDisplay.OpacityArrayName = ['POINTS', 'mean_xy']

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
slice_Mean_xyDisplay.OSPRayScaleFunction.Points = [1.05e-09, 0.0, 0.5, 0.0, 2.848, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_Mean_xyDisplay.ScaleTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_Mean_xyDisplay.OpacityTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# get color legend/bar for mean_xyLUT in view renderView1
mean_xyLUTColorBar = GetScalarBar(mean_xyLUT, renderView1)
mean_xyLUTColorBar.AutoOrient = 0
mean_xyLUTColorBar.Orientation = 'Horizontal'
mean_xyLUTColorBar.WindowLocation = 'Any Location'
mean_xyLUTColorBar.Position = [0.6, 0.02]
mean_xyLUTColorBar.Title = 'mean(Ux*Uy)'
mean_xyLUTColorBar.ComponentTitle = ' (t=[T_FIRST_VALUE:T_LAST_VALUE])'
mean_xyLUTColorBar.TitleBold = 1
mean_xyLUTColorBar.TitleFontSize = 20
mean_xyLUTColorBar.AutomaticLabelFormat = 0
mean_xyLUTColorBar.LabelFormat = '%-#6.3f'
mean_xyLUTColorBar.RangeLabelFormat = '%-#6.3f'

# set color bar visibility
mean_xyLUTColorBar.Visibility = 0

# Hide view
Hide(slice_Mean_xy, renderView1)

# ### mean(uy*uz) ###

# show data from temporalStatistics1
slice_Mean_yzDisplay = Show(slice_Mean_yz, renderView1, 'UnstructuredGridRepresentation')

# get color transfer function/color map for 'mean_yz'
mean_yzLUT = GetColorTransferFunction('mean_yz')

mean_yzLUT.ColorSpace = 'RGB'
mean_yzLUT.NumberOfTableValues = 310
mean_yzLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'mean_yz'
mean_yzPWF = GetOpacityTransferFunction('mean_yz')
mean_yzPWF.ScalarRangeInitialized = 1

# modified legend
mean_yzLUT.RGBPoints = All_color
mean_yzPWF.Points = All_PWF_Points
mean_yzLUT.RescaleTransferFunction(-0.05, 0.05)
mean_yzPWF.RescaleTransferFunction(-0.05, 0.05)

# trace defaults for the display properties.
slice_Mean_yzDisplay.Representation = 'Surface'
slice_Mean_yzDisplay.ColorArrayName = ['POINTS', 'mean_yz']
slice_Mean_yzDisplay.LookupTable = mean_yzLUT
slice_Mean_yzDisplay.Opacity = 0.6
slice_Mean_yzDisplay.PointSize = 1.0
slice_Mean_yzDisplay.SelectTCoordArray = 'None'
slice_Mean_yzDisplay.SelectNormalArray = 'None'
slice_Mean_yzDisplay.SelectTangentArray = 'None'
slice_Mean_yzDisplay.OSPRayScaleArray = 'mean_yz'
slice_Mean_yzDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
slice_Mean_yzDisplay.SelectOrientationVectors = 'None'
slice_Mean_yzDisplay.ScaleFactor = 2.0
slice_Mean_yzDisplay.SelectScaleArray = 'mean_yz'
slice_Mean_yzDisplay.GlyphType = 'Arrow'
slice_Mean_yzDisplay.GlyphTableIndexArray = 'mean_yz'
slice_Mean_yzDisplay.GaussianRadius = 0.1
slice_Mean_yzDisplay.SetScaleArray = ['POINTS', 'mean_yz']
slice_Mean_yzDisplay.ScaleTransferFunction = 'PiecewiseFunction'
slice_Mean_yzDisplay.OpacityArray = ['POINTS', 'mean_yz']
slice_Mean_yzDisplay.OpacityTransferFunction = 'PiecewiseFunction'
slice_Mean_yzDisplay.DataAxesGrid = 'GridAxesRepresentation'
slice_Mean_yzDisplay.PolarAxes = 'PolarAxesRepresentation'
slice_Mean_yzDisplay.ScalarOpacityFunction = mean_yzPWF
slice_Mean_yzDisplay.ScalarOpacityUnitDistance = 0.315133695380462
slice_Mean_yzDisplay.OpacityArrayName = ['POINTS', 'mean_yz']

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
slice_Mean_yzDisplay.OSPRayScaleFunction.Points = [1.05e-09, 0.0, 0.5, 0.0, 2.848, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_Mean_yzDisplay.ScaleTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_Mean_yzDisplay.OpacityTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# get color legend/bar for mean_yzLUT in view renderView1
mean_yzLUTColorBar = GetScalarBar(mean_yzLUT, renderView1)
mean_yzLUTColorBar.AutoOrient = 0
mean_yzLUTColorBar.Orientation = 'Horizontal'
mean_yzLUTColorBar.WindowLocation = 'Any Location'
mean_yzLUTColorBar.Position = [0.6, 0.02]
mean_yzLUTColorBar.Title = 'mean(Uy*Uz)'
mean_yzLUTColorBar.ComponentTitle = ' (t=[T_FIRST_VALUE:T_LAST_VALUE])'
mean_yzLUTColorBar.TitleBold = 1
mean_yzLUTColorBar.TitleFontSize = 20
mean_yzLUTColorBar.AutomaticLabelFormat = 0
mean_yzLUTColorBar.LabelFormat = '%-#6.3f'
mean_yzLUTColorBar.RangeLabelFormat = '%-#6.3f'

# set color bar visibility
mean_yzLUTColorBar.Visibility = 0

# Hide view
Hide(slice_Mean_yz, renderView1)

# ### mean(uz*ux) ###

# show data from temporalStatistics1
slice_Mean_zxDisplay = Show(slice_Mean_zx, renderView1, 'UnstructuredGridRepresentation')

# get color transfer function/color map for 'mean_zx'
mean_zxLUT = GetColorTransferFunction('mean_zx')

mean_zxLUT.ColorSpace = 'RGB'
mean_zxLUT.NumberOfTableValues = 310
mean_zxLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'mean_zx'
mean_zxPWF = GetOpacityTransferFunction('mean_zx')
mean_zxPWF.ScalarRangeInitialized = 1

# modified legend
mean_zxLUT.RGBPoints = All_color
mean_zxPWF.Points = All_PWF_Points
mean_zxLUT.RescaleTransferFunction(-0.05, 0.05)
mean_zxPWF.RescaleTransferFunction(-0.05, 0.05)

# trace defaults for the display properties.
slice_Mean_zxDisplay.Representation = 'Surface'
slice_Mean_zxDisplay.ColorArrayName = ['POINTS', 'mean_zx']
slice_Mean_zxDisplay.LookupTable = mean_zxLUT
slice_Mean_zxDisplay.Opacity = 0.6
slice_Mean_zxDisplay.PointSize = 1.0
slice_Mean_zxDisplay.SelectTCoordArray = 'None'
slice_Mean_zxDisplay.SelectNormalArray = 'None'
slice_Mean_zxDisplay.SelectTangentArray = 'None'
slice_Mean_zxDisplay.OSPRayScaleArray = 'mean_zx'
slice_Mean_zxDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
slice_Mean_zxDisplay.SelectOrientationVectors = 'None'
slice_Mean_zxDisplay.ScaleFactor = 2.0
slice_Mean_zxDisplay.SelectScaleArray = 'mean_zx'
slice_Mean_zxDisplay.GlyphType = 'Arrow'
slice_Mean_zxDisplay.GlyphTableIndexArray = 'mean_zx'
slice_Mean_zxDisplay.GaussianRadius = 0.1
slice_Mean_zxDisplay.SetScaleArray = ['POINTS', 'mean_zx']
slice_Mean_zxDisplay.ScaleTransferFunction = 'PiecewiseFunction'
slice_Mean_zxDisplay.OpacityArray = ['POINTS', 'mean_zx']
slice_Mean_zxDisplay.OpacityTransferFunction = 'PiecewiseFunction'
slice_Mean_zxDisplay.DataAxesGrid = 'GridAxesRepresentation'
slice_Mean_zxDisplay.PolarAxes = 'PolarAxesRepresentation'
slice_Mean_zxDisplay.ScalarOpacityFunction = mean_zxPWF
slice_Mean_zxDisplay.ScalarOpacityUnitDistance = 0.315133695380462
slice_Mean_zxDisplay.OpacityArrayName = ['POINTS', 'mean_zx']

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
slice_Mean_zxDisplay.OSPRayScaleFunction.Points = [1.05e-09, 0.0, 0.5, 0.0, 2.848, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_Mean_zxDisplay.ScaleTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_Mean_zxDisplay.OpacityTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# ### mean(uz*ux) ###

# get color legend/bar for mean_zxLUT in view renderView1
mean_zxLUTColorBar = GetScalarBar(mean_zxLUT, renderView1)
mean_zxLUTColorBar.AutoOrient = 0
mean_zxLUTColorBar.Orientation = 'Horizontal'
mean_zxLUTColorBar.WindowLocation = 'Any Location'
mean_zxLUTColorBar.Position = [0.6, 0.02]
mean_zxLUTColorBar.Title = 'mean(Uz*Ux)'
mean_zxLUTColorBar.ComponentTitle = ' (t=[T_FIRST_VALUE:T_LAST_VALUE])'
mean_zxLUTColorBar.TitleBold = 1
mean_zxLUTColorBar.TitleFontSize = 20
mean_zxLUTColorBar.AutomaticLabelFormat = 0
mean_zxLUTColorBar.LabelFormat = '%-#6.3f'
mean_zxLUTColorBar.RangeLabelFormat = '%-#6.3f'

# set color bar visibility
mean_zxLUTColorBar.Visibility = 0

# Hide view
Hide(slice_Mean_zx, renderView1)

#############################



# ### cov (ux,uy) ###

# show data from calculator11
slice_Cov_xyDisplay = Show(slice_Cov_xy, renderView1, 'UnstructuredGridRepresentation')

# get color transfer function/color map for 'cov_xy'
cov_xyLUT = GetColorTransferFunction('cov_xy')

cov_xyLUT.ColorSpace = 'RGB'
cov_xyLUT.NumberOfTableValues = 310
cov_xyLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'cov_xy'
cov_xyPWF = GetOpacityTransferFunction('cov_xy')
cov_xyPWF.ScalarRangeInitialized = 1

# modified legend
cov_xyLUT.RGBPoints = All_color
cov_xyPWF.Points = All_PWF_Points
cov_xyLUT.RescaleTransferFunction(-0.05, 0.05)
cov_xyPWF.RescaleTransferFunction(-0.05, 0.05)

# trace defaults for the display properties.
slice_Cov_xyDisplay.Representation = 'Surface'
slice_Cov_xyDisplay.ColorArrayName = ['POINTS', 'cov_xy']
slice_Cov_xyDisplay.LookupTable = cov_xyLUT
slice_Cov_xyDisplay.Opacity = 0.6
slice_Cov_xyDisplay.PointSize = 1.0
slice_Cov_xyDisplay.SelectTCoordArray = 'None'
slice_Cov_xyDisplay.SelectNormalArray = 'None'
slice_Cov_xyDisplay.SelectTangentArray = 'None'
slice_Cov_xyDisplay.OSPRayScaleArray = 'cov_xy'
slice_Cov_xyDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
slice_Cov_xyDisplay.SelectOrientationVectors = 'None'
slice_Cov_xyDisplay.ScaleFactor = 2.0
slice_Cov_xyDisplay.SelectScaleArray = 'cov_xy'
slice_Cov_xyDisplay.GlyphType = 'Arrow'
slice_Cov_xyDisplay.GlyphTableIndexArray = 'cov_xy'
slice_Cov_xyDisplay.GaussianRadius = 0.1
slice_Cov_xyDisplay.SetScaleArray = ['POINTS', 'cov_xy']
slice_Cov_xyDisplay.ScaleTransferFunction = 'PiecewiseFunction'
slice_Cov_xyDisplay.OpacityArray = ['POINTS', 'cov_xy']
slice_Cov_xyDisplay.OpacityTransferFunction = 'PiecewiseFunction'
slice_Cov_xyDisplay.DataAxesGrid = 'GridAxesRepresentation'
slice_Cov_xyDisplay.PolarAxes = 'PolarAxesRepresentation'
slice_Cov_xyDisplay.ScalarOpacityFunction = cov_xyPWF
slice_Cov_xyDisplay.ScalarOpacityUnitDistance = 0.315133695380462
slice_Cov_xyDisplay.OpacityArrayName = ['POINTS', 'cov_xy']

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
slice_Cov_xyDisplay.OSPRayScaleFunction.Points = [1.05e-09, 0.0, 0.5, 0.0, 2.848, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_Cov_xyDisplay.ScaleTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_Cov_xyDisplay.OpacityTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# get color legend/bar for cov_xyLUT in view renderView1
cov_xyLUTColorBar = GetScalarBar(cov_xyLUT, renderView1)
cov_xyLUTColorBar.AutoOrient = 0
cov_xyLUTColorBar.Orientation = 'Horizontal'
cov_xyLUTColorBar.WindowLocation = 'Any Location'
cov_xyLUTColorBar.Position = [0.6, 0.02]
cov_xyLUTColorBar.Title = 'cov(Ux,Uy)'
cov_xyLUTColorBar.ComponentTitle = ' (t=[T_FIRST_VALUE:T_LAST_VALUE])'
cov_xyLUTColorBar.TitleBold = 1
cov_xyLUTColorBar.TitleFontSize = 20
cov_xyLUTColorBar.AutomaticLabelFormat = 0
cov_xyLUTColorBar.LabelFormat = '%-#6.3f'
cov_xyLUTColorBar.RangeLabelFormat = '%-#6.3f'

# set color bar visibility
cov_xyLUTColorBar.Visibility = 0

# Hide view
Hide(slice_Cov_xy, renderView1)

# ### cov (uy,uz) ###

# show data from calculator12
slice_Cov_yzDisplay = Show(slice_Cov_yz, renderView1, 'UnstructuredGridRepresentation')

# get color transfer function/color map for 'cov_yz'
cov_yzLUT = GetColorTransferFunction('cov_yz')

cov_yzLUT.ColorSpace = 'RGB'
cov_yzLUT.NumberOfTableValues = 310
cov_yzLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'cov_yz'
cov_yzPWF = GetOpacityTransferFunction('cov_yz')
cov_yzPWF.ScalarRangeInitialized = 1

# modified legend
cov_yzLUT.RGBPoints = All_color
cov_yzPWF.Points = All_PWF_Points
cov_yzLUT.RescaleTransferFunction(-0.05, 0.05)
cov_yzPWF.RescaleTransferFunction(-0.05, 0.05)

# trace defaults for the display properties.
slice_Cov_yzDisplay.Representation = 'Surface'
slice_Cov_yzDisplay.ColorArrayName = ['POINTS', 'cov_yz']
slice_Cov_yzDisplay.LookupTable = cov_yzLUT
slice_Cov_yzDisplay.Opacity = 0.6
slice_Cov_yzDisplay.PointSize = 1.0
slice_Cov_yzDisplay.SelectTCoordArray = 'None'
slice_Cov_yzDisplay.SelectNormalArray = 'None'
slice_Cov_yzDisplay.SelectTangentArray = 'None'
slice_Cov_yzDisplay.OSPRayScaleArray = 'cov_yz'
slice_Cov_yzDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
slice_Cov_yzDisplay.SelectOrientationVectors = 'None'
slice_Cov_yzDisplay.ScaleFactor = 2.0
slice_Cov_yzDisplay.SelectScaleArray = 'cov_yz'
slice_Cov_yzDisplay.GlyphType = 'Arrow'
slice_Cov_yzDisplay.GlyphTableIndexArray = 'cov_yz'
slice_Cov_yzDisplay.GaussianRadius = 0.1
slice_Cov_yzDisplay.SetScaleArray = ['POINTS', 'cov_yz']
slice_Cov_yzDisplay.ScaleTransferFunction = 'PiecewiseFunction'
slice_Cov_yzDisplay.OpacityArray = ['POINTS', 'cov_yz']
slice_Cov_yzDisplay.OpacityTransferFunction = 'PiecewiseFunction'
slice_Cov_yzDisplay.DataAxesGrid = 'GridAxesRepresentation'
slice_Cov_yzDisplay.PolarAxes = 'PolarAxesRepresentation'
slice_Cov_yzDisplay.ScalarOpacityFunction = cov_yzPWF
slice_Cov_yzDisplay.ScalarOpacityUnitDistance = 0.315133695380462
slice_Cov_yzDisplay.OpacityArrayName = ['POINTS', 'cov_yz']

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
slice_Cov_yzDisplay.OSPRayScaleFunction.Points = [1.05e-09, 0.0, 0.5, 0.0, 2.848, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_Cov_yzDisplay.ScaleTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_Cov_yzDisplay.OpacityTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# get color legend/bar for cov_yzLUT in view renderView1
cov_yzLUTColorBar = GetScalarBar(cov_yzLUT, renderView1)
cov_yzLUTColorBar.AutoOrient = 0
cov_yzLUTColorBar.Orientation = 'Horizontal'
cov_yzLUTColorBar.WindowLocation = 'Any Location'
cov_yzLUTColorBar.Position = [0.6, 0.02]
cov_yzLUTColorBar.Title = 'cov(Uy,Uz)'
cov_yzLUTColorBar.ComponentTitle = ' (t=[T_FIRST_VALUE:T_LAST_VALUE])'
cov_yzLUTColorBar.TitleBold = 1
cov_yzLUTColorBar.TitleFontSize = 20
cov_yzLUTColorBar.AutomaticLabelFormat = 0
cov_yzLUTColorBar.LabelFormat = '%-#6.3f'
cov_yzLUTColorBar.RangeLabelFormat = '%-#6.3f'

# set color bar visibility
cov_yzLUTColorBar.Visibility = 0

# Hide view
Hide(slice_Cov_yz, renderView1)


# ### cov (uz,ux) ###

# show data from calculator13
slice_Cov_zxDisplay = Show(slice_Cov_zx, renderView1, 'UnstructuredGridRepresentation')

# get color transfer function/color map for 'cov_zx'
cov_zxLUT = GetColorTransferFunction('cov_zx')

cov_zxLUT.ColorSpace = 'RGB'
cov_zxLUT.NumberOfTableValues = 310
cov_zxLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'cov_zx'
cov_zxPWF = GetOpacityTransferFunction('cov_zx')
cov_zxPWF.ScalarRangeInitialized = 1

# modified legend
cov_zxLUT.RGBPoints = All_color
cov_zxPWF.Points = All_PWF_Points
cov_zxLUT.RescaleTransferFunction(-0.05, 0.05)
cov_zxPWF.RescaleTransferFunction(-0.05, 0.05)

# trace defaults for the display properties.
slice_Cov_zxDisplay.Representation = 'Surface'
slice_Cov_zxDisplay.ColorArrayName = ['POINTS', 'cov_zx']
slice_Cov_zxDisplay.LookupTable = cov_zxLUT
slice_Cov_zxDisplay.Opacity = 0.6
slice_Cov_zxDisplay.PointSize = 1.0
slice_Cov_zxDisplay.SelectTCoordArray = 'None'
slice_Cov_zxDisplay.SelectNormalArray = 'None'
slice_Cov_zxDisplay.SelectTangentArray = 'None'
slice_Cov_zxDisplay.OSPRayScaleArray = 'cov_zx'
slice_Cov_zxDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
slice_Cov_zxDisplay.SelectOrientationVectors = 'None'
slice_Cov_zxDisplay.ScaleFactor = 2.0
slice_Cov_zxDisplay.SelectScaleArray = 'cov_zx'
slice_Cov_zxDisplay.GlyphType = 'Arrow'
slice_Cov_zxDisplay.GlyphTableIndexArray = 'cov_zx'
slice_Cov_zxDisplay.GaussianRadius = 0.1
slice_Cov_zxDisplay.SetScaleArray = ['POINTS', 'cov_zx']
slice_Cov_zxDisplay.ScaleTransferFunction = 'PiecewiseFunction'
slice_Cov_zxDisplay.OpacityArray = ['POINTS', 'cov_zx']
slice_Cov_zxDisplay.OpacityTransferFunction = 'PiecewiseFunction'
slice_Cov_zxDisplay.DataAxesGrid = 'GridAxesRepresentation'
slice_Cov_zxDisplay.PolarAxes = 'PolarAxesRepresentation'
slice_Cov_zxDisplay.ScalarOpacityFunction = cov_zxPWF
slice_Cov_zxDisplay.ScalarOpacityUnitDistance = 0.315133695380462
slice_Cov_zxDisplay.OpacityArrayName = ['POINTS', 'cov_zx']

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
slice_Cov_zxDisplay.OSPRayScaleFunction.Points = [1.05e-09, 0.0, 0.5, 0.0, 2.848, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_Cov_zxDisplay.ScaleTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_Cov_zxDisplay.OpacityTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# get color legend/bar for cov_zxLUT in view renderView1
cov_zxLUTColorBar = GetScalarBar(cov_zxLUT, renderView1)
cov_zxLUTColorBar.AutoOrient = 0
cov_zxLUTColorBar.Orientation = 'Horizontal'
cov_zxLUTColorBar.WindowLocation = 'Any Location'
cov_zxLUTColorBar.Position = [0.6, 0.02]
cov_zxLUTColorBar.Title = 'cov(Uz,Ux)'
cov_zxLUTColorBar.ComponentTitle = ' (t=[T_FIRST_VALUE:T_LAST_VALUE])'
cov_zxLUTColorBar.TitleBold = 1
cov_zxLUTColorBar.TitleFontSize = 20
cov_zxLUTColorBar.AutomaticLabelFormat = 0
cov_zxLUTColorBar.LabelFormat = '%-#6.3f'
cov_zxLUTColorBar.RangeLabelFormat = '%-#6.3f'

# set color bar visibility
cov_zxLUTColorBar.Visibility = 0

# Hide view
Hide(slice_Cov_zx, renderView1)


#############################

# ### mean(ux*ux) ###

# show data from temporalStatistics2
slice_Mean_xxDisplay = Show(slice_Mean_xx, renderView1, 'UnstructuredGridRepresentation')

# get color transfer function/color map for 'mean_xx'
mean_xxLUT = GetColorTransferFunction('mean_xx')

mean_xxLUT.ColorSpace = 'RGB'
mean_xxLUT.NumberOfTableValues = 310
mean_xxLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'mean_xx'
mean_xxPWF = GetOpacityTransferFunction('mean_xx')
mean_xxPWF.ScalarRangeInitialized = 1

# modified legend
mean_xxLUT.RGBPoints = All_color
mean_xxPWF.Points = All_PWF_Points
mean_xxLUT.RescaleTransferFunction(-0.05, 0.05)
mean_xxPWF.RescaleTransferFunction(-0.05, 0.05)

# trace defaults for the display properties.
slice_Mean_xxDisplay.Representation = 'Surface'
slice_Mean_xxDisplay.ColorArrayName = ['POINTS', 'mean_xx']
slice_Mean_xxDisplay.LookupTable = mean_xxLUT
slice_Mean_xxDisplay.Opacity = 0.6
slice_Mean_xxDisplay.PointSize = 1.0
slice_Mean_xxDisplay.SelectTCoordArray = 'None'
slice_Mean_xxDisplay.SelectNormalArray = 'None'
slice_Mean_xxDisplay.SelectTangentArray = 'None'
slice_Mean_xxDisplay.OSPRayScaleArray = 'mean_xx'
slice_Mean_xxDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
slice_Mean_xxDisplay.SelectOrientationVectors = 'None'
slice_Mean_xxDisplay.ScaleFactor = 2.0
slice_Mean_xxDisplay.SelectScaleArray = 'mean_xx'
slice_Mean_xxDisplay.GlyphType = 'Arrow'
slice_Mean_xxDisplay.GlyphTableIndexArray = 'mean_xx'
slice_Mean_xxDisplay.GaussianRadius = 0.1
slice_Mean_xxDisplay.SetScaleArray = ['POINTS', 'mean_xx']
slice_Mean_xxDisplay.ScaleTransferFunction = 'PiecewiseFunction'
slice_Mean_xxDisplay.OpacityArray = ['POINTS', 'mean_xx']
slice_Mean_xxDisplay.OpacityTransferFunction = 'PiecewiseFunction'
slice_Mean_xxDisplay.DataAxesGrid = 'GridAxesRepresentation'
slice_Mean_xxDisplay.PolarAxes = 'PolarAxesRepresentation'
slice_Mean_xxDisplay.ScalarOpacityFunction = mean_xxPWF
slice_Mean_xxDisplay.ScalarOpacityUnitDistance = 0.315133695380462
slice_Mean_xxDisplay.OpacityArrayName = ['POINTS', 'mean_xx']

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
slice_Mean_xxDisplay.OSPRayScaleFunction.Points = [1.05e-09, 0.0, 0.5, 0.0, 2.848, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_Mean_xxDisplay.ScaleTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_Mean_xxDisplay.OpacityTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# get color legend/bar for mean_xxLUT in view renderView1
mean_xxLUTColorBar = GetScalarBar(mean_xxLUT, renderView1)
mean_xxLUTColorBar.AutoOrient = 0
mean_xxLUTColorBar.Orientation = 'Horizontal'
mean_xxLUTColorBar.WindowLocation = 'Any Location'
mean_xxLUTColorBar.Position = [0.6, 0.02]
mean_xxLUTColorBar.Title = 'mean(Ux*Ux)'
mean_xxLUTColorBar.ComponentTitle = ' (t=[T_FIRST_VALUE:T_LAST_VALUE])'
mean_xxLUTColorBar.TitleBold = 1
mean_xxLUTColorBar.TitleFontSize = 20
mean_xxLUTColorBar.AutomaticLabelFormat = 0
mean_xxLUTColorBar.LabelFormat = '%-#6.3f'
mean_xxLUTColorBar.RangeLabelFormat = '%-#6.3f'

# set color bar visibility
mean_xxLUTColorBar.Visibility = 0

# Hide view
Hide(slice_Mean_xx, renderView1)


# ### mean(uy*uy) ###

# show data from temporalStatistics2
slice_Mean_yyDisplay = Show(slice_Mean_yy, renderView1, 'UnstructuredGridRepresentation')

# get color transfer function/color map for 'mean_yy'
mean_yyLUT = GetColorTransferFunction('mean_yy')

mean_yyLUT.ColorSpace = 'RGB'
mean_yyLUT.NumberOfTableValues = 310
mean_yyLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'mean_yy'
mean_yyPWF = GetOpacityTransferFunction('mean_yy')
mean_yyPWF.ScalarRangeInitialized = 1

# modified legend
mean_yyLUT.RGBPoints = All_color
mean_yyPWF.Points = All_PWF_Points
mean_yyLUT.RescaleTransferFunction(-0.05, 0.05)
mean_yyPWF.RescaleTransferFunction(-0.05, 0.05)

# trace defaults for the display properties.
slice_Mean_yyDisplay.Representation = 'Surface'
slice_Mean_yyDisplay.ColorArrayName = ['POINTS', 'mean_yy']
slice_Mean_yyDisplay.LookupTable = mean_yyLUT
slice_Mean_yyDisplay.Opacity = 0.6
slice_Mean_yyDisplay.PointSize = 1.0
slice_Mean_yyDisplay.SelectTCoordArray = 'None'
slice_Mean_yyDisplay.SelectNormalArray = 'None'
slice_Mean_yyDisplay.SelectTangentArray = 'None'
slice_Mean_yyDisplay.OSPRayScaleArray = 'mean_yy'
slice_Mean_yyDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
slice_Mean_yyDisplay.SelectOrientationVectors = 'None'
slice_Mean_yyDisplay.ScaleFactor = 2.0
slice_Mean_yyDisplay.SelectScaleArray = 'mean_yy'
slice_Mean_yyDisplay.GlyphType = 'Arrow'
slice_Mean_yyDisplay.GlyphTableIndexArray = 'mean_yy'
slice_Mean_yyDisplay.GaussianRadius = 0.1
slice_Mean_yyDisplay.SetScaleArray = ['POINTS', 'mean_yy']
slice_Mean_yyDisplay.ScaleTransferFunction = 'PiecewiseFunction'
slice_Mean_yyDisplay.OpacityArray = ['POINTS', 'mean_yy']
slice_Mean_yyDisplay.OpacityTransferFunction = 'PiecewiseFunction'
slice_Mean_yyDisplay.DataAxesGrid = 'GridAxesRepresentation'
slice_Mean_yyDisplay.PolarAxes = 'PolarAxesRepresentation'
slice_Mean_yyDisplay.ScalarOpacityFunction = mean_yyPWF
slice_Mean_yyDisplay.ScalarOpacityUnitDistance = 0.315133695380462
slice_Mean_yyDisplay.OpacityArrayName = ['POINTS', 'mean_yy']

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
slice_Mean_yyDisplay.OSPRayScaleFunction.Points = [1.05e-09, 0.0, 0.5, 0.0, 2.848, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_Mean_yyDisplay.ScaleTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_Mean_yyDisplay.OpacityTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# get color legend/bar for mean_yyLUT in view renderView1
mean_yyLUTColorBar = GetScalarBar(mean_yyLUT, renderView1)
mean_yyLUTColorBar.AutoOrient = 0
mean_yyLUTColorBar.Orientation = 'Horizontal'
mean_yyLUTColorBar.WindowLocation = 'Any Location'
mean_yyLUTColorBar.Position = [0.6, 0.02]
mean_yyLUTColorBar.Title = 'mean(Uy*Uy)'
mean_yyLUTColorBar.ComponentTitle = ' (t=[T_FIRST_VALUE:T_LAST_VALUE])'
mean_yyLUTColorBar.TitleBold = 1
mean_yyLUTColorBar.TitleFontSize = 20
mean_yyLUTColorBar.AutomaticLabelFormat = 0
mean_yyLUTColorBar.LabelFormat = '%-#6.3f'
mean_yyLUTColorBar.RangeLabelFormat = '%-#6.3f'

# set color bar visibility
mean_yyLUTColorBar.Visibility = 0

# Hide view
Hide(slice_Mean_yy, renderView1)


# ### mean(uz*uz) ###

# show data from temporalStatistics2
slice_Mean_zzDisplay = Show(slice_Mean_zz, renderView1, 'UnstructuredGridRepresentation')

# get color transfer function/color map for 'mean_zz'
mean_zzLUT = GetColorTransferFunction('mean_zz')

mean_zzLUT.ColorSpace = 'RGB'
mean_zzLUT.NumberOfTableValues = 310
mean_zzLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'mean_zz'
mean_zzPWF = GetOpacityTransferFunction('mean_zz')
mean_zzPWF.ScalarRangeInitialized = 1

# modified legend
mean_zzLUT.RGBPoints = All_color
mean_zzPWF.Points = All_PWF_Points
mean_zzLUT.RescaleTransferFunction(-0.05, 0.05)
mean_zzPWF.RescaleTransferFunction(-0.05, 0.05)


# trace defaults for the display properties.
slice_Mean_zzDisplay.Representation = 'Surface'
slice_Mean_zzDisplay.ColorArrayName = ['POINTS', 'mean_zz']
slice_Mean_zzDisplay.LookupTable = mean_zzLUT
slice_Mean_zzDisplay.Opacity = 0.6
slice_Mean_zzDisplay.PointSize = 1.0
slice_Mean_zzDisplay.SelectTCoordArray = 'None'
slice_Mean_zzDisplay.SelectNormalArray = 'None'
slice_Mean_zzDisplay.SelectTangentArray = 'None'
slice_Mean_zzDisplay.OSPRayScaleArray = 'mean_zz'
slice_Mean_zzDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
slice_Mean_zzDisplay.SelectOrientationVectors = 'None'
slice_Mean_zzDisplay.ScaleFactor = 2.0
slice_Mean_zzDisplay.SelectScaleArray = 'mean_zz'
slice_Mean_zzDisplay.GlyphType = 'Arrow'
slice_Mean_zzDisplay.GlyphTableIndexArray = 'mean_zz'
slice_Mean_zzDisplay.GaussianRadius = 0.1
slice_Mean_zzDisplay.SetScaleArray = ['POINTS', 'mean_zz']
slice_Mean_zzDisplay.ScaleTransferFunction = 'PiecewiseFunction'
slice_Mean_zzDisplay.OpacityArray = ['POINTS', 'mean_zz']
slice_Mean_zzDisplay.OpacityTransferFunction = 'PiecewiseFunction'
slice_Mean_zzDisplay.DataAxesGrid = 'GridAxesRepresentation'
slice_Mean_zzDisplay.PolarAxes = 'PolarAxesRepresentation'
slice_Mean_zzDisplay.ScalarOpacityFunction = mean_zzPWF
slice_Mean_zzDisplay.ScalarOpacityUnitDistance = 0.315133695380462
slice_Mean_zzDisplay.OpacityArrayName = ['POINTS', 'mean_zz']

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
slice_Mean_zzDisplay.OSPRayScaleFunction.Points = [1.05e-09, 0.0, 0.5, 0.0, 2.848, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_Mean_zzDisplay.ScaleTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_Mean_zzDisplay.OpacityTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# get color legend/bar for mean_zzLUT in view renderView1
mean_zzLUTColorBar = GetScalarBar(mean_zzLUT, renderView1)
mean_zzLUTColorBar.AutoOrient = 0
mean_zzLUTColorBar.Orientation = 'Horizontal'
mean_zzLUTColorBar.WindowLocation = 'Any Location'
mean_zzLUTColorBar.Position = [0.6, 0.02]
mean_zzLUTColorBar.Title = 'mean(Uz*Uz)'
mean_zzLUTColorBar.ComponentTitle = ' (t=[T_FIRST_VALUE:T_LAST_VALUE])'
mean_zzLUTColorBar.TitleBold = 1
mean_zzLUTColorBar.TitleFontSize = 20
mean_zzLUTColorBar.AutomaticLabelFormat = 0
mean_zzLUTColorBar.LabelFormat = '%-#6.3f'
mean_zzLUTColorBar.RangeLabelFormat = '%-#6.3f'

# set color bar visibility
mean_zzLUTColorBar.Visibility = 0

# Hide view
Hide(slice_Mean_zz, renderView1)


#############################


# ### cov (ux,ux) ###

# show data from calculator21
slice_Cov_xxDisplay = Show(slice_Cov_xx, renderView1, 'UnstructuredGridRepresentation')

# get color transfer function/color map for 'cov_xx'
cov_xxLUT = GetColorTransferFunction('cov_xx')

cov_xxLUT.ColorSpace = 'RGB'
cov_xxLUT.NumberOfTableValues = 310
cov_xxLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'cov_xx'
cov_xxPWF = GetOpacityTransferFunction('cov_xx')
cov_xxPWF.ScalarRangeInitialized = 1

# modified legend
cov_xxLUT.RGBPoints = All_color
cov_xxPWF.Points = All_PWF_Points
cov_xxLUT.RescaleTransferFunction(-0.05, 0.05)
cov_xxPWF.RescaleTransferFunction(-0.05, 0.05)

# trace defaults for the display properties.
slice_Cov_xxDisplay.Representation = 'Surface'
slice_Cov_xxDisplay.ColorArrayName = ['POINTS', 'cov_xx']
slice_Cov_xxDisplay.LookupTable = cov_xxLUT
slice_Cov_xxDisplay.Opacity = 0.6
slice_Cov_xxDisplay.PointSize = 1.0
slice_Cov_xxDisplay.SelectTCoordArray = 'None'
slice_Cov_xxDisplay.SelectNormalArray = 'None'
slice_Cov_xxDisplay.SelectTangentArray = 'None'
slice_Cov_xxDisplay.OSPRayScaleArray = 'cov_xx'
slice_Cov_xxDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
slice_Cov_xxDisplay.SelectOrientationVectors = 'None'
slice_Cov_xxDisplay.ScaleFactor = 2.0
slice_Cov_xxDisplay.SelectScaleArray = 'cov_xx'
slice_Cov_xxDisplay.GlyphType = 'Arrow'
slice_Cov_xxDisplay.GlyphTableIndexArray = 'cov_xx'
slice_Cov_xxDisplay.GaussianRadius = 0.1
slice_Cov_xxDisplay.SetScaleArray = ['POINTS', 'cov_xx']
slice_Cov_xxDisplay.ScaleTransferFunction = 'PiecewiseFunction'
slice_Cov_xxDisplay.OpacityArray = ['POINTS', 'cov_xx']
slice_Cov_xxDisplay.OpacityTransferFunction = 'PiecewiseFunction'
slice_Cov_xxDisplay.DataAxesGrid = 'GridAxesRepresentation'
slice_Cov_xxDisplay.PolarAxes = 'PolarAxesRepresentation'
slice_Cov_xxDisplay.ScalarOpacityFunction = cov_xxPWF
slice_Cov_xxDisplay.ScalarOpacityUnitDistance = 0.315133695380462
slice_Cov_xxDisplay.OpacityArrayName = ['POINTS', 'cov_xx']

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
slice_Cov_xxDisplay.OSPRayScaleFunction.Points = [1.05e-09, 0.0, 0.5, 0.0, 2.848, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_Cov_xxDisplay.ScaleTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_Cov_xxDisplay.OpacityTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# get color legend/bar for cov_xxLUT in view renderView1
cov_xxLUTColorBar = GetScalarBar(cov_xxLUT, renderView1)
cov_xxLUTColorBar.AutoOrient = 0
cov_xxLUTColorBar.Orientation = 'Horizontal'
cov_xxLUTColorBar.WindowLocation = 'Any Location'
cov_xxLUTColorBar.Position = [0.6, 0.02]
cov_xxLUTColorBar.Title = 'cov(Ux,Ux)'
cov_xxLUTColorBar.ComponentTitle = ' (t=[T_FIRST_VALUE:T_LAST_VALUE])'
cov_xxLUTColorBar.TitleBold = 1
cov_xxLUTColorBar.TitleFontSize = 20
cov_xxLUTColorBar.AutomaticLabelFormat = 0
cov_xxLUTColorBar.LabelFormat = '%-#6.3f'
cov_xxLUTColorBar.RangeLabelFormat = '%-#6.3f'

# set color bar visibility
cov_xxLUTColorBar.Visibility = 0

# Hide view
Hide(slice_Cov_xx, renderView1)

# ### cov (uy,uy) ###

# show data from calculator22
slice_Cov_yyDisplay = Show(slice_Cov_yy, renderView1, 'UnstructuredGridRepresentation')

# get color transfer function/color map for 'cov_yy'
cov_yyLUT = GetColorTransferFunction('cov_yy')

cov_yyLUT.ColorSpace = 'RGB'
cov_yyLUT.NumberOfTableValues = 310
cov_yyLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'cov_yy'
cov_yyPWF = GetOpacityTransferFunction('cov_yy')
cov_yyPWF.ScalarRangeInitialized = 1

# modified legend
cov_yyLUT.RGBPoints = All_color
cov_yyPWF.Points = All_PWF_Points
cov_yyLUT.RescaleTransferFunction(-0.05, 0.05)
cov_yyPWF.RescaleTransferFunction(-0.05, 0.05)

# trace defaults for the display properties.
slice_Cov_yyDisplay.Representation = 'Surface'
slice_Cov_yyDisplay.ColorArrayName = ['POINTS', 'cov_yy']
slice_Cov_yyDisplay.LookupTable = cov_yyLUT
slice_Cov_yyDisplay.Opacity = 0.6
slice_Cov_yyDisplay.PointSize = 1.0
slice_Cov_yyDisplay.SelectTCoordArray = 'None'
slice_Cov_yyDisplay.SelectNormalArray = 'None'
slice_Cov_yyDisplay.SelectTangentArray = 'None'
slice_Cov_yyDisplay.OSPRayScaleArray = 'cov_yy'
slice_Cov_yyDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
slice_Cov_yyDisplay.SelectOrientationVectors = 'None'
slice_Cov_yyDisplay.ScaleFactor = 2.0
slice_Cov_yyDisplay.SelectScaleArray = 'cov_yy'
slice_Cov_yyDisplay.GlyphType = 'Arrow'
slice_Cov_yyDisplay.GlyphTableIndexArray = 'cov_yy'
slice_Cov_yyDisplay.GaussianRadius = 0.1
slice_Cov_yyDisplay.SetScaleArray = ['POINTS', 'cov_yy']
slice_Cov_yyDisplay.ScaleTransferFunction = 'PiecewiseFunction'
slice_Cov_yyDisplay.OpacityArray = ['POINTS', 'cov_yy']
slice_Cov_yyDisplay.OpacityTransferFunction = 'PiecewiseFunction'
slice_Cov_yyDisplay.DataAxesGrid = 'GridAxesRepresentation'
slice_Cov_yyDisplay.PolarAxes = 'PolarAxesRepresentation'
slice_Cov_yyDisplay.ScalarOpacityFunction = cov_yyPWF
slice_Cov_yyDisplay.ScalarOpacityUnitDistance = 0.315133695380462
slice_Cov_yyDisplay.OpacityArrayName = ['POINTS', 'cov_yy']

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
slice_Cov_yyDisplay.OSPRayScaleFunction.Points = [1.05e-09, 0.0, 0.5, 0.0, 2.848, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_Cov_yyDisplay.ScaleTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_Cov_yyDisplay.OpacityTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# get color legend/bar for cov_yyLUT in view renderView1
cov_yyLUTColorBar = GetScalarBar(cov_yyLUT, renderView1)
cov_yyLUTColorBar.AutoOrient = 0
cov_yyLUTColorBar.Orientation = 'Horizontal'
cov_yyLUTColorBar.WindowLocation = 'Any Location'
cov_yyLUTColorBar.Position = [0.6, 0.02]
cov_yyLUTColorBar.Title = 'cov(Uy,Uy)'
cov_yyLUTColorBar.ComponentTitle = ' (t=[T_FIRST_VALUE:T_LAST_VALUE])'
cov_yyLUTColorBar.TitleBold = 1
cov_yyLUTColorBar.TitleFontSize = 20
cov_yyLUTColorBar.AutomaticLabelFormat = 0
cov_yyLUTColorBar.LabelFormat = '%-#6.3f'
cov_yyLUTColorBar.RangeLabelFormat = '%-#6.3f'

# set color bar visibility
cov_yyLUTColorBar.Visibility = 0

# Hide view
Hide(slice_Cov_yy, renderView1)


# ### cov (uz,uz) ###

# show data from calculator23
slice_Cov_zzDisplay = Show(slice_Cov_zz, renderView1, 'UnstructuredGridRepresentation')

# get color transfer function/color map for 'cov_zz'
cov_zzLUT = GetColorTransferFunction('cov_zz')

cov_zzLUT.ColorSpace = 'RGB'
cov_zzLUT.NumberOfTableValues = 310
cov_zzLUT.ScalarRangeInitialized = 1.0

# get opacity transfer function/opacity map for 'cov_zz'
cov_zzPWF = GetOpacityTransferFunction('cov_zz')
cov_zzPWF.ScalarRangeInitialized = 1

# modified legend
cov_zzLUT.RGBPoints = All_color
cov_zzPWF.Points = All_PWF_Points
cov_zzLUT.RescaleTransferFunction(-0.05, 0.05)
cov_zzPWF.RescaleTransferFunction(-0.05, 0.05)

# trace defaults for the display properties.
slice_Cov_zzDisplay.Representation = 'Surface'
slice_Cov_zzDisplay.ColorArrayName = ['POINTS', 'cov_zz']
slice_Cov_zzDisplay.LookupTable = cov_zzLUT
slice_Cov_zzDisplay.Opacity = 0.6
slice_Cov_zzDisplay.PointSize = 1.0
slice_Cov_zzDisplay.SelectTCoordArray = 'None'
slice_Cov_zzDisplay.SelectNormalArray = 'None'
slice_Cov_zzDisplay.SelectTangentArray = 'None'
slice_Cov_zzDisplay.OSPRayScaleArray = 'cov_zz'
slice_Cov_zzDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
slice_Cov_zzDisplay.SelectOrientationVectors = 'None'
slice_Cov_zzDisplay.ScaleFactor = 2.0
slice_Cov_zzDisplay.SelectScaleArray = 'cov_zz'
slice_Cov_zzDisplay.GlyphType = 'Arrow'
slice_Cov_zzDisplay.GlyphTableIndexArray = 'cov_zz'
slice_Cov_zzDisplay.GaussianRadius = 0.1
slice_Cov_zzDisplay.SetScaleArray = ['POINTS', 'cov_zz']
slice_Cov_zzDisplay.ScaleTransferFunction = 'PiecewiseFunction'
slice_Cov_zzDisplay.OpacityArray = ['POINTS', 'cov_zz']
slice_Cov_zzDisplay.OpacityTransferFunction = 'PiecewiseFunction'
slice_Cov_zzDisplay.DataAxesGrid = 'GridAxesRepresentation'
slice_Cov_zzDisplay.PolarAxes = 'PolarAxesRepresentation'
slice_Cov_zzDisplay.ScalarOpacityFunction = cov_zzPWF
slice_Cov_zzDisplay.ScalarOpacityUnitDistance = 0.315133695380462
slice_Cov_zzDisplay.OpacityArrayName = ['POINTS', 'cov_zz']

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
slice_Cov_zzDisplay.OSPRayScaleFunction.Points = [1.05e-09, 0.0, 0.5, 0.0, 2.848, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_Cov_zzDisplay.ScaleTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_Cov_zzDisplay.OpacityTransferFunction.Points = [-0.43, 0.0, 0.5, 0.0, 0.43, 1.0, 0.5, 0.0]

# get color legend/bar for cov_zzLUT in view renderView1
cov_zzLUTColorBar = GetScalarBar(cov_zzLUT, renderView1)
cov_zzLUTColorBar.AutoOrient = 0
cov_zzLUTColorBar.Orientation = 'Horizontal'
cov_zzLUTColorBar.WindowLocation = 'Any Location'
cov_zzLUTColorBar.Position = [0.6, 0.02]
cov_zzLUTColorBar.Title = 'cov(Uz,Uz)'
cov_zzLUTColorBar.ComponentTitle = ' (t=[T_FIRST_VALUE:T_LAST_VALUE])'
cov_zzLUTColorBar.TitleBold = 1
cov_zzLUTColorBar.TitleFontSize = 20
cov_zzLUTColorBar.AutomaticLabelFormat = 0
cov_zzLUTColorBar.LabelFormat = '%-#6.3f'
cov_zzLUTColorBar.RangeLabelFormat = '%-#6.3f'

# Hide color legend
slice_Cov_zzDisplay.SetScalarBarVisibility(renderView1, False)

# set color bar visibility
cov_zzLUTColorBar.Visibility = 0

# Hide view
Hide(slice_Cov_zz, renderView1)


######################################################
# hide data in view
#Hide(temporalStatistics1, renderView1)
#Hide(temporalStatistics2, renderView1)

Hide(slice_Mean_xy, renderView1)
Hide(slice_Mean_yz, renderView1)
Hide(slice_Mean_zx, renderView1)
Hide(slice_Mean_xx, renderView1)
Hide(slice_Mean_yy, renderView1)
Hide(slice_Mean_zz, renderView1)

#Hide(calculator1, renderView1)
#Hide(calculator2, renderView1)

Hide(slice_Cov_xy, renderView1)
Hide(slice_Cov_yz, renderView1)
Hide(slice_Cov_zx, renderView1)
Hide(slice_Cov_xx, renderView1)
Hide(slice_Cov_yy, renderView1)
Hide(slice_Cov_zz, renderView1)

# Hide color legend
slice_Mean_xyDisplay.SetScalarBarVisibility(renderView1, False)
slice_Mean_yzDisplay.SetScalarBarVisibility(renderView1, False)
slice_Mean_zxDisplay.SetScalarBarVisibility(renderView1, False)
slice_Mean_xxDisplay.SetScalarBarVisibility(renderView1, False)
slice_Mean_yyDisplay.SetScalarBarVisibility(renderView1, False)
slice_Mean_zzDisplay.SetScalarBarVisibility(renderView1, False)

slice_Cov_xyDisplay.SetScalarBarVisibility(renderView1, False)
slice_Cov_yzDisplay.SetScalarBarVisibility(renderView1, False)
slice_Cov_zxDisplay.SetScalarBarVisibility(renderView1, False)
slice_Cov_xxDisplay.SetScalarBarVisibility(renderView1, False)
slice_Cov_yyDisplay.SetScalarBarVisibility(renderView1, False)
slice_Cov_zzDisplay.SetScalarBarVisibility(renderView1, False)

# legend
mean_xyLUTColorBar.Visibility = 0
mean_yzLUTColorBar.Visibility = 0
mean_zxLUTColorBar.Visibility = 0
mean_xxLUTColorBar.Visibility = 0
mean_yyLUTColorBar.Visibility = 0
mean_zzLUTColorBar.Visibility = 0

cov_xyLUTColorBar.Visibility = 0
cov_yzLUTColorBar.Visibility = 0
cov_zxLUTColorBar.Visibility = 0
cov_xxLUTColorBar.Visibility = 0
cov_yyLUTColorBar.Visibility = 0
cov_zzLUTColorBar.Visibility = 0

######################################################

### U ###

# show data in view
Show(base_Calcfoam, renderView1)
base_CalcfoamDisplay.SetScalarBarVisibility(renderView1, True)
uLUTColorBar.Visibility = 1

SetActiveSource(base_Calcfoam)
Render()
view = GetActiveView()

Hide(base_Calcfoam, renderView1)
base_CalcfoamDisplay.SetScalarBarVisibility(renderView1, False)
uLUTColorBar.Visibility = 0

######################################################

# ### mean (ux,uy) ###

Show(slice_Mean_xy, renderView1)
slice_Mean_xyDisplay.SetScalarBarVisibility(renderView1, True)
mean_xyLUTColorBar.Visibility = 1

SetActiveSource(slice_Mean_xy)
Render()
view = GetActiveView()
view.ViewSize = [ viewSize_length, viewSize_height ]

mean_xyLUT.RescaleTransferFunction(-0.05, 0.05)
mean_xyPWF.RescaleTransferFunction(-0.05, 0.05)

slice_Mean_xyDisplay.Representation = 'Surface'
slice_Mean_xyDisplay.PointSize = pointSize_for_SurfaceDisplay

#slice_Mean_xyDisplay.Representation = 'Points'
#slice_Mean_xyDisplay.PointSize = pointSize_for_PointsDisplay

SaveScreenshot('mean_xy.png',view)

Hide(slice_Mean_xy, renderView1)
slice_Mean_xyDisplay.SetScalarBarVisibility(renderView1, False)
mean_xyLUTColorBar.Visibility = 0

# ### mean (uy,uz) ###

Show(slice_Mean_yz, renderView1)
slice_Mean_yzDisplay.SetScalarBarVisibility(renderView1, True)
mean_yzLUTColorBar.Visibility = 1

SetActiveSource(slice_Mean_yz)
Render()
view = GetActiveView()
view.ViewSize = [ viewSize_length, viewSize_height ]
mean_yzLUT.RescaleTransferFunction(-0.05, 0.05)
mean_yzPWF.RescaleTransferFunction(-0.05, 0.05)

slice_Mean_yzDisplay.Representation = 'Surface'
slice_Mean_yzDisplay.PointSize = pointSize_for_SurfaceDisplay

#slice_Mean_yzDisplay.Representation = 'Points'
#slice_Mean_yzDisplay.PointSize = pointSize_for_PointsDisplay

SaveScreenshot('mean_yz.png',view)

Hide(slice_Mean_yz, renderView1)
slice_Mean_yzDisplay.SetScalarBarVisibility(renderView1, False)
mean_yzLUTColorBar.Visibility = 0

# ### mean (uz,ux) ###

Show(slice_Mean_zx, renderView1)
slice_Mean_zxDisplay.SetScalarBarVisibility(renderView1, True)
mean_zxLUTColorBar.Visibility = 1

SetActiveSource(slice_Mean_zx)
Render()
view = GetActiveView()
view.ViewSize = [ viewSize_length, viewSize_height ]
mean_zxLUT.RescaleTransferFunction(-0.05, 0.05)
mean_zxPWF.RescaleTransferFunction(-0.05, 0.05)

slice_Mean_zxDisplay.Representation = 'Surface'
slice_Mean_zxDisplay.PointSize = pointSize_for_SurfaceDisplay

#slice_Mean_zxDisplay.Representation = 'Points'
#slice_Mean_zxDisplay.PointSize = pointSize_for_PointsDisplay

SaveScreenshot('mean_zx.png',view)

Hide(slice_Mean_zx, renderView1)
slice_Mean_zxDisplay.SetScalarBarVisibility(renderView1, False)
mean_zxLUTColorBar.Visibility = 0

######################################################

# ### cov (ux,uy) ###

Show(slice_Cov_xy, renderView1)
slice_Cov_xyDisplay.SetScalarBarVisibility(renderView1, True)
cov_xyLUTColorBar.Visibility = 1

SetActiveSource(slice_Cov_xy)
Render()
view = GetActiveView()
view.ViewSize = [ viewSize_length, viewSize_height ]
cov_xyLUT.RescaleTransferFunction(-0.05, 0.05)
cov_xyPWF.RescaleTransferFunction(-0.05, 0.05)

slice_Cov_xyDisplay.Representation = 'Surface'
slice_Cov_xyDisplay.PointSize = pointSize_for_SurfaceDisplay

#slice_Cov_xyDisplay.Representation = 'Points'
#slice_Cov_xyDisplay.PointSize = pointSize_for_PointsDisplay

SaveScreenshot('cov_xy.png',view)

Hide(slice_Cov_xy, renderView1)
slice_Cov_xyDisplay.SetScalarBarVisibility(renderView1, False)
cov_xyLUTColorBar.Visibility = 0

# ### cov (uy,uz) ###

Show(slice_Cov_yz, renderView1)
slice_Cov_yzDisplay.SetScalarBarVisibility(renderView1, True)
cov_yzLUTColorBar.Visibility = 1

SetActiveSource(slice_Cov_yz)
Render()
view = GetActiveView()
view.ViewSize = [ viewSize_length, viewSize_height ]
cov_yzLUT.RescaleTransferFunction(-0.05, 0.05)
cov_yzPWF.RescaleTransferFunction(-0.05, 0.05)

slice_Cov_yzDisplay.Representation = 'Surface'
slice_Cov_yzDisplay.PointSize = pointSize_for_SurfaceDisplay

#slice_Cov_yzDisplay.Representation = 'Points'
#slice_Cov_yzDisplay.PointSize = pointSize_for_PointsDisplay

SaveScreenshot('cov_yz.png',view)

Hide(slice_Cov_yz, renderView1)
slice_Cov_yzDisplay.SetScalarBarVisibility(renderView1, False)
cov_yzLUTColorBar.Visibility = 0

# ### cov (uz,ux) ###

Show(slice_Cov_zx, renderView1)
slice_Cov_zxDisplay.SetScalarBarVisibility(renderView1, True)
cov_zxLUTColorBar.Visibility = 1

SetActiveSource(slice_Cov_zx)
Render()
view = GetActiveView()
view.ViewSize = [ viewSize_length, viewSize_height ]
cov_zxLUT.RescaleTransferFunction(-0.05, 0.05)
cov_zxPWF.RescaleTransferFunction(-0.05, 0.05)

slice_Cov_zxDisplay.Representation = 'Surface'
slice_Cov_zxDisplay.PointSize = pointSize_for_SurfaceDisplay

#slice_Cov_zxDisplay.Representation = 'Points'
#slice_Cov_zxDisplay.PointSize = pointSize_for_PointsDisplay

SaveScreenshot('cov_zx.png',view)

Hide(slice_Cov_zx, renderView1)
slice_Cov_zxDisplay.SetScalarBarVisibility(renderView1, False)
cov_zxLUTColorBar.Visibility = 0

######################################################

# ### mean (ux,ux) ###

Show(slice_Mean_xx, renderView1)
slice_Mean_xxDisplay.SetScalarBarVisibility(renderView1, True)
mean_xxLUTColorBar.Visibility = 1

SetActiveSource(slice_Mean_xx)
Render()
view = GetActiveView()
view.ViewSize = [ viewSize_length, viewSize_height ]
mean_xxLUT.RescaleTransferFunction(-0.05, 0.05)
mean_xxPWF.RescaleTransferFunction(-0.05, 0.05)

slice_Mean_xxDisplay.Representation = 'Surface'
slice_Mean_xxDisplay.PointSize = pointSize_for_SurfaceDisplay

#slice_Mean_xxDisplay.Representation = 'Points'
#slice_Mean_xxDisplay.PointSize = pointSize_for_PointsDisplay

SaveScreenshot('mean_xx.png',view)

Hide(slice_Mean_xx, renderView1)
slice_Mean_xxDisplay.SetScalarBarVisibility(renderView1, False)
mean_xxLUTColorBar.Visibility = 0

# ### mean (uy,uy) ###

Show(slice_Mean_yy, renderView1)
slice_Mean_yyDisplay.SetScalarBarVisibility(renderView1, True)
mean_yyLUTColorBar.Visibility = 1

SetActiveSource(slice_Mean_yy)
Render()
view = GetActiveView()
view.ViewSize = [ viewSize_length, viewSize_height ]
mean_yyLUT.RescaleTransferFunction(-0.05, 0.05)
mean_yyPWF.RescaleTransferFunction(-0.05, 0.05)

slice_Mean_yyDisplay.Representation = 'Surface'
slice_Mean_yyDisplay.PointSize = pointSize_for_SurfaceDisplay

#slice_Mean_yyDisplay.Representation = 'Points'
#slice_Mean_yyDisplay.PointSize = pointSize_for_PointsDisplay

SaveScreenshot('mean_yy.png',view)

Hide(slice_Mean_yy, renderView1)
slice_Mean_yyDisplay.SetScalarBarVisibility(renderView1, False)
mean_yyLUTColorBar.Visibility = 0

# ### mean (uz,ux) ###

Show(slice_Mean_zz, renderView1)
slice_Mean_zzDisplay.SetScalarBarVisibility(renderView1, True)
mean_zzLUTColorBar.Visibility = 1

SetActiveSource(slice_Mean_zz)
Render()
view = GetActiveView()
view.ViewSize = [ viewSize_length, viewSize_height ]
mean_zzLUT.RescaleTransferFunction(-0.05, 0.05)
mean_zzPWF.RescaleTransferFunction(-0.05, 0.05)

slice_Mean_zzDisplay.Representation = 'Surface'
slice_Mean_zzDisplay.PointSize = pointSize_for_SurfaceDisplay

#slice_Mean_zzDisplay.Representation = 'Points'
#slice_Mean_zzDisplay.PointSize = pointSize_for_PointsDisplay

SaveScreenshot('mean_zz.png',view)

Hide(slice_Mean_zz, renderView1)
slice_Mean_zzDisplay.SetScalarBarVisibility(renderView1, False)
mean_zzLUTColorBar.Visibility = 0

######################################################

# ### cov (ux,ux) ###

Show(slice_Cov_xx, renderView1)
slice_Cov_xxDisplay.SetScalarBarVisibility(renderView1, True)
cov_xxLUTColorBar.Visibility = 1

SetActiveSource(slice_Cov_xx)
Render()
view = GetActiveView()
view.ViewSize = [ viewSize_length, viewSize_height ]
cov_xxLUT.RescaleTransferFunction(-0.05, 0.05)
cov_xxPWF.RescaleTransferFunction(-0.05, 0.05)

slice_Cov_xxDisplay.Representation = 'Surface'
slice_Cov_xxDisplay.PointSize = pointSize_for_SurfaceDisplay

#slice_Cov_xxDisplay.Representation = 'Points'
#slice_Cov_xxDisplay.PointSize = pointSize_for_PointsDisplay

SaveScreenshot('cov_xx.png',view)

Hide(slice_Cov_xx, renderView1)
slice_Cov_xxDisplay.SetScalarBarVisibility(renderView1, False)
cov_xxLUTColorBar.Visibility = 0

# ### cov (uy,uy) ###

Show(slice_Cov_yy, renderView1)
slice_Cov_yyDisplay.SetScalarBarVisibility(renderView1, True)
cov_yyLUTColorBar.Visibility = 1

SetActiveSource(slice_Cov_yy)
Render()
view = GetActiveView()
view.ViewSize = [ viewSize_length, viewSize_height ]
cov_yyLUT.RescaleTransferFunction(-0.05, 0.05)
cov_yyPWF.RescaleTransferFunction(-0.05, 0.05)

slice_Cov_yyDisplay.Representation = 'Surface'
slice_Cov_yyDisplay.PointSize = pointSize_for_SurfaceDisplay

#slice_Cov_yyDisplay.Representation = 'Points'
#slice_Cov_yyDisplay.PointSize = pointSize_for_PointsDisplay

SaveScreenshot('cov_yy.png',view)

Hide(slice_Cov_yy, renderView1)
slice_Cov_yyDisplay.SetScalarBarVisibility(renderView1, False)
cov_yyLUTColorBar.Visibility = 0

# ### cov (uz,uz) ###

Show(slice_Cov_zz, renderView1)
slice_Cov_zzDisplay.SetScalarBarVisibility(renderView1, True)
cov_zzLUTColorBar.Visibility = 1

SetActiveSource(slice_Cov_zz)
Render()
view = GetActiveView()
view.ViewSize = [ viewSize_length, viewSize_height ]
cov_zzLUT.RescaleTransferFunction(-0.05, 0.05)
cov_zzPWF.RescaleTransferFunction(-0.05, 0.05)

slice_Cov_zzDisplay.Representation = 'Surface'
slice_Cov_zzDisplay.PointSize = pointSize_for_SurfaceDisplay

#slice_Cov_zzDisplay.Representation = 'Points'
#slice_Cov_zzDisplay.PointSize = pointSize_for_PointsDisplay

SaveScreenshot('cov_zz.png',view)

Hide(slice_Cov_zz, renderView1)
slice_Cov_zzDisplay.SetScalarBarVisibility(renderView1, False)
cov_zzLUTColorBar.Visibility = 0


# ----------------------------------------------------------------

# ----------------------------------------------------------------
# CSV files

# Cf. https://kitware.github.io/paraview-docs/latest/python/paraview.simple.DataSetCSVWriter.html

# first files : x,y,z,Var -> AddMetaData=1
# other files : Var -> AddMetaData=0
   
code_Z = 0

# ### mean (ux,uy) ###

SaveData('mean_xy.csv',
proxy=slice_Mean_xy,
ChooseArraysToWrite=1,
PointDataArrays=['mean_xy'],
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
   
# ### mean (uy,uz) ###

if code_Z == 1:
  SaveData('mean_yz.csv',
  proxy=temporalStatistics12,
  ChooseArraysToWrite=1,
  PointDataArrays=['mean_yz'],
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
   
# ### mean (uz,ux) ###

if code_Z == 1:
  SaveData('mean_zx.csv',
  proxy=temporalStatistics13,
  ChooseArraysToWrite=1,
  PointDataArrays=['mean_zx'],
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
  
# ### cov (ux,uy)=mean(ux*uy)-mean(ux)*mean(uy) ###

SaveData('cov_xy.csv',
proxy=slice_Cov_xy,
ChooseArraysToWrite=1,
PointDataArrays=['cov_xy'],
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
   
# ### cov (uy,uz)=mean(uy*uz)-mean(uy)*mean(uz) ###

if code_Z == 1:
  SaveData('cov_yz.csv',
  proxy=calculator12,
  ChooseArraysToWrite=1,
  PointDataArrays=['cov_yz'],
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
   
# ### cov (uz,ux)=mean(uz*ux)-mean(uz)*mean(ux) ###

if code_Z == 1:
  SaveData('cov_zx.csv',
  proxy=calculator13,
  ChooseArraysToWrite=1,
  PointDataArrays=['cov_zx'],
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

   
# ### mean (ux,ux) ###

SaveData('mean_xx.csv',
proxy=slice_Mean_xx,
ChooseArraysToWrite=1,
PointDataArrays=['mean_xx'],
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
   
# ### mean (uy,uy) ###

SaveData('mean_yy.csv',
proxy=slice_Mean_yy,
ChooseArraysToWrite=1,
PointDataArrays=['mean_yy'],
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
   
# ### mean (uz,uz) ###

if code_Z == 1:
  SaveData('mean_zz.csv',
  proxy=slice_Mean_zz,
  ChooseArraysToWrite=1,
  PointDataArrays=['mean_zz'],
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
  
# ### cov (ux,ux)=mean(ux*ux)-mean(ux)*mean(ux) ###

SaveData('cov_xx.csv',
proxy=slice_Cov_xx,
ChooseArraysToWrite=1,
PointDataArrays=['cov_xx'],
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
   
# ### cov (uy,uy)=mean(uy*uy)-mean(uy)*mean(uy) ###

SaveData('cov_yy.csv',
proxy=slice_Cov_yy,
ChooseArraysToWrite=1,
PointDataArrays=['cov_yy'],
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
   
# ### cov (uz,uz)=mean(uz*uz)-mean(uz)*mean(uz) ###

if code_Z == 1:
  SaveData('cov_zz.csv',
  proxy=slice_Cov_zz,
  ChooseArraysToWrite=1,
  PointDataArrays=['cov_zz'],
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

# ----------------------------------------------------------------


if __name__ == '__main__':
    # generate extracts
    SaveExtracts(ExtractsOutputDirectory='extracts')
