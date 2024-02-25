#============================== perceiver.monitor ==============================
"""!

@brief    A simple interface class for monitoring the outcomes of a perceived scene.

A Monitor tacks on some form of action recognition to make sense of the perceiver
information. As in it monitors the activity state of the perceived scene and
reports out the activity observations.  If the intent is to compare against some
target state or establish completion, then take a look at the Progress subclass.
It tacks on a target/goal state and includes a progress estimator.

The choice was made to have the Monitor class independent of the Perceiver class
(i.e., not a derived class of it).  Rather it will receive a Perceiver instance and
snag the signals from it as needed.  Doing so permits a little more flexibility
regarding how the actual implementation operates, which may be a future need.
It is still put in the perceiver package based on the implicit messaging of the
"perceiver" name. Of course, such a design might interfere with or render
difficult factory methods (24/01/12: to be determined as implemented).

One reason to change this later on would be that some systems might start with
a perceiver but then later receive an upgrade to a monitor but keep the same overall
API.  While it doesn't make sense in a standard sequential processing setting, it
does make sense in a federated processing (like ROS) setting as it will simply
adjust the published topics in a natural manner.  We won't know what's best until
actually getting there.  I do believe that it is possible to create an interface
that is agnostic to this difference.  The core interface may not be agnostic, but
specialized builder methods could be; one that takes argument minimal inputs and one
that takes argument maximal inputs and builds intermediate instances before passing
on the argument minimal version. That might be best. [01/04/2024]

@author   Patricio A. Vela,     pvela@gatech.edu 
@date     2024/01/04            [created]
"""
#============================== perceiver.monitor ==============================
#!
#!NOTE:
#!  set indent to 2 spaces.
#!  do not indent function code.
#!  set tab to 4 spaces with conversion to spaces.
#!  90 columns 
#
#============================== perceiver.monitor ==============================

# Import any necessary libraries/packages.

import os
import matplotlib.pyplot as plt
import time
import numpy as np
from dataclasses import dataclass

from ivapy.Configuration import AlgConfig
from ivapy.Configuration import BuildConfig
import perceiver.perceiver as Perceiver
from detector.base import ActivityState

# PERCEIVER DATACLASS: State
# PERCEIVER DATACLASS: Info


#
#-------------------------------------------------------------------------------
#============================= Configuration Nodes =============================
#-------------------------------------------------------------------------------
#


#================================== CfgMonitor =================================
#
class CfgMonitor(AlgConfig):
  """!
  @ingroup  Perceiver
  @brief    Configuration instance for a Monitor.  

  Instantiating a monitor requires the perceiver and activity detector instances to
  be complete.  Thus any other settings should be specific to how the perceiver will
  operate or what to do with the processed information.

  Fields of the CfgMonitor include:

  | Field       | Meaning |
  | :---        | :------- |
  | external    | Is the perceiver already externally called? If so, then Monitor implementation avoids invoking Perceiver process routine during its own processing. |
  | display     | Set to "basic" for simple display; "overlay" for pure
  image-based display. |
  | displayDebug    | Set to "basic" for simple display; "overlay" for pure
  image-based display. |
  """

  #------------------------------ __init__ -----------------------------
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    """!
    @brief    Instantiate a monitor configuration node.
    """

    if init_dict is None:
      init_dict = CfgMonitor.get_default_settings()

    super(CfgMonitor,self).__init__(init_dict, key_list, new_allowed)


  #------------------------ get_default_settings -----------------------
  #
  @staticmethod
  def get_default_settings():

    default_settings = dict(external = False, display = "basic", 
                            displayDebug = "basic")
    return default_settings

    # @todo     What should this be?


#=============================== BuildCfgMonitor ===============================
#
class BuildCfgMonitor(BuildConfig):
  """!
  @ingroup  Perceiver
  @brief    Build configuration instance for a monitor.  

  Instantiating a monitor requires perceiver and activity recognition instances
  (with some very specific exceptions).  These need to be defined to build
  out a monitor. 
  """
  #
  # @todo   Unlike Perceiver, setting as BuildConfig instance in Configuration
  #         package space.  If implementation should change because a better
  #         approach has been established, then change there.  At this level, the
  #         implementation is abstracted.  Left as todo because of chained
  #         dependence on the BuildCfgPerceiver for consistency of implementation.
  #         When that todo goes, then so should this one.
  #

  #------------------------------ __init__ -----------------------------
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    """!
    @brief    Instantiate an (empty) monitor builder configuration.
    """

    if init_dict is None:
      init_dict = BuildCfgPerceiver.get_default_settings()
      # Default settings are empty.  

    super(BuildCfgMonitor,self).__init__(init_dict, key_list, new_allowed)


  #------------------------ get_default_settings -----------------------
  #
  @staticmethod
  def get_default_settings():
    """!
    @brief  Default (empty) build configuration for monitor.
    """

    default_settings = dict(perceiver = None, activity = None)
    return default_settings



#
#-------------------------------------------------------------------------------
#=============================== Monitor Class =================================
#-------------------------------------------------------------------------------
#

class Monitor(object):
  """!
  @ingroup  Perceiver
  @brief    A simple interface class for monitoring the outcomes of a perceived scene.
  
  A Monitor tacks on some form of action recognition to make sense of the perceiver
  information.  If the intent is to compare against some target state or establish
  completion, then take a look at the Progress subclass.  It tacks on a target/goal
  state and includes a progress estimator.
  
  The choice was made to have the Monitor class independent of the Perceiver class
  (i.e., not a derived class of it).  Rather it will receive a Perceiver instance and
  snag the signals from it as needed.  Doing so permits a little more flexibility
  regarding how the actual implementation operates, which may be a future need.
  It is still put in the perceiver package based on the implicit messaging of the
  "perceiver" name.

  """

  #================================ Monitor ================================
  #
  #
  def __init__(self, theParams, thePerceiver, theActivity, theReporter = None):
    """!
    @brief  Constructor for the perceiver.monitor class.
  
    @param[in] theParams    Option set of paramters. 
    @param[in] thePerceiver Perceiver instance (or possibly not).
    @param[in] theActivity  Activity detector/recognizer.
    @param[in] theReporter  Reporting mechanism for activity outputs.
    """

    if theParams is None:            # Done this way since first arg.
      theParams = CfgMonitor()

    self.perceiver = thePerceiver   #< Perceiver instance.
    self.activity  = theActivity    #< Activity detection/recognition instance.
    self.reporter  = theReporter    #< Takes activity outcomes and creates report out.

    self.params = theParams
    # TODO: Delete this code when finalized and confirmed to work.
    # COMMENTED OUT MEMBER VARIABLES SINCE CONTAINED IN perceiver and activity.
    #states
    #self.xActivity = None  # Activity state.
    #self.haveRun   = False # Was an observation measured? - e.g. detect a tracker
    #self.haveObs   = False # Do we have a state estimate? - e.g. human activity
    #self.haveState = False # Has not been run before.
    #
    # @todo One reason the Monitor member variables aren't fully locked down is
    # because the perceiver itself is not really fully implemented.  Only what
    # has been needed.  That needs to change.

    # @todo Code missing. Process the run-time parameters. Maybe no need for base
    #       version.


  #============================== emptyState =============================
  #
  #
  def emptyState(self):
    """!
    @brief      Returns an empty activity state structure.

    Snags default empty state from the activity instance.
    
    @return     Empty activity state structure.
    """

    estate = self.activity.getEmptyState()
    return estate

  #=============================== getState ==============================
  #
  #
  def getState(self):
    """!
    @brief      Returns the current activity state structure.

    Default is to pass request along to the activity detector.
    
    @param  cstate  The current state structure.
    """

    cstate = self.activity.getState()
    return cstate

  #============================== setState =============================
  #
  #
  def setState(self, nstate):
    """!
    @brief      Sets the state of the tracker.

    Sends passed state along to the activity detector.
   
    @param[in]  nstate  The new state structure.
    """

    self.activity.setState(nstate)

  
  #=============================== process ===============================
  #
  #
  def process(self, I):
    """!
    @brief  Run perceive + activity recognize pipeline for one step/image
            measurement.
    """

    self.predict()
    self.measure(I)
    self.correct()
    self.adapt()

  #============================ displayState ===========================
  #
  def displayState(self, dState = None):
    """!
    @brief  Display the perceiver state and activity state per configuration
            specification.

    @param[in]  dState  Monitor state to display (optional). Default is current state.
    """

    if (self.params.display == 'basic'):
      if dState is None: 
        self.perceiver.displayState()
        self.activity.printState()
      else:
        self.perceiver.displayState(dState.perceiver)
        self.activity.printState(dState.activity)

    elif (self.params.display == 'overlay'):
      # @todo Need to implement.  Requires window name.  Not an argument.
      #       For now do not invoke this version.
      if dState is None: 
        self.perceiver.displayState()
        self.activity.displayState()
      else:
        self.perceiver.displayState(dState.perceiver)
        self.activity.displayState(dState.activity)

  #============================ displayDebug ===========================
  #
  def displayDebug(self, dbState = None):
    """!
    @brief  Display the debug state. Punts to contained instances.
    """
    if (params.displayDebug == 'basic'):
      if dState is None: 
        self.perceiver.displayState()
        self.activity.printState()
      else:
        self.perceiver.displayState(dState.perceiver)
        self.activity.printState(dState.activity)

    elif (params.display == 'overlay'):
      # @todo Need to implement.  Requires window name.  Not an argument.
      #       For now do not invoke this version.
      if dState is None: 
        self.perceiver.displayState()
        self.activity.displayState()
      else:
        self.perceiver.displayState(dState.perceiver)
        self.activity.displayState(dState.activity)

  #================================ info ===============================
  #
  #
  def info(self):
    """!
    @brief      Return the information structure used for saving or
                otherwise determining the tracker setup for
                reproducibility.
   
    @param[out] tinfo   The tracking configuration information structure.
    """

    return None
#    tinfo = Info(name=os.path.basename(__file__),
#         version='1.0.0',
#         data=time.strftime('%Y/%m/%d'),
#         time=time.strftime('%H:%M:%S'),
#         params=self.params)
#
#    return tinfo

  #================================= free ================================
  #
  #
  def free(self):
    """!
    @brief      Destructor.  Just in case other stuff needs to be done.
    """
    pass

  # @todo Eventually make these member functions protected and not public.

  #=============================== predict ===============================
  #
  def predict(self):
    """!
    @brief  Predict next measurement, if applicable.
   
    @todo Is this proper way to conceive of monitor predict?
    """
    # Both will run in measure as of now.
    pass

  #=============================== measure ===============================
  #
  #
  def measure(self, I):
    """!
    @brief  Run activity detection process to generate activity state measurement. 
            If perceiver has no measurement/observation, then does nothing.

    @param[in]  I   Image to process. Depending on implementation, might be optional.
    """

    if not self.params.external:    # Perceiver process not externally called.
      self.perceiver.process(I)     # so should run perceiver process now.

    self.activity.process(self.perceiver.getState())

    # do post processing to collect what is needed.

  #=============================== correct ===============================
  #
  #
  def correct(self):
    """!
    @brief  Correct the estimated state based on measured and predicted.
   
    Currently the perceiver and activty detector have already run their
    version of correct by this point.  Overload this class should that not 
    be the case.
    """
    pass

  #================================ adapt ================================
  #
  #
  def adapt(self):
    """!
    @brief  Adapt parts of the process based on measurements and corrections.
   
    Currently the perceiver and activty detector have already run their
    version of adapt by this point.  Overload this class should that not 
    be the case.
    """
    pass



#
#============================== perceiver.monitor ==============================
