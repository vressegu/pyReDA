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

# for time PNG genration, Cf. http://runinchaos.com/CFD/python_paravew.html

# ----------------------------------------------------------------
# setup
# ----------------------------------------------------------------
IsoQ = Q_VALUE
IsoQ_text = "Q=%3.1f" % IsoQ

planZ = Z_VALUE
planZ_text = "Z=%3.1f" % planZ
                      
time = TIME_VALUE
time_text = "t=%6.2f" % time

title1 = IsoQ_text + " colored by U "
title2 = ": "+time_text

timeStart = 1100
timeEnd = 1200

timeStart = TIME_START_VALUE
timeEnd = TIME_END_VALUE

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

# ----------------------------------------------------------------
# setup views used in the visualization
# ----------------------------------------------------------------

# get the material library
materialLibrary1 = GetMaterialLibrary()

# Create a new 'Render View'
renderView1 = CreateView('RenderView')
renderView1.ViewSize = [950, 430]
renderView1.AxesGrid = 'GridAxes3DActor'
renderView1.CenterAxesVisibility = 1
renderView1.StereoType = 'Crystal Eyes'
renderView1.CameraFocalDisk = 1.0
renderView1.BackEnd = 'OSPRay raycaster'
renderView1.OSPRayMaterialLibrary = materialLibrary1

# Geometry LES3900
renderView1.CenterOfRotation = [10.0, 0.0, planZ]
renderView1.CameraPosition = [2.10, 10.22, 13.40]
renderView1.CameraFocalPoint = [10.00, 0, planZ]
renderView1.CameraViewUp = [0.33, 0.81, -0.48]
renderView1.CameraParallelScale = 14.23

# init the 'GridAxes3DActor' selected for 'AxesGrid'
renderView1.AxesGrid.Visibility = 1

SetActiveView(None)

# ----------------------------------------------------------------
# setup view layouts
# ----------------------------------------------------------------

# create new layout object 'Layout #1'
layout1 = CreateLayout(name='Layout #1')
layout1.AssignView(0, renderView1)
layout1.SetSize(950, 430)

# ----------------------------------------------------------------
# restore active view
SetActiveView(renderView1)
# ----------------------------------------------------------------

# ----------------------------------------------------------------
# setup the data processing pipelines
# ----------------------------------------------------------------

# Geometry LES3900

# create a new 'Cylinder'
cylinder1 = Cylinder(registrationName='Cylinder1')
cylinder1.Resolution = 208
cylinder1.Height = 4.0
cylinder1.Center = [5.0, 0.0, 0.0]

# create a new 'Plane'
plane1 = Plane(registrationName='Plane1')
plane1.Origin = [3.5, -3.0, planZ]
plane1.Point1 = [18.0, -3.0, planZ]
plane1.Point2 = [3.5, 3.0, planZ]

# create a new '3D Text'
a3DText1 = a3DText(registrationName='a3DText1')
a3DText1.Text = str(planZ_text)

# create a new 'OpenFOAMReader'
mORAANE_GEO_LES3900foam = OpenFOAMReader(registrationName='IsoQ.foam', FileName='PATH_to_DATA/IsoQ.foam')
mORAANE_GEO_LES3900foam.MeshRegions = ['internalMesh']
mORAANE_GEO_LES3900foam.CellArrays = ['Q', 'U', 'p']
mORAANE_GEO_LES3900foam.CellArrays = ['Q', 'U']

# create a new 'Contour'
contour1 = Contour(registrationName='Contour1', Input=mORAANE_GEO_LES3900foam)
contour1.ContourBy = ['POINTS', 'Q']
contour1.Isosurfaces = [IsoQ]
contour1.PointMergeMethod = 'Uniform Binning'

# time
tsteps=mORAANE_GEO_LES3900foam.TimestepValues

# ----------------------------------------------------------------
# setup the visualization in view 'renderView1'
# ----------------------------------------------------------------

########### Zplan text ############

# show data from a3DText1
a3DText1Display = Show(a3DText1, renderView1, 'GeometryRepresentation')

# trace defaults for the display properties.
a3DText1Display.Representation = 'Surface'
a3DText1Display.AmbientColor = [0.78, 0.78, 0.78]
a3DText1Display.ColorArrayName = [None, '']
a3DText1Display.DiffuseColor = [0.78, 0.78, 0.78]
a3DText1Display.SelectTCoordArray = 'None'
a3DText1Display.SelectNormalArray = 'None'
a3DText1Display.SelectTangentArray = 'None'
a3DText1Display.Position = [4.5, 1.3, 0.0]
a3DText1Display.Scale = [0.4, 0.6, 1.0]
a3DText1Display.OSPRayScaleFunction = 'PiecewiseFunction'
a3DText1Display.SelectOrientationVectors = 'None'
a3DText1Display.ScaleFactor = 0.57
a3DText1Display.SelectScaleArray = 'None'
a3DText1Display.GlyphType = 'Arrow'
a3DText1Display.GlyphTableIndexArray = 'None'
a3DText1Display.GaussianRadius = 0.03
a3DText1Display.SetScaleArray = [None, '']
a3DText1Display.ScaleTransferFunction = 'PiecewiseFunction'
a3DText1Display.OpacityArray = [None, '']
a3DText1Display.OpacityTransferFunction = 'PiecewiseFunction'
a3DText1Display.DataAxesGrid = 'GridAxesRepresentation'
a3DText1Display.PolarAxes = 'PolarAxesRepresentation'

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
a3DText1Display.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 0.03, 1.0, 0.5, 0.0]

# init the 'PolarAxesRepresentation' selected for 'PolarAxes'
a3DText1Display.PolarAxes.Translation = [3.7, -4.5, 0.0]
a3DText1Display.PolarAxes.Scale = [0.5, 0.7, 1.0]

# hide Text
Hide(a3DText1, renderView1)

########### IsoQ ############

# show data from contour1
contour1Display = Show(contour1, renderView1, 'GeometryRepresentation')

# get color transfer function/color map for 'U'
uLUT = GetColorTransferFunction('U')
uLUT.RGBPoints = [0.0, 0.0862745098039216, 0.00392156862745098, 0.298039215686275, 0.046367815071800565, 0.113725, 0.0235294, 0.45098, 0.08487658345407437, 0.105882, 0.0509804, 0.509804, 0.11159700624079659, 0.0392157, 0.0392157, 0.560784, 0.1375315631515215, 0.0313725, 0.0980392, 0.6, 0.1626801648223663, 0.0431373, 0.164706, 0.639216, 0.19883124621275605, 0.054902, 0.243137, 0.678431, 0.24677085192643508, 0.054902, 0.317647, 0.709804, 0.30571286624600613, 0.0509804, 0.396078, 0.741176, 0.3439269745267575, 0.0392157, 0.466667, 0.768627, 0.38214108280750886, 0.0313725, 0.537255, 0.788235, 0.422025287110225, 0.0313725, 0.615686, 0.811765, 0.46289174248437825, 0.0235294, 0.709804, 0.831373, 0.5037582872224098, 0.0509804, 0.8, 0.85098, 0.5375516816209155, 0.0705882, 0.854902, 0.870588, 0.5689874783914057, 0.262745, 0.901961, 0.862745, 0.5964937670541347, 0.423529, 0.941176, 0.87451, 0.6389320435441748, 0.572549, 0.964706, 0.835294, 0.6672242874467791, 0.658824, 0.980392, 0.843137, 0.6876575151338558, 0.764706, 0.980392, 0.866667, 0.7096625192548801, 0.827451, 0.980392, 0.886275, 0.7528867063028566, 0.913725, 0.988235, 0.937255, 0.7662469176962199, 1.0, 1.0, 0.972549019607843, 0.7796071290895835, 0.988235, 0.980392, 0.870588, 0.7992544909006535, 0.992156862745098, 0.972549019607843, 0.803921568627451, 0.8141864787279647, 0.992157, 0.964706, 0.713725, 0.8393350803988096, 0.988235, 0.956863, 0.643137, 0.8794156698969606, 0.980392, 0.917647, 0.509804, 0.9132091536593399, 0.968627, 0.87451, 0.407843, 0.9477885032977211, 0.94902, 0.823529, 0.321569, 0.9729371049685649, 0.929412, 0.776471, 0.278431, 1.0098741415988297, 0.909804, 0.717647, 0.235294, 1.0428816701213315, 0.890196, 0.658824, 0.196078, 1.0699950318610296, 0.878431, 0.619608, 0.168627, 1.1082091401417806, 0.870588, 0.54902, 0.156863, 1.1464232484225318, 0.85098, 0.47451, 0.145098, 1.1846373567032829, 0.831373, 0.411765, 0.133333, 1.2228514649840343, 0.811765, 0.345098, 0.113725, 1.2610655732647853, 0.788235, 0.266667, 0.0941176, 1.2992796815455363, 0.741176, 0.184314, 0.0745098, 1.3374937898262873, 0.690196, 0.12549, 0.0627451, 1.3757078981070383, 0.619608, 0.0627451, 0.0431373, 1.4114660895619668, 0.54902, 0.027451, 0.0705882, 1.4429018598025607, 0.470588, 0.0156863, 0.0901961, 1.4782670990542244, 0.4, 0.00392157, 0.101961, 1.5285643312300428, 0.188235294117647, 0.0, 0.0705882352941176]
uLUT.ColorSpace = 'Lab'
uLUT.NumberOfTableValues = 310
uLUT.ScalarRangeInitialized = 1.0

uLUT.RGBPoints = U_color_blueOrange
uLUT.RescaleTransferFunction(0,1.5)

# trace defaults for the display properties.
contour1Display.Representation = 'Surface'
contour1Display.ColorArrayName = ['POINTS', 'U']
contour1Display.LookupTable = uLUT
contour1Display.SelectTCoordArray = 'None'
contour1Display.SelectNormalArray = 'Normals'
contour1Display.SelectTangentArray = 'None'
contour1Display.OSPRayScaleArray = 'p'
contour1Display.OSPRayScaleFunction = 'PiecewiseFunction'
contour1Display.SelectOrientationVectors = 'U'
contour1Display.ScaleFactor = 0.6766788959503174
contour1Display.SelectScaleArray = 'p'
contour1Display.GlyphType = 'Arrow'
contour1Display.GlyphTableIndexArray = 'p'
contour1Display.GaussianRadius = 0.03383394479751587
contour1Display.SetScaleArray = ['POINTS', 'Q']
contour1Display.ScaleTransferFunction = 'PiecewiseFunction'
contour1Display.OpacityArray = ['POINTS', 'p']
contour1Display.OpacityTransferFunction = 'PiecewiseFunction'
contour1Display.DataAxesGrid = 'GridAxesRepresentation'
contour1Display.PolarAxes = 'PolarAxesRepresentation'

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
contour1Display.OSPRayScaleFunction.Points = [1.0486473911441863e-09, 0.0, 0.5, 0.0, 2.847604226310929, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
contour1Display.ScaleTransferFunction.Points = [-0.994351863861084, 0.0, 0.5, 0.0, 0.7060377597808838, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
contour1Display.OpacityTransferFunction.Points = [-0.994351863861084, 0.0, 0.5, 0.0, 0.7060377597808838, 1.0, 0.5, 0.0]

########### Cylinder ############

# show data from cylinder1
cylinder1Display = Show(cylinder1, renderView1, 'GeometryRepresentation')

# trace defaults for the display properties.
cylinder1Display.Representation = 'Surface'
cylinder1Display.Opacity = 1.0
#cylinder1Display.ColorArrayName = ['POINTS', '']

# color = pink
cylinder1Display.AmbientColor = [1.0, 0.67, 1.0]
cylinder1Display.DiffuseColor = [1.0, 0.67, 1.0]

cylinder1Display.SelectTCoordArray = 'TCoords'
cylinder1Display.SelectNormalArray = 'Normals'
cylinder1Display.SelectTangentArray = 'None'
cylinder1Display.Position = [0.0, 0.0, 1.5]
cylinder1Display.Orientation = [90.0, 0.0, 0.0]
cylinder1Display.OSPRayScaleArray = 'Normals'
cylinder1Display.OSPRayScaleFunction = 'PiecewiseFunction'
cylinder1Display.SelectOrientationVectors = 'None'
cylinder1Display.ScaleFactor = 0.2
cylinder1Display.SelectScaleArray = 'None'
cylinder1Display.GlyphType = 'Arrow'
cylinder1Display.GlyphTableIndexArray = 'None'
cylinder1Display.GaussianRadius = 0.01
cylinder1Display.SetScaleArray = ['POINTS', 'Normals']
cylinder1Display.ScaleTransferFunction = 'PiecewiseFunction'
cylinder1Display.OpacityArray = ['POINTS', 'Normals']
cylinder1Display.OpacityTransferFunction = 'PiecewiseFunction'
cylinder1Display.DataAxesGrid = 'GridAxesRepresentation'
cylinder1Display.PolarAxes = 'PolarAxesRepresentation'

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
cylinder1Display.OSPRayScaleFunction.Points = [-0.997704267501831, 0.0, 0.5, 0.0, -0.12169825285673141, 0.15000000596046448, 0.5, 0.0, 0.5842812657356262, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
cylinder1Display.ScaleTransferFunction.Points = [-1.0, 0.0, 0.5, 0.0, 0.10747664405299018, 0.15000000596046448, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
cylinder1Display.OpacityTransferFunction.Points = [-1.0, 0.0, 0.5, 0.0, 0.10747664405299018, 0.15000000596046448, 0.5, 0.0, 1.0, 1.0, 0.5, 0.0]

# init the 'PolarAxesRepresentation' selected for 'PolarAxes'
cylinder1Display.PolarAxes.Translation = [0.0, 0.0, 1.5]
cylinder1Display.PolarAxes.Orientation = [90.0, 0.0, 0.0]

########### Plane ############

# show data from plane1
plane1Display = Show(plane1, renderView1, 'GeometryRepresentation')

# trace defaults for the display properties.
plane1Display.Representation = 'Surface'
plane1Display.Luminosity = 100.0
plane1Display.Ambient = 0.32
#plane1Display.ColorArrayName = [None, '']

# color = green
plane1Display.Opacity = 0.3
plane1Display.AmbientColor = [0.14, 1.0, 0.01]
plane1Display.DiffuseColor = [0.14, 1.0, 0.01]

# color = green/yellow
plane1Display.Opacity = 0.3
plane1Display.AmbientColor = [0.90, 1.0, 0.01]
plane1Display.DiffuseColor = [0.10, 1.0, 0.10]

# color = gray
plane1Display.Opacity = 0.4
plane1Display.AmbientColor = [0.90, 0.90, 0.90]
plane1Display.DiffuseColor = [0.90, 0.90, 0.90]

plane1Display.SelectTCoordArray = 'TextureCoordinates'
plane1Display.SelectNormalArray = 'Normals'
plane1Display.SelectTangentArray = 'Normals'
plane1Display.OSPRayScaleArray = 'Normals'
plane1Display.OSPRayScaleFunction = 'PiecewiseFunction'
plane1Display.SelectOrientationVectors = 'None'
plane1Display.ScaleFactor = 0.1
plane1Display.SelectScaleArray = 'None'
plane1Display.GlyphType = 'Arrow'
plane1Display.GlyphTableIndexArray = 'None'
plane1Display.GaussianRadius = 0.005
plane1Display.SetScaleArray = ['POINTS', 'Normals']
plane1Display.ScaleTransferFunction = 'PiecewiseFunction'
plane1Display.OpacityArray = ['POINTS', 'Normals']
plane1Display.OpacityTransferFunction = 'PiecewiseFunction'
plane1Display.DataAxesGrid = 'GridAxesRepresentation'
plane1Display.PolarAxes = 'PolarAxesRepresentation'

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
plane1Display.OSPRayScaleFunction.Points = [0.0, 0.0, 0.5, 0.0, 0.030465299263596535, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
plane1Display.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.1757813367477812e-38, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
plane1Display.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.1757813367477812e-38, 1.0, 0.5, 0.0]


########### Legend ############

# setup the color legend parameters for each legend in this view

# get color legend/bar for uLUT in view renderView1
uLUTColorBar = GetScalarBar(uLUT, renderView1)
uLUTColorBar.AutoOrient = 0
uLUTColorBar.Orientation = 'Horizontal'
uLUTColorBar.Title = str(title1)
uLUTColorBar.ComponentTitle = str(title2)
uLUTColorBar.TitleBold = 1
uLUTColorBar.TitleFontSize = 20
uLUTColorBar.AutomaticLabelFormat = 0
#uLUTColorBar.LabelFormat = '%-#6.3f'
#uLUTColorBar.RangeLabelFormat = '%-#6.3f'
uLUTColorBar.LabelFormat = '%-#4.1f'
uLUTColorBar.RangeLabelFormat = '%-#4.1f'

# set color bar visibility
uLUTColorBar.Visibility = 1

# show color legend
contour1Display.SetScalarBarVisibility(renderView1, True)

# ----------------------------------------------------------------
# setup color maps and opacity mapes used in the visualization
# note: the Get..() functions create a new object, if needed
# ----------------------------------------------------------------

# get opacity transfer function/opacity map for 'U'
uPWF = GetOpacityTransferFunction('U')
uPWF.Points = [0.0, 0.0, 0.5, 0.0, 0.8464246478848755, 0.15000000596046448, 0.5, 0.0, 1.5285643312300428, 1.0, 0.5, 0.0]
uPWF.ScalarRangeInitialized = 1

# ----------------------------------------------------------------
# restore active source
SetActiveSource(contour1)
# ----------------------------------------------------------------

Show(contour1, renderView1)

Render()

#view = GetActiveView()
#view.ViewSize = [ 1200, 800 ]
#png_file='IsoQ%.0f_Z%.0f_t%.0f.png' % (IsoQ*10, planZ*10, time*100)
#SaveScreenshot(png_file,view)
 
view = GetActiveView()
view.ViewSize = [ 1200, 800 ]

print("--- START ---")

for n,t in enumerate (tsteps):
  
  if ( (t >= timeStart) and (t<=timeEnd) ):
    print ("rendering for time %f if t=[%f:%f]" % (t, timeStart, timeEnd))
    time_text = "t=%6.2f" % (t)
    title2 = ": "+time_text
    uLUTColorBar.ComponentTitle = str(title2)
    view.ViewTime = t
    png_file='IsoQ/IsoQ%.0f_Z%.0f_t%.0f.png' % (IsoQ*10, planZ*10, time*100)
    png_file='IsoQ/IsoQ%.0f_Z%.0f_t%.0f.png' % (IsoQ*10, planZ*10, t*100)
    SaveScreenshot(png_file,view)

print("--- END ---")

#if __name__ == '__main__':
    ## generate extracts
    #SaveExtracts(ExtractsOutputDirectory='extracts')
