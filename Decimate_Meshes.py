'''
Created on Apr 1, 2016

@author: roger
'''

from Surface_Utilities import *
import glob
import gc


OPENMESHPATH='/home/roger/Downloads/OpenMesh-5.1/build/Build/bin/commandlineDecimater'
if __name__ == '__main__':
    indir='/media/roger/48BCFC2BBCFC1562/dataset/labels_registered_mha'  
    nvertices=2000
    validlabel=2
    ext='mha'
    #This needs files numbered with 2 Digits!!!
    li=len(ext)+1
    filelist=[filename for filename in glob.iglob(os.path.join(indir,'*.'+ext))]    
    assert len(filelist)> 0, 'No Files Found'
    print len(filelist)," Files Found " 
    
    for i in xrange(len(filelist)):
        _,nfile=os.path.split(filelist[i])       
        idfile= int(nfile[-(li+2):-li])#number in the name of the file
        imgitk = sitk.ReadImage(filelist[i])
        imgclean=clean_itkbin(imgitk,validlabel)
        meshvtk=generate_mesh(imgclean)
        WriteSTLMesh(meshvtk, 'meshdecimated.stl')
        
        filetmp=os.path.join(os.getcwd(),'meshdecimated.stl')        
        command=OPENMESHPATH+' -i {0} -o {0} -n -{1:d} -M Q'.format(filetmp,nvertices)
        os.system(command)   
   

        meshvtktmp=LoadSTLMesh('meshdecimated.stl')         
        WriteVTKMesh(meshvtktmp,"mesh{0:02d}.vtk".format(idfile))
        vertices,triangles=compute_info_mesh(meshvtktmp)
        assert vertices==nvertices,' Reduction not acomplished'