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


import ivapy.display_cv as display
import ivapy.test.path as pathgen
import ivapy.test.vision as visgen



pathPts = numpy.array([ [10,10] , [40, 40], [50, 50] ])
thePath = pathgen.PiecewiseLinear(waypoints = pathPts)


while True:

  cpt = thePath.next()

  theImage = visgen.squareInImage([100, 100], cpt, 5, 50)

  theMonitor.process(theImage)

  theMonitor.displayState()

  kp = display.wait()
  if (kp == 'q'):
    quit()