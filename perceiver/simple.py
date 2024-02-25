#============================ perceiver.simple ===========================
#
# @quitf
# @file     simple.m
#
# @author   Yiye Chen,       yychen2019@gatech.edu
#           Yunzhi Lin,      yunzhi.lin@gatech.edu
# @date     2021/04/05  [created]
#           2021/07/11  [modified]
#!NOTE:
#!  set indent to 2 spaces.
#!  do not indent function code.
#!  set tab to 4 spaces with conversion to spaces.
#!  90 columns 
#
#============================ perceiver.simple ===========================

# Import any necessary libraries/packages.

import os
import matplotlib.pyplot as plt
import time
import numpy as np
from dataclasses import dataclass

from Lie.group.SE2.Homog import Homog
from detector.Configuration import AlgConfig


@dataclass
class State:
  tMeas: any
  g: Homog = None
  tPts: np.ndarray = np.array([])
  gOB: Homog = None
  haveObs: bool = False
  haveState:  bool = False


@dataclass
class Info:
  name: str
  version: str
  data: str
  time: str
  params: dict

#
#-------------------------------------------------------------------------------
#============================= Configuration Nodes =============================
#-------------------------------------------------------------------------------
#


#============================== CfgPerceiver =============================
#
class CfgPerceiver(AlgConfig):
  """!
  @brief    Configuration instance for a perceiver.  

  Instantiating a perceiver usually requires the detector, tracker, and filter
  instances to be complete.  Thus any other settings should be specific to how
  the perceiver will operate or what to do with the processed information.
  """

  #------------------------------ __init__ -----------------------------
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    '''!
    @brief    Instantiate a puzzle scene (black mat) detector.
    '''

    if init_dict is None:
      init_dict = CfgPerceiver.get_default_settings()

    super(CfgPerceiver,self).__init__(init_dict, key_list, new_allowed)


  #------------------------ get_default_settings -----------------------
  #
  @staticmethod
  def get_default_settings():

    default_settings = dict(display = None, version = None)
    return default_settings


#=========================== BuildCfgPerceiver ===========================
#
class BuildCfgPerceiver(AlgConfig):
  """!
  @brief    Build configuration instance for a perceiver.  

  Instantiating a perceiver usually requires the detector, tracker, and filter
  instances to be complete.  These need to be defined. So do any other settings
  should be specific to how the perceiver will operate or what to do with the
  processed information, which will lie in the perceiver config field.
  """

  #
  # @todo   Why set as Algconfig and not dataclass?? What's proper approach?
  #         For now coding up since implementation is abstracted.  What matters
  #         is API. Can change later.
  #

  #------------------------------ __init__ -----------------------------
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    '''!
    @brief    Instantiate an (empty) perceiver builder configuration.
    '''

    if init_dict is None:
      init_dict = BuildCfgPerceiver.get_default_settings()
      # Default settings are empty.  

    super(BuildCfgPerceiver,self).__init__(init_dict, key_list, new_allowed)


  #------------------------ get_default_settings -----------------------
  #
  @staticmethod
  def get_default_settings():

    default_settings = dict(perceiver = None, detector = None, 
                            tracker = None, filter = None)
    return default_settings



#
#-------------------------------------------------------------------------------
#=============================== Perceiver Class ===============================
#-------------------------------------------------------------------------------
#

# Class description
class Perceiver(object):
  """!
  @ingroup  Perceiver
  @brief    Simple perceiver class.  Most basic implementation.
  """

  #============================== Perceiver ==============================
  #
  #
  def __init__(self, theParams, theDetector, theTracker, trackFilter):
    """!
    @brief  Constructor for the Perceiver class.
   
    @param[in] theParams    Option set of paramters. 
    @param[in] theDetector  The binary segmentation method.
    @param[in] theTracker   The binary image trackpoint method.
    @param[in] trackFilter  The track point filtering / data association approach.
    """

    print("This package file is deprecated. Move to perceiver.py")

    self.detector = theDetector
    self.tracker  = theTracker
    self.filter   = trackFilter

    if theParams:
      self.params = theParams
    else:
      self.params = CfgPerceiver()

    # states
    self.tPts = None
    self.haveRun   = False #< Was an observation measured? - e.g. detect a tracker
    self.haveObs   = False #< Do we have a state estimate? - e.g. human activity
    self.haveState = False #< Has not been run before.

    # data storage
    self.I = None

    # results. e.g., tpt of the trackpointers class
    self.tMeas = None #< The last measured track state of the target.

    # @note     Aren't tPts and tMeas the same?  I think so.  tMeas is
    # the revised name for tPts if I am not mistaken.  Review code to
    # see if use indicates different functionality.  If not, then please
    # have all be consistently named.

    # Process the run-time parameters.
    # Code missing.


  #================================ set ================================
  #
  # @brief      Set the state or parameters of the rigid body tracker.
  #
  # @param[in]  fname   Name of the field to set.
  # @param[in]  fval    Value to set.
  # 
  def set(self, fname, fval):

    if fname == 'state':
        self.setState(fval)


  #================================ get ================================
  #
  # @brief      Get the state or parameters of the tracker.
  #
  # @param[in]  fname   Name of the field to set.
  #
  # @param[out] fval    Value returned.
  #
  def get(self, fname):

    if fname == 'state':
      fval = self.getState()
    elif fname == 'trackParams'or fname == 'params':
      fval = self.params
    else:
      fval = []

    return fval
  
  #============================== getState =============================
  #
  # @brief      Returns the current state structure.
  # 
  # @param  cstate  The current state structure.
  #
  def getState(self):

    # @todo
    # Not used yet
    # cstate.g = self.gFilter.getState()
    # cstate.gOB   = self.gOB;

    cstate = State(tMeas = self.tMeas, haveObs = self.haveObs, haveState = self.haveState)

    return cstate

  #============================== setState =============================
  #
  # @brief      Sets the state of the tracker.
  #
  # @param[in]  nstate  The new state structure.
  #
  def setState(self, nstate):

    # @todo
    # gFilter.setState(nstate.g) NEED TO RECONSIDER HOW DONE.
    # FOR NOW USING A PASS THROUGH BUT COMMENTING OUT.
    # self.tracker.setState(nstate)

    if nstate.tPts:   # Permit empty: simply won't plot.
      self.tPts = nstate.tPts

    # @todo
    # Yiye had removed gOB. Not sure why. Bring back in when the
    # Lie group class package/namespace/library is up to date.
    #
    #if (isfield(nstate,'gOB') && ~isempty(nstate.gOB))
    #  this.gOB = nstate.gOB
    #end

    self.haveObs   = nstate.haveObs
    self.haveState = nstate.haveState

  
  #============================= emptyState ============================
  #
  # @brief      Return state structure with no information.
  #
  # @param[out] estate  The state structure with no content.
  #
  def emptyState(self):

    estate = State(haveObs=False, haveState=False)

    return estate

  #============================== process ==============================
  #
  # @brief  Run the tracking pipeline for one step/image measurement.
  #
  def process(self, I):

    self.predict()
    self.measure(I)
    self.correct()
    self.adapt()

  #============================ displayState ===========================
  #
  def displayState(self, dState=None):

    if not isinstance(dState,State):
      dState = self.getState()
  
    self.tracker.displayState()

    if self.params.display:
      if self.params.dispargs:
        self.params.display(dState, self.params.dispargs)
      else:
        self.params.display(dState)

  

  #============================ displayDebug ===========================
  #
  def displayDebug(self, fh, dbState):
    # Not implemented yet
    pass

  #================================ info ===============================
  #
  # @brief      Return the information structure used for saving or
  #             otherwise determining the tracker setup for
  #             reproducibility.
  #
  # @param[out] tinfo   The tracking configuration information structure.
  #
  def info(self):

    tinfo = Info(name=os.path.basename(__file__),
         version='1.0.0',
         data=time.strftime('%Y/%m/%d'),
         time=time.strftime('%H:%M:%S'),
         params=self.params)

    return tinfo

  #================================ free ===============================
  #
  # @brief      Destructor.  Just in case other stuff needs to be done.
  #
  def free(self):
    # Not implemented yet
    pass

  # @todo Eventually make these member functions protected and not public.

  #============================== predict ==============================
  #
  # @brief  Predict next measurement, if applicable.
  #
  def predict(self):
    # Not implemented yet
    pass
  # NOTE: this predict is designed to be any separate predictor other
  #       than that in the detector and tracker.  the component
  #       detector/tracker's predict (whole process) is executed in the
  #       measure function

  #============================== measure ==============================
  #
  # @brief  Recover track point or track frame based on detector +
  #         trackPointer output.
  #
  #
  def measure(self, I):

    # @note
    # NOTE TO YUNZHI: DO NOT FOLLOW THE DESIGN PATTERN OF YIYE.
    # THE RGB-D DATA IS A UNIT AND GETS PROCESSED AS SUCH.
    # ANY NECESSARY DECOUPLED DETECTION AND POST-PROCESSING SHOULD RESIDE
    # IN THE DETECTOR USING A HIERARCHICAL STRATEGY. IF RGB-D IMAGERY IS
    # PROCESSED IN A SPECIAL WAY, THEN LET THE DETECTOR HANDLE IT.
    # IT MIGHT BE TWO SEPARATE A THREADS WITH A UNION OR INTERSECTION
    # OPERATION TO JOIN, OR IT MIGHT BE A SEQUENTIAL OPERATION. DO NOT
    # FOLLOW THE MATLAB CODE. 
    #
    # IT UNDERMINES THE SIMPLICITY OF THE PROGRAMMING AND THE FLEXIBILITY
    # OF THE INTERFACE.
  
    #! Run measurement/processing.

    # Image-based detection and post processing.
    self.detector.process(I)

    # # @todo Not implemented yet
    # fgLayer = self.detector.getForeground()

    # Use Ip instead for now
    detState = self.detector.getState()
    fgLayer = detState.x

    # Tracking on binary segmentation mask.
    self.tracker.process(fgLayer)
    tstate = self.tracker.getState()

    if hasattr(tstate, 'g') and tstate.g is not None:
     self.tMeas = tstate.g
    elif hasattr(tstate, 'tpt') and tstate.tpt is not None:
     self.tMeas = tstate.tpt

    # @todo
    # MAYBE SHOULD JUST SET TO tstate IN CASE IT HAS EXTRA INFORMATION
    # THEN THIS CLASS JUST GRABS THE x FIELD. LET'S THE FIELD TAKE CARE
    # OF ITS OWN FUNCTIONALITY?
    #
    # YUNZHI: YES, GOING WITH THE ABOVE. IT MIGHT BREAK SOMETHING, BUT
    # THEN WE FIX IT.  WILL REQUIRE A Euclidean CLASS OR A
    # Lie.group.Euclidean INSTANCE (which is really just a vector).
    # SHOULD BE QUICK TO CODE UP AT ITS MOST BASIC.

    # @todo
    # self.gFilter.correct(this.tMeas) # DO WE NEED A FILTER? WHY NOT IN TRACKPOINTER?
     
    # Set observation flag
    self.haveObs = not np.isnan(self.tMeas).any()

  #============================== correct ==============================
  #
  # @brief  Correct the estimated state based on measured and predicted.
  #
  def correct(self):
    # Not implemented yet
    pass

  #=============================== adapt ===============================
  #
  # @brief  Adapt parts of the process based on measurements and
  # corrections.
  #
  def adapt(self):
    # Not implemented yet
    pass

  #=========================== displaySimple ===========================
  #
  # @brief      Basic rigid body display routine. Plots SE(2) frame.
  #
  @staticmethod
  def displaySimple(cstate, dispArgs):
    # Not implemented yet
    pass

  #============================ displayFull ============================
  #
  # @brief      Fill rigid body display routine. Plots SE(2) frame and
  #             marker positions.
  #
  # @todo
  # This function has not been tested yet
  #
  @staticmethod
  def displayFull(cstate, dispArgs):

    gCurr = cstate.gOB * cstate.g

    if dispArgs.state:
      gCurr.plot(dispArgs.state)
    else:
      gCurr.plot()
  
    if dispArgs.plotAll and dispArgs.plotAll:
      plt.plot(cstate.tPts[0,:], cstate.tPts[1,:])
  
    if dispArgs.noTicks and dispArgs.noTicks:
      plt.tick_params(labelleft=False, labelbottom=False)

    plt.show()
    plt.pause(0.1)

#
#============================ simple ============================
