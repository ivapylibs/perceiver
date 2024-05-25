#========================== perceiver.reports.trigger ==========================
"""!


@author   Patricio A. Vela,     pvela@gatech.edu 
@date     2024/04/04            [created]
"""
#========================== perceiver.reports.trigger ==========================
#!
#!NOTE:
#!  set indent to 2 spaces.
#!  do not indent function code.
#!  set tab to 4 spaces with conversion to spaces.
#!  90 columns, word margin 9 or 10. 
#
#========================== perceiver.reports.trigger ==========================

from ivapy.Configuration import AlgConfig


#=============================== BuildCfgTrigger ===============================
#

class BuildCfgTrigger(AlgConfig):
  """!
  @ingroup  Reports
  @brief    Configuration instance for building a Trigger.

  @warning  Not coded yet.
  """

  #------------------------------ __init__ -----------------------------
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    '''!
    @brief    Instantiate a trigger build configuration.
    '''

    if init_dict is None:
      init_dict = BuildCfgTrigger.get_default_settings()

    super(BuildCfgTrigger,self).__init__(init_dict, key_list, new_allowed)


  #------------------------ get_default_settings -----------------------
  #
  @staticmethod
  def get_default_settings():
    """!
    @brief  Get default build configuration settings for Trigger.
    """

    default_settings = dict()
    return default_settings



#=================================== Trigger ===================================
#

class CfgTrigger(AlgConfig):
  """!
  @ingroup  Reports
  @brief    Configuration instance for a Trigger.
  """

  #------------------------------ __init__ -----------------------------
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    '''!
    @brief    Instantiate a trigger build configuration.
    '''

    if init_dict is None:
      init_dict = CfgTrigger.get_default_settings()

    super(CfgTrigger,self).__init__(init_dict, key_list, new_allowed)


  #------------------------ get_default_settings -----------------------
  #
  @staticmethod
  def get_default_settings():
    """!
    @brief  Get default build configuration settings for Trigger.
    """

    default_settings = dict()
    return default_settings


class Trigger:
  """!
  @ingroup  Reports
  @brief    Base/abstract trigger class.

  A trigger determines when a particular state or signal should be reported.  In
  the python logging API, a trigger is similar to a filter and is tested before
  constructing the message or moving forward on state/signal reporting.  Usually,
  in logging some external process requests the log to happen, and the filter
  applies some logic to determine if the logging should be permitted.  

  Here, there is a continuously submitted state/signal and the choice must be made
  as to whether the state should be reported or not.   A trigger uses the history
  of a state--or possible other externally derived states--to estalish when to
  "announce" or report a given piece of information.  The announcer then pipes the
  message or announcement to the proper channel.  In the python logging API, a
  trigger is similar to a filter is tested before constructing the message or
  moving forward on state/signal reporting.  Usually, in logging some external
  process requests the log to happen, and the filter applies some logic to
  determine if the logging should be permitted.  Here, there is a continuously
  submitted state/signal and the choice must be made as to whether the state should
  be reported or not.   

  Various triggers are possible, such as always report, report only on change,
  report if equal to some reference, etc. The role of the trigger is to provide
  a binary indication as to whether the state/signal should be reported.
  """

  #============================== Trigger __init__ =============================
  #
  def __init__(self, theConfig = CfgTrigger()):
    """!
    @brief  Constructor for base trigger class.
    """
    if (theConfig is None):
      theConfig = CfgTrigger()

    self.config = theConfig

  #==================================== test ===================================
  #
  def test(self, theSig):
    """!
    @brief  Check if a report should be triggered for the supplied signal.

    The base class is the worst trigger possible. Always false.  There is
    no reporting.  For the opposite, use the always trigger.
    """
    return  False


#==================================== Always ===================================
#

class Always(Trigger):
  """!
  @ingroup  Reports
  @brief    Class that always triggers a report.
  """

  #============================== Always __init__ =============================
  #
  def __init__(self, theConfig = CfgTrigger()):
    """!
    @brief  Constructor for always trigger class.
    """
    super(Always,self).__init__(theConfig)

  #==================================== test ===================================
  #
  def test(self, theSig):
    """!
    @brief  Returns that a report should be triggered for the supplied signal.

    Always return True (opposite of the base class). 
    """
    return  True


#=================================== onChange ==================================
#

class onChange(Trigger):
  """!
  @ingroup  Reports
  @brief    Class that triggers a report when the state changes.

  In principle, the equality binary operator should work (be defined) for it.
  If the signal doesn't support equality, then try the whenDiffers trigger.
  """

  #============================== onChange __init__ =============================
  #
  def __init__(self, theConfig = CfgTrigger()):
    """!
    @brief  Constructor for onChange trigger class.
    """
    super(onChange,self).__init__(theConfig)

    self.prevSig = None
    self.isInit  = False

  #==================================== test ===================================
  #
  def test(self, theSig):
    """!
    @brief  Check if a report should be triggered for the supplied signal.

    Compare the passed signal to that from the last check (if there was one)
    and return true if they are not equal.  For non-trivial signals, the equality
    binary test should be overloading to return a meaningful binary outcome.

    On startup, there may be no previous signal.  In that case the first invocation
    returns a False and stores the signal for future invocations.
    """

    if self.isInit:
      changeCheck = not (self.prevSig == theSig)
    else:
      changeCheck = False

    self.prevSig = theSig

    return changeCheck

#================================== onMatch ==================================
#

class onMatch(Trigger):
  """!
  @ingroup  Reports
  @brief    Class that triggers a report when the state matches a target state.

  In principle, the equality binary operator should work (be defined) for it.
  If the signal doesn't support equality, then try the whenClose trigger.
  """

  #============================== onMatch __init__ =============================
  #
  def __init__(self, theConfig = CfgTrigger(), target):
    """!
    @brief  Constructor for onChange trigger class.
    """
    super(onMatch,self).__init__(theConfig)
    self.targSig = target

  #================================= newTarget =================================
  #
  #
  def newTarget(self, theTarg):
    """!
    @brief  Define the new target to check against.

    @param[in]  theTarg     New target instance.
    """

    self.targSig = theTarg;

  #==================================== test ===================================
  #
  def test(self, theSig):
    """!
    @brief  Report triggered when the passed signal matches the target signal.

    @param[in]  theSig      The passed signal.
    """
    return (self.targSig == theSig)


#================================== whenClose ==================================
#


class CfgWhenClose(AlgConfig):
  """!
  @ingroup  Reports
  @brief    Configuration instance for a Trigger.
  """

  #------------------------------ __init__ -----------------------------
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    '''!
    @brief    Instantiate a trigger build configuration.
    '''

    if init_dict is None:
      init_dict = CfgWhenClose.get_default_settings()

    super(CfgWhenClose,self).__init__(init_dict, key_list, new_allowed)


  #------------------------ get_default_settings -----------------------
  #
  @staticmethod
  def get_default_settings():
    """!
    @brief  Get default build configuration settings for Trigger.
    """

    default_settings = dict(tau = 0, distance = None)
    return default_settings


class whenClose(Trigger):
  """!
  @ingroup  Reports
  @brief    Class that triggers a report when current state is close to target state.

  If the signal differense is less than some specified quantity then trigger a report.
  Use when the the equality binary operator does not work (is not defined) or has
  non-robust behavior.
  """

  #============================= whenClose __init__ ============================
  #
  def __init__(self, theConfig, targSig):
    """!
    @brief  Constructor for whenClose trigger class.
    """
    super(whenDiffers,self).__init__(theConfig)
    self.targSig  = targSig

  #==================================== test ===================================
  #
  def test(self, theSig):
    """!
    @brief  Check if a report should be triggered for the supplied signal.

    The base class is the worst trigger possible. Always false.  There is
    no reporting.  For the opposite, use the always trigger.
    """

    return (self.config.distance(self.targSig, theSig) < self.config.tau)

#
#========================== perceiver.reports.trigger ==========================
