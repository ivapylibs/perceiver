import matplotlib.pyplot as plt

import trackpointer.centroid as tracker
import perceiver.simple as perceiver

from detector.fgmodel.targetMagenta import targetMagenta
from trackpointer.centroid import Params
import cv2


#==[1] Build the perceiver.

#--[1.1] Create the detector instance.

magentaDetector = targetMagenta.build_model(25)

#--[1.2] and the track pointer instance.

trackptr = tracker.centroid(params=Params(plotStyle="cx"))

#--[1.3] Package up into a perceiver.

ptsPer=perceiver.simple(theDetector=magentaDetector , theTracker=trackptr, trackFilter=None, theParams=None)

#==[2] Apply perceiver to simple image.

#--[2.1] Load test image

img_test = cv2.imread('data/img.png')[:, :, ::-1]


#--[2.2] Apply to test image

ptsPer.process(img_test)


#--[2.3] Visualize the output.

tstate = ptsPer.tracker.getState()
ptsPer.tracker.setState(tstate)

plt.imshow(img_test)
ptsPer.tracker.displayState()
plt.show()
