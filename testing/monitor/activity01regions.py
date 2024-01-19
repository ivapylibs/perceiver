#!/usr/bin/python3
#============================== activity01regions ==============================
## @file
# @brief    Code to test out the basic activity monitor for a scenario with 
#           top-left/lower-right semantics of a tracked square in an image.
# 
# The image is "grayscale"  and gets thresholded to generate a single region.
# That region is processed to generate a track point, which is used to establish
# activity state semantics. The implementation builds out a Monitor.
# 
# The code below
# 
# > ./activity01regions
# 
# runs the script.  
#
# OUTCOMES:
#
# The square starts off in activity region 1, leaves the region into undefined
# space, enters activity region 2, then leaves it and stops at the path terminal 
# point.
# 
# @ingroup  TestMonitor
# @quitf
#
# @author   Patricio A. Vela,   pvela@gatech.edu
# @date     2024/01/12 [created]
#
#============================== activity01regions ==============================
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#============================== activity01regions ==============================


import numpy as np

import ivapy.display_cv as display
import ivapy.test.paths as pathgen
import ivapy.test.vision as visgen

import perceiver.perceiver as perceiver
import perceiver.builders as perbuild
import detector.activity.byRegion as regact
import perceiver.monitor as monitor




pathPts = np.transpose(np.array([ [10,10] , [35, 35], [50, 50] ]))
thePath = pathgen.StepLines(None, pathPts)

thePerceiver = perbuild.buildTesterGS(10)

theActivity  = regact.imageRegions()
theActivity.initRegions([50, 50])
theActivity.addRegionByPolygon([[ 5,  5, 15, 15],[ 5, 15, 15, 5]])
theActivity.addRegionByPolygon([[35, 35, 45, 45],[35, 45, 45, 35]])

theMonitor = monitor.Monitor(None, thePerceiver, theActivity)


while True:

  cpt = thePath.next()
  # @todo   IAMHERE - Code works but path doesn't update.  Need to add that.

  theImage = visgen.squareInImage([100, 100], cpt, 5, [50])

  theMonitor.process(theImage)

  theMonitor.displayState()

  display.gray(theImage)
  kp = display.wait(100)
  if (kp == ord('q')):
    quit()
