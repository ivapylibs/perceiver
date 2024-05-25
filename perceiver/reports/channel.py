#========================== perceiver.reports.channel ==========================
"""!

@author   Patricio A. Vela,     pvela@gatech.edu 
@date     2024/04/04            [created]

IAMHERE
"""
#========================== perceiver.reports.channel ==========================
#!
#!NOTE:
#!  set indent to 2 spaces.
#!  do not indent function code.
#!  set tab to 4 spaces with conversion to spaces.
#!  90 columns, word margin 9 or 10. 
#
#========================== perceiver.reports.channel ==========================

from ivapy.Configuration import AlgConfig


#=============================== BuildCfgChannel ===============================
#

class BuildCfgChannelr(AlgConfig):
  """!
  @ingroup  Reports
  @brief    Configuration instance for a Channel.

  """

  #------------------------------ __init__ -----------------------------
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    '''!
    @brief    Instantiate a channel build configuration.
    '''

    if init_dict is None:
      init_dict = BuildCfgChannel.get_default_settings()

    super(BuildCfgChannel,self).__init__(init_dict, key_list, new_allowed)


  #------------------------ get_default_settings -----------------------
  #
  @staticmethod
  def get_default_settings():
    """!
    @brief  Get default build configuration settings for Trigger.
    """

    default_settings = dict()
    return default_settings


#=================================== Channel ===================================
#

class Channel:
  """!
  @ingroup  Reports
  @brief    Base/abstract trigger class.

  A channel implements a reporting scheme.  In the python logging API, a channel is
  similar to the combination of a handler and a formatter.  When a report is
  triggered, then the channel needs to take care of outputting to the desired
  reporting output "stream" the proper message.

  Various channel types are possible. 
  """

  #============================== Channel __init__ =============================
  #
  def __init__(self):
    """!
    @brief  Constructor for base trigger class.
    """
    pass

    return  False

  #==================================== send ===================================
  #
  def send(self):
    pass

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
