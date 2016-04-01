#!/bin/bash
#
dim=3 # image dimensionality
AP="/opt/antsbin/bin/" # /home/yourself/code/ANTS/bin/bin/  # path to ANTs binaries
ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=8  # controls multi-threading
export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS
f=$1 ; m=$2; OUTPUTNAME=$3    # fixed and moving image file names
if [[ ! -s $f ]] ; then echo no fixed $f ; exit; fi
if [[ ! -s $m ]] ; then echo no moving $m ;exit; fi
nm1=` basename $f | cut -d '.' -f 1 `
nm2=` basename $m | cut -d '.' -f 1 `
nm=${D}${nm1}_fixed_${nm2}_moving   # construct output prefix
reg=${AP}antsRegistration           # path to antsRegistration

echo affine $m $f outname is $nm

RIGIDCONVERGENCE="[1000x500x250x100,1.e-6,10]"
RIGIDSHRINKFACTORS="8x4x2x1"
RIGIDSMOOTHINGSIGMAS="4x3x2x1vox"

AFFINECONVERGENCE="[1000x500x250x100,1.e-6,10]"
AFFINESHRINKFACTORS="8x4x2x1"
AFFINESMOOTHINGSIGMAS="3x2x1x0vox"

AFFINECONVERGENCE="[1000x500x250x0,1.e-6,10]"
AFFINESHRINKFACTORS="12x8x4x2"
AFFINESMOOTHINGSIGMAS="4x3x2x1vox"

SYNCONVERGENCE="[100x70x50x10,1.e-6,10]"
SYNSHRINKFACTORS="6x4x2x1"
SYNSMOOTHINGSIGMAS="3x2x1x0vox"

RIGIDSTAGE="--transform Rigid[0.25] \
            --metric Mattes[$f, $m, 1,32,Regular,0.25] \
            --convergence $RIGIDCONVERGENCE \
            --shrink-factors $RIGIDSHRINKFACTORS \
            --smoothing-sigmas $RIGIDSMOOTHINGSIGMAS"

AFFINESTAGE="--transform affine[0.25] \
             --metric Mattes[$f, $m ,1,32,Regular,0.25] \
             --convergence $AFFINECONVERGENCE \
             --shrink-factors $AFFINESHRINKFACTORS \
             --smoothing-sigmas $AFFINESMOOTHINGSIGMAS"

SYNSTAGE="--transform SyN[0.25,3,0] \
	  --metric Mattes[$f, $m ,1,32] \
          --convergence $SYNCONVERGENCE \
          --shrink-factors $SYNSHRINKFACTORS \
          --smoothing-sigmas $SYNSMOOTHINGSIGMAS"

STAGES="$RIGIDSTAGE $AFFINESTAGE"

COMMAND="${reg} --use-histogram-matching \
		-d 3 -r [ $f, $m ,1] --verbose 1\
		$STAGES -l 1 -o [$OUTPUTNAME,Warped${OUTPUTNAME}.mha] --float"


#${COMMAND}
$COMMAND

