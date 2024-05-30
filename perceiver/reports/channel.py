#========================== perceiver.reports.channel ==========================
"""!

@author   Patricio A. Vela,     pvela@gatech.edu 
@date     2024/04/04            [created]

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



#=================================== Channel ===================================
#

class CfgChannel(AlgConfig):
  """!
  @ingroup  Reports
  @brief    Configuration instance for a Channel.
  """

  #------------------------------ __init__ -----------------------------
  #
  def __init__(self, init_dict=None, key_list=None, new_allowed=True):
    """!
    @brief    Instantiate a channel build configuration.
    """

    if init_dict is None:
      init_dict = CfgChannel.get_default_settings()

    super(CfgChannel,self).__init__(init_dict, key_list, new_allowed)


  #------------------------ get_default_settings -----------------------
  #
  @staticmethod
  def get_default_settings():
    """!
    @brief  Get default build configuration settings for Trigger.
    """

    default_settings = dict()
    return default_settings


class Channel:
  """!
  @ingroup  Reports
  @brief    Base/abstract channel class.

  A channel implements a reporting scheme.  In the python logging API, a channel is
  similar to the combination of a handler and a formatter.  When a report is
  triggered, then the channel needs to take care of outputting to the desired
  reporting output "stream" the proper message.

  Various channel types are possible, with stdout and a text file being more typical
  examples.  Using stdout provides a similar functionality to a logger but with the
  signal to text conversion encapsulated within its processing structure.  In contrast
  a logger would be given the converted string to start with.

  The base class here implicitly uses stdout through a print statement.  Overload via
  a derived class to send elsewhere.
  """

  #============================== Channel __init__ =============================
  #
  def __init__(self, theConfig = CfgChannel()):
    """!
    @brief  Constructor for base trigger class.
    """
    self.config = theConfig

  #==================================== send ===================================
  #
  def send(self, theAnnouncement):
    print(theAnnouncement)

#
#========================== perceiver.reports.channel ==========================
