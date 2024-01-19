#!/usr/bin/python3
#============================== activity02regions ==============================
## @file
# @brief    Code to test out the basic activity monitor for a scenario with 
#           cyclic tracking of a square in an image through top-left and lower-right
#           states.
# 
# The image is "grayscale"  and gets thresholded to generate a single region.
# That region is processed to generate a track point, which is used to establish
# activity state semantics. The implementation builds out a Monitor.  The path is
# adjusted to be cyclic/periodic so that is cycles between states 1 -> 0 -> 2 -> 0. 
# 
# The code below
# 
# > ./activity02regions
# 
# runs the script.  
#
# ### Outcome ###
# The square starts off in activity region 1, leaves the region into undefined space, 
# enters activity region 2, then leaves it and cycles back to activity region 1.
# The process repeats.
# 
# @todo     Need to improve the visualization/display routines.
#
# @ingroup  TestMonitor
# @quitf
#
# @author   Patricio A. Vela,   pvela@gatech.edu
# @date     2024/01/12 [created]
#
#============================== activity02regions ==============================
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#============================== activity02regions ==============================


#==[0] Environment dependencies.
#
import numpy as np

import ivapy.display_cv as display
import ivapy.test.paths as pathgen
import ivapy.test.vision as visgen

import perceiver.perceiver as perceiver
import perceiver.builders as perbuild
import detector.activity.byRegion as regact
import perceiver.monitor as monitor


#==[1] Setup necessary class instances.
#
imsize   = [100,100]

pathPts  = np.transpose(np.array([ [10,10] , [40, 20], [50, 50], [20, 40] , [10, 10] ]))
pathSpec = pathgen.CfgStepLines()
pathSpec.isPeriodic = True
thePath  = pathgen.StepLines(pathSpec, pathPts)

thePerceiver = perbuild.buildTesterGS(10)

theActivity  = regact.imageRegions()
theActivity.initRegions(imsize)
theActivity.addRegionByPolygon([[ 5,  5, 15, 15], [ 5, 15, 15, 5]])
theActivity.addRegionByPolygon([[45, 45, 55, 55], [45, 55, 55, 45]])

theMonitor = monitor.Monitor(None, thePerceiver, theActivity)

#==[2] Process in a loop until terminated by user.
#
while True:

  cpt = thePath.next()
  theImage = visgen.squareInImage(imsize, cpt, 5, [50])

  theMonitor.process(theImage)


  theMonitor.displayState()
  display.gray(theImage)
  display.gray(theActivity.imRegions.astype('float'),window_name="regions")

  kp = display.wait(100)
  if (kp == ord('q')):
    quit()

#
#============================== activity02regions ==============================
