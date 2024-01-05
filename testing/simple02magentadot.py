#!/usr/bin/python
#============================= simple02magentadot ==============================
## @file    simple02magentadot.py
# @brief    Test simple perceiver with magenta target detector applied to image
#           of Mary the manipulator with a small magenta dot at wrist.
# 
# The magenta detector isolates the dot as a binary image region.  That region is
# processed to generate a track point.  Implementation is constructed and
# encapsulated within a simple perceiver.
# 
# The code below
# 
# > ./simple02magentadot
# 
# runs the script.  
# 
# @author   Caleb Chang
# @date     2023/02/XX [created]
# @ingroup  TestPerceiver
# @quitf
#
#============================= simple02magentadot ==============================
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#============================= simple02magentadot ==============================

#==[0] Prep environment/dependencies.
#
import matplotlib.pyplot as plt

import trackpointer.centroid as tracker
import perceiver.simple as perceiver

from detector.fgmodel.targetMagenta import targetMagenta
import cv2


#==[1] Build the perceiver.
#
#--[1.1] Create the detector instance.

magentaDetector = targetMagenta.build_model(25)

#--[1.2] and the track pointer instance.

trackptr = tracker.centroid(params=tracker.CfgCentroid(init_dict=dict(plotStyle="cx")))

#--[1.3] Package up into a perceiver.

ptsPer=perceiver.Perceiver(theDetector=magentaDetector , theTracker=trackptr, trackFilter=None, theParams=None)

#==[2] Apply perceiver to simple image.
#
#--[2.1] Load test image

img_test = cv2.imread('data/magenta.png')[:, :, ::-1]

#--[2.2] Apply to test image

ptsPer.process(img_test)

#--[2.3] Visualize the output.

tstate = ptsPer.tracker.getState()
ptsPer.tracker.setState(tstate)

plt.imshow(img_test)
ptsPer.tracker.displayState()
plt.show()

#
#============================= simple02magentadot ==============================
