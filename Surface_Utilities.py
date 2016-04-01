'''
Created on Apr 1, 2016

@author: roger
'''
import openmesh as om
import SimpleITK as sitk
import vtk
import os
#This line is for using a 3D viewer with itk images we need to set the env var
os.environ["SITK_SHOW_3D_COMMAND"] = "/home/roger/Downloads/Slicer-4.5.0-1-linux-amd64/Slicer"


def DisplayVTKMesh(meshi,windowname):
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(meshi)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetInterpolationToPhong()
    actor.GetProperty().SetAmbient(0.2)
    actor.GetProperty().SetDiffuse(0.7)
    actor.GetProperty().SetSpecular(0.6)
    actor.GetProperty().SetSpecularPower(100)
    actor.GetProperty().SetColor(0.8,0.8,1)
    ren1 = vtk.vtkRenderer()
    ren1.AddActor(actor)
    ren1.SetBackground(0, 0, 0)
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren1)
    renWin.SetSize(300, 300)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    style = vtk.vtkInteractorStyleTrackballCamera()
    iren.SetInteractorStyle(style)
    iren.Initialize()
    renWin.SetWindowName(windowname)
    iren.Start()
    
    
def compute_info_mesh(mesh):
    vertices= mesh.GetNumberOfPoints()
    triangles= mesh.GetNumberOfCells()
    extractEdges = vtk.vtkExtractEdges()
    extractEdges.SetInputData(mesh)
    extractEdges.Update()
    lines=extractEdges.GetOutput()
    edges=lines.GetNumberOfCells()
    print "triangles: ",triangles
    print "vertices: ",vertices
    print "edges: ",edges

    return vertices,triangles

def clean_itkbin(imgitk,validlabel=1,variance=0.1,showimage=False):
    
    imgbin=imgitk==validlabel#only consider 1 valid label
    connectedfilter=sitk.ConnectedComponentImageFilter()
    morfilter=sitk.BinaryMorphologicalOpeningImageFilter()    
    imgbin=morfilter.Execute(imgbin)
    
    gfilter=sitk.DiscreteGaussianImageFilter()
    gfilter.SetVariance(variance)
    imgbin=gfilter.Execute(imgbin)

    imgconn=connectedfilter.Execute(imgbin)
    imgconn=imgconn==1
    holesfilter=sitk.BinaryFillholeImageFilter()
    imgfin=holesfilter.Execute(imgconn,True,1.0)
    if showimage:
        sitk.Show(imgfin)
    return imgfin

def generate_mesh(imgbinitk):
    sitk.WriteImage( imgbinitk,'label_cleaned_tmp.mha')
    
    reader=vtk.vtkMetaImageReader()
    reader.SetFileName('label_cleaned_tmp.mha')
    reader.Update()
    
    imgbin=reader.GetOutput()
    dmc = vtk.vtkDiscreteMarchingCubes()
    dmc.SetInputData(imgbin)
    dmc.ComputeNormalsOn()
    dmc.GenerateValues(1, 1, 1)
    dmc.Update()
    meshout=dmc.GetOutput()
    #DisplayVTKMesh(meshout,"mesh from marchin cubes")
    return meshout

def Decimate_mesh(meshvtk,name_vtkmesh,nvertices=2000):
    print 'test'
    stlWriter = vtk.vtkSTLWriter()
    stlWriter.SetFileName('meshdecimated.stl')
    stlWriter.SetInputData(meshvtk)
    stlWriter.Write()
    
    mesh_om = om.PolyMesh()
    Result=om.read_mesh(mesh_om, "meshdecimated.stl")
    print Result
    deci_om=om.PolyMeshDecimater(mesh_om)
    mh=om.PolyMeshModQuadricHandle()   
    
    deci_om.add(mh)
    deci_om.initialize()
    deci_om.decimate_to(nvertices)
    mesh_om.garbage_collection()
    
    
    
    assert mesh_om.n_vertices()==nvertices, 'vertices goal not acomplished; nvertices={0:d}'.format(mesh_om.n_vertices())
    print "Decimation to {0} vertices Sucessful".format(nvertices)
    om.write_mesh(mesh_om,'meshdecimated.stl')
    stlReader = vtk.vtkSTLReader()
    stlReader.SetFileName('meshdecimated.stl')
    stlReader.Update()   
      
    vtkwrite=vtk.vtkPolyDataWriter()
    vtkwrite.SetInputData(stlReader.GetOutput())
    vtkwrite.SetFileName(name_vtkmesh)
    vtkwrite.Write()
    
    print "enters"
      
    
def LoadVTKMesh(filename):
    reader = vtk.vtkPolyDataReader()
    reader.SetFileName(filename)
    reader.Update()
    return reader.GetOutput()    

def LoadSTLMesh(filename):
    stlReader = vtk.vtkSTLReader()
    stlReader.SetFileName(filename)
    stlReader.Update()   
    return stlReader.GetOutput() 

def WriteSTLMesh(meshvtk,filename):
    stlWriter = vtk.vtkSTLWriter()
    stlWriter.SetFileName(filename)
    stlWriter.SetInputData(meshvtk)
    stlWriter.Write()
    
def WriteVTKMesh(meshvtk,filename):
    vtkwrite=vtk.vtkPolyDataWriter()
    vtkwrite.SetInputData(meshvtk)
    vtkwrite.SetFileName(filename)
    vtkwrite.Write()
    
    
def Compute_Normals(vtkmesh):
    normfilter=vtk.vtkPolyDataNormals()
    normfilter.SetInputData(vtkmesh)
    normfilter.ComputePointNormalsOn()
    normfilter.ComputeCellNormalsOff
    normfilter.SplittingOff()
    normfilter.Update()    
    return normfilter.GetOutput()


def MakeGlyphs(src):
    '''
    Glyph the normals on the surface.
 
    You may need to adjust the parameters for maskPts, arrow and glyph for a
    nice appearance.
 
    :param: src - the surface to glyph.
    :param: reverseNormals - if True the normals on the surface are reversed.
    :return: The glyph object.
 
    '''
    # Sometimes the contouring algorithm can create a volume whose gradient
    # vector and ordering of polygon (using the right hand rule) are
    # inconsistent. vtkReverseSense cures this problem.
    
 
    # Choose a random subset of points.
    maskPts = vtk.vtkMaskPoints()
    maskPts.SetOnRatio(2)
    maskPts.RandomModeOn()
    maskPts.SetInputData(src)
 
    # Source for the glyph filter
    arrow = vtk.vtkArrowSource()
    arrow.SetTipResolution(16)
    arrow.SetTipLength(0.3)
    arrow.SetTipRadius(0.1)
 
    glyph = vtk.vtkGlyph3D()
    glyph.SetSourceConnection(arrow.GetOutputPort())
    glyph.SetInputConnection(maskPts.GetOutputPort())
    glyph.SetVectorModeToUseNormal()
    glyph.SetScaleFactor(1)
    glyph.SetColorModeToColorByVector()
    glyph.SetScaleModeToScaleByVector()
    glyph.OrientOn()
    glyph.Update()
    return glyph

def Display_Normal_Mesh(meshi,glyph,windowname):
    print ('test')
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(meshi)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetInterpolationToPhong()
    actor.GetProperty().SetAmbient(0.2)
    actor.GetProperty().SetDiffuse(0.7)
    actor.GetProperty().SetSpecular(0.6)
    actor.GetProperty().SetSpecularPower(100)
    actor.GetProperty().SetColor(0.8,0.8,1)
    
    glyphMapper = vtk.vtkPolyDataMapper()
    glyphMapper.SetInputConnection(glyph.GetOutputPort())
    glyphMapper.SetScalarModeToUsePointFieldData()
    glyphMapper.SetColorModeToMapScalars()
    glyphMapper.ScalarVisibilityOn()
    glyphMapper.SelectColorArray('Elevation')
    # Colour by scalars.
    
    scalarRange = glyph.GetOutput().GetScalarRange()
    glyphMapper.SetScalarRange(scalarRange)
 
    glyphActor = vtk.vtkActor()
    glyphActor.SetMapper(glyphMapper)
    
    
    ren1 = vtk.vtkRenderer()
    ren1.AddActor(actor)
    ren1.AddViewProp(glyphActor)
    ren1.SetBackground(0, 0, 0)
    
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren1)
    renWin.SetSize(300, 300)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    style = vtk.vtkInteractorStyleTrackballCamera()
    iren.SetInteractorStyle(style)
    iren.Initialize()
    renWin.SetWindowName(windowname)
    iren.Start()

    
    
if __name__ == '__main__':
    inpath='/media/roger/48BCFC2BBCFC1562/dataset/labels_registered_mha/label_warped10.mha'
    nvertices=2000
    imgitk = sitk.ReadImage(inpath)
    imgclean=clean_itkbin(imgitk,validlabel=2)
    meshvtk=generate_mesh(imgclean)
    _,_=compute_info_mesh(meshvtk)    
    WriteSTLMesh(meshvtk, 'meshdecimated.stl')
 
#===============================================================================
# 
# This part should be in a function but it crashes duw to openmesh :/  
#===============================================================================
    mesh_om = om.PolyMesh()
    Result=om.read_mesh(mesh_om, "meshdecimated.stl")
    assert Result, "Open mesh could not read file"
    deci_om=om.PolyMeshDecimater(mesh_om)
    mh=om.PolyMeshModQuadricHandle()   
    
    deci_om.add(mh)
    deci_om.initialize()
    deci_om.decimate_to(nvertices)
    mesh_om.garbage_collection()
    
    assert mesh_om.n_vertices()==nvertices, 'vertices goal not acomplished; nvertices={0:d}'.format(mesh_om.n_vertices())
    print "Decimation to {0} vertices Sucessful".format(nvertices)
    om.write_mesh(mesh_om,'meshdecimated.stl')
################################################################################    
    
    meshvtktmp=LoadSTLMesh('meshdecimated.stl') 
    WriteVTKMesh(meshvtktmp,"mymesh.vtk")
    
    meshvtk_dec=LoadVTKMesh('mymesh.vtk')
    compute_info_mesh(meshvtk_dec)
    
    
    
    norms=Compute_Normals(meshvtk_dec)
    glyph = MakeGlyphs(norms)
    Display_Normal_Mesh(meshvtk_dec,glyph,"arrows")