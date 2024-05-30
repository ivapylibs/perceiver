#========================= perceiver.reports.announcer =========================
"""!

@brief    API for (text) serializing an activity report.

An announcer generates the output that will be sent through the reporting channel.
The most basic version should be plain text, but we can envision other versions
like JSON or csv compliant outputs.  Any data storage scheme is valid as long as
it permits some form of sequential outputting and does not require backtracking.

@author   Patricio A. Vela,     pvela@gatech.edu 
@date     2024/05/23            [created]

IAMHERE
"""
#========================= perceiver.reports.announcer =========================
#!
#!NOTE:
#!  set indent to 2 spaces.
#!  do not indent function code.
#!  set tab to 4 spaces with conversion to spaces.
#!  90 columns, word margin 9 or 10. 
#
#========================= perceiver.reports.announcer =========================

from ivapy.Configuration import AlgConfig



#================================== Announcer ==================================
#

class CfgAnnouncer(AlgConfig):
  """!
  @ingroup  Reports
  @brief    Configuration instance for an Announcer.

  """

  #------------------------------ __init__ -----------------------------
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    '''!
    @brief    Instantiate a channel build configuration.
    '''

    if init_dict is None:
      init_dict = CfgAnnouncer.get_default_settings()

    super(CfgAnnouncer,self).__init__(init_dict, key_list, new_allowed)


  #------------------------ get_default_settings -----------------------
  #
  @staticmethod
  def get_default_settings():
    """!
    @brief  Get default build configuration settings for Trigger.
    """

    default_settings = dict(signal2text = None)
    return default_settings



class Announcer:
  """!
  @ingroup  Reports
  @brief    Base/abstract announcer class.

  An announcer packages a signal into text for reporting purposes.  The python
  logging API does not really have an analog to this because a logger is given the
  text to output.  Here, the signal is given and it must be converted to text.
  The conversion may require specific formatting needs to render it interpretable by a
  follow-up post-processing routine, or it might even not be text.  An overloaded
  announcer may package it up differently for the channel to output, based on the
  channel design (it may serialize data provided in a specific format as in the case
  of ROS messages).

  The base announcer relies on function pointers that perform signal translation.
  """

  #============================== Channel __init__ =============================
  #
  def __init__(self, theConfig):
    """!
    @brief  Constructor for announcer class.
    """
    self.config = theConfig
    self.announcement = None

  #================================== prepare ==================================
  #
  def prepare(self, theSignal):
    self.announcement = self.config.signal2text(theSignal)


  #========================= signal2text static methods ========================
  #

  @staticmethod
  def float2text(fspec):
    """!
    @brief  Convert float to string based on preset specification.

    @param[in]  fspec   The given specification.

    @return     Returns a function pointer that convert float to string.
    """

    return inF2T

    def inF2T(fsig):
      return fspec.format(fsig)


  @staticmethod
  def int2text(isig):
    """!
    @brief  Convert integer to string.

    @param[in]  isig   The integer.

    @return     Returns integer as a string. 
    """
    return str(isig)

  @staticmethod
  def text2text(ssig):
    """!
    @brief  Signal is already a string, so just return. (Should be rare)

    @param[in]  ssig   The string.

    @return     Returns same string. 
    """
    return ssig


#
#========================= perceiver.reports.announcer =========================
