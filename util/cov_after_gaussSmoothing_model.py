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
## step1 = Ux gaussian interpolation
## step2 = slice Z=Zslice (=Lz/2) of the Ux gaussian interpolation
## 
##           => CSV file
##
## Next operation (C++ code) : CSV file -> time averaging 
##
## Next operation (tcsh shell script) : CSV file -> synthetic PIV file
##
## step1 = rewritting with column IsValid
## step2 = adding noise for data type [raw openfoam results only]
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

#base_Calcfoam = OpenFOAMReader(registrationName='toto.foam', FileName='/workspace/MORAANE/exemple_openfoam/toto/toto.foam')

base_Calcfoam.MeshRegions = ['internalMesh']
base_Calcfoam.CellArrays = ['U']

# create a new 'Point Volume Interpolator'
box_Calcfoam = PointVolumeInterpolator(registrationName='Box_smoothGaussianCrop', Input=base_Calcfoam,
    Source='Bounded Volume')
box_Calcfoam.Kernel = 'GaussianKernel'
box_Calcfoam.Locator = 'Static Point Locator'

# init the 'GaussianKernel' selected for 'Kernel'
box_Calcfoam.Kernel.Radius = Radius

# init the 'Bounded Volume' selected for 'Source'
box_Calcfoam.Source.Origin = [Origin_X, Origin_Y, Origin_Z]
box_Calcfoam.Source.Scale = [Scale_X, Scale_Y, Scale_Z]

#box_Calcfoam.Source.RefinementMode = 'Use cell-size'
#box_Calcfoam.Source.CellSize = 0.0470 # slice : 298x184x1 points / PIV ref : 295 x 182 points

box_Calcfoam.Source.RefinementMode = 'Use resolution'
box_Calcfoam.Source.Resolution = [Resolution_X, Resolution_Y, Resolution_Z]

box_Calcfoam.NullPointsStrategy = 0 # ->MaskPoints (MASK_POINTS)
#box_Calcfoam.NullPointsStrategy = 1 # -> NullPoint (NULL_VALUE)
#box_Calcfoam.NullPointsStrategy = 2 # -> CLOSEST_POINT
box_Calcfoam.NullValue = 0.0

# create a new 'Slice'
slice_box = Slice(registrationName='Slice_xy', Input=box_Calcfoam)
slice_box.SliceType = 'Plane'
slice_box.HyperTreeGridSlicer = 'Plane'
slice_box.SliceOffsetValues = [0.0]

# init the 'Plane' selected for 'SliceType'
slice_box.SliceType.Origin = [x0_dom, y0_dom, Zslice]
slice_box.SliceType.Normal = [0.0, 0.0, 1.0]

# init the 'Plane' selected for 'HyperTreeGridSlicer'
slice_box.HyperTreeGridSlicer.Origin = [x0_dom, y0_dom, Zslice]


# ----------------------------------------------------------------
# setup the visualization in view 'renderView1'
# ----------------------------------------------------------------

# show data from slice_box
slice_boxDisplay = Show(slice_box, renderView1, 'GeometryRepresentation')

# get color transfer function/color map for 'U'
uLUT = GetColorTransferFunction('U')
uLUT.RGBPoints = [0.0, 0.0862745098039216, 0.00392156862745098, 0.298039215686275, 0.05201483531791077, 0.113725, 0.0235294, 0.45098, 0.0952134903030088, 0.105882, 0.0509804, 0.509804, 0.12518812656145897, 0.0392157, 0.0392157, 0.560784, 0.15428118830408033, 0.0313725, 0.0980392, 0.6, 0.18249257528358612, 0.0431373, 0.164706, 0.639216, 0.22304640647390042, 0.054902, 0.243137, 0.678431, 0.2768244568854045, 0.054902, 0.317647, 0.709804, 0.3429448717333102, 0.0509804, 0.396078, 0.741176, 0.3858129806999746, 0.0392157, 0.466667, 0.768627, 0.42868108966663904, 0.0313725, 0.537255, 0.788235, 0.47342269147339266, 0.0313725, 0.615686, 0.811765, 0.5192661702532692, 0.0235294, 0.709804, 0.831373, 0.5651097492804272, 0.0509804, 0.8, 0.85098, 0.603018756675958, 0.0705882, 0.854902, 0.870588, 0.6382830405239756, 0.262745, 0.901961, 0.862745, 0.6691392512982651, 0.423529, 0.941176, 0.87451, 0.7167459793570966, 0.572549, 0.964706, 0.835294, 0.7484838648944965, 0.658824, 0.980392, 0.843137, 0.7714056042844348, 0.764706, 0.980392, 0.866667, 0.7960905428296873, 0.827451, 0.980392, 0.886275, 0.8445788955279885, 0.913725, 0.988235, 0.937255, 0.859566213657216, 1.0, 1.0, 0.972549019607843, 0.8745535317864439, 0.988235, 0.980392, 0.870588, 0.8965936966605428, 0.992156862745098, 0.972549019607843, 0.803921568627451, 0.9133442139450846, 0.992157, 0.964706, 0.713725, 0.9415556009245906, 0.988235, 0.956863, 0.643137, 0.9865175051886329, 0.980392, 0.917647, 0.509804, 1.0244266128314397, 0.968627, 0.87451, 0.407843, 1.0632172949900807, 0.94902, 0.823529, 0.321569, 1.0914286819695853, 0.929412, 0.776471, 0.278431, 1.1328641879230095, 0.909804, 0.717647, 0.235294, 1.1698916208027037, 0.890196, 0.658824, 0.196078, 1.2003070510665947, 0.878431, 0.619608, 0.168627, 1.2431751600332588, 0.870588, 0.54902, 0.156863, 1.286043268999923, 0.85098, 0.47451, 0.145098, 1.328911377966587, 0.831373, 0.411765, 0.133333, 1.3717794869332516, 0.811765, 0.345098, 0.113725, 1.4146475958999156, 0.788235, 0.266667, 0.0941176, 1.4575157048665797, 0.741176, 0.184314, 0.0745098, 1.5003838138332437, 0.690196, 0.12549, 0.0627451, 1.5432519227999077, 0.619608, 0.0627451, 0.0431373, 1.5833650149720166, 0.54902, 0.027451, 0.0705882, 1.618629269059128, 0.470588, 0.0156863, 0.0901961, 1.6583015523617874, 0.4, 0.00392157, 0.101961, 1.7147243586665644, 0.188235294117647, 0.0, 0.0705882352941176]
uLUT.ColorSpace = 'Lab'
uLUT.NumberOfTableValues = 310
uLUT.ScalarRangeInitialized = 1.0

# trace defaults for the display properties.
slice_boxDisplay.Representation = 'Surface'
slice_boxDisplay.ColorArrayName = ['POINTS', 'U']
slice_boxDisplay.LookupTable = uLUT
slice_boxDisplay.SelectTCoordArray = 'None'
slice_boxDisplay.SelectNormalArray = 'None'
slice_boxDisplay.SelectTangentArray = 'None'
slice_boxDisplay.OSPRayScaleArray = 'p'
slice_boxDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
slice_boxDisplay.SelectOrientationVectors = 'U'
slice_boxDisplay.ScaleFactor = 1.2000000000000002
slice_boxDisplay.SelectScaleArray = 'p'
slice_boxDisplay.GlyphType = 'Arrow'
slice_boxDisplay.GlyphTableIndexArray = 'p'
slice_boxDisplay.GaussianRadius = 0.06
slice_boxDisplay.SetScaleArray = ['POINTS', 'p']
slice_boxDisplay.ScaleTransferFunction = 'PiecewiseFunction'
slice_boxDisplay.OpacityArray = ['POINTS', 'p']
slice_boxDisplay.OpacityTransferFunction = 'PiecewiseFunction'
slice_boxDisplay.DataAxesGrid = 'GridAxesRepresentation'
slice_boxDisplay.PolarAxes = 'PolarAxesRepresentation'

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
slice_boxDisplay.OSPRayScaleFunction.Points = [273.0, 0.0, 0.5, 0.0, 293.0, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
slice_boxDisplay.ScaleTransferFunction.Points = [-0.276429146528244, 0.0, 0.5, 0.0, 0.05624571070075035, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
slice_boxDisplay.OpacityTransferFunction.Points = [-0.276429146528244, 0.0, 0.5, 0.0, 0.05624571070075035, 1.0, 0.5, 0.0]

# setup the color legend parameters for each legend in this view

# get color legend/bar for uLUT in view renderView1
uLUTColorBar = GetScalarBar(uLUT, renderView1)
uLUTColorBar.Title = 'U'
uLUTColorBar.ComponentTitle = 'Magnitude'
uLUTColorBar.TitleBold = 1
uLUTColorBar.TitleFontSize = 20
uLUTColorBar.AutomaticLabelFormat = 0
uLUTColorBar.LabelFormat = '%-#6.3f'
uLUTColorBar.RangeLabelFormat = '%-#6.3f'

# set color bar visibility
uLUTColorBar.Visibility = 1

# show color legend
slice_boxDisplay.SetScalarBarVisibility(renderView1, True)

# ----------------------------------------------------------------
# setup color maps and opacity mapes used in the visualization
# note: the Get..() functions create a new object, if needed
# ----------------------------------------------------------------

# get opacity transfer function/opacity map for 'U'
uPWF = GetOpacityTransferFunction('U')
uPWF.Points = [0.0, 0.0, 0.5, 0.0, 1.7147243586665644, 1.0, 0.5, 0.0]
uPWF.ScalarRangeInitialized = 1

SaveData('U.csv',
proxy=slice_box,
ChooseArraysToWrite=1,
PointDataArrays=['U'],
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

# ----------------------------------------------------------------

if __name__ == '__main__':
    # generate extracts
    SaveExtracts(ExtractsOutputDirectory='extracts')
