import matplotlib.pyplot as plt

import trackpointer.centroid as tracker
import perceiver.simple as perceiver

from detector.fgmodel.targetMagenta import targetMagenta
from trackpointer.centroid import Params
import cv2
import pyrealsense2 as rs                 # Intel RealSense cross-platform open-source API
import numpy as np


# perceiver 
magentaDetector = targetMagenta.build_model(25)
trackptr = tracker.centroid(params=Params(plotStyle="cx"))
ptsPer=perceiver.simple(theDetector=magentaDetector , theTracker=trackptr, trackFilter=None, theParams=None)

# video pipeline
pipe = rs.pipeline()
cfg = rs.config()
cfg.enable_device_from_file("data/magenta_demo.bag")
profile = pipe.start(cfg)


# skip first few frames
for i in range(40):
    pipe.wait_for_frames()

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


pipe.stop()




# img_test = cv2.imread('data/img.png')[:, :, ::-1]
# ptsPer.process(img_test)

# tstate = ptsPer.tracker.getState()
# ptsPer.tracker.setState(tstate)
# plt.imshow(img_test)
# ptsPer.tracker.displayState()
# plt.show()
