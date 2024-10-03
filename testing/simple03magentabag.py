#!/usr/bin/python
#============================= simple03magentabag ==============================
## @file      simple03magentabag.py
# @brief      Test simple perceiver on streaming data with magenta target detector
#             applied to image of Mary the manipulator with a small magenta dot at
#             wrist.
# 
# The magenta detector isolates the dot at Mary's wrist as a binary image region.  
# That region is processed to generate a track point.  Builds in simple03magentadot
# by obtaining from a streaming source rather than a single image source.
# 
# The code below
# 
# > ./simple03magentabag
# 
# runs the script.  It looks like the red wiring is being detected as magenta and
# influencing the centroid.  There is visible jitter.
# 
# @attention  The magenta_demo.bag file is not in the repo since due to size.
#             Get copy from someone who has it.  Eventually a smaller ROS bag will
#             be made for this test.
# 
# @ingroup    TestPerceiver
# @quitf
#
# @author     Caleb Chang,    
# @author     Patricio A. Vela,       pvela@gatech.edu
# @date       2023/02/XX [created]
#
#============================= simple03magentabag ==============================
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#============================= simple03magentabag ==============================

#==[0] Setup environment/dependencies.
#
import matplotlib.pyplot as plt

import trackpointer.centroid as tracker
import perceiver.simple as perceiver

from detector.fgmodel.targetMagenta import targetMagenta
import cv2
import pyrealsense2 as rs                 # Intel RealSense cross-platform open-source API
import numpy as np


print("Code will fail due to missing ROS bag.")
print("A new one needs to be recorded.")
print("Terminating")
quit()

#==[1] Instantiate perceiver and open stream.
#
#--[1.1] Perceiver 
magentaDetector = targetMagenta.build_model(25)
trackptr    = tracker.centroid(params=tracker.CfgCentroid(init_dict=dict(plotStyle="cx")))
ptsPer      = perceiver.Perceiver(theDetector=magentaDetector , theTracker=trackptr, \
                                              trackFilter=None, theParams=None)

#--[1.2] Video pipeline
pipe    = rs.pipeline()
cfg     = rs.config()
cfg.enable_device_from_file("data/magenta_demo.bag")
profile = pipe.start(cfg)

for i in range(40):                 # skip first few frames
    pipe.wait_for_frames()


#==[2] Processing loop.
#
for i in range(80):
    # get frame from video
    frameset = pipe.wait_for_frames()
    color_frame = frameset.get_color_frame()
    frame = np.asanyarray(color_frame.get_data())

    # process frame
    ptsPer.process(frame)

    # draw image then draw marker
    plt.cla()
    plt.imshow(frame)
    tstate = ptsPer.tracker.getState()
    ptsPer.tracker.setState(tstate)
    ptsPer.tracker.displayState()
    plt.pause(0.001)

plt.ioff()
plt.draw()

#==[3] Close out. User needs to close window.
#
pipe.stop()

