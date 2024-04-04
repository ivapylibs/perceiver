#========================== perceiver.reports.trigger ==========================
"""!

@brief    API for reporting triggers. 

A trigger determines when a particular state or signal should be reported.  In
the python logging API, a trigger is similar to a filter is tested before
constructing the message or moving forward on state/signal reporting.  Usually,
in logging some external process requests the log to happen, and the filter
applies some logic to determine if the logging should be permitted.  Here, there
is a continuously submitted state/signal and the choice must be made as to
whether the state should be reported or not.   

Various triggers are possible, such as always report, report only on change,
report if equal to some reference, etc.


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

#IAMHERE: NEED TO REVIEW AND REVISE QUICKLY DUMPED/PASTED CODE.

class BuildCfgReporter(AlgConfig):
  """!
  @ingroup  Reporter_Trigger
  @brief    Configuration instance for a Trigger.

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

class Trigger:
  """!
  @ingroup  Reporter_Trigger
  @brief    Base/abstract trigger class.

  A trigger uses history of a state--or possible other externally derived 
  states--to estalish when to "announce" or report a given piece of information.
  The announcer then pipes the message or announcement to the proper channel.  In
  the python logging API, a trigger is similar to a filter is tested before
  constructing the message or moving forward on state/signal reporting.  Usually,
  in logging some external process requests the log to happen, and the filter
  applies some logic to determine if the logging should be permitted.  Here,
  there is a continuously submitted state/signal and the choice must be made as
  to whether the state should be reported or not.   

  Various triggers are possible, such as always report, report only on change,
  report if equal to some reference, etc. The role of the trigger is to provide
  a binary indication as to whether the state/signal should be reported.
  """

  #============================== Trigger __init__ =============================
  #
  def __init__(self):
    """!
    @brief  Constructor for base trigger class.
    """
    pass

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
  @ingroup  Reporter_Trigger
  @brief    Class that always triggers a report.
  """

  #============================== Always __init__ =============================
  #
  def __init__(self):
    """!
    @brief  Constructor for always trigger class.
    """
    super(Always,self).__init__(init_dict, key_list, new_allowed)

  #==================================== test ===================================
  #
  def test(self, theSig):
    """!
    @brief  Check if a report should be triggered for the supplied signal.

    The base class is the worst trigger possible. Always false.  There is
    no reporting.  For the opposite, use the always trigger.
    """

    return  True


#=================================== onChange ==================================
#

class onChange(Trigger):
  """!
  @ingroup  Reporter_Trigger
  @brief    Class that triggers a report when the state changes.

  In principle, the equality binary operator should work (be defined) for it.
  If the signal doesn't support equality, then try the whenDiffers trigger.
  """

  #============================== onChange __init__ =============================
  #
  def __init__(self, theConfig = CfgOnChange()):
    """!
    @brief  Constructor for onChange trigger class.
    """
    super(onChange,self).__init__(init_dict, key_list, new_allowed)

    if (theConfig is None):
      theConfig = CfgOnChange()

    self.xPrev = None

  #==================================== test ===================================
  #
  def test(self, theSig):
    """!
    @brief  Check if a report should be triggered for the supplied signal.

    The base class is the worst trigger possible. Always false.  There is
    no reporting.  For the opposite, use the always trigger.
    """

    eqCheck = (self.prevSig == theSig)
    return  True


#================================== onMatch ==================================
#

class onMatch(Trigger):
  """!
  @ingroup  Reporter_Trigger
  @brief    Class that triggers a report when the state matches a target state.

  In principle, the equality binary operator should work (be defined) for it.
  If the signal doesn't support equality, then try the whenClose trigger.
  """

  #============================== onMatch __init__ =============================
  #
  def __init__(self, theConfig = CfgOnMatch()):
    """!
    @brief  Constructor for onChange trigger class.
    """
    super(onMatch,self).__init__(init_dict, key_list, new_allowed)

    if (theConfig is None):
      theConfig = CfgOnMatch()

    self.targSig = None

  #==================================== test ===================================
  #
  def test(self, theSig):
    """!
    @brief  Check if a report should be triggered for the supplied signal.

    The base class is the worst trigger possible. Always false.  There is
    no reporting.  For the opposite, use the always trigger.
    """

    eqCheck = (self.targSig == theSig)
    return  True


#================================== whenClose ==================================
#

class whenClose(Trigger):
  """!
  @ingroup  Reporter_Trigger
  @brief    Class that triggers a report when current state is close to target state.

  If the signal differense is less than some specified quantity then trigger a report.
  Use when the the equality binary operator does not work (is not defined) or has
  non-robust behavior.
  """

  #============================= whenClose __init__ ============================
  #
  def __init__(self, theConfig = CfgWhenClose()):
    """!
    @brief  Constructor for whenClose trigger class.
    """
    super(whenDiffers,self).__init__(init_dict, key_list, new_allowed)

    if (theConfig is None):
      theConfig = CfgWhenClose()

    self.xPrev = None

  #==================================== test ===================================
  #
  def test(self, theSig):
    """!
    @brief  Check if a report should be triggered for the supplied signal.

    The base class is the worst trigger possible. Always false.  There is
    no reporting.  For the opposite, use the always trigger.
    """

    eqCheck = (self.prevSig == theSig)
    return  self.distance(self.targSig, theSig) < self.config.tau



#
#============================== perceiver.reporter =============================
