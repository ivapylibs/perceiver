#!/usr/bin/python3
#============================== activity01regions ==============================
## @file
# @brief    Code to test out the basic activity monitor for a scenario with 
#           left/right tracking semantics of a square in an image.
# 
# The image is not "grayscale"  and gets thresholded to generate a single region.
# That region is processed to generate a track point, which is used to establish
# left/right/none semantics. The implementation builds out a Monitor.
# 
# The code below
# 
# > ./activity01regions
# 
# runs the script.  
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




pathPts = np.array([ [10,10] , [40, 40], [50, 50] ])
thePath = pathgen.PiecewiseLines(waypoints = pathPts)

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

  kp = display.wait()
  if (kp == 'q'):
    quit()
