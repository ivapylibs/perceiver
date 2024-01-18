
import operator
import improcessor.basic as improcessor
import detector.inImage as detector                                             
import trackpointer.centroid as tracker

import perceiver.perceiver as perceiver

#=========================== buildTesterGS ===========================
#
def buildTesterGS(tauGS = 1, theParams = None, theFilt = None):
  """!
  @brief  Builds a simple grayscale thresholding detector and centroid tracker with
          filtering based on argument.

  The purpose of this builder is to shorten testing code that basically involves
  this same construction over and over again.  It is much easier to have it
  all packaged up into a static member function for the test script to have
  a single line invocation and instantiation of the necessary perceiver.  Permits
  the non-trivial code to focus on the demonstration at hand (in the test script).

  @param[in]  tauGS   Threshold to apply to grayscale image input. Default is 1.
  @param[in   theFilt Temporal filter to use. Default = None. 
  """

  # Create the grayscale detector instance with given threshold.
  improc = improcessor.basic(operator.ge,(tauGS,))
  binDet = detector.inImage(improc)

  # Assuming single object will be tracker (e.g., a single centroid).
  trackptr = tracker.centroid()

  # Package up into a single point perceiver.
  ptPer = perceiver.Perceiver(theDetector=binDet , theTracker=trackptr, \
                              trackFilter=theFilt, theParams=theParams)

  return ptPer


