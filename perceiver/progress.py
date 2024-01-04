#============================== perceiver.progress =============================
"""!

@brief    A simple interface class for monitoring the outcomes of a perceived scene.

A progress monitor accepts a target or goal state and attempts to estimate the
progress towards it based on perceiver extracted state estimates.

The choice was made to have the Progress monitor class independent of the Perceiver
class (i.e., not a derived class of it).  Rather it will receive a Perceiver instance
and snag the signals from it as needed.  Doing so permits a little more flexibility
regarding how the actual implementation operates, which may be a future need.  It is
still put in the perceiver package based on the implicit messaging of the "perceiver"
name and its reliance on a perceiver to get the job done.

See Monitor class documentation for more justification of having a perceiver be a
contained instance.  A good example would be that both activity and progress
monitoring rely on the same underlying perceiver.  There should be no reason to
require the entire process to be run twice for both monitors.  The outer scope may
even call the perceiver processing first, then pass on the outcomes to these two
individual monitors.

@author   Patricio A. Vela,     pvela@gatech.edu 
@date     2024/01/04            [created]
"""
#============================== perceiver.progress =============================
#!
#!NOTE:
#!  set indent to 2 spaces.
#!  do not indent function code.
#!  set tab to 4 spaces with conversion to spaces.
#!  90 columns 
#
#============================== perceiver.progress =============================

# Import any necessary libraries/packages.

import os
import matplotlib.pyplot as plt
import time
import numpy as np
from dataclasses import dataclass

from ivapy.Configuration import AlgConfig
from ivapy.Configuration import BuildConfig
import perceiver.perceiver as Perceiver

# PERCEIVER DATACLASS: State
# PERCEIVER DATACLASS: Info


@dataclass
class ProgressState:
  pLevel:    any
  haveObs:   bool = False

#
#-------------------------------------------------------------------------------
#============================= Configuration Nodes =============================
#-------------------------------------------------------------------------------
#


#================================= CfgProgress =================================
#
class CfgProgress(AlgConfig):
  """!
  @ingroup  Perceiver
  @brief    Configuration instance for a Progress monitor.  

  Instantiating a progress monitor requires the perceiver and goal comparator
  instances to be complete.  Any other settings should be specific to how the
  progress monitor will operate or what to do with the processed information.
  """

  #------------------------------ __init__ -----------------------------
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    """!
    @brief    Instantiate a progress monitor configuration node.
    """

    if init_dict is None:
      init_dict = CfgMonitor.get_default_settings()

    super(CfgMonitor,self).__init__(init_dict, key_list, new_allowed)


  #------------------------ get_default_settings -----------------------
  #
  @staticmethod
  def get_default_settings():

    default_settings = dict(display = None, version = None)
    return default_settings

    # @todo     What should this be?


#=============================== BuildCfgProgress ==============================
#
class BuildCfgProgress(BuildConfig):
  """!
  @ingroup  Perceiver
  @brief    Build configuration instance for a progress monitor.  

  Instantiating a monitor requires perceiver and state comparator instances
  (with some very specific exceptions).  These need to be defined to build
  out a monitor. 
  """
  #
  # @note   See todo markdowns in Monitor and Perceiver classes.
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

    default_settings = dict(perceiver = None, comparator = None)
    return default_settings


#
#-------------------------------------------------------------------------------
#================================ Progress Class ===============================
#-------------------------------------------------------------------------------
#

class Progress(object):
  """!
  @ingroup  Perceiver
  @brief    A simple interface class for progress monitoring a perceived scene.
  
  A Progress monitor tacks on some form of state comparison to make interpret the
  perceiver information.  
  
  The Progress monitoring class is independent of the Perceiver class (i.e., not a
  derived class of it).  Rather it contains a Perceiver instance from which to snags
  the signals needed.  This construction permits flexibility regarding how the actual
  implementation operates.  Progress monitoring is in the perceiver package based on
  the implicit messaging of the "perceiver" name and the consequence of progress
  monitoring.

  """

  #================================ Monitor ================================
  #
  #
  def __init__(self, theParams, thePerceiver, theComparator):
    """!
    @brief  Constructor for the perceiver.monitor class.
  
    @param[in] theParams        Option set of paramters. 
    @param[in] thePerceiver     Perceiver instance (or possibly not).
    @param[in] theComparator    State comparator instance.
    """

    self.perceiver  = thePerceiver  #< Perceiver instance.
    self.comparator = theComparator #< State comparison.

    if theParams:
      self.params = theParams
    else:
      self.params = CfgProgress()

    # states
    self.pLevel    = 0   #< progress level. 

    # @todo Does comparator have the level, or does it return level to this scope?

    # @todo Code missing. Process the run-time parameters. Maybe no need for base
    #       version.


  #============================== emptyState =============================
  #
  #
  def emptyState(self):
    """!
    @brief      Returns an empty activity state structure.
    
    @return     Empty activity state structure.
    """

    estate = ProgressState(pLevel = 0)
    return estate

  #=============================== getState ==============================
  #
  #
  def getState(self):
    """!
    @brief      Returns the current activity state structure.
    
    @param  cstate  The current state structure.
    """

    cstate = ProgressState(pLevel = self.pLevel) 
    return cstate

  #============================== setState =============================
  #
  #
  def setState(self, nstate):
    """!
    @brief      Sets the state of the tracker. Dangerous to override if inconsistent
                with scene.
   
    @param[in]  nstate  The new state structure.
    """

    self.pLevel  = nstate.pLevel
    self.haveObs = nstate.haveObs

  
  #=============================== process ===============================
  #
  #
  def process(self, I):
    """!
    @brief  Run perceive + progress estimation pipeline for one step/image
            measurement.
    """

    self.predict()
    self.measure(I)
    self.correct()
    self.adapt()

  #============================ displayState ===========================
  #
  def displayState(self, dState = None):

    if dState is None: 
      dState = self.getState()
  
    self.perceiver.displayState()

    # @todo Missing code here. Just doing a print. Change later on.
    print("Progress: " + str(self.pLevel))


  #============================ displayDebug ===========================
  #
  def displayDebug(self, fh, dbState):
    # Not implemented yet
    pass

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

    tinfo = Info(name=os.path.basename(__file__),
         version='1.0.0',
         data=time.strftime('%Y/%m/%d'),
         time=time.strftime('%H:%M:%S'),
         params=self.params)

    return tinfo

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
   
    @todo Is this proper way to conceive of progress monitor predict?
    """
    # Both will run in measure as of now.
    pass

  #=============================== measure ===============================
  #
  #
  def measure(self, I):
    """!
    @brief  Measure progress level from raw scene input.
    """

    self.perceiver.process(I)
    self.activity.process(self.perceiver.getState())

    # do post processing to collect what is needed.

  #=============================== correct ===============================
  #
  #
  def correct(self):
    """!
    @brief  Correct the estimated level based on measured and predicted.
   
    Currently the perceiver and comparator have already run their version of 
    correct by this point.  Overload this class should that not be the case.
    """
    pass

  #================================ adapt ================================
  #
  #
  def adapt(self):
    """!
    @brief  Adapt parts of the process based on measurements and corrections.
   
    Currently the perceiver and comparator have already run their version of 
    adapt by this point.  Overload this class should that not be the case.
    """
    pass

#
#============================== perceiver.progress =============================
