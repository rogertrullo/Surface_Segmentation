'''
Created on Mar 31, 2016

@author: roger 

This Module needs ANTs toolbox for registration and the script reg3.sh
'''
import os
import glob


ANTSPATH='/opt/antsbin/bin/'

def register2one(indir,indirlabels,prefix,prefixlabels,ext,idx_ref):
    

#===============================================================================
# This function register all the images in indir directory to a ref 
# (whose idx is idx_ref) image also in indir.
# The images must have the same prefix eg. patient00.mha.-> patient19.mha 
# for a 20 files dataset. The function apply the transformation found to 
# the label images which must be in indirlabels directory. 
# These labels must have also a labelprefix.
# TODO-- So far only reads labelxx.ext, that is 2 digits :/
#===============================================================================
    
    
    filelist=[filename for filename in glob.iglob(os.path.join(indir,'*.'+ext))]    
    assert len(filelist)> 0, 'No Files Found'
    print len(filelist)," Files Found: " 
    
    li=len(prefix)
    lf=len(ext)+1#for the dot
    
    indices_list=[]
    index_ref=None
    for i in xrange(len(filelist)):
        _,nfile=os.path.split(filelist[i])       
        intid=int(nfile[li:-lf])
        indices_list.append(intid)      
        if intid==idx_ref:
            index_ref=i
            
    assert index_ref!=None, 'the reference id was not found'
    
    refname=filelist[index_ref]
    
    for i in xrange(len(filelist)):
          
        if i==index_ref:
            continue        
        movname=filelist[i]
                
        command1=ANTSPATH+'ImageMath 3 fixPad.mha PadImage '+ refname+' 20'
        command2=ANTSPATH+'ImageMath 3 movPad.mha PadImage '+ movname+' 20'
        command3='./reg3.sh fixPad.mha movPad.mha'+' %02d'%indices_list[i]
        outname="Warped{0:02d}.mha".format(indices_list[i])
        command4=ANTSPATH+'ImageMath 3 {0} PadImage '.format(outname)+ outname+' -20'
        print "registering ", os.path.split(movname)[1],"to ",os.path.split(refname)[1]
        os.system(command1)
        os.system(command2)
        os.system(command3) 
        os.system(command4)
        
        ###### Apply Transform to Labels
        
        label_name=prefixlabels+'{0:02d}'.format(indices_list[i])+'.'+ext        
        moving_label_name = os.path.join(indirlabels,label_name)
        assert os.path.exists(moving_label_name),'{0} does not exist'.format(os.path.split(moving_label_name)[1])
        command=ANTSPATH+'antsApplyTransforms -d 3 -i {0} -r {1} -n NearestNeighbor -t {2:02d}0GenericAffine.mat -o label_warped{2:02d}.mha --verbose 1'.format(moving_label_name,'fixPad.mha',indices_list[i])
        os.system(command)
	tmpname='label_warped{0:02d}.mha'.format(indices_list[i])
	command=ANTSPATH+'ImageMath 3 {0} PadImage '.format(tmpname)+ tmpname+' -20'
        os.system(command)

if __name__ == '__main__':
    register2one('/home/scr/etu/sin811/trullro1/prostate/3T','/home/scr/etu/sin811/trullro1/prostate/3T/labels','patient','label','mha',1)
