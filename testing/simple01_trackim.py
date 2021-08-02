#!/usr/bin/python3
#=========================== simple01_trackim ============================
#
# @brief    Code to test out the simple perceiver for a fairly
#           contrived scenario.
#
# Here the image is not binary, but grayscale.  It gets thresholded to
# generate a single region.  That region is processed to generate a
# track point. The entire implementation is constructed and
# encapsulated within a simple perceiver.
#
# The code below
#
# > simple01_trackim
# 
# runs the script.  
#
#=========================== simple01_trackim ============================

# 
# @file     simple01_trackim.m
#
# @author   Patricio A. Vela,   pvela@gatech.edu
#           Yunzhi Lin,         yunzhi.lin@gatech.edu
# @date     2021/07/03 [created]
#           2021/07/14 [modified]
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
# @quit
#=========================== simple01_trackim ============================


#==[0] Create environment. Import necessary libraries/packages.

import numpy as np
import matplotlib.pyplot as plt
import operator

import improcessor.basic as improcessor
import detector.inImage as detector
import trackpointer.centroid as tracker
import perceiver.simple as perceiver


#==[1] Build the perceiver.

#--[1.1] Create the detector instance.

improc = improcessor.basic(operator.ge,(7,))

binDet = detector.inImage(improc)

#--[1.2] and the track pointer instance.

trackptr = tracker.centroid()

#--[1.3] Package up into a perceiver.

ptsPer=perceiver.simple(theDetector=binDet , theTracker=trackptr, trackFilter=None, theParams=None)

#==[2] Apply perceiver to simple image.

#--[2.1] Create a simple image.

image = np.zeros((10,25))
image[4:9,7:20] = 10

#--[2.2] Apply to simple image

ptsPer.process(image)


#--[2.3] Visualize the output.

tstate = ptsPer.tracker.getState()
ptsPer.tracker.setState(tstate.tpt)

print("\nShould see a box with a red X in the center.\n")
plt.imshow(image,cmap='Greys')
ptsPer.tracker.displayState()
plt.show()

#
#=========================== simple01_trackim ============================
